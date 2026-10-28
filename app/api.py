"""API HTTP du skill tree (FastAPI) + service de l'interface statique."""
from __future__ import annotations

import asyncio
import copy
import io
import json
import os
import random
import re
import secrets
from . import db_compat as sqlite3
import tempfile
import time
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from collections import Counter
from contextlib import asynccontextmanager
from functools import lru_cache
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from .auth import (
    AUTH_COOKIE_NAME,
    AUTH_SESSION_TTL_SECONDS,
    auth_configuration_ready,
    auth_required,
    clear_login_failures,
    create_session_token,
    login_is_limited,
    record_failed_login,
    verify_password,
    verify_session_token,
)
from .db import (
    DEFAULT_DB, XP_REWARDS, add_xp, award_attempt_xp, connect, ensure_ready,
    get_user_stats, touch_daily_streak, streak_days,
)
from .domain import Node, ProofKind, Question, Requirement, Status
from .exam_rules import EXAM_PASS_SCORE, effective_requirement_score
from .engine import (
    BADGE_DEFINITIONS, DomainError, SkillTree, get_daily_plan, is_validated, requirement_met, status_of,
)
from .labs_runner import (
    LabRunnerError, LabSessionError, exec_in_lab, start_interactive_lab, validate_lab,
)
from .loader import CONTENT_DIR, ContentError, find_lab_dir, load_content, load_lessons, sync_content_additions
from .lab_routes import (
    _fetch_lab,
    _strip_legacy_auto_practice_branch,
    router as lab_v2_router,
    seed_lab_v2_catalog,
)
from .lab_schema_v2 import Topology
from .scenario_loader import (SCENARIO_DIR, build_scenario, generate_random_scenario, get_scenario_options, load_scenario, list_scenarios)
from .war_badges import build_war_badges

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")

DB_PATH = Path(os.environ.get("SKILLTREE_DB", DEFAULT_DB))
STATIC_DIR = PROJECT_ROOT / "static"
FLASHCARDS_FILE = CONTENT_DIR / "flashcards" / "network.json"
SANDBOX_FILE = CONTENT_DIR / "sandbox" / "cisco_basics.json"
DIAGNOSTICS_DIR = CONTENT_DIR / "diagnostics"
TTS_VOICES = {"fr-FR-DeniseNeural", "fr-FR-HenriNeural"}
EXAM_QUESTION_COUNT = 20
EXAM_DURATION_SECONDS = 30 * 60
# Le seuil officiel est partagé par toutes les formes d’examen.
EXAM_SUBMIT_GRACE_SECONDS = 15
EXAM_MAX_QUESTION_COUNT = 500
EXAM_MIN_DURATION_SECONDS = 60
EXAM_MAX_DURATION_SECONDS = 8 * 60 * 60
GROQ_DEFAULT_MODEL = "openai/gpt-oss-120b"
GROQ_FALLBACK_MODEL = "openai/gpt-oss-20b"
GROQ_DEPRECATED_MODELS = {"llama3-8b-8192", "llama3-70b-8192"}
TUTOR_MAX_CONTEXT_CHARS = 14_000
CERTIFICATE_NAME = (os.environ.get("CERTIFICATE_NAME") or "Ton Nom").strip() or "Ton Nom"
CERTIFICATE_VERIFY_BASE_URL = (os.environ.get("CERTIFICATE_VERIFY_BASE_URL") or "").strip().rstrip("/")
DIAGNOSTIC_TIME_LIMIT_SECONDS = 120
DIAGNOSTIC_FAST_BONUS_SECONDS = 60
DIAGNOSTIC_FAST_BONUS_XP = 50


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

class AuthLoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2600)
    rate: float = Field(default=1.0, ge=0.8, le=1.6)

class SandboxCheckRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)

class ShopBuyRequest(BaseModel):
    item_id: str = Field(min_length=1, max_length=64)

class DiagnosticCompleteRequest(BaseModel):
    path: list[str] = Field(min_length=1, max_length=50)
    elapsed_seconds: float | None = Field(default=None, ge=0, le=86400)
    time_limit_seconds: int = Field(default=DIAGNOSTIC_TIME_LIMIT_SECONDS, ge=1, le=3600)


# --- GESTIONNAIRE WEBSOCKET ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()


def _markdown_to_plain_text(markdown: str) -> str:
    text = re.sub(r"```.*?```", " ", markdown, flags=re.S)
    text = re.sub(r"~~~.*?~~~", " ", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\|?[\s:|\-]+\|?\s*$", "", text, flags=re.M)
    text = text.replace("|", " ")
    text = re.sub(r"[*_~`]", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    conn = connect(DB_PATH)
    try:
        ensure_ready(conn)
        catalog_sync = sync_content_additions(conn)
        if any(catalog_sync.values()):
            print(f"Synchronisation additive du catalogue pédagogique : {catalog_sync}")
        seed_lab_v2_catalog(conn)
        _seed_war_room_tickets(conn)
    finally:
        conn.close()
    yield

from urllib.parse import quote, urlsplit

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware


def _cors_origins_from_environment(value: str | None = None) -> list[str]:
    """Charge une liste stricte d'origines CORS; une configuration vide reste same-origin."""
    raw = os.environ.get("SKILLTREE_CORS_ORIGINS", "") if value is None else value
    origins: list[str] = []
    for raw_origin in raw.split(","):
        origin = raw_origin.strip().rstrip("/")
        if not origin:
            continue
        if origin == "*":
            raise ValueError("SKILLTREE_CORS_ORIGINS interdit l'origine générique '*'.")
        parsed = urlsplit(origin)
        try:
            parsed.port
        except ValueError as error:
            raise ValueError("Origine CORS invalide dans SKILLTREE_CORS_ORIGINS.") from error
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "SKILLTREE_CORS_ORIGINS doit contenir uniquement des origines HTTP(S) explicites."
            )
        origins.append(origin)
    return list(dict.fromkeys(origins))


app = FastAPI(title="Skilltree API", lifespan=lifespan)

# Compresse les réponses textuelles volumineuses (HTML, JavaScript, CSS et JSON).
# Le navigateur reçoit moins de données sur le réseau, sans changer les payloads API.
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=6)

# Le frontend est servi depuis la même origine. Les intégrations cross-origin
# doivent être explicitement déclarées dans SKILLTREE_CORS_ORIGINS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins_from_environment(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


_AUTH_EXEMPT_PATHS = {
    "/api/auth/status",
    "/api/auth/login",
    "/api/auth/logout",
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
}
_AUTH_GATED_PAGES = {"/", "/index.html", "/lab.html"}


def _same_origin_request(request: Request) -> bool:
    """Reject browser state-changing requests whose Origin does not match this host."""
    origin = request.headers.get("origin")
    if not origin:
        return True
    try:
        parsed = urlsplit(origin)
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
        and parsed.netloc.lower() == request.url.netloc.lower()
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
    )


@app.middleware("http")
async def enforce_site_authentication(request: Request, call_next):
    """Protect the single-owner application's data API when auth is required."""
    if not auth_required():
        return await call_next(request)

    path = request.url.path
    if (
        request.method in {"POST", "PUT", "PATCH", "DELETE"}
        and path in {"/api/auth/login", "/api/auth/logout"}
        and not _same_origin_request(request)
    ):
        return JSONResponse(
            status_code=403,
            content={"detail": "Origine de requête refusée."},
            headers={"Cache-Control": "no-store"},
        )
    if path == "/login.html" or path in _AUTH_EXEMPT_PATHS:
        return await call_next(request)

    configured = auth_configuration_ready()
    authenticated = configured and verify_session_token(
        request.cookies.get(AUTH_COOKIE_NAME)
    )

    is_gated_page = (
        path in _AUTH_GATED_PAGES
        or (path.lower().endswith(".html") and path != "/login.html")
    )
    if is_gated_page and not authenticated:
        # Conserver la destination et ses paramètres (ex. ?openLab=... ou ?openTab=labs)
        # afin que la connexion reprenne l'action demandée au lieu du tableau de bord.
        requested_path = request.url.path
        if request.url.query:
            requested_path += "?" + request.url.query
        login_url = "/login.html"
        if requested_path != "/" or request.url.query:
            login_url += "?next=" + quote(requested_path, safe="")
        return RedirectResponse(url=login_url, status_code=303)

    if path.startswith("/api/"):
        if not configured:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": (
                        "Authentification non configurée. Configure SKILLTREE_AUTH_PASSWORD_HASH "
                        "et SKILLTREE_AUTH_SECRET avant d'ouvrir l'application."
                    )
                },
                headers={"Cache-Control": "no-store"},
            )
        if not authenticated:
            return JSONResponse(
                status_code=401,
                content={"detail": "Connexion requise."},
                headers={"Cache-Control": "no-store"},
            )
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if not _same_origin_request(request):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Origine de requête refusée."},
                    headers={"Cache-Control": "no-store"},
                )

    return await call_next(request)



@app.middleware("http")
async def cache_static_assets(request: Request, call_next):
    """Cache longtemps les ressources versionnées, sans figer les pages HTML."""
    response = await call_next(request)
    if response.status_code == 200:
        path = request.url.path
        version = request.query_params.get("v", "")
        if path.startswith("/assets/") and re.fullmatch(r"[0-9a-f]{12}", version):
            # Le paramètre v est calculé à partir du contenu minifié ; une nouvelle version a une nouvelle URL.
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif path.startswith(("/lab/assets/", "/lab/chunks/")):
            # Ces noms contiennent un hash : leur contenu ne change pas à URL identique.
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif path.endswith((".js", ".css", ".svg", ".woff", ".woff2", ".png", ".jpg", ".jpeg", ".webp", ".ico")):
            # Ressources sans version : TTL court pour éviter les versions périmées.
            response.headers["Cache-Control"] = "public, max-age=60, must-revalidate"
        elif path == "/" or path.endswith(".html"):
            # Revalidation à chaque navigation pour conserver les déploiements à jour.
            response.headers["Cache-Control"] = "no-cache"
    return response


@app.get("/api/auth/status")
def auth_status(request: Request, response: Response) -> dict[str, Any]:
    """Expose only non-sensitive auth state so the login page can render correctly."""
    required = auth_required()
    configured = auth_configuration_ready()
    response.headers["Cache-Control"] = "no-store, private, max-age=0"
    return {
        "required": required,
        "configured": configured,
        "authenticated": (
            not required
            or (
                configured
                and verify_session_token(request.cookies.get(AUTH_COOKIE_NAME))
            )
        ),
    }


@app.post("/api/auth/login")
def auth_login(payload: AuthLoginRequest, request: Request) -> Response:
    if not auth_required():
        return JSONResponse(
            {"success": True, "required": False, "authenticated": True},
            headers={"Cache-Control": "no-store"},
        )
    if not auth_configuration_ready():
        raise HTTPException(
            status_code=503,
            detail=(
                "Connexion indisponible : configure le hash de mot de passe et le secret "
                "de session dans les variables d'environnement du serveur."
            ),
            headers={"Cache-Control": "no-store"},
        )

    client_key = request.client.host if request.client else "unknown"
    if login_is_limited(client_key):
        raise HTTPException(
            status_code=429,
            detail="Trop de tentatives de connexion. Réessaie dans 15 minutes.",
            headers={"Retry-After": "900", "Cache-Control": "no-store"},
        )
    if not verify_password(payload.password):
        record_failed_login(client_key)
        raise HTTPException(
            status_code=401,
            detail="Mot de passe incorrect.",
            headers={"Cache-Control": "no-store"},
        )

    clear_login_failures(client_key)
    token = create_session_token()
    response = JSONResponse(
        {"success": True, "required": True, "authenticated": True},
        headers={"Cache-Control": "no-store"},
    )
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        max_age=AUTH_SESSION_TTL_SECONDS,
        httponly=True,
        secure=bool(os.environ.get("RENDER_SERVICE_ID")) or request.url.scheme == "https",
        samesite="strict",
        path="/",
    )
    return response


@app.post("/api/auth/logout")
def auth_logout(request: Request) -> Response:
    response = Response(status_code=204, headers={"Cache-Control": "no-store"})
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=bool(os.environ.get("RENDER_SERVICE_ID")) or request.url.scheme == "https",
        samesite="strict",
    )
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Ajoute des en-têtes de défense en profondeur sans casser le frontend actuel."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), geolocation=(), payment=()")
    return response


# Lab Workspace v2 : nouvelles routes séparées des endpoints legacy.

app.include_router(lab_v2_router, prefix="/api")


class TicketResolveRequest(BaseModel):
    topology: dict[str, Any]
    elapsed_seconds: float = Field(ge=0, le=86400)


class TicketPostMortemRequest(BaseModel):
    root_cause: str = Field(min_length=3, max_length=5000)
    impact: str = Field(min_length=3, max_length=5000)
    corrective_action: str = Field(min_length=3, max_length=5000)

