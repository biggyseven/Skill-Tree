"""API HTTP du skill tree (FastAPI) + service de l'interface statique."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import time
import uuid
from collections import Counter
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from .db import DEFAULT_DB, connect, ensure_ready
from .domain import Node, ProofKind, Requirement, Status
from .engine import DomainError, SkillTree, requirement_met
from .loader import CONTENT_DIR, load_lessons

DB_PATH = Path(os.environ.get("SKILLTREE_DB", DEFAULT_DB))
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Prépare la base (schéma + contenu) au démarrage du serveur."""
    conn = connect(DB_PATH)
    try:
        ensure_ready(conn)
    finally:
        conn.close()
    yield


app = FastAPI(
    title="Skilltree API",
    description="Arbre de compétences réseau : lecture de l'état et réinitialisation.",
    version="0.1.0",
    lifespan=lifespan,
)


def get_tree() -> Iterator[SkillTree]:
    """Une connexion SQLite par requête (fermée quoi qu'il arrive).

    check_same_thread=False : FastAPI exécute les dépendances et les endpoints
    synchrones dans le pool de threads, pas forcément sur le même thread.
    """
    conn = connect(DB_PATH, check_same_thread=False)
    try:
        yield SkillTree(conn)
    finally:
        conn.close()


def _requirement_label(requirement: Requirement) -> str:
    return f"{requirement.kind.value}>{requirement.min_score}"


def _requirements_label(node: Node) -> str:
    return " + ".join(_requirement_label(requirement) for requirement in node.requirements)


def _get_node(tree: SkillTree, node_id: str) -> Node:
    try:
        return tree.node(node_id)
    except DomainError as error:
        raise HTTPException(status_code=404, detail=str(error))


def _playable(tree: SkillTree, node_id: str) -> Node:
    try:
        return tree.playable(node_id)
    except DomainError as error:
        raise HTTPException(status_code=409, detail=str(error))


def _answer_matches(pattern: str, answer: str, *, terminal: bool = False) -> bool:
    candidate = " ".join(answer.split()) if terminal else answer
    return re.fullmatch(pattern, candidate, re.IGNORECASE) is not None


@app.get("/api/node/{node_id}/lesson", response_class=PlainTextResponse)
def read_lesson(node_id: str, tree: SkillTree = Depends(get_tree)) -> PlainTextResponse:
    """Retourne le Markdown associé au nœud, ou une chaîne vide sans leçon."""
    node = _get_node(tree, node_id)
    lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
    return PlainTextResponse(
        lessons.get(node.id, ""),
        media_type="text/markdown; charset=utf-8",
    )


def _attempt_payload(attempt) -> dict:
    return {
        "id": attempt.id,
        "kind": attempt.kind.value,
        "score": attempt.score,
        "passed": attempt.passed,
        "detail": attempt.detail,
        "evidence": attempt.evidence,
        "created_at": attempt.created_at,
    }


def _challenge_row(tree: SkillTree, node_id: str):
    return tree.conn.execute(
        "SELECT expected_topology, time_limit FROM challenges WHERE node_id = ?",
        (node_id,),
    ).fetchone()


def _topology_signature(topology: dict[str, Any]) -> tuple[Counter, Counter]:
    drawflow = topology.get("drawflow")
    if not isinstance(drawflow, dict):
        raise ValueError("Le schéma Drawflow est invalide.")

    nodes: Counter = Counter()
    module_nodes: dict[str, dict[str, str]] = {}
    for module_name, module in drawflow.items():
        if not isinstance(module, dict) or not isinstance(module.get("data"), dict):
            raise ValueError("Un module Drawflow ne contient pas de liste de nœuds valide.")
        module_nodes[module_name] = {}
        for node_id, node in module["data"].items():
            if not isinstance(node, dict):
                raise ValueError("Un nœud Drawflow est invalide.")
            data = node.get("data")
            data = data if isinstance(data, dict) else {}
            device_type = data.get("type") or node.get("name")
            if not isinstance(device_type, str):
                raise ValueError("Un nœud Drawflow n'a pas de type d'équipement.")
            device_type = device_type.lower()
            module_nodes[module_name][str(node_id)] = device_type
            nodes[device_type] += 1

    connections: Counter = Counter()
    for module_name, module in drawflow.items():
        for node_id, node in module["data"].items():
            source_type = module_nodes[module_name][str(node_id)]
            outputs = node.get("outputs", {})
            if not isinstance(outputs, dict):
                raise ValueError("Les sorties d'un nœud Drawflow sont invalides.")
            for output in outputs.values():
                if not isinstance(output, dict):
                    raise ValueError("Une sortie Drawflow est invalide.")
                linked_nodes = output.get("connections", [])
                if not isinstance(linked_nodes, list):
                    raise ValueError("Les connexions Drawflow sont invalides.")
                for link in linked_nodes:
                    if not isinstance(link, dict) or "node" not in link:
                        raise ValueError("Une connexion Drawflow est invalide.")
                    target_type = module_nodes[module_name].get(str(link["node"]))
                    if target_type is None:
                        raise ValueError("Une connexion cible un nœud inexistant.")
                    connections[tuple(sorted((source_type, target_type)))] += 1

    return nodes, connections


