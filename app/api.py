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
from collections import Counter
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse, StreamingResponse, FileResponse
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
from .lab_routes import router as lab_v2_router

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
EXAM_PASS_SCORE = 85
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
        (session_id, category, json.dumps([q.id for _, q in selected]), now, now + EXAM_DURATION_SECONDS)
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


# ==========================================
# M9 : LOGIQUE DE VERIFICATION DES LABS (V2)
# ==========================================

def get_nested_value(data, path):
    """Récupère une valeur profonde dans un dict via un chemin (ex: 'config.ospf.areas')"""
    keys = path.replace('[', '.').replace(']', '').split('.')
    for key in keys:
        if not key: continue
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and key.isdigit() and int(key) < len(data):
            data = data[int(key)]
        else:
            return None
    return data

# ==========================================
# M9 : LOGIQUE DE VERIFICATION DES LABS (V2)
# ==========================================

LABS_V2_DIR = PROJECT_ROOT / "labs_v2"

def get_nested_value(data, path):
    keys = path.replace('[', '.').replace(']', '').split('.')
    for key in keys:
        if not key: continue
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and key.isdigit() and int(key) < len(data):
            data = data[int(key)]
        else:
            return None
    return data

@app.get("/api/lab/v2/{lab_id}")
async def get_lab_v2(lab_id: str):
    lab_path = LABS_V2_DIR / f"{lab_id}.json"
    if not lab_path.exists():
        raise HTTPException(status_code=404, detail=f"Lab introuvable sur le serveur : {lab_path}")
        
    with open(lab_path, "r", encoding="utf-8") as f:
        lab_data = json.load(f)
        
    return {
        "id": lab_id,
        "schema_version": 2,
        "definition": lab_data,
        "initial_topology": lab_data.get("initial_topology", {
            "schema_version": 2, "nodes": [], "links": []
        })
    }

@app.post("/api/lab/v2/{lab_id}/check")
async def check_lab_v2(lab_id: str, payload: dict):
    lab_path = LABS_V2_DIR / f"{lab_id}.json"
    if not lab_path.exists():
        return {"passed": False, "score": 0, "results": [{"rule_id": "error", "passed": False, "message": f"Fichier {lab_id}.json introuvable."}]}
    
    with open(lab_path, "r", encoding="utf-8") as f:
        lab_def = json.load(f)

    rules = lab_def.get("check", {}).get("rules", [])
    if not rules:
        return {"passed": True, "score": 1.0, "results": [{"rule_id": "no_rules", "passed": True, "message": "Aucune règle définie."}]}

    topo = payload.get("topology", {})
    nodes = {n["id"]: n for n in topo.get("nodes", [])}
    results = []
    passed_count = 0

    for rule in rules:
        dev_id = rule.get("device")
        path = rule.get("path")
        operator = rule.get("operator")
        expected = rule.get("expected")
        
        device = nodes.get(dev_id)
        if not device:
            results.append({"rule_id": rule["id"], "passed": False, "message": f"Équipement {dev_id} manquant."})
            continue

        actual = get_nested_value(device, path)
        passed = False
        if operator == "equals":
            passed = (str(actual) == str(expected))
        elif operator == "contains_network":
            if actual and isinstance(actual, list):
                passed = any(str(expected["network"]) in str(a.get("network", "")) for a in actual)
        
        if passed: passed_count += 1
        results.append({
            "rule_id": rule["id"],
            "passed": passed,
            "message": rule.get("description", "Règle") + (" (OK)" if passed else " (Échec)")
        })

    score = passed_count / len(rules) if rules else 1.0
    return {"passed": score >= 0.7, "score": score, "results": results}

# ---------------------------------------------------------
# FICHIERS STATIQUES & LANCEMENT (TOUJOURS À LA FIN)
# ---------------------------------------------------------

@app.get("/lab.html")
async def lab_workspace_page():
    return FileResponse("lab.html")

STATIC_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)