class ScenarioSaveRequest(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    type: str
    severity: str
    topology: str
    fault_id: str
    target_device: str
    target_port: str
    sla_minutes: int = Field(ge=5, le=240)


def _war_room_now() -> datetime:
    return datetime.now(timezone.utc)


def _war_room_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _war_room_iso_precise(value: datetime) -> str:
    """Horodatage à la microseconde pour distinguer deux tentatives démarrées dans la même seconde."""
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _war_room_parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _ticket_payload(row: Any) -> dict[str, Any]:
    ticket = dict(row)
    try:
        ticket["resolution_data"] = json.loads(ticket.get("resolution_data") or "{}")
    except (TypeError, json.JSONDecodeError):
        ticket["resolution_data"] = {}
    return ticket


def _ticket_active_elapsed_seconds(ticket: dict[str, Any], ended_at: datetime | None = None) -> float:
    """Temps actif d'un ticket, hors périodes de pause SLA enregistrées."""
    opened_at = _war_room_parse_time(ticket.get("opened_at"))
    ended = ended_at or _war_room_parse_time(ticket.get("resolved_at")) or _war_room_now()
    if opened_at is None:
        return 0.0
    data = ticket.get("resolution_data")
    if not isinstance(data, dict):
        data = {}
    paused_total = max(0.0, float(data.get("paused_total_seconds") or 0))
    return max(0.0, (ended - opened_at).total_seconds() - paused_total)


def _ticket_sla_met(ticket: dict[str, Any]) -> bool:
    if ticket.get("status") != "resolved":
        return False
    data = ticket.get("resolution_data")
    if not isinstance(data, dict):
        data = {}
    if isinstance(data.get("sla_met"), bool):
        return data["sla_met"]
    ended = _war_room_parse_time(ticket.get("resolved_at"))
    deadline = _war_room_parse_time(ticket.get("sla_deadline"))
    return ended is not None and (deadline is None or ended <= deadline)


def _ticket_action(conn: Any, ticket_id: str, action_type: str, payload: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO ticket_actions (ticket_id, action_type, payload, at) VALUES (?, ?, ?, ?)",
        (ticket_id, action_type, json.dumps(payload, ensure_ascii=False), _war_room_iso(_war_room_now())),
    )

def _load_scenario_by_id(scenario_id: str, conn: Any | None = None) -> dict[str, Any]:
    """Charge les scénarios fichier, puis les scénarios RND enregistrés en base."""
    try:
        return load_scenario(scenario_id)
    except FileNotFoundError:
        if conn is not None:
            row = conn.execute(
                "SELECT scenario_json FROM war_room_scenarios WHERE scenario_id = ?",
                (str(scenario_id),),
            ).fetchone()
            if row:
                try:
                    scenario = json.loads(row["scenario_json"])
                    if isinstance(scenario, dict) and scenario.get("id") == scenario_id:
                        return scenario
                except (TypeError, json.JSONDecodeError):
                    pass
        raise FileNotFoundError(f"Scénario introuvable : {scenario_id}") from None


def _new_user_scenario_id() -> str:
    return "USER-" + _war_room_now().strftime("%Y%m%d%H%M%S%f") + "-" + secrets.token_hex(3).upper()


def _save_user_scenario_file(scenario: dict[str, Any]) -> str:
    """Écrit uniquement des identifiants USER-* et ne remplace jamais un fichier existant."""
    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    for _ in range(5):
        scenario_id = _new_user_scenario_id()
        path = SCENARIO_DIR / f"{scenario_id}.json"
        candidate = dict(scenario)
        candidate["id"] = scenario_id
        try:
            with path.open("x", encoding="utf-8") as handle:
                json.dump(candidate, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            scenario.clear()
            scenario.update(candidate)
            return f"content/scenarios/{path.name}"
        except FileExistsError:
            continue
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"Impossible d'enregistrer le scénario : {exc}") from exc
    raise HTTPException(status_code=500, detail="Impossible de générer un identifiant utilisateur unique.")


def _validate_scenario_document(scenario: Any) -> dict[str, Any]:
    """Vérifie les clés et la forme minimale d'un scénario partagé."""
    if not isinstance(scenario, dict):
        raise HTTPException(status_code=422, detail="Le scénario doit être un objet JSON.")
    missing = [key for key in ("id", "type", "initial_topology", "resolution_check") if key not in scenario]
    if missing:
        raise HTTPException(status_code=422, detail=f"Clés manquantes : {', '.join(missing)}.")
    if not isinstance(scenario.get("id"), str) or not scenario["id"].strip():
        raise HTTPException(status_code=422, detail="L'identifiant source du scénario est invalide.")
    if scenario.get("type") not in {"incident", "change", "problem"}:
        raise HTTPException(status_code=422, detail="Le type doit être incident, change ou problem.")
    topology = scenario.get("initial_topology")
    if not isinstance(topology, dict) or not isinstance(topology.get("nodes"), list) or not isinstance(topology.get("links"), list):
        raise HTTPException(status_code=422, detail="initial_topology doit contenir nodes et links.")
    node_ids = [str(node.get("id", "")) for node in topology["nodes"] if isinstance(node, dict)]
    if not node_ids or len(node_ids) != len(topology["nodes"]) or any(not node_id for node_id in node_ids):
        raise HTTPException(status_code=422, detail="La topologie doit contenir des équipements identifiés.")
    if len(node_ids) != len(set(node_ids)):
        raise HTTPException(status_code=422, detail="Les identifiants des équipements doivent être uniques.")
    checks = scenario.get("resolution_check")
    if not isinstance(checks, dict) or not isinstance(checks.get("rules"), list) or not checks["rules"]:
        raise HTTPException(status_code=422, detail="resolution_check doit contenir au moins une règle.")
    if not str(scenario.get("title") or "").strip():
        scenario["title"] = scenario["id"]
    if scenario.get("severity") not in {"low", "normal", "medium", "high", "critical"}:
        scenario["severity"] = "normal"
    scenario.setdefault("sla_minutes", 30)
    scenario.setdefault("reward_xp", 150)
    return scenario


def _expire_war_room_tickets(conn: Any, now: datetime | None = None) -> int:
    """Marque comme échoués les tickets actifs dont l'échéance SLA est dépassée."""
    current = now or _war_room_now()
    current_iso = _war_room_iso(current)
    rows = conn.execute(
        "SELECT * FROM tickets WHERE status IN ('open', 'pending_postmortem') AND sla_deadline IS NOT NULL"
    ).fetchall()
    expired = 0
    for row in rows:
        ticket = _ticket_payload(row)
        deadline = _war_room_parse_time(ticket.get("sla_deadline"))
        if deadline is None or current <= deadline:
            continue
        resolution_data = ticket.get("resolution_data") if isinstance(ticket.get("resolution_data"), dict) else {}
        resolution_data.update({
            "reason": "sla_exceeded",
            "failed_at": current_iso,
            "sla_met": False,
        })
        conn.execute(
            "UPDATE tickets SET status = 'failed', resolved_at = ?, resolution_data = ? WHERE id = ?",
            (current_iso, json.dumps(resolution_data, ensure_ascii=False), ticket["id"]),
        )
        _ticket_action(conn, ticket["id"], "failed", {
            "reason": "sla_exceeded",
            "sla_deadline": ticket.get("sla_deadline"),
            "failed_at": current_iso,
        })
        expired += 1
    if expired:
        conn.commit()
    return expired


def _war_ticket_summary(row: Any, conn: Any | None = None) -> dict[str, Any]:
    ticket = _ticket_payload(row)
    try:
        scenario = _load_scenario_by_id(ticket["scenario_id"], conn)
    except FileNotFoundError:
        scenario = {}
    opened_at = _war_room_parse_time(ticket.get("opened_at"))
    ended_at = _war_room_parse_time(ticket.get("resolved_at"))
    duration_seconds = int(_ticket_active_elapsed_seconds(ticket, ended_at)) if opened_at and ended_at else None
    ticket.update({
        "title": scenario.get("title", ticket.get("scenario_id", ticket.get("id"))),
        "scenario_title": scenario.get("title", ticket.get("scenario_id", ticket.get("id"))),
        "type": scenario.get("type", ticket.get("type")),
        "severity": scenario.get("severity", ticket.get("severity")),
        "duration_seconds": duration_seconds,
        "duration_minutes": round(duration_seconds / 60, 1) if duration_seconds is not None else None,
    })
    return ticket


def _seed_war_room_tickets(conn: Any) -> None:
    """Crée une seule fois les trois tickets pilotes pour que la file NOC soit immédiatement exploitable."""
    for scenario in list_scenarios():
        scenario_id = str(scenario["id"])
        # Un scénario ayant déjà un historique ne doit pas être réensemencé au redémarrage.
        exists = conn.execute("SELECT id FROM tickets WHERE scenario_id = ? LIMIT 1", (scenario_id,)).fetchone()
        if exists:
            continue
        now = _war_room_now()
        sla_minutes = scenario.get("sla_minutes")
        deadline = _war_room_iso(now + timedelta(minutes=int(sla_minutes))) if sla_minutes is not None else None
        conn.execute(
            "INSERT INTO tickets (id, scenario_id, type, severity, status, opened_at, sla_deadline, resolution_data, xp_earned) "
            "VALUES (?, ?, ?, ?, 'open', ?, ?, '{}', 0)",
            (scenario_id, scenario_id, scenario["type"], scenario["severity"], _war_room_iso(now), deadline),
        )
        _ticket_action(conn, scenario_id, "opened", {"source": "pilot_seed"})
    conn.commit()


def _scenario_topology_checks(scenario: dict[str, Any], topology: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = topology.get("nodes") if isinstance(topology, dict) else []
    if not isinstance(nodes, list):
        nodes = []
    checks: list[dict[str, Any]] = []
    for rule in (scenario.get("resolution_check") or {}).get("rules", []):
        if rule.get("type") == "post_mortem_contains" or str(rule.get("field", "")).startswith("post_mortem."):
            # Ces règles sont volontairement évaluées après la saisie du post-mortem.
            continue
        target_id = str(rule.get("target") or rule.get("node") or "")
        node = next((item for item in nodes if str(item.get("id", "")) == target_id or str(item.get("label", "")) == target_id), None)
        actual: Any = None
        path = str(rule.get("path") or "")
        if node is not None and path:
            parts = path.split(".")
            current: Any = node
            index = 0
            while index < len(parts):
                part = parts[index]
                if part == "ports" and index + 1 < len(parts):
                    port_id = parts[index + 1]
                    ports = current.get("ports", []) if isinstance(current, dict) else []
                    current = next((port for port in ports if str(port.get("id", "")) == port_id or str(port.get("name", "")) == port_id), None) if isinstance(ports, list) else None
                    index += 2
                    continue
                if part == "config":
                    current = current.get("config") if isinstance(current, dict) else None
                elif isinstance(current, dict):
                    current = current.get(part)
                else:
                    current = None
                index += 1
            actual = current
        operator = str(rule.get("operator") or "equals")
        expected = rule.get("value")
        if operator == "equals":
            passed = str(actual).casefold() == str(expected).casefold() if actual is not None and expected is not None else actual == expected
        elif operator == "contains":
            if isinstance(actual, (list, tuple, set)):
                passed = any(str(expected).casefold() in str(value).casefold() for value in actual)
            else:
                passed = str(expected).casefold() in str(actual or "").casefold()
        elif operator == "exists":
            passed = actual is not None
        else:
            passed = False
        checks.append({
            "passed": bool(passed),
            "target": target_id,
            "path": path,
            "operator": operator,
            "expected": expected,
            "actual": actual,
            "description": rule.get("description", ""),
        })
    return checks


def _open_ticket_conn():
    conn = connect(DB_PATH, check_same_thread=False)
    ensure_ready(conn)
    return conn


@app.get("/api/tickets")
def list_open_tickets() -> list[dict[str, Any]]:
    conn = _open_ticket_conn()
    try:
        _expire_war_room_tickets(conn)
        rows = conn.execute(
            "SELECT * FROM tickets WHERE status IN ('open', 'pending_postmortem', 'paused') ORDER BY opened_at ASC"
        ).fetchall()
        now = _war_room_now()
        result: list[dict[str, Any]] = []
        for row in rows:
            ticket = _ticket_payload(row)
            try:
                scenario = _load_scenario_by_id(ticket["scenario_id"], conn)
            except FileNotFoundError:
                scenario = {}
            deadline = _war_room_parse_time(ticket.get("sla_deadline"))
            pause = ticket["resolution_data"].get("sla_pause") if isinstance(ticket.get("resolution_data"), dict) else None
            if ticket.get("status") == "paused" and isinstance(pause, dict):
                ticket["sla_left"] = pause.get("remaining_sla_seconds")
            else:
                ticket["sla_left"] = max(0, int((deadline - now).total_seconds())) if deadline else None
            ticket["scenario"] = scenario
            ticket["title"] = scenario.get("title", ticket["scenario_id"])
            ticket["story"] = scenario.get("story", "")
            ticket["impact"] = scenario.get("impact", "")
            ticket["reported_by"] = scenario.get("reported_by", "")
            ticket["sla_minutes"] = scenario.get("sla_minutes")
            ticket["reward_xp"] = scenario.get("reward_xp", 0)
            result.append(ticket)
        return result
    finally:
        conn.close()


@app.get("/api/scenarios/options")
def war_room_scenario_options() -> dict[str, Any]:
    return get_scenario_options()


@app.post("/api/tickets/random")
def create_random_war_room_ticket() -> dict[str, Any]:
    """Crée un ticket surprise ; le scénario est stocké en base, jamais en fichier."""
    scenario = generate_random_scenario()
    conn = _open_ticket_conn()
    try:
        now = _war_room_now()
        deadline = _war_room_iso(now + timedelta(minutes=int(scenario["sla_minutes"])))
        conn.execute(
            "INSERT INTO war_room_scenarios (scenario_id, scenario_json, created_at) VALUES (?, ?, ?)",
            (scenario["id"], json.dumps(scenario, ensure_ascii=False), _war_room_iso(now)),
        )
        conn.execute(
            "INSERT INTO tickets (id, scenario_id, type, severity, status, opened_at, sla_deadline, resolution_data, xp_earned) "
            "VALUES (?, ?, ?, ?, 'open', ?, ?, '{}', 0)",
            (scenario["id"], scenario["id"], scenario["type"], scenario["severity"], _war_room_iso(now), deadline),
        )
        _ticket_action(conn, scenario["id"], "opened", {
            "source": "random", "fault_id": scenario["fault_id"],
            "target_device": scenario["target_device"], "target_port": scenario["target_port"],
        })
        conn.commit()
        return {"ticket_id": scenario["id"], "scenario": scenario}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@app.post("/api/scenarios/save")
def save_user_scenario(payload: ScenarioSaveRequest) -> dict[str, Any]:
    try:
        topology_id = {
            "LAN simple": "lan_simple", "LAN+WAN": "lan_wan", "LAN + WAN": "lan_wan",
            "VLANs multiples": "multi_vlan",
        }.get(payload.topology, payload.topology)
        scenario = build_scenario(
            scenario_id=_new_user_scenario_id(),
            title=payload.name,
            scenario_type=payload.type,
            severity=payload.severity,
            topology_id=topology_id,
            fault_id=payload.fault_id,
            target_device=payload.target_device,
            target_port=payload.target_port,
            sla_minutes=payload.sla_minutes,
            reward_xp=150,
        )
        _validate_scenario_document(scenario)
        file_path = _save_user_scenario_file(scenario)
        return {"scenario_id": scenario["id"], "file_path": file_path, "scenario": scenario}
    except HTTPException:
        raise
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/scenarios/list")
def list_war_room_scenarios() -> list[dict[str, Any]]:
    return [
        {"id": scenario["id"], "title": scenario.get("title", scenario["id"]),
         "type": scenario.get("type", "incident"),
         "is_user_created": str(scenario["id"]).startswith("USER-")}
        for scenario in list_scenarios()
    ]


@app.post("/api/scenarios/import")
def import_user_scenario(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    scenario = payload.get("scenario") if isinstance(payload, dict) and isinstance(payload.get("scenario"), dict) else payload
    scenario = _validate_scenario_document(scenario)
    imported = copy.deepcopy(scenario)
    file_path = _save_user_scenario_file(imported)
    return {"scenario_id": imported["id"], "file_path": file_path, "title": imported["title"]}


@app.get("/api/scenarios/{scenario_id}/export")
def export_war_room_scenario(scenario_id: str) -> Response:
    conn = _open_ticket_conn()
    try:
        try:
            scenario = _validate_scenario_document(_load_scenario_by_id(scenario_id, conn))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Scénario War Room introuvable.")
        content = json.dumps(scenario, ensure_ascii=False, indent=2) + "\n"
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{scenario_id}.json"'},
        )
    finally:
        conn.close()


@app.get("/api/tickets/archive")
def list_archived_tickets() -> list[dict[str, Any]]:
    """Retourne l'historique des tickets résolus ou échoués, du plus récent au plus ancien."""
    conn = _open_ticket_conn()
    try:
        _expire_war_room_tickets(conn)
        rows = conn.execute(
            "SELECT * FROM tickets WHERE status IN ('resolved', 'failed') "
            "ORDER BY COALESCE(resolved_at, opened_at) DESC, opened_at DESC"
        ).fetchall()
        return [_war_ticket_summary(row, conn) for row in rows]
    finally:
        conn.close()


@app.get("/api/itsm/stats")
def get_itsm_stats() -> dict[str, Any]:
    """Calcule les indicateurs ITSM directement avec les fonctions de dates SQLite."""
    conn = _open_ticket_conn()
    try:
        now = _war_room_now()
        _expire_war_room_tickets(conn, now)
        row = conn.execute(
            """
            SELECT
                COALESCE(AVG(
                    CASE WHEN status = 'resolved' AND resolved_at IS NOT NULL
                    THEN (julianday(resolved_at) - julianday(opened_at)) * 1440.0 END
                ), 0) AS mttr_minutes,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) AS total_resolved,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) AS total_failed,
                COUNT(CASE WHEN status = 'resolved' AND resolved_at IS NOT NULL
                    AND sla_deadline IS NOT NULL
                    AND julianday(resolved_at) <= julianday(sla_deadline) THEN 1 END) AS sla_met
            FROM tickets
            """
        ).fetchone()
        total_resolved = int(row["total_resolved"] or 0)
        sla_compliance_pct = (int(row["sla_met"] or 0) / total_resolved * 100.0) if total_resolved else 0.0
        today = conn.execute(
            "SELECT COUNT(*) AS n FROM tickets WHERE date(opened_at) = date(?)",
            (_war_room_iso(now),),
        ).fetchone()
        recent_rows = conn.execute(
            "SELECT * FROM tickets WHERE status = 'resolved' ORDER BY resolved_at DESC LIMIT 5"
        ).fetchall()
        return {
            "mttr_minutes": round(float(row["mttr_minutes"] or 0), 1),
            "sla_compliance_pct": round(sla_compliance_pct, 1),
            "total_resolved": total_resolved,
            "total_failed": int(row["total_failed"] or 0),
            "incidents_today": int(today["n"] or 0),
            "recent_resolved": [_war_ticket_summary(item, conn) for item in recent_rows],
        }
    finally:
        conn.close()


@app.post("/api/tickets/{scenario_id}/open")
def open_ticket(scenario_id: str) -> dict[str, Any]:
    conn = _open_ticket_conn()
    try:
        # Les tickets RND ont leur JSON en base ; les USER/pilotes sont des fichiers.
        active = conn.execute(
            "SELECT * FROM tickets WHERE (scenario_id = ? OR id = ?) "
            "AND status IN ('open', 'pending_postmortem', 'paused') ORDER BY opened_at DESC LIMIT 1",
            (scenario_id, scenario_id),
        ).fetchone()
        if active:
            scenario = _load_scenario_by_id(str(active["scenario_id"]), conn)
            return {"ticket": _ticket_payload(active), "scenario": scenario, "existing": True}
        try:
            scenario = _load_scenario_by_id(scenario_id, conn)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Scénario War Room introuvable.")
        base_exists = conn.execute("SELECT id FROM tickets WHERE id = ?", (scenario_id,)).fetchone()
        ticket_id = f"{scenario_id}-{uuid.uuid4().hex[:6].upper()}" if base_exists else scenario_id
        now = _war_room_now()
        sla_minutes = scenario.get("sla_minutes")
        deadline = _war_room_iso(now + timedelta(minutes=int(sla_minutes))) if sla_minutes is not None else None
        conn.execute(
            "INSERT INTO tickets (id, scenario_id, type, severity, status, opened_at, sla_deadline, resolution_data, xp_earned) "
            "VALUES (?, ?, ?, ?, 'open', ?, ?, '{}', 0)",
            (ticket_id, scenario_id, scenario["type"], scenario["severity"], _war_room_iso(now), deadline),
        )
        _ticket_action(conn, ticket_id, "opened", {"source": "api"})
        conn.commit()
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return {"ticket": _ticket_payload(row), "scenario": scenario, "existing": False}
    finally:
        conn.close()


@app.post("/api/tickets/{scenario_id}/replay")
def replay_ticket(scenario_id: str) -> dict[str, Any]:
    """Rouvre le scénario avec un nouveau timer SLA sans effacer l'historique du ticket précédent."""
    conn = _open_ticket_conn()
    try:
        _expire_war_room_tickets(conn)
        old = conn.execute("SELECT * FROM tickets WHERE id = ?", (scenario_id,)).fetchone()
        # L'API accepte à la fois l'ID du ticket archivé (utilisé par l'UI)
        # et l'ID du scénario (contrat public de cette route).
        if not old:
            old = conn.execute(
                "SELECT * FROM tickets WHERE scenario_id = ? AND status IN ('resolved', 'failed') "
                "ORDER BY COALESCE(resolved_at, opened_at) DESC LIMIT 1",
                (scenario_id,),
            ).fetchone()
        target_scenario_id = str(old["scenario_id"]) if old else scenario_id
        try:
            scenario = _load_scenario_by_id(target_scenario_id, conn)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Ticket ou scénario War Room introuvable.")
        active = conn.execute(
            "SELECT id FROM tickets WHERE scenario_id = ? AND status IN ('open', 'pending_postmortem', 'paused') LIMIT 1",
            (target_scenario_id,),
        ).fetchone()
        if active and (not old or str(active["id"]) != str(old["id"])):
            raise HTTPException(status_code=409, detail="Ce scénario possède déjà un ticket actif.")
        # Conserver le ticket précédent pour l'Archive, les rapports et le badge Comeback Kid.
        ticket_id = f"{target_scenario_id}-{uuid.uuid4().hex[:8].upper()}"
        now = _war_room_now()
        opened_at_iso = _war_room_iso_precise(now)
        sla_minutes = scenario.get("sla_minutes")
        deadline = _war_room_iso_precise(now + timedelta(minutes=int(sla_minutes))) if sla_minutes is not None else None
        conn.execute(
            "INSERT INTO tickets (id, scenario_id, type, severity, status, opened_at, sla_deadline, resolution_data, xp_earned) "
            "VALUES (?, ?, ?, ?, 'open', ?, ?, '{}', 0)",
            (ticket_id, target_scenario_id, scenario["type"], scenario["severity"], opened_at_iso, deadline),
        )
        _ticket_action(conn, ticket_id, "opened", {"source": "replay", "replayed_ticket_id": str(old["id"]) if old else None})
        conn.commit()
        return {"success": True, "new_ticket_id": ticket_id}
    finally:
        conn.close()



@app.get("/api/tickets/open-count")
def get_open_ticket_count() -> dict[str, int]:
    """Nombre de tickets dont le statut est strictement « open »."""
    conn = _open_ticket_conn()
    try:
        _expire_war_room_tickets(conn)
        row = conn.execute("SELECT COUNT(*) AS count FROM tickets WHERE status = 'open'").fetchone()
        return {"count": int(row["count"] or 0)}
    finally:
        conn.close()


@app.post("/api/tickets/{ticket_id}/pause")
def pause_ticket(ticket_id: str) -> dict[str, Any]:
    """Suspend le SLA en stockant le temps restant dans resolution_data."""
    conn = _open_ticket_conn()
    try:
        _expire_war_room_tickets(conn)
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket introuvable.")
        ticket = _ticket_payload(row)
        if ticket["status"] == "paused":
            pause = ticket["resolution_data"].get("sla_pause", {})
            return {"success": True, "ticket_id": ticket_id, "status": "paused",
                    "sla_left": pause.get("remaining_sla_seconds")}
        if ticket["status"] != "open":
            raise HTTPException(status_code=409, detail="Seul un ticket ouvert peut être mis en pause.")
        now = _war_room_now()
        now_iso = _war_room_iso_precise(now)
        deadline = _war_room_parse_time(ticket.get("sla_deadline"))
        remaining = max(0.0, (deadline - now).total_seconds()) if deadline else None
        if deadline is not None and remaining <= 0:
            _expire_war_room_tickets(conn, now)
            raise HTTPException(status_code=409, detail="SLA dépassé : ce ticket ne peut plus être mis en pause.")
        data = ticket.get("resolution_data")
        if not isinstance(data, dict):
            data = {}
        data["sla_pause"] = {"paused_at": now_iso, "remaining_sla_seconds": int(remaining) if remaining is not None else None}
        conn.execute("UPDATE tickets SET status = 'paused', resolution_data = ? WHERE id = ?",
                     (json.dumps(data, ensure_ascii=False), ticket_id))
        _ticket_action(conn, ticket_id, "paused", {"paused_at": now_iso, "remaining_sla_seconds": data["sla_pause"]["remaining_sla_seconds"]})
        conn.commit()
        return {"success": True, "ticket_id": ticket_id, "status": "paused",
                "sla_left": data["sla_pause"]["remaining_sla_seconds"]}
    finally:
        conn.close()


@app.post("/api/tickets/{ticket_id}/resume")
def resume_ticket(ticket_id: str) -> dict[str, Any]:
    """Reprend un ticket et recrée son échéance à partir du temps SLA sauvegardé."""
    conn = _open_ticket_conn()
    try:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket introuvable.")
        ticket = _ticket_payload(row)
        if ticket["status"] != "paused":
            raise HTTPException(status_code=409, detail="Ce ticket n'est pas en pause.")
        data = ticket.get("resolution_data")
        if not isinstance(data, dict):
            data = {}
        pause = data.get("sla_pause")
        if not isinstance(pause, dict):
            raise HTTPException(status_code=409, detail="Les données de pause SLA sont absentes.")
        now = _war_room_now()
        paused_at = _war_room_parse_time(pause.get("paused_at"))
        if paused_at:
            pause_duration = max(0.0, (now - paused_at).total_seconds())
            data["paused_total_seconds"] = round(float(data.get("paused_total_seconds") or 0) + pause_duration, 2)
        remaining = pause.get("remaining_sla_seconds")
        deadline = _war_room_parse_time(ticket.get("sla_deadline"))
        new_deadline = _war_room_iso_precise(now + timedelta(seconds=max(0, float(remaining)))) if remaining is not None else None
        data.pop("sla_pause", None)
        conn.execute("UPDATE tickets SET status = 'open', sla_deadline = ?, resolution_data = ? WHERE id = ?",
                     (new_deadline if deadline is not None or remaining is not None else None,
                      json.dumps(data, ensure_ascii=False), ticket_id))
        _ticket_action(conn, ticket_id, "resumed", {"resumed_at": _war_room_iso_precise(now), "paused_total_seconds": data.get("paused_total_seconds", 0)})
        conn.commit()
        return {"success": True, "ticket_id": ticket_id, "status": "open", "sla_left": remaining}
    finally:
        conn.close()


@app.get("/api/tickets/badges")
def get_war_room_badges() -> list[dict[str, Any]]:
    """Calcule les badges War Room depuis les tickets et leur historique."""
    conn = _open_ticket_conn()
    try:
        return build_war_badges(conn)
    finally:
        conn.close()


@app.post("/api/tickets/stress-test")
def create_stress_test() -> dict[str, Any]:
    """Crée trois tickets aléatoires avec une échéance de mission commune à 45 minutes."""
    conn = _open_ticket_conn()
    try:
        now = _war_room_now()
        now_iso = _war_room_iso_precise(now)
        mission_id = "STRESS-" + uuid.uuid4().hex[:10].upper()
        deadline = now + timedelta(minutes=45)
        deadline_iso = _war_room_iso_precise(deadline)
        created: list[dict[str, Any]] = []
        for _ in range(3):
            scenario = generate_random_scenario()
            scenario_id = "RND-" + uuid.uuid4().hex[:10].upper()
            scenario["id"] = scenario_id
            _validate_scenario_document(scenario)
            conn.execute(
                "INSERT INTO war_room_scenarios (scenario_id, scenario_json, created_at) VALUES (?, ?, ?)",
                (scenario_id, json.dumps(scenario, ensure_ascii=False), now_iso),
            )
            conn.execute(
                "INSERT INTO tickets (id, scenario_id, type, severity, status, opened_at, sla_deadline, resolution_data, xp_earned) "
                "VALUES (?, ?, ?, ?, 'open', ?, ?, ?, 0)",
                (scenario_id, scenario_id, scenario["type"], scenario["severity"], now_iso, deadline_iso,
                 json.dumps({"stress_test": {"mission_id": mission_id, "deadline_at": deadline_iso, "xp_multiplier": 2}}, ensure_ascii=False)),
            )
            _ticket_action(conn, scenario_id, "opened", {"source": "stress_test", "mission_id": mission_id})
            created.append({"ticket_id": scenario_id, "title": scenario.get("title", scenario_id), "type": scenario["type"]})
        conn.commit()
        return {"mission_id": mission_id, "deadline_at": deadline_iso, "tickets": created,
                "message": "3 incidents simultanés. Tu as 45 minutes pour tous les résoudre. Bon courage !"}
    finally:
        conn.close()


@app.get("/api/itsm/stress-test/{mission_id}")
def get_stress_test_status(mission_id: str) -> dict[str, Any]:
    conn = _open_ticket_conn()
    try:
        now = _war_room_now()
        all_rows = conn.execute("SELECT * FROM tickets ORDER BY opened_at ASC").fetchall()
        mission_rows: list[dict[str, Any]] = []
        for row in all_rows:
            ticket = _ticket_payload(row)
            stress = ticket["resolution_data"].get("stress_test") if isinstance(ticket.get("resolution_data"), dict) else None
            if isinstance(stress, dict) and stress.get("mission_id") == mission_id:
                mission_rows.append(ticket)
        if not mission_rows:
            raise HTTPException(status_code=404, detail="Mission Stress Test introuvable.")
        deadline = next((_war_room_parse_time((ticket.get("resolution_data") or {}).get("stress_test", {}).get("deadline_at"))
                         for ticket in mission_rows if (ticket.get("resolution_data") or {}).get("stress_test", {}).get("deadline_at")), None)
        if deadline and now > deadline:
            for ticket in mission_rows:
                if ticket.get("status") in {"open", "paused", "pending_postmortem"}:
                    data = ticket.get("resolution_data") if isinstance(ticket.get("resolution_data"), dict) else {}
                    data.update({"reason": "stress_test_timeout", "failed_at": _war_room_iso(now), "sla_met": False})
                    conn.execute("UPDATE tickets SET status = 'failed', resolved_at = ?, resolution_data = ? WHERE id = ?",
                                 (_war_room_iso(now), json.dumps(data, ensure_ascii=False), ticket["id"]))
                    _ticket_action(conn, ticket["id"], "failed", {"reason": "stress_test_timeout", "mission_id": mission_id})
            conn.commit()
            all_rows = conn.execute("SELECT * FROM tickets ORDER BY opened_at ASC").fetchall()
            mission_rows = []
            for row in all_rows:
                ticket = _ticket_payload(row)
                stress = ticket["resolution_data"].get("stress_test") if isinstance(ticket.get("resolution_data"), dict) else None
                if isinstance(stress, dict) and stress.get("mission_id") == mission_id:
                    mission_rows.append(ticket)
        summaries = [{"ticket_id": ticket["id"], "status": ticket["status"],
                      "xp_earned": int(ticket.get("xp_earned") or 0)} for ticket in mission_rows]
        done = all(ticket.get("status") in {"resolved", "failed"} for ticket in mission_rows)
        succeeded = len(mission_rows) == 3 and all(ticket.get("status") == "resolved" for ticket in mission_rows)
        status = "succeeded" if done and succeeded else ("failed" if done or (deadline and now > deadline) else "in_progress")
        return {"mission_id": mission_id, "deadline_at": _war_room_iso(deadline) if deadline else None,
                "status": status, "tickets": summaries,
                "resolved": sum(item["status"] == "resolved" for item in summaries), "total": len(summaries)}
    finally:
        conn.close()


@app.get("/api/itsm/weekly-report")
def get_itsm_weekly_report() -> dict[str, Any]:
    """Rapport des sept derniers jours calendaires en UTC."""
    conn = _open_ticket_conn()
    try:
        now = _war_room_now()
        _expire_war_room_tickets(conn, now)
        start_day = now.date() - timedelta(days=6)
        start = datetime.combine(start_day, datetime.min.time(), tzinfo=timezone.utc)
        start_iso = _war_room_iso_precise(start)
        rows_raw = conn.execute(
            "SELECT * FROM tickets WHERE opened_at >= ? OR resolved_at >= ? ORDER BY opened_at ASC",
            (start_iso, start_iso),
        ).fetchall()
        rows = [_ticket_payload(row) for row in rows_raw]
        days = [(start_day + timedelta(days=index)).isoformat() for index in range(7)]
        daily = {day: {"date": day, "opened": 0, "resolved": 0, "failed": 0} for day in days}
        opened_rows: list[dict[str, Any]] = []
        resolved_rows: list[dict[str, Any]] = []
        failed_rows: list[dict[str, Any]] = []
        type_counts: Counter[str] = Counter()
        for ticket in rows:
            opened = _war_room_parse_time(ticket.get("opened_at"))
            ended = _war_room_parse_time(ticket.get("resolved_at"))
            if opened and opened >= start:
                opened_rows.append(ticket)
                day = opened.date().isoformat()
                if day in daily:
                    daily[day]["opened"] += 1
                type_counts[str(ticket.get("type") or "inconnu")] += 1
            if ended and ended >= start:
                day = ended.date().isoformat()
                if ticket.get("status") == "resolved":
                    resolved_rows.append(ticket)
                    if day in daily:
                        daily[day]["resolved"] += 1
                elif ticket.get("status") == "failed":
                    failed_rows.append(ticket)
                    if day in daily:
                        daily[day]["failed"] += 1
        duration_pairs = [(ticket, _ticket_active_elapsed_seconds(ticket, _war_room_parse_time(ticket.get("resolved_at"))))
                          for ticket in resolved_rows if _war_room_parse_time(ticket.get("resolved_at"))]
        duration_pairs.sort(key=lambda pair: pair[1])
        sla_good = [ticket for ticket in resolved_rows if _ticket_sla_met(ticket)]
        best_margin_ticket = None
        best_margin_seconds = None
        for ticket in sla_good:
            deadline = _war_room_parse_time(ticket.get("sla_deadline"))
            ended = _war_room_parse_time(ticket.get("resolved_at"))
            if deadline and ended:
                margin = (deadline - ended).total_seconds()
                if best_margin_seconds is None or margin > best_margin_seconds:
                    best_margin_seconds, best_margin_ticket = margin, ticket
        return {
            "period_start": start_day.isoformat(),
            "period_end": now.date().isoformat(),
            "tickets_opened": len(opened_rows),
            "tickets_resolved": len(resolved_rows),
            "tickets_failed": len(failed_rows),
            "mttr_minutes": round(sum(value for _, value in duration_pairs) / len(duration_pairs) / 60, 1) if duration_pairs else 0.0,
            "sla_compliance_pct": round(len(sla_good) / len(resolved_rows) * 100, 1) if resolved_rows else 0.0,
            "fastest_resolution_minutes": round(duration_pairs[0][1] / 60, 2) if duration_pairs else None,
            "fastest_ticket_id": duration_pairs[0][0]["id"] if duration_pairs else None,
            "slowest_resolution_minutes": round(duration_pairs[-1][1] / 60, 2) if duration_pairs else None,
            "slowest_ticket_id": duration_pairs[-1][0]["id"] if duration_pairs else None,
            "best_sla": ({"ticket_id": best_margin_ticket["id"], "margin_minutes": round(best_margin_seconds / 60, 1)}
                         if best_margin_ticket is not None and best_margin_seconds is not None else None),
            "top_scenario_type": type_counts.most_common(1)[0][0] if type_counts else None,
            "daily_breakdown": [daily[day] for day in days],
        }
    finally:
        conn.close()


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str) -> dict[str, Any]:
    conn = _open_ticket_conn()
    try:
        _expire_war_room_tickets(conn)
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket introuvable.")
        ticket = _ticket_payload(row)
        try:
            scenario = _load_scenario_by_id(ticket["scenario_id"], conn)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Scénario associé au ticket introuvable.")
        deadline = _war_room_parse_time(ticket.get("sla_deadline"))
        now = _war_room_now()
        pause = ticket["resolution_data"].get("sla_pause") if isinstance(ticket.get("resolution_data"), dict) else None
        if ticket.get("status") == "paused" and isinstance(pause, dict):
            ticket["sla_left"] = pause.get("remaining_sla_seconds")
        else:
            ticket["sla_left"] = max(0, int((deadline - now).total_seconds())) if deadline else None
        return {"ticket": ticket, "scenario": scenario}
    finally:
        conn.close()


@app.post("/api/tickets/{ticket_id}/resolve")
def resolve_ticket(ticket_id: str, payload: TicketResolveRequest) -> dict[str, Any]:
    conn = _open_ticket_conn()
    try:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket introuvable.")
        ticket = _ticket_payload(row)
        if ticket["status"] in {"resolved", "failed"}:
            raise HTTPException(status_code=409, detail="Ce ticket est déjà clôturé.")
        if ticket["status"] == "paused":
            raise HTTPException(status_code=409, detail="Reprenez le ticket avant de tenter sa résolution.")
        if ticket["status"] == "pending_postmortem":
            raise HTTPException(status_code=409, detail="Le post-mortem de ce ticket reste à valider.")
        scenario = _load_scenario_by_id(ticket["scenario_id"], conn)
        checks = _scenario_topology_checks(scenario, payload.topology)
        config_passed = all(check["passed"] for check in checks)
        now = _war_room_now()
        opened_at = _war_room_parse_time(ticket.get("opened_at"))
        server_elapsed = _ticket_active_elapsed_seconds(ticket, now) if opened_at else float(payload.elapsed_seconds)
        deadline = _war_room_parse_time(ticket.get("sla_deadline"))
        sla_met = deadline is None or now <= deadline
        reason = "sla_exceeded" if not sla_met else (None if config_passed else "config_incorrect")
        passed = config_passed and sla_met
        resolution_data = ticket.get("resolution_data")
        if not isinstance(resolution_data, dict):
            resolution_data = {}
        resolution_data.update({
            "topology": payload.topology,
            "checks": checks,
            "submitted_elapsed_seconds": float(payload.elapsed_seconds),
            "server_elapsed_seconds": round(server_elapsed, 2),
            "sla_met": sla_met,
            "checked_at": _war_room_iso(now),
        })
        if passed:
            conn.execute(
                "UPDATE tickets SET status = 'pending_postmortem', resolution_data = ? WHERE id = ?",
                (json.dumps(resolution_data, ensure_ascii=False), ticket_id),
            )
            _ticket_action(conn, ticket_id, "configuration_verified", {"checks": checks, "sla_met": sla_met, "server_elapsed_seconds": round(server_elapsed, 2)})
        else:
            resolution_data["reason"] = reason
            resolution_data["failed_at"] = _war_room_iso(now)
            conn.execute(
                "UPDATE tickets SET status = 'failed', resolved_at = ?, resolution_data = ? WHERE id = ?",
                (_war_room_iso(now), json.dumps(resolution_data, ensure_ascii=False), ticket_id),
            )
            _ticket_action(conn, ticket_id, "failed", {
                "reason": reason,
                "checks": checks,
                "sla_met": sla_met,
                "server_elapsed_seconds": round(server_elapsed, 2),
            })
        conn.commit()
        return {
            "passed": bool(passed),
            "reason": reason,
            "checks": checks,
            "message": (
                "Configuration validée. Complétez le post-mortem pour clôturer le ticket."
                if passed else (
                    "Échec SLA : le délai de résolution est dépassé."
                    if reason == "sla_exceeded" else
                    "Échec de validation : la configuration ne satisfait pas les règles du scénario."
                )
            ),
            "sla_met": sla_met,
            "elapsed_seconds": round(server_elapsed, 2),
        }
    finally:
        conn.close()


@app.post("/api/tickets/{ticket_id}/post-mortem")
def save_ticket_post_mortem(ticket_id: str, payload: TicketPostMortemRequest) -> dict[str, Any]:
    conn = _open_ticket_conn()
    try:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket introuvable.")
        ticket = _ticket_payload(row)
        if ticket["status"] in {"resolved", "failed"}:
            raise HTTPException(status_code=409, detail="Ce ticket est déjà clôturé.")
        deadline = _war_room_parse_time(ticket.get("sla_deadline"))
        if deadline is not None and _war_room_now() > deadline:
            now = _war_room_now()
            resolution_data = ticket.get("resolution_data") if isinstance(ticket.get("resolution_data"), dict) else {}
            resolution_data.update({"reason": "sla_exceeded", "failed_at": _war_room_iso(now), "sla_met": False})
            conn.execute(
                "UPDATE tickets SET status = 'failed', resolved_at = ?, resolution_data = ? WHERE id = ?",
                (_war_room_iso(now), json.dumps(resolution_data, ensure_ascii=False), ticket_id),
            )
            _ticket_action(conn, ticket_id, "failed", {"reason": "sla_exceeded", "failed_at": _war_room_iso(now)})
            conn.commit()
            raise HTTPException(status_code=409, detail="SLA dépassé : le ticket a été marqué comme échoué.")
        if ticket["status"] != "pending_postmortem":
            raise HTTPException(status_code=409, detail="Validez d'abord la résolution technique du ticket.")
        scenario = _load_scenario_by_id(ticket["scenario_id"], conn)
        post_mortem = {
            "root_cause": payload.root_cause.strip(),
            "impact": payload.impact.strip(),
            "corrective_action": payload.corrective_action.strip(),
        }
        pm_rules = [
            rule for rule in (scenario.get("resolution_check") or {}).get("rules", [])
            if rule.get("type") == "post_mortem_contains" or str(rule.get("field", "")).startswith("post_mortem.")
        ]
        for rule in pm_rules:
            field = str(rule.get("field") or "root_cause").removeprefix("post_mortem.")
            value = str(post_mortem.get(field, "")).casefold()
            needles = rule.get("any_of") or rule.get("contains_any") or []
            if needles and not any(str(needle).casefold() in value for needle in needles):
                raise HTTPException(
                    status_code=422,
                    detail=f"La cause racine doit citer au moins un des termes suivants : {', '.join(map(str, needles))}.",
                )
        resolution_data = ticket.get("resolution_data") if isinstance(ticket.get("resolution_data"), dict) else {}
        resolution_data["post_mortem"] = post_mortem
        resolution_data["closed_at"] = _war_room_iso(_war_room_now())
        now = _war_room_now()
        xp = max(0, int(scenario.get("reward_xp") or 0))
        stress = resolution_data.get("stress_test") if isinstance(resolution_data.get("stress_test"), dict) else None
        stress_deadline = _war_room_parse_time(stress.get("deadline_at")) if stress else None
        if stress and stress_deadline and now <= stress_deadline:
            xp *= 2
            stress["xp_multiplier_applied"] = 2
        now_iso = _war_room_iso(now)
        conn.execute(
            "UPDATE tickets SET status = 'resolved', resolved_at = ?, resolution_data = ?, xp_earned = ? WHERE id = ?",
            (now_iso, json.dumps(resolution_data, ensure_ascii=False), xp, ticket_id),
        )
        stats = add_xp(conn, xp, 0, commit=False)
        _ticket_action(conn, ticket_id, "post_mortem_submitted", {"post_mortem": post_mortem})
        _ticket_action(conn, ticket_id, "resolved", {"xp_earned": xp})
        conn.commit()
        return {"passed": True, "ticket_id": ticket_id, "status": "resolved", "xp_earned": xp, "stats": stats}
    finally:
        conn.close()


def get_tree() -> Iterator[SkillTree]:
    conn = connect(DB_PATH, check_same_thread=False)
    try:
        yield SkillTree(conn)
    finally:
        conn.close()


def _get_node(tree: SkillTree, node_id: str) -> Node:
    try:
        return tree.node(node_id)
    except DomainError as error:
        raise HTTPException(status_code=404, detail=str(error))


def _challenge_row(tree: SkillTree, node_id: str):
    return tree.conn.execute(
        "SELECT expected_topology, time_limit FROM challenges WHERE node_id = ?",
        (node_id,),
    ).fetchone()


def _streak_payload(tree: SkillTree) -> dict:
    rows = tree.conn.execute(
        "SELECT date_jour, minutes_etudiees FROM daily_streak ORDER BY date_jour DESC"
    ).fetchall()

    today = date.today()
    dates: set[date] = set()
    for row in rows:
        try:
            day = date.fromisoformat(row["date_jour"])
        except (TypeError, ValueError):
            continue
        if day <= today:
            dates.add(day)

    latest = max(dates) if dates else None
    # Le helper partagé est la source de vérité pour l'expiration de la série.
    # Les totaux de minutes et les dates affichés ci-dessous restent calculés ici.
    streak = streak_days(tree.conn, today)

    minutes_total = sum(int(row["minutes_etudiees"] or 0) for row in rows)
    minutes_today = sum(
        int(row["minutes_etudiees"] or 0)
        for row in rows
        if row["date_jour"] == today.isoformat()
    )
    freeze_row = tree.conn.execute(
        "SELECT quantity FROM shop_inventory WHERE item_id = 'streak_freeze'"
    ).fetchone()
    freezes = int(freeze_row["quantity"] or 0) if freeze_row else 0

    return {
        "days": streak,
        "minutes_today": minutes_today,
        "minutes_total": minutes_total,
        "last_date": latest.isoformat() if latest else None,
        "active_today": latest == today if latest else False,
        "freezes": freezes,
    }


def _answer_matches(pattern: str, answer: str, *, terminal: bool = False) -> bool:
    candidate = " ".join(answer.split()) if terminal else answer
    return re.fullmatch(pattern, candidate, re.IGNORECASE) is not None


# ---------------------------------------------------------
# ROUTES DE BASE
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def _configured_lesson_sources() -> dict[str, str]:
    """Retourne les identifiants de leçon canoniques déclarés dans nodes.json."""
    path = CONTENT_DIR / "nodes.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, list):
        return {}

    sources: dict[str, str] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        node_id = item.get("id")
        source_id = item.get("lesson_source_id")
        if isinstance(node_id, str) and node_id and isinstance(source_id, str) and source_id:
            sources[node_id] = source_id
    return sources


@app.get("/api/node/{node_id}/lesson", response_class=PlainTextResponse)
def read_lesson(node_id: str, tree: SkillTree = Depends(get_tree)):
    node = _get_node(tree, node_id)
    source_id = _configured_lesson_sources().get(node.id, node.id)
    try:
        lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
        content = lessons.get(source_id, "")
    except ContentError as e:
        print(f"Avertissement Loader : {e}")
        file_path = CONTENT_DIR / "lessons" / f"{source_id}.md"
        content = file_path.read_text(encoding="utf-8").strip() if file_path.exists() else ""

    # Une leçon réutilisée garde le contenu canonique mais affiche le titre du nœud demandé.
    if content and source_id != node.id:
        content = re.sub(r"(?m)^# .+$", f"# {node.title}", content, count=1)

    return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")

@lru_cache(maxsize=1)
def _configured_node_orders() -> dict[str, int]:
    """Retourne l'ordre pédagogique faisant autorité dans content/nodes.json.

    La base peut être persistante et dater d'un déploiement antérieur : sa colonne
    sort_order n'est donc pas une source fiable lorsque le catalogue JSON a changé.
    """
    path = CONTENT_DIR / "nodes.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, list):
        return {}

    orders: dict[str, int] = {}
    for item in payload:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        raw_order = item.get("order")
        if isinstance(raw_order, bool):
            continue
        try:
            order = int(raw_order)
        except (TypeError, ValueError, OverflowError):
            continue
        orders[item["id"]] = order
    return orders


@lru_cache(maxsize=1)
def _configured_node_positions() -> dict[str, int]:
    """Retourne la position exacte des cours dans le catalogue JSON.

    Le champ order est local et peut être partagé par plusieurs cours d'un même module ;
    l'index du catalogue sert donc de départage stable lorsque deux ordres sont égaux.
    """
    path = CONTENT_DIR / 'nodes.json'
    try:
        payload = json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, list):
        return {}
    return {
        item['id']: index
        for index, item in enumerate(payload)
        if isinstance(item, dict) and isinstance(item.get('id'), str)
    }


