"""API HTTP du skill tree (FastAPI) + service de l'interface statique."""
from __future__ import annotations

import asyncio
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
from fastapi.responses import PlainTextResponse, StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from .db import (
    DEFAULT_DB, XP_REWARDS, add_xp, award_attempt_xp, connect, ensure_ready,
    get_user_stats, touch_daily_streak, streak_days,
)
from .domain import Node, ProofKind, Question, Requirement, Status
from .engine import (
    BADGE_DEFINITIONS, DomainError, SkillTree, get_daily_plan, is_validated, requirement_met,
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
# Le seuil affiché partout dans le Centre d'examens et les diplômes est de 70 %.
EXAM_PASS_SCORE = 70
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
    finally:
        conn.close()
    yield

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Skilltree API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lab Workspace v2 : nouvelles routes séparées des endpoints legacy.
app.include_router(lab_v2_router, prefix="/api")

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
        "requirements": [{"kind": r.kind.value, "min_score": r.min_score, "met": requirement_met(r, node)} for r in node.requirements],
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
    statuses = tree.statuses()
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
            "requirements_detail": [{"kind": r.kind.value, "min_score": r.min_score} for r in n.requirements],
        } for fallback_index, n in enumerate(nodes)]
    }

@app.get("/api/stats")
def read_stats(tree: SkillTree = Depends(get_tree)) -> dict:
    nodes = tree.nodes()
    statuses = tree.statuses()
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
        "totals": {"nodes": len(nodes), "validated": sum(1 for s in statuses.values() if s is Status.VALIDATED), "attempts": total_attempts, "success_rate": round(100 * total_passed / total_attempts) if total_attempts else 0},
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

@app.post("/api/lab/start")
def start_lab(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
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
    result = exec_in_lab(payload.get("lab_id"), payload.get("command"))
    return {"success": True, "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.exit_code}

@app.post("/api/lab/validate")
def validate_lab_route(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
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


def _exam_question_pool(tree: SkillTree, nodes: list[Node]) -> list[Question]:
    """Privilégie la banque d'examen; utilise le quiz uniquement si ce cours n'en a pas."""
    pool: list[Question] = []
    for node in nodes:
        dedicated = tree.questions(node.id, ProofKind.EXAM)
        pool.extend(dedicated if dedicated else tree.questions(node.id, ProofKind.QUIZ))
    return pool


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
    passing_score: int | None = None,
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
    effective_pass_score = EXAM_PASS_SCORE if passing_score is None else int(passing_score)
    tree.conn.execute(
        "INSERT INTO exam_sessions "
        "(session_id, category, question_ids, started_at, expires_at, submitted, "
        "score, passed, correct, total, submitted_at, time_expired, answers_json, details_json, "
        "paused_at, paused_seconds, node_id, exam_type, passing_score, result_json) "
        "VALUES (?, ?, ?, ?, ?, 0, NULL, NULL, NULL, ?, NULL, 0, '[]', '[]', NULL, 0, ?, ?, ?, '')",
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
        passing_score = int(requirement.min_score)
    else:
        if node_id:
            raise HTTPException(409, "Le périmètre de cette session d’examen est incohérent.")
        passing_score = int(row["passing_score"] if row["passing_score"] is not None else EXAM_PASS_SCORE)

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
    }

    if course_node is not None:
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
            )
        except DomainError as error:
            raise HTTPException(409, str(error)) from error
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
    tree.conn.commit()
    if getattr(cursor, "rowcount", 1) == 0:
        latest = tree.conn.execute("SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)).fetchone()
        return _exam_result_payload(latest)
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
            passing_score=requirement.min_score,
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


@app.get("/api/certificate")
def download_certificate(request: Request, tree: SkillTree = Depends(get_tree)):
    return StreamingResponse(io.BytesIO(b"PDF EXEMPLE"), media_type="application/pdf")

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