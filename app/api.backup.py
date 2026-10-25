"""API HTTP du skill tree (FastAPI) + service de l'interface statique."""
from __future__ import annotations

import io
import json
import os
import random
import re
import secrets
import sqlite3
import tempfile
import time
import uuid
from fastapi import WebSocket, WebSocketDisconnect
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
from collections import Counter
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

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
from .loader import CONTENT_DIR, ContentError, find_lab_dir, load_content, load_lessons

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
EXAM_PASS_SCORE = 70
EXAM_SUBMIT_GRACE_SECONDS = 15
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"
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

class SandboxCheckRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)

class ShopBuyRequest(BaseModel):
    item_id: str = Field(min_length=1, max_length=64)

class DiagnosticCompleteRequest(BaseModel):
    path: list[str] = Field(min_length=1, max_length=50)
    elapsed_seconds: float | None = Field(default=None, ge=0, le=86400)
    time_limit_seconds: int = Field(default=DIAGNOSTIC_TIME_LIMIT_SECONDS, ge=1, le=3600)


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
    finally:
        conn.close()
    yield


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Skilltree API", lifespan=lifespan)

# Ajout du CORS pour autoriser les WebSockets locaux
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Récupère les données d'un défi d'architecture pour un nœud donné."""
    return tree.conn.execute(
        "SELECT expected_topology, time_limit FROM challenges WHERE node_id = ?",
        (node_id,),
    ).fetchone()


def _streak_payload(tree: SkillTree) -> dict:
    """Calcule le streak actuel et les minutes d'étude."""
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
    if latest is None:
        streak = 0
    elif latest < today - timedelta(days=1):
        streak = 1
    else:
        streak = 0
        cursor = latest
        while cursor in dates:
            streak += 1
            cursor -= timedelta(days=1)

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

@app.get("/api/node/{node_id}/lesson", response_class=PlainTextResponse)
def read_lesson(node_id: str, tree: SkillTree = Depends(get_tree)):
    node = _get_node(tree, node_id)
    content = ""

    try:
        lessons = load_lessons(
            CONTENT_DIR,
            {item.id for item in tree.nodes()},
        )
        content = lessons.get(node.id, "")
    except ContentError as error:
        print(f"Avertissement Loader : {error}")

    # Toujours tenter le fichier individuel si le contenu est absent.
    file_path = CONTENT_DIR / "lessons" / f"{node.id}.md"

    if not content.strip() and file_path.is_file():
        content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Cours introuvable pour le nœud '{node.id}'. "
                f"Fichier attendu : {file_path.name}"
            ),
        )

    return PlainTextResponse(
        content,
        media_type="text/markdown; charset=utf-8",
    )