@lru_cache(maxsize=1)
def _configured_node_labs() -> dict[str, dict[str, Any]]:
    """Lit les métadonnées de lab attachées aux nœuds du catalogue JSON."""
    path = CONTENT_DIR / "nodes.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, list):
        return {}
    return {
        str(item["id"]): item["lab"]
        for item in payload
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and isinstance(item.get("lab"), dict)
        and isinstance(item["lab"].get("prompt"), str)
        and item["lab"]["prompt"].strip()
    }


@app.get("/api/node/{node_id}")
def read_node(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    node = _get_node(tree, node_id)
    status = tree.status(node.id)
    lab = tree.lab_spec(node.id)
    lab_payload = {"kind": lab.kind, "prompt": lab.prompt, "hint": lab.hint} if lab else None
    if lab_payload is None:
        configured_lab = _configured_node_labs().get(node.id)
        if configured_lab:
            lab_payload = {
                "kind": str(configured_lab.get("kind") or "text"),
                "prompt": str(configured_lab.get("prompt") or ""),
                "hint": str(configured_lab.get("hint") or ""),
            }

    # Les nouveaux scénarios React Flow peuvent exister sans ancienne entrée
    # lab_specs ni métadonnée « lab » dans nodes.json. Exposer alors leur consigne
    # au lecteur du cours pour qu'il affiche le bouton vers le vrai workspace.
    has_lab_requirement = any(
        requirement.kind is ProofKind.LAB for requirement in node.requirements
    )
    if lab_payload is None and has_lab_requirement:
        try:
            v2_lab_payload = _fetch_lab(node.id)
        except HTTPException:
            # Le détail du cours doit rester disponible même si le scénario manque
            # ou si sa définition ne peut pas être chargée.
            v2_lab_payload = None

        if v2_lab_payload and not v2_lab_payload.get("sandbox"):
            definition = v2_lab_payload.get("definition")
            topology = getattr(definition, "initial_topology", None)
            topology_nodes = getattr(topology, "nodes", None)
            if isinstance(topology_nodes, list) and topology_nodes:
                duration_min = getattr(definition, "duration_min", None)
                hints = getattr(definition, "hints", None) or []
                lab_payload = {
                    "kind": "workspace-v2",
                    "prompt": str(
                        getattr(definition, "prompt", "") or node.description or node.title
                    ),
                    "hint": "\n".join(str(hint) for hint in hints if str(hint).strip()),
                    "duration": f"{duration_min} min" if duration_min else "",
                    "difficulty": str(
                        getattr(definition, "difficulty", "")
                        or getattr(definition, "level", "")
                        or ""
                    ),
                    "workspace_v2": True,
                }

    challenge = _challenge_row(tree, node.id)
    terminal = tree.conn.execute("SELECT prompt, explanation FROM terminal_specs WHERE node_id = ?", (node.id,)).fetchone()
    terminal_spec = tree.terminal_spec(node.id)

    challenge_payload = None
    if challenge:
        try:
            expected_topology = json.loads(challenge["expected_topology"])
        except (TypeError, ValueError) as error:
            raise HTTPException(500, "La définition de la topologie attendue est invalide.") from error
        if (
            not isinstance(expected_topology, dict)
            or not isinstance(expected_topology.get("nodes"), dict)
            or not isinstance(expected_topology.get("connections"), list)
        ):
            raise HTTPException(500, "La définition de la topologie attendue est invalide.")
        # Seul un résumé pédagogique est exposé au navigateur, jamais la correction complète.
        brief = expected_topology.get("brief", {})
        if not isinstance(brief, dict):
            brief = {}
        challenge_payload = {
            "prompt": node.description,
            "time_limit": challenge["time_limit"],
            "brief": brief,
            "expected_summary": {
                "nodes": expected_topology["nodes"],
                "connections": len(expected_topology["connections"]),
            },
        }

    return {
        "id": node.id,
        "title": node.title,
        "category": node.category,
        "module": node.module,
        "description": node.description,
        "status": status.value,
        "prereqs": [{"id": p, "title": tree.node(p).title, "status": tree.status(p).value} for p in node.prereqs],
        "requirements": [{"kind": r.kind.value, "min_score": effective_requirement_score(r.kind, r.min_score), "met": requirement_met(r, node)} for r in node.requirements],
        "lab": lab_payload,
        "terminal": terminal_spec,
        "challenge": challenge_payload,
    }


def _topology_histograms(topology: Any) -> tuple[Counter, Counter]:
    """Construit les histogrammes de types et de liens depuis l'export Drawflow."""
    if not isinstance(topology, dict):
        raise HTTPException(422, "La topologie envoyée doit être un objet Drawflow.")
    if len(topology) > 200:
        raise HTTPException(422, "La topologie dépasse la limite de 200 équipements.")

    node_types: dict[str, str] = {}
    for raw_id, raw_node in topology.items():
        if not isinstance(raw_node, dict):
            raise HTTPException(422, "Un équipement de la topologie est invalide.")
        name = raw_node.get("name")
        if not isinstance(name, str) or not name.strip():
            raise HTTPException(422, "Chaque équipement doit avoir un type valide.")
        node_types[str(raw_id)] = name.strip().lower()

    node_counts = Counter(node_types.values())
    link_counts: Counter = Counter()
    connection_total = 0
    for raw_id, raw_node in topology.items():
        outputs = raw_node.get("outputs") or {}
        if not isinstance(outputs, dict):
            raise HTTPException(422, "Les sorties d'un équipement sont invalides.")
        for output in outputs.values():
            if not isinstance(output, dict):
                raise HTTPException(422, "Un port de sortie est invalide.")
            connections = output.get("connections") or []
            if not isinstance(connections, list):
                raise HTTPException(422, "La liste de connexions d'un port est invalide.")
            connection_total += len(connections)
            if connection_total > 1000:
                raise HTTPException(422, "La topologie dépasse la limite de 1 000 connexions.")
            for connection in connections:
                if not isinstance(connection, dict):
                    raise HTTPException(422, "Une connexion est invalide.")
                target_id = str(connection.get("node", ""))
                if target_id not in node_types:
                    raise HTTPException(422, "Une connexion pointe vers un équipement inexistant.")
                pair = tuple(sorted((node_types[str(raw_id)], node_types[target_id])))
                link_counts[pair] += 1

    return node_counts, link_counts


def _expected_topology_histograms(expected_topology: Any) -> tuple[Counter, Counter]:
    if not isinstance(expected_topology, dict):
        raise HTTPException(500, "La définition du défi est invalide.")
    expected_nodes = expected_topology.get("nodes")
    expected_connections = expected_topology.get("connections")
    if not isinstance(expected_nodes, dict) or not isinstance(expected_connections, list):
        raise HTTPException(500, "La définition du défi est invalide.")

    node_counts: Counter = Counter()
    for node_type, count in expected_nodes.items():
        if not isinstance(node_type, str) or not node_type.strip() or isinstance(count, bool):
            raise HTTPException(500, "La définition des équipements attendus est invalide.")
        try:
            count = int(count)
        except (TypeError, ValueError) as error:
            raise HTTPException(500, "Le nombre d'équipements attendus est invalide.") from error
        if count < 0:
            raise HTTPException(500, "Le nombre d'équipements attendus est invalide.")
        if count:
            node_counts[node_type.strip().lower()] += count

    link_counts: Counter = Counter()
    for connection in expected_connections:
        if not isinstance(connection, dict):
            raise HTTPException(500, "La définition des connexions attendues est invalide.")
        source, target = connection.get("from"), connection.get("to")
        if not isinstance(source, str) or not isinstance(target, str) or not source.strip() or not target.strip():
            raise HTTPException(500, "La définition des connexions attendues est invalide.")
        link_counts[tuple(sorted((source.strip().lower(), target.strip().lower())))] += 1

    if not node_counts:
        raise HTTPException(500, "La définition du défi doit contenir au moins un équipement.")
    return node_counts, link_counts


def _compare_topology_counts(actual: Counter, expected: Counter, render) -> tuple[float, list[str], list[str]]:
    keys = set(actual) | set(expected)
    matched = sum(min(actual.get(key, 0), expected.get(key, 0)) for key in keys)
    denominator = max(sum(actual.values()), sum(expected.values()))
    ratio = matched / denominator if denominator else 1.0
    missing = [render(key, expected[key] - actual.get(key, 0)) for key in sorted(expected) if expected[key] > actual.get(key, 0)]
    extra = [render(key, actual[key] - expected.get(key, 0)) for key in sorted(actual) if actual[key] > expected.get(key, 0)]
    return ratio, missing, extra


def _topology_adjacency(topology: dict) -> tuple[dict[str, str], dict[str, set[str]], dict[str, str]]:
    """Construit le graphe non orienté des équipements depuis l'export Drawflow."""
    node_types = {
        str(raw_id): str(raw_node.get("name", "")).strip().lower()
        for raw_id, raw_node in topology.items()
    }
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_types}
    labels: dict[str, str] = {}
    for raw_id, raw_node in topology.items():
        node_id = str(raw_id)
        data = raw_node.get("data")
        label = data.get("label") if isinstance(data, dict) else None
        labels[node_id] = label.strip()[:80] if isinstance(label, str) and label.strip() else f"{node_types[node_id]} #{node_id}"
        outputs = raw_node.get("outputs") or {}
        for output in outputs.values():
            for connection in output.get("connections") or []:
                target_id = str(connection.get("node", ""))
                if target_id in adjacency and target_id != node_id:
                    adjacency[node_id].add(target_id)
                    adjacency[target_id].add(node_id)
    return node_types, adjacency, labels