def _compare_topology(topology: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, str]:
    try:
        actual_nodes, actual_connections = _topology_signature(topology)
    except ValueError as error:
        return False, str(error)

    expected_nodes = Counter(expected["nodes"])
    expected_connections = Counter(
        tuple(sorted((connection["from"], connection["to"])))
        for connection in expected["connections"]
    )
    if actual_nodes != expected_nodes:
        return False, "Le nombre de nœuds par type ne correspond pas à la consigne."
    if actual_connections != expected_connections:
        return False, "Les connexions entre équipements ne correspondent pas à la consigne."
    return True, "Topologie correcte."


@app.get("/api/tree")
def read_tree(tree: SkillTree = Depends(get_tree)) -> dict:
    """Tous les nœuds avec leur statut et leurs exigences."""
    nodes = tree.nodes()
    statuses = tree.statuses()
    validated = sum(1 for status in statuses.values() if status is Status.VALIDATED)
    architecture_nodes = {
        row["node_id"] for row in tree.conn.execute("SELECT node_id FROM challenges")
    }

    return {
        "total": len(nodes),
        "validated": validated,
        "nodes": [
            {
                "id": node.id,
                "type": "architecture" if node.id in architecture_nodes else "skill",
                "title": node.title,
                "category": node.category,
                "order": node.sort_order,
                "status": statuses[node.id].value,
                "prereqs": list(node.prereqs),
                "requirements": _requirements_label(node),
                "requirements_detail": [
                    {"kind": requirement.kind.value, "min_score": requirement.min_score}
                    for requirement in node.requirements
                ],
            }
            for node in nodes
        ],
    }