@app.get("/api/node/{node_id}")
def read_node(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    node = _get_node(tree, node_id)
    status = tree.status(node.id)
    lab = tree.lab_spec(node.id)
    challenge_payload = None
    if challenge:
        expected_topology = challenge["expected_topology"]
        if isinstance(expected_topology, str):
            try:
                expected_topology = json.loads(expected_topology)
            except (TypeError, ValueError):
                expected_topology = None
        challenge_payload = {"prompt": node.description, "time_limit": challenge["time_limit"], "expected_topology": expected_topology}

        # Récupérer le défi AVANT de l'utiliser
    challenge = _challenge_row(tree, node.id)
    challenge_payload = None

    if challenge:
        expected_topology = challenge["expected_topology"]

        if isinstance(expected_topology, str):
            try:
                expected_topology = json.loads(expected_topology)
            except (TypeError, ValueError):
                expected_topology = None

        challenge_payload = {
            "prompt": node.description,
            "time_limit": challenge["time_limit"],
            "expected_topology": expected_topology,
        }
    
    return {
        "id": node.id,
        "title": node.title,
        "category": node.category,
        "description": node.description,
        "status": status.value,
        "prereqs": [{"id": p, "title": tree.node(p).title, "status": tree.status(p).value} for p in node.prereqs],
        "requirements": [{"kind": r.kind.value, "min_score": r.min_score, "met": requirement_met(r, node)} for r in node.requirements],
        "lab": {"kind": lab.kind, "prompt": lab.prompt, "hint": lab.hint} if lab else None,
        "terminal": terminal_spec,
        "challenge": challenge_payload,
    }

@app.get("/api/node/{node_id}/quiz")
def read_quiz(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict[str, Any]:
    """Fournit uniquement l'énoncé et les choix; les réponses restent côté serveur."""
    try:
        tree.playable(node_id)
    except DomainError as error:
        raise HTTPException(status_code=409, detail=str(error))

    questions = tree.questions(node_id, ProofKind.QUIZ)
    if not questions:
        raise HTTPException(status_code=404, detail="Aucun quiz défini pour ce cours.")
    return {
        "questions": [
            {
                "id": question.id,
                "type": question.question_type,
                "prompt": question.prompt,
                "choices": list(question.choices),
            }
            for question in questions
        ]
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
    validated = sum(1 for status in statuses.values() if status is Status.VALIDATED)
    architecture_nodes = {row["node_id"] for row in tree.conn.execute("SELECT node_id FROM challenges")}
    return {
        "total": len(nodes), "validated": validated,
        "nodes": [{"id": n.id, "title": n.title, "category": n.category, "status": statuses[n.id].value, "prereqs": list(n.prereqs), "requirements_detail": [{"kind": r.kind.value, "min_score": r.min_score} for r in n.requirements]} for n in nodes]
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
    exams = tree.conn.execute("SELECT COUNT(*) FROM attempts WHERE kind='exam' AND passed=1").fetchone()[0]
    try:
        stored_exam_passes = tree.conn.execute("SELECT COUNT(*) FROM exam_submissions WHERE passed = 1").fetchone()[0]
        exams += int(stored_exam_passes or 0)
    except sqlite3.OperationalError:
        # Table creee lors de la premiere soumission.
        pass

    return {
        "level": stats, "total_nodes": total_nodes, "validated_nodes": validated_nodes,
        "progress_percent": int((validated_nodes / total_nodes) * 100) if total_nodes else 0,
        "streak": {"days": days}, "labs_validated": labs, "exams_passed": exams, "badges": [],
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
# ROUTES DOCKER & LABS
# ---------------------------------------------------------

@app.post("/api/lab/start")
def start_lab(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    node_id = payload.get("node_id")
    
    # On vérifie si le nœud est accessible
    try:
        node = tree.playable(node_id)
    except DomainError as error:
        # On renvoie l'erreur "Verrouillé" proprement en HTTP 409 (Conflit)
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
    
    return {
        "lab_id": session.lab_id, 
        "container_id": session.container_id, 
        "setup_logs": session.setup_logs
    }

@app.post("/api/lab/exec")
def exec_lab(payload: dict = Body(...)) -> dict:
    result = exec_in_lab(payload.get("lab_id"), payload.get("command"))
    return {"success": True, "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.exit_code}

@app.post("/api/lab/validate")
def validate_lab_route(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    lab_id = payload.get("lab_id")
    if not lab_id:
        raise HTTPException(400, "lab_id manquant")
    
    try:
        validation = validate_lab(lab_id)
        attempt, validated = tree.record_docker_lab(validation.node_id, validation.commands, validation.result)
        return {
            "success": True, 
            "passed": validation.result.passed, 
            "score": validation.result.score, 
            "detail": validation.result.detail, 
            "validated": validated
        }
    except LabSessionError as error:
        raise HTTPException(404, str(error))
    except LabRunnerError as error:
        raise HTTPException(503, str(error))
    except DomainError as error:
        raise HTTPException(409, str(error))
    except Exception as error:
        raise HTTPException(500, f"Erreur inattendue : {str(error)}")


# ---------------------------------------------------------
# ALIAS POUR L'INTERFACE HTML
# ---------------------------------------------------------

@app.post("/api/exam/build")
def exam_build(payload: dict[str, Any] = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    """Construit un examen filtré par les nœuds envoyés par l'interface."""
    raw_node_ids = payload.get("node_ids")
    if not isinstance(raw_node_ids, list) or not raw_node_ids:
        raise HTTPException(status_code=422, detail="node_ids doit être une liste non vide.")
    if len(raw_node_ids) > 500 or any(not isinstance(value, str) or not value.strip() for value in raw_node_ids):
        raise HTTPException(status_code=422, detail="Liste node_ids invalide.")

    node_ids = list(dict.fromkeys(value.strip() for value in raw_node_ids))
    count = payload.get("count", EXAM_QUESTION_COUNT)
    time_limit = payload.get("time_limit", EXAM_DURATION_SECONDS)
    if type(count) is not int or not 1 <= count <= 100:
        raise HTTPException(status_code=422, detail="count doit être un entier entre 1 et 100.")
    if type(time_limit) is not int or not 60 <= time_limit <= 3600:
        raise HTTPException(status_code=422, detail="time_limit doit être compris entre 60 et 3600 secondes.")

    available_nodes = {node.id: node for node in tree.nodes()}
    unknown = [node_id for node_id in node_ids if node_id not in available_nodes]
    if unknown:
        raise HTTPException(status_code=404, detail={"message": "Cours inconnus.", "node_ids": unknown})

    pool = [
        (available_nodes[node_id], question)
        for node_id in node_ids
        for question in tree.questions(node_id, ProofKind.QUIZ)
    ]
    if not pool:
        raise HTTPException(status_code=422, detail="Aucune question de quiz dans ce périmètre.")

    selected = random.sample(pool, min(count, len(pool)))
    now = int(time.time())
    session_id = uuid.uuid4().hex
    module = str(payload.get("module") or "custom")
    levels = payload.get("levels", [])
    if not isinstance(levels, list) or any(not isinstance(level, str) for level in levels):
        raise HTTPException(status_code=422, detail="levels doit être une liste de chaînes.")

    # Stockage des couples nœud/question : aucun changement de schéma SQLite requis.
    question_refs = [{"node_id": node.id, "question_id": question.id} for node, question in selected]
    tree.conn.execute(
        "INSERT INTO exam_sessions (session_id, category, question_ids, started_at, expires_at) VALUES (?, ?, ?, ?, ?)",
        (session_id, module, json.dumps(question_refs, ensure_ascii=False), now, now + time_limit),
    )
    tree.conn.commit()
    return {
        "id": session_id,
        "category": module,
        "module": module,
        "levels": levels,
        "time_limit": time_limit,
        "duration_seconds": time_limit,
        "questions": [
            {"id": question.id, "type": question.question_type, "prompt": question.prompt, "choices": list(question.choices)}
            for _, question in selected
        ],
    }


@app.post("/api/exam/submit")
def exam_submit(payload: dict[str, Any] = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    """Corrige un examen côté serveur et rend la soumission idempotente."""
    session_id = payload.get("session_id")
    answers = payload.get("answers")
    if not isinstance(session_id, str) or not session_id.strip():
        raise HTTPException(status_code=422, detail="session_id manquant ou invalide.")
    if not isinstance(answers, list):
        raise HTTPException(status_code=422, detail="answers doit être une liste.")

    # Table additive indépendante; les sessions existantes restent compatibles.
    tree.conn.execute(
        "CREATE TABLE IF NOT EXISTS exam_submissions ("
        "session_id TEXT PRIMARY KEY, submitted_at INTEGER NOT NULL, result_json TEXT NOT NULL, passed INTEGER NOT NULL DEFAULT 0)"
    )
    previous = tree.conn.execute(
        "SELECT result_json FROM exam_submissions WHERE session_id = ?", (session_id,)
    ).fetchone()
    if previous:
        try:
            return json.loads(previous["result_json"])
        except (TypeError, ValueError, KeyError):
            raise HTTPException(status_code=500, detail="Résultat d'examen enregistré illisible.")

    session = tree.conn.execute(
        "SELECT session_id, category, question_ids, started_at, expires_at FROM exam_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Session d'examen introuvable. Relance l'examen.")
    if int(time.time()) > int(session["expires_at"]) + EXAM_SUBMIT_GRACE_SECONDS:
        raise HTTPException(status_code=409, detail="Session expirée. Relance l'examen.")

    try:
        stored_refs = json.loads(session["question_ids"] or "[]")
    except (TypeError, ValueError):
        raise HTTPException(status_code=500, detail="La liste des questions de cette session est invalide.")
    all_nodes = {node.id: node for node in tree.nodes()}
    selected: list[tuple[Node, Question]] = []

    if stored_refs and isinstance(stored_refs[0], dict):
        # Format utilisé par le correctif et par les sessions créées depuis /api/exam/build.
        cache: dict[str, dict[str, Question]] = {}
        for ref in stored_refs:
            node_id = ref.get("node_id")
            question_id = ref.get("question_id")
            if node_id not in all_nodes or not isinstance(question_id, str):
                raise HTTPException(status_code=409, detail="Une question de la session n'existe plus.")
            if node_id not in cache:
                cache[node_id] = {q.id: q for q in tree.questions(node_id, ProofKind.QUIZ)}
            question = cache[node_id].get(question_id)
            if question is None:
                raise HTTPException(status_code=409, detail="Une question de la session n'existe plus.")
            selected.append((all_nodes[node_id], question))
    else:
        # Compatibilité avec les sessions créées avant le patch, qui ne stockaient que q.id.
        legacy_nodes = [node for node in tree.nodes() if node.category == session["category"]]
        by_id: dict[str, list[tuple[Node, Question]]] = {}
        for node in legacy_nodes:
            for question in tree.questions(node.id, ProofKind.QUIZ):
                by_id.setdefault(question.id, []).append((node, question))
        for question_id in stored_refs:
            candidates = by_id.get(question_id, []) if isinstance(question_id, str) else []
            if len(candidates) != 1:
                raise HTTPException(
                    status_code=409,
                    detail="Cette ancienne session ne peut pas être associée sans ambiguïté à ses questions. Relance l'examen.",
                )
            selected.append(candidates[0])

    if not selected:
        raise HTTPException(status_code=409, detail="La session ne contient aucune question exploitable.")
    if len(answers) != len(selected):
        raise HTTPException(status_code=422, detail=f"Nombre de réponses incorrect : {len(answers)} reçues pour {len(selected)} questions.")

    details = []
    correct = 0
    for (_, question), answer in zip(selected, answers):
        if answer is None:
            matches = False
        elif question.question_type in {"input", "terminal"}:
            matches = _answer_matches(
                question.answer_regex or "", str(answer), terminal=question.question_type == "terminal"
            )
        else:
            matches = answer == question.answer
        correct += int(matches)
        details.append({
            "id": question.id,
            "correct": matches,
            "answer": question.answer,
            "explanation": question.explanation,
        })

    total = len(selected)
    score = round(100 * correct / total)
    result = {
        "success": True,
        "score": score,
        "passed": score >= EXAM_PASS_SCORE,
        "correct": correct,
        "total": total,
        "details": details,
        "submitted_at": int(time.time()),
    }
    tree.conn.execute(
        "INSERT OR IGNORE INTO exam_submissions (session_id, submitted_at, result_json, passed) VALUES (?, ?, ?, ?)",
        (session_id, result["submitted_at"], json.dumps(result, ensure_ascii=False), int(result["passed"])),
    )
    tree.conn.commit()
    # En cas de double soumission concurrente, renvoyer le résultat canonique enregistré.
    saved = tree.conn.execute(
        "SELECT result_json FROM exam_submissions WHERE session_id = ?", (session_id,)
    ).fetchone()
    return json.loads(saved["result_json"]) if saved else result


@app.post("/api/exam/start")
def exam_start_alias(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    category = payload.get("category")
    nodes = [node for node in tree.nodes() if node.category == category]
    pool = [(node, q) for node in nodes for q in tree.questions(node.id, ProofKind.QUIZ)]
    selected = random.sample(pool, min(EXAM_QUESTION_COUNT, len(pool)))
    
    now = int(time.time())
    session_id = uuid.uuid4().hex
    tree.conn.execute(
        "INSERT INTO exam_sessions (session_id, category, question_ids, started_at, expires_at) VALUES (?, ?, ?, ?, ?)",
        (session_id, category, json.dumps([{"node_id": node.id, "question_id": q.id} for node, q in selected], ensure_ascii=False), now, now + EXAM_DURATION_SECONDS)
    )
    tree.conn.commit()
    return {
        "id": session_id, "category": category, "duration_seconds": EXAM_DURATION_SECONDS,
        "questions": [{"id": q.id, "type": q.question_type, "prompt": q.prompt, "choices": list(q.choices)} for _, q in selected]
    }

@app.post("/api/tutor")
def tutor_alias(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    node_id = payload.get("node_id")
    question = payload.get("question")
    if not node_id: raise HTTPException(400, "node_id manquant")
    
    node = _get_node(tree, node_id)
    lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
    context = lessons.get(node.id, "")[:TUTOR_MAX_CONTEXT_CHARS]
    
    api_key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not api_key: return {"answer": "Tuteur IA non configuré (GROQ_API_KEY manquante dans le .env)."}
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=GROQ_DEFAULT_MODEL,
            messages=[{"role": "system", "content": f"Contexte: {context}"}, {"role": "user", "content": question}],
            temperature=0.25, max_tokens=900
        )
        return {"answer": completion.choices[0].message.content}
    except Exception as e:
        return {"answer": f"Erreur Tuteur : {str(e)}"}

@app.get("/api/topology")
def read_topology(tree: SkillTree = Depends(get_tree)) -> dict:
    """Renvoie la dernière topologie sauvegardée, au format attendu par Drawflow."""
    row = tree.conn.execute(
        "SELECT data FROM topologies ORDER BY updated_at DESC, rowid DESC LIMIT 1"
    ).fetchone()
    if not row:
        return {}
    try:
        data = json.loads(row["data"])
    except (TypeError, ValueError, KeyError):
        raise HTTPException(status_code=500, detail="La topologie sauvegardée est invalide.")
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="Le format de la topologie sauvegardée est invalide.")
    return data


@app.post("/api/topology")
def save_topology_alias(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tree.conn.execute("INSERT INTO topologies (name, data, updated_at) VALUES (?, ?, ?)", ("Mon lab", json.dumps(payload, ensure_ascii=False), updated_at))
    tree.conn.commit()
    return {"success": True}

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

STATIC_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)