def _topology_constraint_errors(expected_topology: dict, topology: dict) -> list[str]:
    """Vérifie les relations entre instances d'équipements, au-delà des simples compteurs."""
    constraints = expected_topology.get("constraints", [])
    if not isinstance(constraints, list):
        raise HTTPException(500, "Les contraintes du défi sont invalides.")

    node_types, adjacency, labels = _topology_adjacency(topology)
    errors: list[str] = []
    for index, constraint in enumerate(constraints, 1):
        if not isinstance(constraint, dict):
            raise HTTPException(500, f"Contrainte de défi invalide (position {index}).")
        kind = constraint.get("kind")
        if kind == "all_pairs":
            source = constraint.get("from")
            target = constraint.get("to")
            if not isinstance(source, str) or not isinstance(target, str):
                raise HTTPException(500, f"Contrainte all_pairs invalide (position {index}).")
            left = [node_id for node_id, node_type in node_types.items() if node_type == source]
            right = [node_id for node_id, node_type in node_types.items() if node_type == target]
            for left_id in left:
                for right_id in right:
                    if right_id not in adjacency[left_id]:
                        errors.append(f"Liaison requise manquante : {labels[left_id]} ↔ {labels[right_id]}.")
        elif kind == "min_peer_count":
            source = constraint.get("from")
            target = constraint.get("to")
            minimum = constraint.get("min_peers")
            if (
                not isinstance(source, str)
                or not isinstance(target, str)
                or isinstance(minimum, bool)
                or not isinstance(minimum, int)
                or minimum < 1
            ):
                raise HTTPException(500, f"Contrainte min_peer_count invalide (position {index}).")
            for node_id, node_type in node_types.items():
                if node_type != source:
                    continue
                peers = {peer_id for peer_id in adjacency[node_id] if node_types.get(peer_id) == target}
                if len(peers) < minimum:
                    errors.append(
                        f"{labels[node_id]} doit être relié à au moins {minimum} équipement(s) "
                        f"de type « {target} » (actuellement {len(peers)})."
                    )
        elif kind == "separated_by":
            source = constraint.get("from")
            target = constraint.get("to")
            via = constraint.get("via")
            if (
                not isinstance(source, str) or not isinstance(target, str)
                or not isinstance(via, str) or len({source, target, via}) != 3
            ):
                raise HTTPException(500, f"Contrainte separated_by invalide (position {index}).")
            gateways = {node_id for node_id, node_type in node_types.items() if node_type == via}
            if not gateways:
                errors.append(
                    f"Aucun équipement de type « {via} » ne peut assurer la séparation entre "
                    f"« {source} » et « {target} »."
                )
                continue
            source_ids = [node_id for node_id, node_type in node_types.items() if node_type == source]
            target_ids = {node_id for node_id, node_type in node_types.items() if node_type == target}
            for source_id in source_ids:
                visited = {source_id}
                stack = [source_id]
                while stack:
                    current = stack.pop()
                    for peer_id in adjacency[current]:
                        if peer_id in gateways or peer_id in visited:
                            continue
                        visited.add(peer_id)
                        stack.append(peer_id)
                for target_id in target_ids:
                    if target_id in visited:
                        errors.append(
                            f"Le chemin entre {labels[source_id]} et {labels[target_id]} contourne "
                            f"les équipements de type « {via} » : le trafic doit passer par ce "
                            "point de contrôle."
                        )
        elif kind == "connected":
            device_type = constraint.get("type")
            if not isinstance(device_type, str) or not device_type.strip():
                raise HTTPException(500, f"Contrainte connected invalide (position {index}).")
            selected = [node_id for node_id, node_type in node_types.items() if node_type == device_type]
            if len(selected) > 1:
                visited = {selected[0]}
                stack = [selected[0]]
                while stack:
                    current = stack.pop()
                    for peer_id in adjacency[current]:
                        if node_types.get(peer_id) == device_type and peer_id not in visited:
                            visited.add(peer_id)
                            stack.append(peer_id)
                disconnected = [labels[node_id] for node_id in selected if node_id not in visited]
                if disconnected:
                    errors.append(
                        f"Les équipements de type « {device_type} » doivent former un réseau connecté. "
                        f"À relier au groupe : {', '.join(disconnected)}."
                    )
        else:
            raise HTTPException(500, f"Type de contrainte inconnu à la position {index}.")
    return errors


