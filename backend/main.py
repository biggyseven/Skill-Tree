"""Skill Tree — API FastAPI pour le frontend Alpine.js."""
import io
import os
import random
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from store import Store
from labs import lab_manager
import tutor

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT.parent  # dossier où se trouve le HTML

store = Store()
app = FastAPI(title="Skill Tree API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------- Modèles Pydantic -------------------------
class QuizSubmit(BaseModel):
    answers: list

class AnswerSubmit(BaseModel):
    answer: str

class LabStart(BaseModel):
    node_id: str

class LabExec(BaseModel):
    lab_id: str
    command: str

class LabValidate(BaseModel):
    lab_id: str

class ExamStart(BaseModel):
    category: str

class ExamSubmit(BaseModel):
    exam_id: str
    answers: list

class TutorAsk(BaseModel):
    node_id: str | None = None
    question: str

# ------------------------- Tree & profil -------------------------
@app.get("/api/tree")
def get_tree():
    nodes = [store.public_node(n) for n in store.nodes]
    return {
        "nodes": nodes,
        "total": len(nodes),
        "validated": len(store.state["validated_nodes"]),
    }

@app.get("/api/user-stats")
def user_stats():
    s = store.state
    return {
        "total_xp": s["total_xp"],
        "current_level": s["current_level"],
        "level_name": s["level_name"],
        "coins": s["coins"],
        "progress_percent": (
            len(s["validated_nodes"]) * 100 // max(len(store.nodes), 1)
        ),
    }

@app.get("/api/profile")
def profile():
    return {
        "name": store.state["user_name"],
        "level": store.state["current_level"],
        "level_name": store.state["level_name"],
        "xp": store.state["total_xp"],
        "coins": store.state["coins"],
    }

@app.get("/api/streak")
def streak():
    return {"days": store.state["streak_days"]}

@app.get("/api/daily-plan")
def daily_plan():
    actions = []
    for n in store.nodes:
        status = store.compute_status(n)
        if status == "in_progress":
            actions.append({
                "node_id": n["id"],
                "action": "lab" if n.get("lab") else "start",
                "label": f"Continuer {n['title']}",
                "reason": "Reprendre là où tu t'es arrêté",
            })
        elif status == "available":
            actions.append({
                "node_id": n["id"],
                "action": "start",
                "label": f"Commencer {n['title']}",
                "reason": "Nouveau nœud disponible",
            })
    if not actions:
        for nid in store.state["validated_nodes"][:3]:
            n = store.nodes_by_id[nid]
            actions.append({
                "node_id": nid,
                "action": "review",
                "label": f"Réviser {n['title']}",
                "reason": "Ancrage mémoriel",
            })
    return {"actions": actions[:3]}

# ------------------------- Stats / radar -------------------------
@app.get("/api/stats")
def stats():
    attempts = store.state["attempts"]
    total = len(attempts)
    successful = sum(1 for a in attempts if a.get("passed"))
    success_rate = round(successful * 100 / total) if total else 0

    by_cat: dict[str, list[bool]] = {}
    for a in attempts:
        n = store.nodes_by_id.get(a["node_id"])
        if not n:
            continue
        by_cat.setdefault(n["category"], []).append(a.get("passed", False))

    categories = [
        {
            "name": cat,
            "success_rate": round(sum(1 for x in vals if x) * 100 / len(vals)) if vals else 0,
        }
        for cat, vals in by_cat.items()
    ]
    weak_points = sum(1 for c in categories if c["success_rate"] < 60)

    return {
        "totals": {
            "attempts": total,
            "success_rate": success_rate,
            "weak_points": weak_points,
            "validated": len(store.state["validated_nodes"]),
            "nodes": len(store.nodes),
        },
        "categories": categories,
    }

# ------------------------- Flashcards -------------------------
@app.get("/api/flashcards")
def flashcards():
    return {"cards": store.flashcards}

# ------------------------- Diagnostic -------------------------
@app.get("/api/diagnostics/{diag_id}")
def diagnostic(diag_id: str):
    if diag_id not in store.diagnostics:
        raise HTTPException(404, "Diagnostic inconnu")
    return store.diagnostics[diag_id]

# ------------------------- Nœuds -------------------------
@app.get("/api/node/{node_id}")
def node_detail(node_id: str):
    node = store.nodes_by_id.get(node_id)
    if not node:
        raise HTTPException(404, "Nœud introuvable")
    return store.public_node(node, include_detail=True)

@app.get("/api/node/{node_id}/lesson", response_class=PlainTextResponse)
def node_lesson(node_id: str):
    if node_id not in store.nodes_by_id:
        raise HTTPException(404, "Nœud introuvable")
    md = store.get_lesson(node_id)
    if md is None:
        raise HTTPException(404, "Cours en cours de rédaction")
    return md

# ------------------------- Quiz -------------------------
def _public_question(q):
    return {
        "id": q["id"],
        "type": q.get("type", "qcm"),
        "prompt": q["prompt"],
        "choices": q.get("choices", []),
    }

@app.get("/api/node/{node_id}/quiz")
def node_quiz(node_id: str):
    node = store.nodes_by_id.get(node_id)
    if not node or not node.get("quiz"):
        raise HTTPException(404, "Pas de quiz pour ce nœud")
    return {"questions": [_public_question(q) for q in node["quiz"]]}

@app.post("/api/node/{node_id}/quiz")
def node_quiz_submit(node_id: str, body: QuizSubmit):
    node = store.nodes_by_id.get(node_id)
    if not node or not node.get("quiz"):
        raise HTTPException(404, "Pas de quiz pour ce nœud")
    questions = node["quiz"]
    if len(body.answers) != len(questions):
        raise HTTPException(400, "Nombre de réponses incorrect")

    correct_count = 0
    for q, ans in zip(questions, body.answers):
        if q.get("type", "qcm") == "qcm":
            if ans == q.get("correct"):
                correct_count += 1
        else:
            if str(ans).strip() == str(q.get("correct", "")).strip():
                correct_count += 1

    score = round(correct_count * 100 / len(questions))
    store.register_attempt(node_id, "quiz", score)
    return {"score": score, "passed": score >= 70}

# ------------------------- Exercice terminal / input -------------------------
@app.post("/api/node/{node_id}/submit-answer")
def node_submit_answer(node_id: str, body: AnswerSubmit):
    node = store.nodes_by_id.get(node_id)
    if not node:
        raise HTTPException(404, "Nœud introuvable")

    terminal = node.get("terminal")
    if not terminal:
        raise HTTPException(400, "Ce nœud n'a pas d'exercice libre")

    expected = terminal.get("expected", "").strip()
    got = body.answer.strip()
    correct = got.lower() == expected.lower()
    score = 100 if correct else 0
    store.register_attempt(node_id, "terminal", score)
    return {
        "correct": correct,
        "explanation": terminal.get("explanation", f"Réponse attendue : {expected}"),
    }

# ------------------------- Labs -------------------------
@app.post("/api/lab/start")
def lab_start(body: LabStart):
    node = store.nodes_by_id.get(body.node_id)
    if not node or not node.get("lab"):
        raise HTTPException(404, "Pas de lab pour ce nœud")
    image = node["lab"].get("image", "alpine:latest")
    try:
        return lab_manager.start(body.node_id, image=image)
    except RuntimeError as e:
        raise HTTPException(500, str(e))

@app.post("/api/lab/exec")
def lab_exec(body: LabExec):
    return lab_manager.exec(body.lab_id, body.command)

@app.post("/api/lab/validate")
def lab_validate(body: LabValidate):
    # Retrouve le nœud pour l'éventuelle commande attendue
    session = lab_manager.sessions.get(body.lab_id)
    expected = None
    if session:
        node = store.nodes_by_id.get(session["node_id"])
        if node and node.get("lab"):
            expected = node["lab"].get("expected_cmd")
    result = lab_manager.validate(body.lab_id, expected_cmd=expected)
    if result["passed"] and session:
        store.register_attempt(session["node_id"], "lab", 100)
        lab_manager.stop(body.lab_id)
    return result

# ------------------------- Examen -------------------------
EXAMS: dict[str, dict] = {}

@app.post("/api/exam/start")
def exam_start(body: ExamStart):
    pool = []
    for n in store.nodes:
        if n["category"] == body.category and n.get("quiz"):
            for q in n["quiz"]:
                pool.append(_public_question(q))
    if not pool:
        raise HTTPException(404, f"Aucune question pour la catégorie {body.category}")
    random.shuffle(pool)
    exam_id = str(uuid.uuid4())
    questions = pool[:5]
    EXAMS[exam_id] = {
        "category": body.category,
        "questions": questions,
        "started_at": datetime.utcnow().isoformat(),
    }
    return {
        "id": exam_id,
        "category": body.category,
        "questions": questions,
    }

@app.post("/api/exam/submit")
def exam_submit(body: ExamSubmit):
    exam = EXAMS.pop(body.exam_id, None)
    if not exam:
        raise HTTPException(404, "Examen introuvable ou expiré")
    questions = exam["questions"]
    # Réponses "correctes" : on régénère à partir des nœuds car on a stocké les questions publiques
    all_q = {}
    for n in store.nodes:
        for q in n.get("quiz", []):
            all_q[q["id"]] = q
    correct = 0
    for q, ans in zip(questions, body.answers):
        src = all_q.get(q["id"])
        if not src:
            continue
        if src.get("type", "qcm") == "qcm":
            if ans == src.get("correct"):
                correct += 1
        else:
            if str(ans).strip() == str(src.get("correct", "")).strip():
                correct += 1
    total = len(questions)
    score = round(correct * 100 / total) if total else 0
    return {
        "score": score,
        "correct": correct,
        "total": total,
        "passed": score >= 70,
    }

# ------------------------- Tuteur IA -------------------------
@app.post("/api/tutor")
def tutor_endpoint(body: TutorAsk):
    return {"answer": tutor.ask(body.node_id, body.question)}

# ------------------------- Topologie -------------------------
@app.post("/api/topology")
async def save_topology(request: Request):
    data = await request.json()
    store.update_state(topology=data)
    return {"ok": True}

# ------------------------- Certificat PDF -------------------------
@app.get("/api/certificate")
def certificate():
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
    except ImportError:
        raise HTTPException(500, "reportlab non installé")

    name = store.state["user_name"]
    level = store.state["level_name"]
    date_str = datetime.utcnow().strftime("%d/%m/%Y")

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4))
    w, h = landscape(A4)

    # Cadre
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(4)
    c.rect(30, 30, w - 60, h - 60)

    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(w / 2, h - 130, "Certificat")
    c.setFont("Helvetica", 16)
    c.drawCentredString(w / 2, h - 165, "Admin Réseau Senior")

    c.setFont("Helvetica", 14)
    c.drawCentredString(w / 2, h - 240, "Décerné à")

    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(w / 2, h - 290, name)

    c.setFont("Helvetica", 14)
    c.drawCentredString(w / 2, h - 340, f"Niveau {level} · XP {store.state['total_xp']}")
    c.drawCentredString(w / 2, h - 370, f"Le {date_str}")

    c.showPage()
    c.save()
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="certificat-{name}.pdf"'},
    )

# ------------------------- Frontend statique (optionnel) -------------------------
if (FRONTEND_DIR / "index.html").exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

@app.get("/")
def root():
    return {
        "service": "Skill Tree API",
        "docs": "/docs",
        "frontend": "/app" if (FRONTEND_DIR / "index.html").exists() else "non monté",
    }