@app.get("/api/node/{node_id}")
def read_node(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    """Détail d'un nœud : description, prérequis, exigences, historique."""
    node = _get_node(tree, node_id)
    status = tree.status(node.id)

    lab = tree.lab_spec(node.id)
    challenge = _challenge_row(tree, node.id)
    terminal = tree.conn.execute(
        "SELECT prompt, explanation FROM terminal_specs WHERE node_id = ?", (node.id,)
    ).fetchone()
    return {
        "id": node.id,
        "type": (
            "architecture"
            if challenge is not None
            else "terminal"
            if terminal is not None
            else "skill"
        ),
        "title": node.title,
        "category": node.category,
        "order": node.sort_order,
        "description": node.description,
        "status": status.value,
        "prereqs": [
            {"id": prereq, "title": tree.node(prereq).title, "status": tree.status(prereq).value}
            for prereq in node.prereqs
        ],
        "requirements": [
            {
                "kind": requirement.kind.value,
                "min_score": requirement.min_score,
                "met": requirement_met(requirement, node),
            }
            for requirement in node.requirements
        ],
        "lab": (
            {"kind": lab.kind, "prompt": lab.prompt, "hint": lab.hint} if lab is not None else None
        ),
        "challenge": (
            {
                "prompt": node.description,
                "time_limit": challenge["time_limit"],
            }
            if challenge is not None
            else None
        ),
        "terminal": (
            {
                "prompt": terminal["prompt"],
                "explanation": terminal["explanation"],
            }
            if terminal is not None
            else None
        ),
        "attempts": [_attempt_payload(attempt) for attempt in node.attempts],
    }


@app.get("/api/node/{node_id}/quiz")
def read_quiz(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    """Retourne les questions sans divulguer les réponses attendues."""
    node = _get_node(tree, node_id)
    if node.requirement(ProofKind.QUIZ) is None:
        raise HTTPException(status_code=404, detail="Ce nœud n'a pas d'exercice.")

    questions = tree.questions(node_id, ProofKind.QUIZ)
    if not questions:
        raise HTTPException(status_code=404, detail="Aucune question pour cet exercice.")
    return {
        "node_id": node_id,
        "scope": "quiz",
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
def submit_quiz(
    node_id: str,
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Corrige les réponses de l'exercice et enregistre la tentative."""
    node = _playable(tree, node_id)
    requirement = node.requirement(ProofKind.QUIZ)
    if requirement is None:
        raise HTTPException(status_code=404, detail="Ce nœud n'a pas d'exercice.")

    questions = tree.questions(node_id, ProofKind.QUIZ)
    answers = payload.get("answers")
    if not questions:
        raise HTTPException(status_code=404, detail="Aucune question pour cet exercice.")
    if not isinstance(answers, list) or len(answers) != len(questions):
        raise HTTPException(
            status_code=422,
            detail=f"L'exercice attend exactement {len(questions)} réponses.",
        )

    results = []
    correct = 0
    for index, (question, answer) in enumerate(zip(questions, answers), 1):
        if question.question_type in {"input", "terminal"}:
            if not isinstance(answer, str):
                raise HTTPException(
                    status_code=422,
                    detail=f"La réponse à la question {index} doit être du texte.",
                )
            matches = _answer_matches(
                question.answer_regex or "",
                answer,
                terminal=question.question_type == "terminal",
            )
        else:
            if not isinstance(answer, int) or isinstance(answer, bool):
                raise HTTPException(
                    status_code=422,
                    detail=f"La réponse à la question {index} doit être un index de choix.",
                )
            matches = answer == question.answer

        correct += int(matches)
        results.append(
            {
                "id": question.id,
                "correct": matches,
                "explanation": question.explanation,
            }
        )

    score = round(100 * correct / len(questions))
    passed = score >= requirement.min_score
    attempt, validated = tree.record(
        node_id,
        ProofKind.QUIZ,
        score,
        passed,
        detail=f"{correct}/{len(questions)} bonnes réponses",
    )
    return {
        "success": True,
        "score": score,
        "passed": passed,
        "threshold": requirement.min_score,
        "correct": correct,
        "total": len(questions),
        "validated": validated,
        "status": tree.status(node_id).value,
        "attempt": _attempt_payload(attempt),
        "results": results,
    }


@app.post("/api/node/{node_id}/submit-answer")
def submit_answer(
    node_id: str,
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Corrige une réponse saisie et enregistre la preuve de l'exercice."""
    node = _playable(tree, node_id)
    answer = payload.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise HTTPException(status_code=422, detail="Le champ answer doit contenir une réponse.")
    if len(answer) > 5000:
        raise HTTPException(status_code=422, detail="La réponse dépasse 5000 caractères.")

    question_id = payload.get("question_id")
    if question_id is not None:
        if not isinstance(question_id, int) or isinstance(question_id, bool):
            raise HTTPException(status_code=422, detail="Le champ question_id doit être un entier.")
        requirement = node.requirement(ProofKind.QUIZ)
        question = next(
            (
                item
                for item in tree.questions(node_id, ProofKind.QUIZ)
                if item.id == question_id
            ),
            None,
        )
        if requirement is None or question is None:
            raise HTTPException(status_code=404, detail="Question d'exercice introuvable.")
        if question.question_type not in {"input", "terminal"}:
            raise HTTPException(
                status_code=422,
                detail="Cette question attend une sélection de réponse, pas du texte.",
            )
        pattern = question.answer_regex or ""
        explanation = question.explanation
        kind = ProofKind.QUIZ
        terminal_answer = question.question_type == "terminal"
    else:
        requirement = node.requirement(ProofKind.TERMINAL)
        if requirement is None:
            raise HTTPException(status_code=404, detail="Ce nœud n'a pas d'exercice de saisie.")
        spec = tree.conn.execute(
            "SELECT pattern, explanation FROM terminal_specs WHERE node_id = ?",
            (node_id,),
        ).fetchone()
        if spec is None:
            raise HTTPException(status_code=404, detail="Spécification terminal absente.")
        pattern = spec["pattern"]
        explanation = spec["explanation"]
        kind = ProofKind.TERMINAL
        terminal_answer = True

    correct = _answer_matches(
        pattern,
        answer,
        terminal=terminal_answer,
    )
    detail = "Réponse correcte." if correct else "Réponse incorrecte."
    attempt, validated = tree.record(
        node_id,
        kind,
        100 if correct else 0,
        correct,
        evidence=answer,
        detail=detail,
    )
    if not explanation:
        explanation = (
            "La réponse correspond au format attendu."
            if correct
            else "Vérifie le format de l'adresse ou la syntaxe de la commande."
        )
    return {
        "success": True,
        "correct": correct,
        "explanation": explanation,
        "score": attempt.score,
        "passed": attempt.passed,
        "validated": validated,
        "status": tree.status(node_id).value,
        "attempt": _attempt_payload(attempt),
    }


@app.post("/api/node/{node_id}/check-command")
def check_command(
    node_id: str,
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Vérifie une commande terminal, puis enregistre la preuve."""
    node = _playable(tree, node_id)
    requirement = node.requirement(ProofKind.TERMINAL)
    if requirement is None:
        raise HTTPException(status_code=404, detail="Ce nœud n'a pas d'exigence terminal.")

    command = payload.get("command")
    if not isinstance(command, str) or not command.strip():
        raise HTTPException(status_code=422, detail="Le champ command doit contenir une commande.")
    if len(command) > 500:
        raise HTTPException(status_code=422, detail="La commande dépasse 500 caractères.")

    spec = tree.conn.execute(
        "SELECT pattern FROM terminal_specs WHERE node_id = ?", (node_id,)
    ).fetchone()
    if spec is None:
        raise HTTPException(status_code=404, detail="Spécification terminal absente.")

    accepted = _answer_matches(spec["pattern"], command, terminal=True)
    detail = "Commande acceptée." if accepted else "Commande incorrecte."
    attempt, validated = tree.record(
        node_id,
        ProofKind.TERMINAL,
        100 if accepted else 0,
        accepted,
        evidence=command,
        detail=detail,
    )
    return {
        "success": True,
        "accepted": accepted,
        "message": detail,
        "score": attempt.score,
        "validated": validated,
        "status": tree.status(node_id).value,
    }


@app.post("/api/node/{node_id}/start-architecture")
def start_architecture_challenge(
    node_id: str,
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Ouvre une session serveur horodatée pour un défi d'architecture."""
    _get_node(tree, node_id)
    challenge = _challenge_row(tree, node_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Ce nœud n'a pas de défi d'architecture.")
    try:
        tree.playable(node_id)
    except DomainError as error:
        raise HTTPException(status_code=409, detail=str(error))

    now = int(time.time())
    session_id = uuid.uuid4().hex
    expires_at = now + challenge["time_limit"]
    tree.conn.execute("DELETE FROM challenge_sessions WHERE expires_at < ?", (now,))
    tree.conn.execute(
        "INSERT INTO challenge_sessions (session_id, node_id, expires_at) VALUES (?, ?, ?)",
        (session_id, node_id, expires_at),
    )
    tree.conn.commit()
    return {
        "session_id": session_id,
        "time_limit": challenge["time_limit"],
        "expires_at": expires_at,
        "prompt": tree.node(node_id).description,
    }


@app.post("/api/node/{node_id}/validate-architecture")
def validate_architecture(
    node_id: str,
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Compare un schéma Drawflow à la topologie attendue et enregistre la preuve."""
    _get_node(tree, node_id)
    challenge = _challenge_row(tree, node_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Ce nœud n'a pas de défi d'architecture.")

    session_id = payload.get("session_id")
    topology = payload.get("topology")
    if not isinstance(session_id, str) or not isinstance(topology, dict):
        raise HTTPException(
            status_code=422,
            detail="Le corps doit contenir session_id et topology (export Drawflow).",
        )

    session = tree.conn.execute(
        "SELECT expires_at FROM challenge_sessions WHERE session_id = ? AND node_id = ?",
        (session_id, node_id),
    ).fetchone()
    if session is None:
        raise HTTPException(status_code=409, detail="Session de défi absente ou déjà terminée.")

    tree.conn.execute("DELETE FROM challenge_sessions WHERE session_id = ?", (session_id,))
    tree.conn.commit()

    if int(time.time()) >= session["expires_at"]:
        passed = False
        detail = "Temps écoulé."
    else:
        expected = json.loads(challenge["expected_topology"])
        passed, detail = _compare_topology(topology, expected)

    try:
        attempt, validated = tree.record(
            node_id,
            ProofKind.MANUAL,
            score=100 if passed else 0,
            passed=passed,
            evidence="Défi d'architecture Drawflow",
            detail=detail,
        )
    except DomainError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "success": True,
        "passed": passed,
        "score": attempt.score,
        "detail": detail,
        "validated": validated,
        "status": tree.status(node_id).value,
    }


@app.post("/api/node/{node_id}/reset")
def reset_node(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict:
    """Supprime les tentatives d'un nœud (quiz, lab, examen, preuve)."""
    _get_node(tree, node_id)
    deleted = tree.reset(node_id)
    return {
        "node_id": node_id,
        "deleted_attempts": deleted,
        "status": tree.status(node_id).value,
    }


@app.get("/api/topology")
def read_topology(tree: SkillTree = Depends(get_tree)) -> dict:
    """Retourne le dernier schéma sauvegardé, ou un objet vide."""
    row = tree.conn.execute(
        "SELECT data FROM topologies ORDER BY updated_at DESC, id DESC LIMIT 1"
    ).fetchone()
    return json.loads(row["data"]) if row else {}


@app.post("/api/topology")
def save_topology(
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Enregistre un schéma Drawflow."""
    updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cursor = tree.conn.execute(
        "INSERT INTO topologies (name, data, updated_at) VALUES (?, ?, ?)",
        ("Mon lab de routage", json.dumps(payload, ensure_ascii=False), updated_at),
    )
    tree.conn.commit()
    return {"success": True, "id": cursor.lastrowid, "updated_at": updated_at}


STATIC_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)
