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
from .loader import CONTENT_DIR, ContentError, find_lab_dir, load_content, load_lessons, sync_content_additions

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
EXAM_PASS_SCORE = 80
EXAM_MAX_QUESTION_COUNT = 500
EXAM_MIN_DURATION_SECONDS = 60
EXAM_MAX_DURATION_SECONDS = 8 * 60 * 60
EXAM_SUBMIT_GRACE_SECONDS = 15
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
        catalog_sync = sync_content_additions(conn)
        if any(catalog_sync.values()):
            print(f"Synchronisation additive du catalogue pédagogique : {catalog_sync}")
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
    try:
        lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
        content = lessons.get(node.id, "")
    except ContentError as e:
        # Si le nœud n'est pas encore en base de données, on lit le fichier .md directement
        print(f"Avertissement Loader : {e}")
        file_path = CONTENT_DIR / "lessons" / f"{node_id}.md"
        content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""

    return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")

@app.get("/api/node/{node_id}")
def read_node(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    node = _get_node(tree, node_id)
    status = tree.status(node.id)
    lab = tree.lab_spec(node.id)
    challenge = _challenge_row(tree, node.id)
    terminal = tree.conn.execute("SELECT prompt, explanation FROM terminal_specs WHERE node_id = ?", (node.id,)).fetchone()
    terminal_spec = tree.terminal_spec(node.id)
    
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
        "challenge": {"prompt": node.description, "time_limit": challenge["time_limit"]} if challenge else None,
    }