@app.post("/api/node/{node_id}/challenge")
def submit_challenge(node_id: str, payload: dict[str, Any] = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    """Calcule et enregistre un défi d'architecture à partir de la topologie reçue."""
    node = _get_node(tree, node_id)
    challenge = _challenge_row(tree, node_id)
    if challenge is None:
        raise HTTPException(404, "Aucun défi d'architecture n'est défini pour ce cours.")

    try:
        expected_topology = json.loads(challenge["expected_topology"])
    except (TypeError, ValueError) as error:
        raise HTTPException(500, "La définition de la topologie attendue est invalide.") from error

    requirement = node.requirement(ProofKind.MANUAL)
    if requirement is None:
        raise HTTPException(409, "Ce défi ne possède pas d'exigence de validation manuelle.")

    topology = payload.get("topology")
    actual_nodes, actual_links = _topology_histograms(topology)
    expected_nodes, expected_links = _expected_topology_histograms(expected_topology)

    node_ratio, missing_nodes, extra_nodes = _compare_topology_counts(
        actual_nodes, expected_nodes,
        lambda name, count: f"{count} × {name}",
    )
    link_ratio, missing_links, extra_links = _compare_topology_counts(
        actual_links, expected_links,
        lambda pair, count: f"{count} × {pair[0]} ↔ {pair[1]}",
    )
    score = round(100 * (0.5 * node_ratio + 0.5 * link_ratio))
    constraint_errors = _topology_constraint_errors(expected_topology, topology)
    if constraint_errors:
        # Les contraintes d'architecture ne doivent jamais être compensées par un bon comptage.
        score = min(score, 95)
        missing_links.extend(constraint_errors)
    timed_out = payload.get("timeout") is True
    passed = score >= requirement.min_score and not timed_out and not constraint_errors
    current_status = tree.status(node_id)

    if current_status is Status.LOCKED:
        missing_prereqs = [prereq for prereq in node.prereqs if tree.status(prereq) is not Status.VALIDATED]
        raise HTTPException(
            409,
            f"Défi verrouillé. Prérequis manquants : {', '.join(missing_prereqs)}.",
        )

    if current_status is Status.VALIDATED:
        return {
            "success": True, "score": score, "passed": passed, "timeout": timed_out,
            "validated": True, "status": Status.VALIDATED.value,
            "attempt_recorded": False, "xp_gained": 0, "coins_gained": 0, "badges_unlocked": [],
            "missing_nodes": missing_nodes, "extra_nodes": extra_nodes,
            "missing_links": missing_links, "extra_links": extra_links,
        }

    evidence = json.dumps(
        {
            "nodes": dict(actual_nodes),
            "links": {f"{a}|{b}": count for (a, b), count in actual_links.items()},
            "constraint_errors": constraint_errors,
        },
        ensure_ascii=False,
    )[:4000]
    detail = f"Défi d'architecture : {score}/100"
    if timed_out:
        detail += " (temps écoulé)"
    try:
        _attempt, validated = tree.record(
            node_id, ProofKind.MANUAL, score, passed, evidence=evidence, detail=detail,
        )
    except DomainError as error:
        raise HTTPException(409, str(error)) from error

    return {
        "success": True,
        "score": score,
        "passed": passed,
        "timeout": timed_out,
        "validated": validated,
        "status": tree.status(node_id).value,
        "attempt_recorded": True,
        "xp_gained": (tree.last_reward or {}).get("xp", 0),
        "coins_gained": (tree.last_reward or {}).get("coins", 0),
        "badges_unlocked": tree.last_badges,
        "missing_nodes": missing_nodes,
        "extra_nodes": extra_nodes,
        "missing_links": missing_links,
        "extra_links": extra_links,
    }

@app.get("/api/node/{node_id}/quiz")
def read_quiz(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    """Retourne les questions d'un cours sans exposer les réponses attendues."""
    node = _get_node(tree, node_id)
    if node.requirement(ProofKind.QUIZ) is None:
        raise HTTPException(404, "Aucun quiz n'est configuré pour ce cours.")

    questions = tree.questions(node_id, ProofKind.QUIZ)
    if not questions:
        raise HTTPException(404, "Aucune question n'est disponible pour ce quiz.")

    return {
        "node_id": node.id,
        "questions": [
            {
                "id": question.id,
                "type": question.question_type,
                "prompt": question.prompt,
                "choices": list(question.choices),
            }
            for question in questions
        ],
    }


@app.post("/api/node/{node_id}/quiz")
def submit_quiz(node_id: str, payload: dict[str, Any] = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    node = tree.playable(node_id)
    requirement = node.requirement(ProofKind.QUIZ)
    questions = tree.questions(node_id, ProofKind.QUIZ)
    answers = payload.get("answers")
    
    results = []
    correct = 0
    for index, (question, answer) in enumerate(zip(questions, answers), 1):
        if question.question_type in {"input", "terminal"}:
            matches = _answer_matches(question.answer_regex or "", answer, terminal=question.question_type == "terminal")
        else:
            matches = answer == question.answer
        correct += int(matches)
        results.append({"id": question.id, "correct": matches, "explanation": question.explanation})

    score = round(100 * correct / len(questions))
    passed = score >= requirement.min_score
    attempt, validated = tree.record(node_id, ProofKind.QUIZ, score, passed, detail=f"{correct}/{len(questions)} bonnes réponses")
    
    return {
        "success": True, "score": score, "passed": passed, "correct": correct, "total": len(questions),
        "validated": validated, "status": tree.status(node_id).value, "results": results,
    }

@app.post("/api/node/{node_id}/submit-answer")
def submit_answer(node_id: str, payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    node = _get_node(tree, node_id)
    answer = str(payload.get("answer", "")).strip()
    spec = tree.terminal_spec(node_id)
    if not spec:
        raise HTTPException(400, "Type d'exercice non reconnu")
        
    pattern = spec.get("pattern")
    is_correct = re.match(pattern, answer, re.IGNORECASE) is not None if pattern else False
    score = 100 if is_correct else 0
    attempt, validated = tree.record(node_id, ProofKind.TERMINAL, score, is_correct, evidence=answer, detail="terminal")
    return {"success": True, "correct": is_correct, "explanation": spec.get("explanation", ""), "validated": validated}

@app.get("/api/tree")
def read_tree(tree: SkillTree = Depends(get_tree)) -> dict:
    nodes = tree.nodes()
    # Réutiliser les nœuds déjà assemblés : tree.statuses() relirait nodes, edges,
    # requirements et attempts une seconde fois pour cette même réponse.
    validated_ids = {node.id for node in nodes if is_validated(node)}
    statuses = {node.id: status_of(node, validated_ids) for node in nodes}
    configured_orders = _configured_node_orders()
    configured_positions = _configured_node_positions()
    validated = sum(1 for status in statuses.values() if status is Status.VALIDATED)
    return {
        "total": len(nodes), "validated": validated,
        "progress_percent": round((validated / len(nodes)) * 100) if nodes else 0,
        "nodes": [{
            "id": n.id,
            "title": n.title,
            "category": n.category,
            "module": n.module,
            "order": configured_orders.get(n.id, n.sort_order),
            "catalog_index": configured_positions.get(n.id, fallback_index),
            "sort_order": n.sort_order,
            "status": statuses[n.id].value,
            "prereqs": list(n.prereqs),
            "requirements_detail": [{"kind": r.kind.value, "min_score": effective_requirement_score(r.kind, r.min_score)} for r in n.requirements],
        } for fallback_index, n in enumerate(nodes)]
    }

@app.get("/api/stats")
def read_stats(tree: SkillTree = Depends(get_tree)) -> dict:
    nodes = tree.nodes()
    validated_count = sum(1 for node in nodes if is_validated(node))
    categories: dict[str, dict[str, Any]] = {}
    total_attempts = 0
    total_passed = 0
    for node in nodes:
        attempts = len(node.attempts)
        passed = sum(1 for a in node.attempts if a.passed)
        category = categories.setdefault(node.category, {"name": node.category, "attempts": 0, "passed": 0})
        category["attempts"] += attempts
        category["passed"] += passed
        total_attempts += attempts
        total_passed += passed
    for cat in categories.values():
        cat["success_rate"] = round(100 * cat["passed"] / cat["attempts"]) if cat["attempts"] else 0
    return {
        "totals": {"nodes": len(nodes), "validated": validated_count, "attempts": total_attempts, "success_rate": round(100 * total_passed / total_attempts) if total_attempts else 0},
        "categories": list(categories.values())
    }

@app.get("/api/daily-plan")
def read_daily_plan(tree: SkillTree = Depends(get_tree)) -> dict:
    return get_daily_plan(tree)

@app.get("/api/user-stats")
def read_user_stats(tree: SkillTree = Depends(get_tree)) -> dict:
    return get_user_stats(tree.conn)

@app.get("/api/streak")
def read_streak(tree: SkillTree = Depends(get_tree)) -> dict:
    return _streak_payload(tree)

@app.get("/api/profile")
def read_profile(tree: SkillTree = Depends(get_tree)) -> dict:
    stats = get_user_stats(tree.conn)
    total_nodes = len(tree.nodes())
    validated_nodes = len(tree.validated_ids())
    days = streak_days(tree.conn)
    labs = tree.conn.execute("SELECT COUNT(*) FROM attempts WHERE kind='lab' AND passed=1").fetchone()[0]
    legacy_exams = tree.conn.execute("SELECT COUNT(*) FROM attempts WHERE kind='exam' AND passed=1").fetchone()[0]
    saved_exams = tree.conn.execute(
        "SELECT COUNT(*) FROM exam_sessions WHERE submitted=1 AND passed=1 AND node_id IS NULL"
    ).fetchone()[0]
    exams = int(legacy_exams or 0) + int(saved_exams or 0)
    return {
        "level": stats, "total_nodes": total_nodes, "validated_nodes": validated_nodes,
        "progress_percent": round((validated_nodes / total_nodes) * 100) if total_nodes else 0,
        "streak": {"days": days}, "labs_validated": labs, "exams_passed": exams,
        "badges": [
            dict(row) for row in tree.conn.execute(
                "SELECT id, nom, description, icone, condition_debloquee_le "
                "FROM badges ORDER BY condition_debloquee_le, id"
            ).fetchall()
        ],
        "certificate": {"name": CERTIFICATE_NAME, "date": date.today().isoformat()}
    }

@app.get("/api/flashcards")
def read_flashcards() -> dict:
    try:
        payload = json.loads(FLASHCARDS_FILE.read_text(encoding="utf-8"))
        return {"count": len(payload), "cards": payload}
    except Exception:
        return {"count": 0, "cards": []}

@app.get("/api/diagnostics/{diag_id}")
def read_diagnostic(diag_id: str) -> dict:
    path = DIAGNOSTICS_DIR / f"{diag_id}.json"
    if not path.exists(): raise HTTPException(404, "Diagnostic introuvable.")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------
# ROUTES DOCKER & LABS (Legacy)
# ---------------------------------------------------------

def _require_legacy_docker_labs_enabled() -> None:
    """Refuse les anciens labs shell tant qu'un opérateur ne les active pas explicitement."""
    enabled = os.environ.get("SKILLTREE_ENABLE_LEGACY_DOCKER_LABS", "").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        raise HTTPException(
            status_code=503,
            detail=(
                "Les anciens laboratoires Docker sont désactivés par défaut pour des raisons "
                "de sécurité. Utilise Lab Workspace v2. L'option "
                "SKILLTREE_ENABLE_LEGACY_DOCKER_LABS ne doit être activée que dans un "
                "environnement de développement de confiance."
            ),
        )


@app.post("/api/lab/start")
def start_lab(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    _require_legacy_docker_labs_enabled()
    node_id = payload.get("node_id")
    try:
        node = tree.playable(node_id)
    except DomainError as error:
        raise HTTPException(status_code=409, detail=str(error))

    lab_dir = find_lab_dir(node.id)
    if lab_dir is None:
        raise HTTPException(status_code=404, detail="Le dossier du lab est introuvable.")
        
    try:
        session = start_interactive_lab(node.id, lab_dir)
    except LabRunnerError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(error)}")
    
    return {"lab_id": session.lab_id, "container_id": session.container_id, "setup_logs": session.setup_logs}

@app.post("/api/lab/exec")
def exec_lab(payload: dict = Body(...)) -> dict:
    _require_legacy_docker_labs_enabled()
    result = exec_in_lab(payload.get("lab_id"), payload.get("command"))
    return {"success": True, "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.exit_code}

@app.post("/api/lab/validate")
def validate_lab_route(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    _require_legacy_docker_labs_enabled()
    lab_id = payload.get("lab_id")
    if not lab_id: raise HTTPException(400, "lab_id manquant")
    try:
        validation = validate_lab(lab_id)
        attempt, validated = tree.record_docker_lab(validation.node_id, validation.commands, validation.result)
        return {"success": True, "passed": validation.result.passed, "score": validation.result.score, "detail": validation.result.detail, "validated": validated}
    except LabSessionError as error: raise HTTPException(404, str(error))
    except LabRunnerError as error: raise HTTPException(503, str(error))
    except DomainError as error: raise HTTPException(409, str(error))
    except Exception as error: raise HTTPException(500, f"Erreur inattendue : {str(error)}")


# ---------------------------------------------------------
# ALIAS POUR L'INTERFACE HTML
# ---------------------------------------------------------

def _exam_level(node_id: str, title: str = "") -> str:
    """Déduit le niveau d'un cours depuis son identifiant canonique."""
    suffix = str(node_id or "").strip().lower().replace("_", "-").rsplit("-", 1)[-1]
    if suffix in {"debutant", "intermediaire", "expert"}:
        return suffix
    lowered_title = str(title or "").casefold()
    if lowered_title.rstrip().endswith("expert"):
        return "expert"
    if lowered_title.rstrip().endswith(("intermédiaire", "intermediaire")):
        return "intermediaire"
    if lowered_title.rstrip().endswith("débutant"):
        return "debutant"
    return ""


def _exam_is_placeholder(question: Question) -> bool:
    """Écarte les entrées provisoires qui ne constituent pas une vraie question."""
    return re.search(
        r"question temporaire|réponse provisoire|option temporaire",
        str(question.prompt or ""),
        flags=re.IGNORECASE,
    ) is not None


def _exam_question_pool(tree: SkillTree, nodes: list[Node]) -> list[Question]:
    """Charge les banques par lots pour que les examens volumineux restent réactifs."""
    node_ids = list(dict.fromkeys(str(node.id) for node in nodes))
    if not node_ids:
        return []

    def load_questions(scope: ProofKind, selected_ids: list[str]) -> dict[str, list[Question]]:
        by_node: dict[str, list[Question]] = {}
        # Rester sous les limites de paramètres des versions courantes de SQLite.
        for start in range(0, len(selected_ids), 400):
            chunk = selected_ids[start:start + 400]
            placeholders = ",".join("?" for _ in chunk)
            rows = tree.conn.execute(
                f"SELECT * FROM questions WHERE node_id IN ({placeholders}) AND scope = ? "
                "ORDER BY node_id, position, id",
                (*chunk, scope.value),
            ).fetchall()
            for row in rows:
                question = _exam_question_from_row(row)
                if _exam_is_placeholder(question):
                    continue
                by_node.setdefault(question.node_id, []).append(question)
        return by_node

    exam_by_node = load_questions(ProofKind.EXAM, node_ids)
    # Une banque d'examen composée uniquement de questions provisoires est traitée
    # comme une banque inutilisable : on tente alors le quiz du même cours.
    missing_exam_ids = [node_id for node_id in node_ids if not exam_by_node.get(node_id)]
    quiz_by_node = load_questions(ProofKind.QUIZ, missing_exam_ids) if missing_exam_ids else {}

    # Garder l'ordre des cours demandé par l'interface, puis l'ordre des questions de chaque cours.
    return [
        question
        for node in nodes
        for question in (exam_by_node.get(str(node.id)) or quiz_by_node.get(str(node.id), []))
    ]


def _exam_nodes_from_payload(payload: dict, tree: SkillTree) -> list[Node]:
    all_nodes = tree.nodes()
    by_id = {node.id: node for node in all_nodes}
    raw_ids = payload.get("node_ids")
    if raw_ids is not None:
        if not isinstance(raw_ids, list) or not raw_ids:
            raise HTTPException(422, "La sélection de cours est vide ou invalide.")
        if len(raw_ids) > 1000:
            raise HTTPException(422, "La sélection dépasse 1 000 cours.")
        requested: list[str] = []
        for value in raw_ids:
            if not isinstance(value, str) or not value.strip():
                raise HTTPException(422, "Un identifiant de cours est invalide.")
            node_id = value.strip()
            if node_id not in by_id:
                raise HTTPException(422, f"Cours inconnu dans la sélection : {node_id}.")
            if node_id not in requested:
                requested.append(node_id)
        return [by_id[node_id] for node_id in requested]

    category = str(payload.get("category") or "").strip()
    module = str(payload.get("module") or "").strip()
    nodes = all_nodes
    if category and category.lower() != "all":
        nodes = [node for node in nodes if node.category == category]
    elif module and module.lower() not in {"all", "*"}:
        # L'interface actuelle envoie les identifiants de cours. Ce chemin reste utile
        # aux intégrations qui construisent une session uniquement depuis un module.
        exact = [node for node in nodes if node.module.casefold() == module.casefold()]
        nodes = exact if exact else [node for node in nodes if module.casefold() in node.module.casefold()]

    raw_levels = payload.get("levels")
    if isinstance(raw_levels, list) and raw_levels and "all" not in [str(level).lower() for level in raw_levels]:
        levels = {str(level).strip().lower() for level in raw_levels}
        nodes = [node for node in nodes if _exam_level(node.id, node.title) in levels]
    return nodes


def _exam_question_from_row(row) -> Question:
    question_type = row["question_type"] or "qcm"
    try:
        choices = tuple(json.loads(row["choices"] or "[]"))
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(500, "Une question de l'examen possède des choix invalides.") from error
    answer = row["answer_text"] if question_type in {"input", "terminal"} else row["answer"]
    return Question(
        id=int(row["id"]),
        node_id=str(row["node_id"]),
        scope=ProofKind(row["scope"]),
        prompt=str(row["prompt"]),
        choices=choices,
        answer=answer,
        explanation=str(row["explanation"] or ""),
        question_type=str(question_type),
        answer_regex=row["answer_regex"],
    )


def _exam_load_session_questions(tree: SkillTree, raw_ids: list) -> list[Question]:
    if not isinstance(raw_ids, list) or not raw_ids:
        raise HTTPException(409, "Cette session ne contient aucune question.")
    try:
        ids = [int(value) for value in raw_ids]
    except (TypeError, ValueError) as error:
        raise HTTPException(409, "La liste des questions de cette session est invalide.") from error
    placeholders = ",".join("?" for _ in ids)
    rows = tree.conn.execute(
        f"SELECT * FROM questions WHERE id IN ({placeholders})",
        ids,
    ).fetchall()
    by_id = {int(row["id"]): _exam_question_from_row(row) for row in rows}
    if any(question_id not in by_id for question_id in ids):
        raise HTTPException(409, "La banque de questions a changé depuis le début de cet examen.")
    return [by_id[question_id] for question_id in ids]


def _exam_public_question(question: Question, nodes_by_id: dict[str, Node]) -> dict:
    node = nodes_by_id.get(question.node_id)
    return {
        "id": question.id,
        "node_id": question.node_id,
        "level": _exam_level(question.node_id, node.title if node else ""),
        "type": question.question_type,
        "prompt": question.prompt,
        "choices": list(question.choices),
    }


def _create_exam_session(
    tree: SkillTree,
    nodes: list[Node],
    *,
    count: int,
    time_limit: int,
    category: str,
    question_pool: list[Question] | None = None,
    node_id: str | None = None,
    exam_type: str = "category",
    module_scope: str = "",
    level_scope: str = "",
    scope_node_ids: list[str] | None = None,
) -> dict:
    pool = question_pool if question_pool is not None else _exam_question_pool(tree, nodes)
    if not pool:
        raise HTTPException(
            422,
            "Aucune question exploitable dans ce périmètre. Vérifie les banques de quiz et d'examen de ces cours.",
        )
    selected = random.sample(pool, min(count, len(pool)))
    now = int(time.time())
    session_id = uuid.uuid4().hex
    category = category.strip() or "Examen personnalisé"
    effective_pass_score = EXAM_PASS_SCORE
    effective_scope_ids = list(scope_node_ids if scope_node_ids is not None else (node.id for node in nodes))
    tree.conn.execute(
        "INSERT INTO exam_sessions "
        "(session_id, category, question_ids, started_at, expires_at, submitted, "
        "score, passed, correct, total, submitted_at, time_expired, answers_json, details_json, "
        "paused_at, paused_seconds, node_id, exam_type, passing_score, result_json, "
        "module_scope, level_scope, scope_node_ids_json) "
        "VALUES (?, ?, ?, ?, ?, 0, NULL, NULL, NULL, ?, NULL, 0, '[]', '[]', NULL, 0, ?, ?, ?, '', ?, ?, ?)",
        (
            session_id,
            category,
            json.dumps([question.id for question in selected]),
            now,
            now + time_limit,
            len(selected),
            node_id,
            exam_type,
            effective_pass_score,
            module_scope,
            level_scope,
            json.dumps(effective_scope_ids, ensure_ascii=False),
        ),
    )
    tree.conn.commit()
    nodes_by_id = {node.id: node for node in nodes}
    return {
        "id": session_id,
        "category": category,
        "exam_type": exam_type,
        "node_id": node_id,
        "time_limit": time_limit,
        "duration_seconds": time_limit,
        "pass_score": effective_pass_score,
        "passing_score": effective_pass_score,
        "requested_count": count,
        "question_count": len(selected),
        **({
            "module_scope": module_scope,
            "level_scope": level_scope,
            "scope_node_ids": effective_scope_ids,
        } if exam_type == "certification" else {}),
        "questions": [_exam_public_question(question, nodes_by_id) for question in selected],
    }



def _bounded_exam_integer(value, name: str, default: int, minimum: int, maximum: int) -> int:
    if value is None:
        value = default
    if isinstance(value, bool):
        raise HTTPException(422, f"Le paramètre « {name} » doit être un entier.")
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise HTTPException(422, f"Le paramètre « {name} » doit être un entier.") from error
    if number < minimum or number > maximum:
        raise HTTPException(422, f"Le paramètre « {name} » doit être compris entre {minimum} et {maximum}.")
    return number


def _sanitize_exam_answer(question: Question, value) -> int | str | None:
    if question.question_type == "qcm":
        if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < len(question.choices):
            return value
        return None
    if isinstance(value, str):
        return value[:2000].strip()
    return None


def _grade_exam_question(question: Question, answer: int | str | None) -> dict:
    if question.question_type == "qcm":
        correct = isinstance(answer, int) and not isinstance(answer, bool) and answer == question.answer
    else:
        submitted = answer if isinstance(answer, str) else ""
        expected = str(question.answer or "")
        if not submitted:
            correct = False
        elif question.answer_regex:
            try:
                correct = re.fullmatch(question.answer_regex, submitted, flags=re.IGNORECASE | re.MULTILINE) is not None
            except re.error:
                correct = False
        else:
            correct = re.sub(r"\s+", " ", submitted).strip().casefold() == re.sub(r"\s+", " ", expected).strip().casefold()
    return {
        "question_id": question.id,
        "node_id": question.node_id,
        "correct": bool(correct),
        "answer": question.answer,
        "explanation": question.explanation,
    }


def _exam_result_payload(row) -> dict:
    keys = row.keys() if hasattr(row, "keys") else ()
    stored_json = row["result_json"] if "result_json" in keys else ""
    if stored_json:
        try:
            stored_result = json.loads(stored_json)
            if isinstance(stored_result, dict):
                return stored_result
        except (TypeError, ValueError, json.JSONDecodeError):
            # Les anciennes sessions peuvent ne pas contenir de résultat sérialisé.
            pass

    try:
        answers = json.loads(row["answers_json"] or "[]")
    except (TypeError, ValueError, json.JSONDecodeError):
        answers = []
    try:
        details = json.loads(row["details_json"] or "[]")
    except (TypeError, ValueError, json.JSONDecodeError):
        details = []
    started_at = int(row["started_at"] or 0)
    expires_at = int(row["expires_at"] or started_at)
    submitted_at = int(row["submitted_at"] or started_at)
    paused_seconds = int(row["paused_seconds"] or 0)
    duration = max(0, submitted_at - started_at - paused_seconds)
    duration = min(duration, max(0, expires_at - started_at - paused_seconds))
    passing_score = int(row["passing_score"] if "passing_score" in keys and row["passing_score"] is not None else EXAM_PASS_SCORE)
    node_id = row["node_id"] if "node_id" in keys else None
    exam_type = row["exam_type"] if "exam_type" in keys else "category"
    return {
        "success": bool(row["submitted"]),
        "session_id": row["session_id"],
        "score": int(row["score"] or 0),
        "passed": bool(row["passed"]),
        "correct": int(row["correct"] or 0),
        "total": int(row["total"] or 0),
        "duration": duration,
        "time_expired": bool(row["time_expired"]),
        "answers": answers,
        "details": details,
        "pass_score": passing_score,
        "passing_score": passing_score,
        "node_id": node_id,
        "exam_type": exam_type,
        "submitted": bool(row["submitted"]),
        "offline": False,
    }



@app.post("/api/exam/build")
def exam_build(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    nodes = _exam_nodes_from_payload(payload, tree)
    if not nodes:
        raise HTTPException(422, "Aucun cours ne correspond au périmètre demandé.")
    count = _bounded_exam_integer(payload.get("count"), "count", EXAM_QUESTION_COUNT, 1, EXAM_MAX_QUESTION_COUNT)
    default_time = _bounded_exam_integer(payload.get("minutes"), "minutes", EXAM_DURATION_SECONDS // 60, 1, EXAM_MAX_DURATION_SECONDS // 60) * 60
    time_limit = _bounded_exam_integer(
        payload.get("time_limit"), "time_limit", default_time,
        EXAM_MIN_DURATION_SECONDS, EXAM_MAX_DURATION_SECONDS,
    )
    category = str(payload.get("category") or ("Tous modules" if str(payload.get("module") or "").lower() == "all" else payload.get("module") or nodes[0].category))
    return _create_exam_session(tree, nodes, count=count, time_limit=time_limit, category=category)


@app.post("/api/exam/submit")
def exam_submit(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id or len(session_id) > 64:
        raise HTTPException(422, "Identifiant de session manquant ou invalide.")
    row = tree.conn.execute("SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Session d’examen introuvable.")
    if row["submitted"]:
        return _exam_result_payload(row)
    if row["paused_at"] is not None:
        raise HTTPException(409, "L’examen est en pause. Reprends-le avant de le terminer.")

    try:
        raw_ids = json.loads(row["question_ids"] or "[]")
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(409, "La liste des questions de cette session est invalide.") from error
    questions = _exam_load_session_questions(tree, raw_ids)
    raw_answers = payload.get("answers", [])
    if not isinstance(raw_answers, list):
        raise HTTPException(422, "Les réponses doivent être envoyées sous forme de liste.")
    if len(raw_answers) > len(questions):
        raise HTTPException(422, "Le nombre de réponses dépasse le nombre de questions.")
    answers = [
        _sanitize_exam_answer(question, raw_answers[index] if index < len(raw_answers) else None)
        for index, question in enumerate(questions)
    ]

    node_id = row["node_id"]
    exam_type = str(row["exam_type"] or "category")
    course_node: Node | None = None
    if exam_type == "course":
        if not isinstance(node_id, str) or not node_id:
            raise HTTPException(409, "La session d’examen de cours ne contient pas de cours associé.")
        try:
            course_node = tree.node(node_id)
        except DomainError as error:
            raise HTTPException(409, "Le cours associé à cette session n’existe plus.") from error
        requirement = course_node.requirement(ProofKind.EXAM)
        if requirement is None:
            raise HTTPException(409, "Le cours ne possède plus d’exigence d’examen.")
        if any(question.node_id != node_id or question.scope is not ProofKind.EXAM for question in questions):
            raise HTTPException(409, "Les questions ne correspondent pas à la banque d’examen de ce cours.")
        passing_score = EXAM_PASS_SCORE
    else:
        if node_id:
            raise HTTPException(409, "Le périmètre de cette session d’examen est incohérent.")
        # Les sessions non terminées suivent la règle officielle courante, même si elles
        # ont été créées avant le déploiement du seuil uniforme.
        passing_score = EXAM_PASS_SCORE

    now = int(time.time())
    expires_at = int(row["expires_at"])
    too_late = now > expires_at + EXAM_SUBMIT_GRACE_SECONDS
    timed_out = now >= expires_at or too_late
    if too_late:
        # Après le délai réseau de grâce, aucune réponse reçue tardivement n’est retenue.
        answers = [None] * len(questions)

    details = [_grade_exam_question(question, answers[index]) for index, question in enumerate(questions)]
    correct = sum(1 for item in details if item["correct"])
    total = len(questions)
    score = round(100 * correct / total) if total else 0
    passed = score >= passing_score
    submitted_at = min(now, expires_at) if timed_out else now
    started_at = int(row["started_at"] or submitted_at)
    paused_seconds = int(row["paused_seconds"] or 0)
    duration = max(0, submitted_at - started_at - paused_seconds)
    duration = min(duration, max(0, expires_at - started_at - paused_seconds))

    result = {
        "success": True,
        "session_id": session_id,
        "score": score,
        "passed": passed,
        "correct": correct,
        "total": total,
        "duration": duration,
        "time_expired": bool(timed_out),
        "answers": answers,
        "details": details,
        "pass_score": passing_score,
        "passing_score": passing_score,
        "node_id": node_id,
        "exam_type": exam_type,
        "submitted": True,
        "offline": False,
        "submitted_at": submitted_at,
        **({
            "module_scope": str(row["module_scope"] or ""),
            "level_scope": str(row["level_scope"] or ""),
            "scope_node_ids": json.loads(row["scope_node_ids_json"] or "[]"),
        } if exam_type == "certification" else {}),
    }

    if course_node is not None:
        # Réserve la session avant tout effet de bord (tentative, XP, badges).
        # L'UPDATE conditionnel sérialise deux soumissions concurrentes sur la même session.
        reservation = tree.conn.execute(
            "UPDATE exam_sessions SET passing_score = ? "
            "WHERE session_id = ? AND submitted = 0 AND paused_at IS NULL",
            (passing_score, session_id),
        )
        if getattr(reservation, "rowcount", 1) == 0:
            tree.conn.rollback()
            latest = tree.conn.execute(
                "SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if latest is not None and latest["submitted"]:
                return _exam_result_payload(latest)
            raise HTTPException(409, "La session d’examen ne peut plus être corrigée.")

        try:
            _attempt, validated = tree.record(
                course_node.id,
                ProofKind.EXAM,
                score,
                passed,
                evidence=json.dumps(
                    {"session_id": session_id, "question_ids": [question.id for question in questions]},
                    ensure_ascii=False,
                ),
                detail=f"Examen : {correct}/{total} bonnes réponses",
                commit=False,
            )
        except DomainError as error:
            tree.conn.rollback()
            raise HTTPException(409, str(error)) from error
        except Exception:
            tree.conn.rollback()
            raise
        result["validated"] = validated
        result["status"] = tree.status(course_node.id).value
        result["xp_gained"] = (tree.last_reward or {}).get("xp", 0)
        result["badges_unlocked"] = tree.last_badges

    cursor = tree.conn.execute(
        "UPDATE exam_sessions SET submitted = 1, score = ?, passed = ?, correct = ?, total = ?, "
        "submitted_at = ?, time_expired = ?, answers_json = ?, details_json = ?, passing_score = ?, "
        "result_json = ?, paused_at = NULL WHERE session_id = ? AND submitted = 0 AND paused_at IS NULL",
        (
            score,
            int(passed),
            correct,
            total,
            submitted_at,
            int(timed_out),
            json.dumps(answers, ensure_ascii=False),
            json.dumps(details, ensure_ascii=False),
            passing_score,
            json.dumps(result, ensure_ascii=False),
            session_id,
        ),
    )
    if getattr(cursor, "rowcount", 1) == 0:
        # Annule également la preuve et les récompenses si une autre requête a gagné.
        tree.conn.rollback()
        latest = tree.conn.execute(
            "SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if latest is not None and latest["submitted"]:
            return _exam_result_payload(latest)
        raise HTTPException(409, "La session d’examen a changé pendant sa correction.")

    # La tentative de cours, les récompenses et le résultat de session sont atomiques.
    tree.conn.commit()
    return result


@app.post("/api/exam/pause")
def exam_pause(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id or len(session_id) > 64:
        raise HTTPException(422, "Identifiant de session manquant ou invalide.")
    row = tree.conn.execute("SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Session d'examen introuvable.")
    if row["submitted"]:
        raise HTTPException(409, "Cet examen est déjà terminé.")
    if row["paused_at"] is not None:
        return {"session_id": session_id, "paused": True, "paused_at": int(row["paused_at"])}
    now = int(time.time())
    if now >= int(row["expires_at"]):
        raise HTTPException(409, "Le temps est écoulé : l'examen ne peut plus être mis en pause.")
    cursor = tree.conn.execute(
        "UPDATE exam_sessions SET paused_at = ? WHERE session_id = ? AND submitted = 0 AND paused_at IS NULL",
        (now, session_id),
    )
    tree.conn.commit()
    if getattr(cursor, "rowcount", 1) == 0:
        row = tree.conn.execute("SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)).fetchone()
        if row is None or row["submitted"]:
            raise HTTPException(409, "La session a été terminée avant la mise en pause.")
        return {"session_id": session_id, "paused": row["paused_at"] is not None, "paused_at": row["paused_at"]}
    return {"session_id": session_id, "paused": True, "paused_at": now}


@app.post("/api/exam/resume")
def exam_resume(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id or len(session_id) > 64:
        raise HTTPException(422, "Identifiant de session manquant ou invalide.")
    row = tree.conn.execute("SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Session d'examen introuvable.")
    if row["submitted"]:
        raise HTTPException(409, "Cet examen est déjà terminé.")
    if row["paused_at"] is None:
        return {"session_id": session_id, "paused": False, "resumed_seconds": 0}
    now = int(time.time())
    paused_at = int(row["paused_at"])
    paused_duration = max(0, now - paused_at)
    new_expiry = int(row["expires_at"]) + paused_duration
    cursor = tree.conn.execute(
        "UPDATE exam_sessions SET expires_at = ?, paused_seconds = paused_seconds + ?, paused_at = NULL "
        "WHERE session_id = ? AND submitted = 0 AND paused_at = ?",
        (new_expiry, paused_duration, session_id, paused_at),
    )
    tree.conn.commit()
    if getattr(cursor, "rowcount", 1) == 0:
        row = tree.conn.execute("SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)).fetchone()
        if row is None or row["submitted"]:
            raise HTTPException(409, "La session a été terminée avant la reprise.")
        return {"session_id": session_id, "paused": row["paused_at"] is not None, "resumed_seconds": 0}
    return {"session_id": session_id, "paused": False, "resumed_seconds": paused_duration, "expires_at": new_expiry}


@app.post("/api/exam/start")
def exam_start_alias(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    """Démarre un examen blanc par catégorie ou l’examen dédié à un cours."""
    if not isinstance(payload, dict):
        raise HTTPException(422, "Un objet JSON est attendu.")

    requested_node_id = payload.get("node_id")
    if requested_node_id is not None:
        if not isinstance(requested_node_id, str) or not requested_node_id.strip():
            raise HTTPException(422, "node_id manquant ou invalide.")
        try:
            node = tree.node(requested_node_id.strip())
        except DomainError as error:
            raise HTTPException(404, str(error)) from error
        requirement = node.requirement(ProofKind.EXAM)
        if requirement is None:
            raise HTTPException(409, "Ce cours ne possède pas d’exigence d’examen dédiée.")
        try:
            tree.playable(node.id)
        except DomainError as error:
            raise HTTPException(409, str(error)) from error

        # Cet examen utilise exclusivement la banque dédiée du cours demandé.
        # Le lecteur actuel rend les QCM ; les questions texte/terminal restent dans le centre avancé.
        question_pool = [
            question
            for question in tree.questions(node.id, ProofKind.EXAM)
            if question.question_type == "qcm"
        ]
        if not question_pool:
            raise HTTPException(422, "Aucune question QCM d’examen dédiée n’est disponible pour ce cours.")
        return _create_exam_session(
            tree,
            [node],
            count=EXAM_QUESTION_COUNT,
            time_limit=EXAM_DURATION_SECONDS,
            category=node.title,
            question_pool=question_pool,
            node_id=node.id,
            exam_type="course",
        )

    category = payload.get("category")
    if not isinstance(category, str) or not category.strip():
        raise HTTPException(422, "Catégorie d’examen manquante ou invalide.")
    category = category.strip()
    nodes = [node for node in tree.nodes() if node.category == category]
    if not nodes:
        raise HTTPException(404, "Catégorie d’examen introuvable.")

    # L’onglet Mode examen présente les questions sous forme de QCM.
    question_pool = [
        question
        for question in _exam_question_pool(tree, nodes)
        if question.question_type == "qcm"
    ]
    return _create_exam_session(
        tree,
        nodes,
        count=EXAM_QUESTION_COUNT,
        time_limit=EXAM_DURATION_SECONDS,
        category=category,
        question_pool=question_pool,
    )


@app.post("/api/tutor")
def tutor_alias(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    """Répond à une question en utilisant le cours courant et, si fourni, le passage sélectionné."""
    node_id = str(payload.get("node_id") or "").strip()
    question = str(payload.get("question") or "").strip()
    selected_text = str(payload.get("selected_text") or "").strip()[:1800]
    if not node_id:
        raise HTTPException(400, "node_id manquant")
    if not question:
        raise HTTPException(422, "Écris une question pour le tuteur.")
    if len(question) > 2000:
        raise HTTPException(422, "La question est trop longue (2 000 caractères maximum).")

    node = _get_node(tree, node_id)
    lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
    context = lessons.get(node.id, "")[:TUTOR_MAX_CONTEXT_CHARS]

    api_key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not api_key:
        return {
            "answer": (
                "Le tuteur IA est désactivé : la variable GROQ_API_KEY manque dans la configuration Render. "
                "Ouvre le tableau de bord Render, sélectionne le service Skill-Tree, puis Environment. "
                "Ajoute GROQ_API_KEY avec une clé créée sur console.groq.com et redéploie le service. "
                "Ne publie jamais cette clé dans GitHub ni dans le chat."
            )
        }

    system_message = (
        "Tu es le tuteur pédagogique intégré à Skill-Tree. Réponds toujours en français, "
        "avec un français grammaticalement soigné, des phrases complètes et une progression logique. "
        "Adapte la profondeur au niveau du cours. Explique l'idée centrale, puis le mécanisme, "
        "un exemple concret, les limites ou erreurs fréquentes, et termine par une synthèse courte. "
        "Définis les acronymes à leur première apparition et explique les relations de cause à effet. "
        "Évite les phrases télégraphiques, les répétitions, les tableaux et les blocs de code sauf demande. "
        "Rédige un texte agréable à lire à voix haute : ponctuation naturelle, transitions explicites et phrases complètes. "
        "Pour expliquer un schéma, ne donne pas seulement un inventaire : présente (1) l'objectif du dessin, "
        "(2) les composants et leur rôle, (3) les liens entre eux, (4) le trajet d'un exemple concret, étape par étape, "
        "(5) la différence entre liaison physique, échanges locaux, routage et protocoles lorsque le cours le permet, "
        "(6) les simplifications du dessin et (7) une synthèse. Explique pourquoi les données passent d'un composant au suivant. "
        "N'invente ni port, adresse IP, câble, protocole, état actif, ni détail visuel absent du contenu. "
        "Une flèche illustrative ne prouve ni un trafic en temps réel ni une liaison physiquement unidirectionnelle. "
        "Si le dessin ne permet pas de conclure, précise cette limite ; si le cours est insuffisant, indique ce qui manque. "
        "Ne prétends pas avoir vu une image qui n'est pas décrite dans le contexte.\n\n"
        f"COURS ACTUEL : {node.title}\nCONTENU DU COURS :\n{context}"
    )
    if selected_text:
        system_message += f"\n\nPASSAGE SÉLECTIONNÉ PAR L'APPRENANT :\n{selected_text}"

    history = payload.get("history")
    chat_messages = []
    if isinstance(history, list):
        for item in history[-8:]:
            if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
                continue
            content = str(item.get("content") or "").strip()
            if content:
                chat_messages.append({"role": item["role"], "content": content[:3000]})
    chat_messages = [{"role": "system", "content": system_message}, *chat_messages, {"role": "user", "content": question}]

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=GROQ_DEFAULT_MODEL,
            messages=chat_messages,
            temperature=0.25,
            max_tokens=1100,
        )
        answer = completion.choices[0].message.content
        return {"answer": answer or "Je n’ai pas pu formuler une réponse. Peux-tu reformuler ta question ?"}
    except Exception as error:
        print(f"Erreur Tuteur Skill-Tree ({type(error).__name__}).")
        return {"answer": "Le tuteur rencontre momentanément un problème. Réessaie dans quelques instants."}

@app.post("/api/tts")
async def generate_speech(payload: SpeechRequest) -> Response:
    """Génère un segment audio MP3 et réessaie avec d'autres voix en cas de panne."""
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="Le texte à prononcer ne peut pas être vide.")

    try:
        import edge_tts
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Le moteur de voix n’est pas installé. Le lecteur va essayer la voix de secours du navigateur.",
        ) from None

    rate_percent = int(round((payload.rate - 1.0) * 100))
    voices = (
        "fr-FR-DeniseNeural",
        "fr-FR-HenriNeural",
        "fr-CA-SylvieNeural",
        "fr-FR-DeniseNeural",
    )
    audio_data = b""
    failures: list[str] = []

    for attempt_index, voice in enumerate(voices):
        try:
            communicate = edge_tts.Communicate(
                payload.text,
                voice=voice,
                rate=f"{rate_percent:+d}%",
            )
            audio_parts: list[bytes] = []
            async for chunk in communicate.stream():
                if chunk.get("type") == "audio" and chunk.get("data"):
                    audio_parts.append(chunk["data"])
            audio_data = b"".join(audio_parts)
            if audio_data:
                break
            raise RuntimeError("NoAudioReceived")
        except Exception as error:
            error_type = type(error).__name__
            failures.append(f"{voice}:{error_type}")
            # Journalise la voix et le type d'erreur, jamais le texte à prononcer.
            print(f"Échec TTS voix={voice} type={error_type}")
            if attempt_index < len(voices) - 1:
                await asyncio.sleep(0.25 * (attempt_index + 1))

    if not audio_data:
        print("Synthèse vocale indisponible après plusieurs tentatives: " + ", ".join(failures))
        raise HTTPException(
            status_code=502,
            detail="La voix en ligne ne répond pas. Le lecteur va essayer la voix de secours du navigateur.",
        ) from None

    return Response(
        content=audio_data,
        media_type="audio/mpeg",
        headers={"Cache-Control": "private, max-age=300"},
    )


@app.post("/api/topology")
def save_topology_alias(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tree.conn.execute("INSERT INTO topologies (name, data, updated_at) VALUES (?, ?, ?)", ("Mon lab", json.dumps(payload, ensure_ascii=False), updated_at))
    tree.conn.commit()
    return {"success": True}


def _validate_workspace_topology(value: Any) -> dict[str, Any]:
    """Valide la structure v2 sans supprimer les champs d'extension du client."""
    if not isinstance(value, dict):
        raise HTTPException(status_code=422, detail="Le champ 'topology' doit être un objet JSON.")
    if value.get("schema_version") != 2:
        raise HTTPException(status_code=422, detail="La topologie doit utiliser schema_version=2.")
    if not isinstance(value.get("nodes"), list) or not isinstance(value.get("links"), list):
        raise HTTPException(
            status_code=422,
            detail="Une topologie v2 doit contenir des listes 'nodes' et 'links'.",
        )
    try:
        # Pydantic vérifie les champs connus (types d'équipement, ports, liens, etc.).
        # On renvoie toutefois l'objet d'origine afin de préserver les champs d'extension.
        Topology(**value)
    except (ValidationError, TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=f"Topologie v2 invalide : {error}")
    return value


@app.post("/api/lab/v2/{lab_id}/save")
def save_lab_topology_v2(lab_id: str, payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Enregistre la dernière topologie de travail associée à un lab v2."""
    topology = _strip_legacy_auto_practice_branch(
        _validate_workspace_topology(payload.get("topology"))
    )

    try:
        serialized = json.dumps(topology, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=f"Topologie non sérialisable : {error}")

    name = f"lab_{lab_id}"
    updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn = connect(DB_PATH)
    try:
        # Render ne doit jamais annoncer une sauvegarde réussie dans le disque
        # SQLite éphémère : la persistance de production exige PostgreSQL/Neon.
        if os.environ.get("RENDER_SERVICE_ID") and not getattr(conn, "is_postgres", False):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Stockage durable indisponible : ce service Render n'utilise pas "
                    "PostgreSQL/Neon. La sauvegarde n'a pas été enregistrée."
                ),
            )

        columns = {row["name"] for row in conn.execute('PRAGMA table_info("topologies")')}
        if not {"id", "name", "data", "updated_at"}.issubset(columns):
            raise HTTPException(status_code=503, detail="La table topologies est absente ou incompatible.")

        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute(
            "SELECT id FROM topologies WHERE name = ? ORDER BY updated_at DESC, id DESC LIMIT 1",
            (name,),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE topologies SET data = ?, updated_at = ? WHERE id = ?",
                (serialized, updated_at, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO topologies (name, data, updated_at) VALUES (?, ?, ?)",
                (name, serialized, updated_at),
            )
        conn.commit()

        # Confirmer la lecture de la valeur réellement persistée avant de renvoyer
        # success=true ; un simple commit sans relecture ne suffit pas au contrat UI.
        persisted = conn.execute(
            "SELECT data, updated_at FROM topologies WHERE name = ? "
            "ORDER BY updated_at DESC, id DESC LIMIT 1",
            (name,),
        ).fetchone()
        if persisted is None or persisted["data"] != serialized:
            raise HTTPException(
                status_code=500,
                detail="La base n'a pas confirmé la topologie après l'enregistrement.",
            )
        updated_at = str(persisted["updated_at"])
    except HTTPException:
        conn.rollback()
        raise
    except sqlite3.ERROR_CLASSES as error:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur SQLite pendant la sauvegarde : {error}")
    finally:
        conn.close()

    return {
        "success": True,
        "lab_id": lab_id,
        "name": name,
        "updated_at": updated_at,
        "storage_backend": "postgresql" if getattr(conn, "is_postgres", False) else "sqlite",
    }


@app.get("/api/lab/v2/{lab_id}/load")
def load_lab_topology_v2(lab_id: str) -> dict[str, Any]:
    """Récupère la dernière topologie sauvegardée pour ce lab v2."""
    name = f"lab_{lab_id}"
    conn = connect(DB_PATH)
    try:
        if os.environ.get("RENDER_SERVICE_ID") and not getattr(conn, "is_postgres", False):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Stockage durable indisponible : ce service Render n'utilise pas "
                    "PostgreSQL/Neon. La topologie sauvegardée ne peut pas être chargée."
                ),
            )

        columns = {row["name"] for row in conn.execute('PRAGMA table_info("topologies")')}
        if not {"id", "name", "data", "updated_at"}.issubset(columns):
            raise HTTPException(status_code=503, detail="La table topologies est absente ou incompatible.")

        row = conn.execute(
            "SELECT data, updated_at FROM topologies WHERE name = ? ORDER BY updated_at DESC, id DESC LIMIT 1",
            (name,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Aucune topologie sauvegardée pour ce lab.")
        try:
            topology_data = json.loads(row["data"])
        except (json.JSONDecodeError, TypeError) as error:
            raise HTTPException(status_code=500, detail=f"Topologie sauvegardée invalide : {error}")
        if not isinstance(topology_data, dict):
            raise HTTPException(status_code=500, detail="La topologie sauvegardée n'est pas un objet JSON.")
        try:
            topology_data = _strip_legacy_auto_practice_branch(
                _validate_workspace_topology(topology_data)
            )
        except HTTPException as error:
            raise HTTPException(
                status_code=500,
                detail=f"Topologie sauvegardée invalide : {error.detail}",
            )

        return {
            "success": True,
            "lab_id": lab_id,
            "name": name,
            "topology": topology_data,
            "updated_at": row["updated_at"],
        }
    except HTTPException:
        raise
    except sqlite3.ERROR_CLASSES as error:
        raise HTTPException(status_code=500, detail=f"Erreur SQLite pendant le chargement : {error}")
    finally:
        conn.close()


def _certificate_scope(tree: SkillTree, module_label: object, level_slug: object) -> tuple[str, list[Node]]:
    if not isinstance(module_label, str) or not module_label.strip():
        raise HTTPException(422, "Le module du diplôme est manquant ou invalide.")
    if not isinstance(level_slug, str) or level_slug.strip().lower() not in {"debutant", "intermediaire", "expert"}:
        raise HTTPException(422, "Le niveau du diplôme est invalide.")

    requested_module = module_label.strip()
    normalized_level = level_slug.strip().lower()
    nodes = tree.nodes()
    canonical_module = next(
        (node.module for node in nodes if node.module.strip().casefold() == requested_module.casefold()),
        None,
    )
    if canonical_module is None:
        raise HTTPException(404, "Module introuvable dans le parcours.")

    scope = [
        node for node in nodes
        if node.module == canonical_module and _exam_level(node.id, node.title) == normalized_level
    ]
    if not scope:
        raise HTTPException(404, "Aucun cours ne correspond à ce module et à ce niveau.")
    return canonical_module, scope


def _certificate_payload(row) -> dict:
    number = str(row["number"])
    return {
        "id": number,
        "number": number,
        "name": str(row["name"]),
        "module": str(row["module_id"] or ""),
        "module_id": str(row["module_id"] or ""),
        "module_label": str(row["module"] or ""),
        "level": str(row["level_slug"] or ""),
        "date": str(row["issued_at"]),
        "issued_at": str(row["issued_at"]),
        "score": int(row["score"] or 0),
        "courses": int(row["courses_count"] or 0),
        "exam_session_id": str(row["exam_session_id"] or ""),
    }


@app.get("/api/certificates")
def list_certificates(tree: SkillTree = Depends(get_tree)) -> dict:
    rows = tree.conn.execute(
        "SELECT number, name, level, issued_at, module, module_id, level_slug, "
        "exam_session_id, score, courses_count FROM certificates "
        "WHERE module <> '' AND level_slug <> '' ORDER BY issued_at DESC"
    ).fetchall()
    certificates = [_certificate_payload(row) for row in rows]

    exam_rows = tree.conn.execute(
        "SELECT session_id, module_scope, level_scope, scope_node_ids_json, score, passed, "
        "total, submitted_at, time_expired FROM exam_sessions "
        "WHERE exam_type = 'certification' AND submitted = 1 "
        "AND module_scope <> '' AND level_scope <> '' ORDER BY submitted_at DESC"
    ).fetchall()
    exams = []
    for row in exam_rows:
        try:
            node_ids = json.loads(row["scope_node_ids_json"] or "[]")
            if not isinstance(node_ids, list) or not all(isinstance(item, str) for item in node_ids):
                node_ids = []
        except (TypeError, ValueError, json.JSONDecodeError):
            node_ids = []
        exams.append({
            "session_id": str(row["session_id"]),
            "module_label": str(row["module_scope"]),
            "level": str(row["level_scope"]),
            "score": int(row["score"] or 0),
            "passed": bool(row["passed"]) and int(row["score"] or 0) >= EXAM_PASS_SCORE,
            "total": int(row["total"] or 0),
            "submitted_at": int(row["submitted_at"] or 0),
            "time_expired": bool(row["time_expired"]),
            "scope_node_ids": node_ids,
        })
    return {"items": certificates, "exams": exams}


@app.post("/api/certificate/exam/start")
def start_certificate_exam(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    module_label, scope = _certificate_scope(tree, payload.get("module"), payload.get("level"))
    statuses = tree.statuses()
    missing = [node.title for node in scope if statuses.get(node.id) is not Status.VALIDATED]
    if missing:
        preview = ", ".join(missing[:4])
        suffix = "…" if len(missing) > 4 else ""
        raise HTTPException(
            409,
            f"Tous les cours du niveau doivent être validés avant l’examen de diplôme. "
            f"Cours restants : {preview}{suffix}",
        )

    question_pool = [
        question for question in _exam_question_pool(tree, scope)
        if question.question_type == "qcm"
    ]
    if not question_pool:
        raise HTTPException(422, "Aucune question QCM disponible pour l’examen officiel de ce niveau.")

    level_slug = str(payload.get("level")).strip().lower()
    level_label = {
        "debutant": "Débutant",
        "intermediaire": "Intermédiaire",
        "expert": "Expert",
    }[level_slug]
    return _create_exam_session(
        tree,
        scope,
        count=EXAM_QUESTION_COUNT,
        time_limit=EXAM_DURATION_SECONDS,
        category=f"Diplôme · {module_label} · {level_label}",
        question_pool=question_pool,
        exam_type="certification",
        module_scope=module_label,
        level_scope=level_slug,
        scope_node_ids=[node.id for node in scope],
    )


@app.post("/api/certificate/issue")
def issue_certificate(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    module_label, scope = _certificate_scope(tree, payload.get("module"), payload.get("level"))
    level_slug = str(payload.get("level")).strip().lower()

    existing = tree.conn.execute(
        "SELECT number, name, level, issued_at, module, module_id, level_slug, "
        "exam_session_id, score, courses_count FROM certificates "
        "WHERE module = ? AND level_slug = ?",
        (module_label, level_slug),
    ).fetchone()
    if existing is not None:
        return {"success": True, "already_issued": True, "certificate": _certificate_payload(existing)}

    statuses = tree.statuses()
    missing = [node.title for node in scope if statuses.get(node.id) is not Status.VALIDATED]
    if missing:
        raise HTTPException(409, "Le diplôme exige la validation de tous les cours du niveau.")

    session_id = str(payload.get("exam_session_id") or "").strip()
    if not session_id or len(session_id) > 64:
        raise HTTPException(422, "Identifiant de session d’examen manquant ou invalide.")
    exam = tree.conn.execute(
        "SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    if exam is None or str(exam["exam_type"] or "") != "certification":
        raise HTTPException(409, "Cette session n’est pas un examen officiel de diplôme.")
    if not exam["submitted"] or not exam["passed"] or int(exam["score"] or 0) < EXAM_PASS_SCORE:
        raise HTTPException(409, f"L’examen officiel doit être terminé avec au moins {EXAM_PASS_SCORE} %.")
    if (
        str(exam["module_scope"] or "") != module_label
        or str(exam["level_scope"] or "") != level_slug
    ):
        raise HTTPException(409, "L’examen réussi ne correspond pas au module et au niveau demandés.")
    try:
        submitted_scope = json.loads(exam["scope_node_ids_json"] or "[]")
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(409, "Le périmètre de la session d’examen est invalide.") from error
    expected_scope = [node.id for node in scope]
    if not isinstance(submitted_scope, list) or sorted(submitted_scope) != sorted(expected_scope):
        raise HTTPException(409, "Le périmètre des cours a changé depuis l’examen ; repasse l’examen du niveau.")

    submitted_name = str(payload.get("name") or "").strip()
    configured_name = str(CERTIFICATE_NAME or "").strip()
    placeholders = {"ton nom", "votre nom", "your name", "full name"}
    if not submitted_name or submitted_name.casefold() in placeholders:
        if not configured_name or configured_name.casefold() in placeholders:
            raise HTTPException(
                422,
                "Renseigne ton nom dans les paramètres avant de délivrer le diplôme.",
            )
        name = configured_name
    else:
        name = submitted_name
    if not name:
        raise HTTPException(422, "Le nom à inscrire sur le diplôme est obligatoire.")
    if len(name) > 100:
        raise HTTPException(422, "Le nom inscrit sur le diplôme doit faire 100 caractères maximum.")
    module_id = str(payload.get("module_id") or "").strip()
    if not module_id or len(module_id) > 100 or not re.fullmatch(r"[a-zA-Z0-9_-]+", module_id):
        raise HTTPException(422, "Identifiant du module invalide.")

    number = "SKT-" + uuid.uuid4().hex[:12].upper()
    issued_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    level_number = {"debutant": 1, "intermediaire": 2, "expert": 3}[level_slug]
    try:
        tree.conn.execute(
            "INSERT INTO certificates "
            "(number, name, level, issued_at, module, module_id, level_slug, exam_session_id, score, courses_count) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                number, name, level_number, issued_at, module_label, module_id,
                level_slug, session_id, int(exam["score"]), len(scope),
            ),
        )
        tree.conn.commit()
    except sqlite3.INTEGRITY_ERROR_CLASSES:
        tree.conn.rollback()
        existing = tree.conn.execute(
            "SELECT number, name, level, issued_at, module, module_id, level_slug, "
            "exam_session_id, score, courses_count FROM certificates "
            "WHERE module = ? AND level_slug = ?",
            (module_label, level_slug),
        ).fetchone()
        if existing is None:
            raise
        return {"success": True, "already_issued": True, "certificate": _certificate_payload(existing)}

    row = tree.conn.execute(
        "SELECT number, name, level, issued_at, module, module_id, level_slug, "
        "exam_session_id, score, courses_count FROM certificates WHERE number = ?",
        (number,),
    ).fetchone()
    return {"success": True, "already_issued": False, "certificate": _certificate_payload(row)}


def _pdf_literal(value: object) -> bytes:
    text = str(value or "").replace("\r", " ").replace("\n", " ")
    encoded = text.encode("cp1252", "replace")
    escaped = encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    return b"(" + escaped + b")"


def _certificate_pdf(certificate: dict) -> bytes:
    module_label = certificate["module"]
    level_label = {
        "debutant": "Débutant",
        "intermediaire": "Intermédiaire",
        "expert": "Expert",
    }.get(certificate["level"], str(certificate["level"]))
    date_label = str(certificate["issued_at"]).replace("T", " ").replace("+00:00", " UTC")
    lines = [
        (b"/F2 30 Tf", 150, 475, "SKILL TREE"),
        (b"/F1 15 Tf", 150, 438, "CERTIFICAT DE RÉUSSITE"),
        (b"/F1 12 Tf", 150, 392, "Ce certificat atteste que"),
        (b"/F2 24 Tf", 150, 350, certificate["name"]),
        (b"/F1 12 Tf", 150, 309, "a validé l’ensemble des cours du niveau"),
        (b"/F2 18 Tf", 150, 279, level_label),
        (b"/F2 15 Tf", 150, 250, module_label),
        (b"/F1 12 Tf", 150, 206, f"Résultat à l’examen officiel : {certificate['score']} %"),
        (b"/F1 12 Tf", 150, 183, f"Cours validés : {certificate['courses']}"),
        (b"/F1 10 Tf", 150, 137, f"Numéro de certificat : {certificate['number']}"),
        (b"/F1 10 Tf", 150, 116, f"Délivré le : {date_label}"),
    ]
    commands = [
        b"q",
        b"0.10 0.20 0.35 RG 3 w 26 26 790 543 re S",
        b"0.73 0.55 0.25 RG 1 w 38 38 766 519 re S",
        b"Q",
    ]
    for font, x, y, label in lines:
        commands.append(b"BT " + font + f" 1 0 0 1 {x} {y} Tm ".encode("ascii") + _pdf_literal(label) + b" Tj ET")
    stream = b"\n".join(commands) + b"\n"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


@app.get("/api/certificate")
def download_certificate(number: str = Query(..., min_length=1, max_length=80), tree: SkillTree = Depends(get_tree)):
    row = tree.conn.execute(
        "SELECT number, name, level, issued_at, module, module_id, level_slug, "
        "exam_session_id, score, courses_count FROM certificates "
        "WHERE number = ? AND module <> '' AND level_slug <> ''",
        (number.strip(),),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Certificat officiel introuvable.")
    certificate = _certificate_payload(row)
    pdf = _certificate_pdf({
        "number": certificate["number"],
        "name": certificate["name"],
        "module": certificate["module_label"],
        "level": certificate["level"],
        "issued_at": certificate["issued_at"],
        "score": certificate["score"],
        "courses": certificate["courses"],
    })
    safe_number = re.sub(r"[^A-Za-z0-9_-]", "", certificate["number"]) or "diplome"
    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="diplome-{safe_number}.pdf"'},
    )


@app.get("/api/shop")
def read_shop(tree: SkillTree = Depends(get_tree)) -> dict:
    try:
        items = [dict(row) for row in tree.conn.execute("SELECT id, nom, description, prix, type FROM shop_items ORDER BY prix, id")]
        stats = get_user_stats(tree.conn)
        return {"coins": stats["coins"], "items": items}
    except Exception:
        return {"coins": 0, "items": []}

@app.post("/api/shop/buy")
def buy_item(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    item_id = payload.get("item_id")
    item = tree.conn.execute("SELECT id, prix FROM shop_items WHERE id = ?", (item_id,)).fetchone()
    if not item: raise HTTPException(404, "Objet inconnu")
    
    stats = get_user_stats(tree.conn)
    if stats["coins"] < item["prix"]: raise HTTPException(400, "Pas assez de pièces")
    
    tree.conn.execute("UPDATE user_stats SET coins = coins - ? WHERE id = 1", (item["prix"],))
    tree.conn.execute("INSERT INTO shop_inventory (item_id, quantity) VALUES (?, 1) ON CONFLICT(item_id) DO UPDATE SET quantity = quantity + 1", (item_id,))
    tree.conn.commit()
    return {"success": True, "coins": stats["coins"] - item["prix"]}


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    if auth_required():
        if not auth_configuration_ready():
            await websocket.close(code=1013, reason="Authentification non configurée.")
            return
        origin = websocket.headers.get("origin")
        if origin:
            try:
                parsed_origin = urlsplit(origin)
            except ValueError:
                parsed_origin = None
            if (
                parsed_origin is None
                or parsed_origin.scheme not in {"http", "https"}
                or parsed_origin.netloc.lower() != websocket.url.netloc.lower()
                or parsed_origin.path not in {"", "/"}
                or parsed_origin.query
                or parsed_origin.fragment
            ):
                await websocket.close(code=4403, reason="Origine de connexion refusée.")
                return
        if not verify_session_token(websocket.cookies.get(AUTH_COOKIE_NAME)):
            await websocket.close(code=4401, reason="Connexion requise.")
            return
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/trigger-update")
async def trigger_update():
    await manager.broadcast("update")
    return {"status": "ok"}


# ---------------------------------------------------------
# FICHIERS STATIQUES & LANCEMENT (TOUJOURS À LA FIN)
# ---------------------------------------------------------

@app.get("/lab.html")
async def lab_workspace_page():
    return FileResponse(PROJECT_ROOT / "lab.html")

STATIC_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)