@app.get("/api/node/{node_id}/quiz")
def read_quiz(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    """Expose les questions d'un quiz sans publier les réponses attendues."""
    node = _get_node(tree, node_id)
    if not any(requirement.kind == ProofKind.QUIZ for requirement in node.requirements):
        raise HTTPException(404, "Aucun quiz n'est associé à ce cours.")

    questions = tree.questions(node_id, ProofKind.QUIZ)
    if not questions:
        raise HTTPException(404, "Quiz indisponible pour ce cours.")

    return {
        "node_id": node.id,
        "questions": [
            {
                "id": question.id,
                "prompt": question.prompt,
                "choices": list(question.choices),
                "type": question.question_type,
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


def _exam_bounded_integer(value, name: str, default: int, minimum: int, maximum: int) -> int:
    if value is None:
        value = default
    if isinstance(value, bool):
        raise HTTPException(422, f"Le paramètre {name} doit être un entier.")
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise HTTPException(422, f"Le paramètre {name} doit être un entier.") from error
    if number < minimum or number > maximum:
        raise HTTPException(422, f"Le paramètre {name} doit être compris entre {minimum} et {maximum}.")
    return number


def _exam_level(node_id: str, title: str = "") -> str:
    suffix = str(node_id or "").strip().lower().replace("_", "-").rsplit("-", 1)[-1]
    if suffix in {"debutant", "intermediaire", "expert"}:
        return suffix
    lowered_title = str(title or "").casefold().rstrip()
    if lowered_title.endswith("expert"):
        return "expert"
    if lowered_title.endswith(("intermédiaire", "intermediaire")):
        return "intermediaire"
    if lowered_title.endswith("débutant"):
        return "debutant"
    return ""


def _exam_is_placeholder(question: Question) -> bool:
    return re.search(
        r"question temporaire|réponse provisoire|option temporaire",
        str(question.prompt or ""),
        flags=re.IGNORECASE,
    ) is not None


def _exam_question_pool(tree: SkillTree, nodes: list[Node]) -> list[Question]:
    pool: list[Question] = []
    seen: set[int] = set()
    for node in nodes:
        dedicated = [
            question for question in tree.questions(node.id, ProofKind.EXAM)
            if not _exam_is_placeholder(question)
        ]
        questions = dedicated or [
            question for question in tree.questions(node.id, ProofKind.QUIZ)
            if not _exam_is_placeholder(question)
        ]
        for question in questions:
            if question.id in seen:
                continue
            seen.add(question.id)
            pool.append(question)
    return pool


def _exam_public_question(question: Question, nodes_by_id: dict[str, Node] | None = None) -> dict:
    node = (nodes_by_id or {}).get(question.node_id)
    return {
        "id": question.id,
        "node_id": question.node_id,
        "level": _exam_level(question.node_id, node.title if node else ""),
        "type": question.question_type,
        "prompt": question.prompt,
        "choices": list(question.choices),
    }


def _exam_load_questions(tree: SkillTree, raw_ids: list) -> list[Question]:
    if not isinstance(raw_ids, list) or not raw_ids or len(raw_ids) > EXAM_MAX_QUESTION_COUNT:
        raise HTTPException(409, "Cette session ne contient pas une liste valide de questions.")
    try:
        ids = [int(value) for value in raw_ids]
    except (TypeError, ValueError) as error:
        raise HTTPException(409, "La liste des questions de cette session est invalide.") from error
    if any(question_id <= 0 for question_id in ids) or len(set(ids)) != len(ids):
        raise HTTPException(409, "La liste des questions de cette session est invalide.")

    placeholders = ",".join("?" for _ in ids)
    rows = tree.conn.execute(
        f"SELECT * FROM questions WHERE id IN ({placeholders})",
        ids,
    ).fetchall()
    by_id: dict[int, Question] = {}
    for row in rows:
        try:
            choices = tuple(json.loads(row["choices"] or "[]"))
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise HTTPException(500, "Une question de l'examen possède des choix invalides.") from error
        question_type = str(row["question_type"] or "qcm")
        answer = row["answer_text"] if question_type in {"input", "terminal"} else row["answer"]
        by_id[int(row["id"])] = Question(
            id=int(row["id"]),
            node_id=str(row["node_id"]),
            scope=ProofKind(row["scope"]),
            prompt=str(row["prompt"]),
            choices=choices,
            answer=answer,
            explanation=str(row["explanation"] or ""),
            question_type=question_type,
            answer_regex=row["answer_regex"],
        )
    if any(question_id not in by_id for question_id in ids):
        raise HTTPException(409, "La banque de questions a changé depuis le début de cet examen.")
    return [by_id[question_id] for question_id in ids]


def _exam_sanitize_answer(question: Question, value) -> int | str | None:
    if question.question_type == "qcm":
        if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < len(question.choices):
            return value
        return None
    if isinstance(value, str):
        return value[:2000].strip()
    return None


def _exam_grade_question(question: Question, answer: int | str | None) -> dict:
    if question.question_type == "qcm":
        correct = isinstance(answer, int) and not isinstance(answer, bool) and answer == question.answer
    else:
        submitted = answer if isinstance(answer, str) else ""
        expected = str(question.answer or "")
        if not submitted:
            correct = False
        elif question.answer_regex:
            try:
                correct = re.fullmatch(
                    question.answer_regex, submitted, flags=re.IGNORECASE | re.MULTILINE
                ) is not None
            except re.error:
                correct = False
        else:
            correct = re.sub(r"\s+", " ", submitted).strip().casefold() == re.sub(
                r"\s+", " ", expected
            ).strip().casefold()
    return {
        "question_id": question.id,
        "node_id": question.node_id,
        "correct": bool(correct),
        "answer": question.answer,
        "explanation": question.explanation,
    }


def _exam_saved_result(row) -> dict:
    try:
        saved = json.loads(row["result_json"] or "")
        if isinstance(saved, dict) and saved:
            return saved
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    try:
        answers = json.loads(row["answers_json"] or "[]")
    except (TypeError, ValueError, json.JSONDecodeError):
        answers = []
    try:
        details = json.loads(row["details_json"] or "[]")
    except (TypeError, ValueError, json.JSONDecodeError):
        details = []
    score = int(row["score"] or 0)
    total = int(row["total"] or 0)
    passing_score = int(row["passing_score"] or EXAM_PASS_SCORE)
    return {
        "success": bool(row["submitted"]),
        "session_id": str(row["session_id"]),
        "score": score,
        "passed": bool(row["passed"]),
        "correct": int(row["correct"] or 0),
        "total": total,
        "duration": max(0, int(row["submitted_at"] or row["started_at"]) - int(row["started_at"])),
        "time_expired": bool(row["time_expired"]),
        "answers": answers,
        "details": details,
        "pass_score": passing_score,
        "passing_score": passing_score,
        "node_id": None,
        "exam_type": "category",
        "submitted": bool(row["submitted"]),
        "offline": False,
    }


@app.post("/api/exam/build")
def exam_build(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    all_nodes = tree.nodes()
    nodes_by_id = {node.id: node for node in all_nodes}
    raw_ids = payload.get("node_ids")
    if raw_ids is not None:
        if not isinstance(raw_ids, list) or not raw_ids:
            raise HTTPException(422, "La sélection de cours est vide ou invalide.")
        if len(raw_ids) > 1000:
            raise HTTPException(422, "La sélection dépasse 1 000 cours.")
        selected_ids: list[str] = []
        for value in raw_ids:
            if not isinstance(value, str) or not value.strip():
                raise HTTPException(422, "Un identifiant de cours est invalide.")
            node_id = value.strip()
            if node_id not in nodes_by_id:
                raise HTTPException(422, f"Cours inconnu dans la sélection : {node_id}.")
            if node_id not in selected_ids:
                selected_ids.append(node_id)
        nodes = [nodes_by_id[node_id] for node_id in selected_ids]
    else:
        category = str(payload.get("category") or "").strip()
        module = str(payload.get("module") or "").strip().lower()
        if category and category.lower() != "all":
            nodes = [node for node in all_nodes if node.category == category]
        elif module in {"", "all", "*"}:
            nodes = list(all_nodes)
        else:
            raise HTTPException(
                422,
                "La sélection de cours est requise pour un examen par module. Recharge le centre d'examens.",
            )

    raw_levels = payload.get("levels")
    if isinstance(raw_levels, list) and raw_levels and "all" not in [
        str(level).strip().lower() for level in raw_levels
    ]:
        levels = {str(level).strip().lower() for level in raw_levels}
        nodes = [node for node in nodes if _exam_level(node.id, node.title) in levels]
    if not nodes:
        raise HTTPException(422, "Aucun cours ne correspond au périmètre demandé.")

    count = _exam_bounded_integer(
        payload.get("count"), "count", EXAM_QUESTION_COUNT, 1, EXAM_MAX_QUESTION_COUNT
    )
    if payload.get("time_limit") is not None:
        time_limit = _exam_bounded_integer(
            payload.get("time_limit"), "time_limit", EXAM_DURATION_SECONDS,
            EXAM_MIN_DURATION_SECONDS, EXAM_MAX_DURATION_SECONDS,
        )
    else:
        minutes = _exam_bounded_integer(
            payload.get("minutes"), "minutes", EXAM_DURATION_SECONDS // 60,
            1, EXAM_MAX_DURATION_SECONDS // 60,
        )
        time_limit = minutes * 60

    pool = _exam_question_pool(tree, nodes)
    if not pool:
        raise HTTPException(
            422,
            "Aucune question exploitable dans ce périmètre. Vérifie les banques de quiz et d'examen de ces cours.",
        )
    selected = random.sample(pool, min(count, len(pool)))
    now = int(time.time())
    session_id = uuid.uuid4().hex
    category = str(
        payload.get("category") or payload.get("module") or
        ("Tous modules" if len(nodes) > 1 else nodes[0].category)
    ).strip() or "Examen personnalisé"
    tree.conn.execute(
        "INSERT INTO exam_sessions "
        "(session_id, category, question_ids, started_at, expires_at, submitted, "
        "score, passed, correct, total, submitted_at, time_expired, answers_json, "
        "details_json, result_json, passing_score) "
        "VALUES (?, ?, ?, ?, ?, 0, NULL, NULL, NULL, ?, NULL, 0, '[]', '[]', '', ?)",
        (
            session_id, category, json.dumps([question.id for question in selected]),
            now, now + time_limit, len(selected), EXAM_PASS_SCORE,
        ),
    )
    tree.conn.commit()
    return {
        "id": session_id,
        "category": category,
        "exam_type": "category",
        "node_id": None,
        "time_limit": time_limit,
        "duration_seconds": time_limit,
        "pass_score": EXAM_PASS_SCORE,
        "passing_score": EXAM_PASS_SCORE,
        "requested_count": count,
        "question_count": len(selected),
        "questions": [_exam_public_question(question, nodes_by_id) for question in selected],
    }


@app.post("/api/exam/submit")
def exam_submit(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id or len(session_id) > 64:
        raise HTTPException(422, "Identifiant de session manquant ou invalide.")
    row = tree.conn.execute(
        "SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Session d'examen introuvable.")
    if row["submitted"]:
        return _exam_saved_result(row)

    try:
        raw_ids = json.loads(row["question_ids"] or "[]")
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(409, "La liste des questions de cette session est invalide.") from error
    questions = _exam_load_questions(tree, raw_ids)
    raw_answers = payload.get("answers", [])
    if not isinstance(raw_answers, list):
        raise HTTPException(422, "Les réponses doivent être envoyées sous forme de liste.")
    if len(raw_answers) > len(questions):
        raise HTTPException(422, "Le nombre de réponses dépasse le nombre de questions.")
    answers = [
        _exam_sanitize_answer(question, raw_answers[index] if index < len(raw_answers) else None)
        for index, question in enumerate(questions)
    ]

    now = int(time.time())
    started_at = int(row["started_at"] or now)
    expires_at = int(row["expires_at"] or started_at)
    too_late = now > expires_at + EXAM_SUBMIT_GRACE_SECONDS
    timed_out = now >= expires_at or too_late
    if too_late:
        answers = [None] * len(questions)
    details = [
        _exam_grade_question(question, answers[index])
        for index, question in enumerate(questions)
    ]
    correct = sum(1 for item in details if item["correct"])
    total = len(questions)
    score = round(100 * correct / total) if total else 0
    passed = score >= EXAM_PASS_SCORE
    submitted_at = min(now, expires_at) if timed_out else now
    duration = min(max(0, submitted_at - started_at), max(0, expires_at - started_at))
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
        "pass_score": EXAM_PASS_SCORE,
        "passing_score": EXAM_PASS_SCORE,
        "node_id": None,
        "exam_type": "category",
        "submitted": True,
        "offline": False,
        "submitted_at": submitted_at,
    }
    update = tree.conn.execute(
        "UPDATE exam_sessions SET submitted = 1, score = ?, passed = ?, correct = ?, "
        "total = ?, submitted_at = ?, time_expired = ?, answers_json = ?, details_json = ?, "
        "passing_score = ?, result_json = ? WHERE session_id = ? AND submitted = 0",
        (
            score, int(passed), correct, total, submitted_at, int(timed_out),
            json.dumps(answers, ensure_ascii=False),
            json.dumps(details, ensure_ascii=False),
            EXAM_PASS_SCORE,
            json.dumps(result, ensure_ascii=False),
            session_id,
        ),
    )
    if getattr(update, "rowcount", 1) == 0:
        tree.conn.rollback()
        latest = tree.conn.execute(
            "SELECT * FROM exam_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if latest is not None and latest["submitted"]:
            return _exam_saved_result(latest)
        raise HTTPException(409, "La session d'examen ne peut plus être corrigée.")
    tree.conn.commit()
    return result


@app.post("/api/exam/start")
def exam_start_alias(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    category = payload.get("category")
    if not isinstance(category, str) or not category.strip():
        raise HTTPException(422, "Catégorie d'examen manquante ou invalide.")
    category = category.strip()
    nodes = [node for node in tree.nodes() if node.category == category]
    if not nodes:
        raise HTTPException(404, "Catégorie d'examen introuvable.")
    pool = [
        (node, question)
        for node in nodes
        for question in (tree.questions(node.id, ProofKind.EXAM) or tree.questions(node.id, ProofKind.QUIZ))
        if not _exam_is_placeholder(question)
    ]
    if not pool:
        raise HTTPException(422, "Aucune question exploitable dans cette catégorie.")
    requested_count = _exam_bounded_integer(
        payload.get("count"), "count", EXAM_QUESTION_COUNT, 1, EXAM_MAX_QUESTION_COUNT
    )
    if payload.get("time_limit") is not None:
        time_limit = _exam_bounded_integer(
            payload.get("time_limit"), "time_limit", EXAM_DURATION_SECONDS,
            EXAM_MIN_DURATION_SECONDS, EXAM_MAX_DURATION_SECONDS,
        )
    else:
        time_limit = EXAM_DURATION_SECONDS
    selected = random.sample(pool, min(requested_count, len(pool)))
    now = int(time.time())
    session_id = uuid.uuid4().hex
    tree.conn.execute(
        "INSERT INTO exam_sessions "
        "(session_id, category, question_ids, started_at, expires_at, total, passing_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            session_id, category, json.dumps([question.id for _, question in selected]),
            now, now + time_limit, len(selected), EXAM_PASS_SCORE,
        ),
    )
    tree.conn.commit()
    nodes_by_id = {node.id: node for node in nodes}
    return {
        "id": session_id,
        "category": category,
        "duration_seconds": time_limit,
        "time_limit": time_limit,
        "pass_score": EXAM_PASS_SCORE,
        "passing_score": EXAM_PASS_SCORE,
        "question_count": len(selected),
        "questions": [_exam_public_question(question, nodes_by_id) for _, question in selected],
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