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
except ImportError:  # pragma: no cover - dépendance optionnelle au runtime
    load_dotenv = None

from .db import (
    DEFAULT_DB,
    XP_REWARDS,
    add_xp,
    award_attempt_xp,
    connect,
    ensure_ready,
    get_user_stats,
    touch_daily_streak,
)
from .domain import Node, ProofKind, Question, Requirement, Status
from .engine import (
    BADGE_DEFINITIONS,
    DomainError,
    SkillTree,
    get_daily_plan,
    is_validated,
    requirement_met,
)
from .labs_runner import (
    LabRunnerError,
    LabSessionError,
    exec_in_lab,
    start_interactive_lab,
    validate_lab,
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
EXAM_PASS_SCORE = 85
EXAM_SUBMIT_GRACE_SECONDS = 15
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"
GROQ_FALLBACK_MODEL = "openai/gpt-oss-20b"
GROQ_DEPRECATED_MODELS = {"llama3-8b-8192", "llama3-70b-8192"}
TUTOR_MAX_CONTEXT_CHARS = 14_000
CERTIFICATE_NAME = (os.environ.get("CERTIFICATE_NAME") or "Ton Nom").strip() or "Ton Nom"
CERTIFICATE_VERIFY_BASE_URL = (
    os.environ.get("CERTIFICATE_VERIFY_BASE_URL") or ""
).strip().rstrip("/")
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
    time_limit_seconds: int = Field(
        default=DIAGNOSTIC_TIME_LIMIT_SECONDS,
        ge=1,
        le=3600,
    )


def _markdown_to_plain_text(markdown: str) -> str:
    """Retire la syntaxe Markdown et les blocs de code avant la synthèse."""
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


def _normalize_cli_command(command: str) -> str:
    return re.sub(r"\s+", " ", command.strip().lower())


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


def _question_rows(tree: SkillTree, ids: list[int]) -> dict[int, sqlite3.Row]:
    if not ids:
        return {}
    placeholders = ",".join("?" for _ in ids)
    rows = tree.conn.execute(
        f"SELECT * FROM questions WHERE id IN ({placeholders})",
        ids,
    ).fetchall()
    return {row["id"]: row for row in rows}


@app.get("/api/node/{node_id}/lesson", response_class=PlainTextResponse)
def read_lesson(node_id: str, tree: SkillTree = Depends(get_tree)) -> PlainTextResponse:
    """Retourne le Markdown associé au nœud, ou une chaîne vide sans leçon."""
    node = _get_node(tree, node_id)
    lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
    return PlainTextResponse(
        lessons.get(node.id, ""),
        media_type="text/markdown; charset=utf-8",
    )


@app.get("/api/node/{node_id}/tts")
async def read_node_tts(
    node_id: str,
    voice: str = Query(default="fr-FR-DeniseNeural"),
    tree: SkillTree = Depends(get_tree),
) -> StreamingResponse:
    """Génère un MP3 temporaire du cours avec edge-tts et le streame."""
    if voice not in TTS_VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Voix inconnue. Choisis parmi : {', '.join(sorted(TTS_VOICES))}.",
        )

    node = _get_node(tree, node_id)
    lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
    markdown = lessons.get(node.id, "").strip()
    if not markdown:
        raise HTTPException(status_code=404, detail="Aucun cours à lire pour ce nœud.")

    text = _markdown_to_plain_text(markdown)
    if not text:
        raise HTTPException(status_code=422, detail="Le cours ne contient pas de texte lisible.")

    try:
        import edge_tts
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="edge-tts n'est pas installé. Lance `pip install -r requirements.txt`.",
        )

    tmp = tempfile.NamedTemporaryFile(
        prefix=f"skilltree_{node.id}_",
        suffix=".mp3",
        delete=False,
    )
    audio_path = Path(tmp.name)
    tmp.close()

    try:
        await edge_tts.Communicate(text, voice).save(str(audio_path))
    except Exception as error:
        audio_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=502,
            detail=f"Génération audio impossible : {error}",
        )

    def stream_audio() -> Iterator[bytes]:
        try:
            with audio_path.open("rb") as audio_file:
                while chunk := audio_file.read(64 * 1024):
                    yield chunk
        finally:
            audio_path.unlink(missing_ok=True)

    return StreamingResponse(
        stream_audio(),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-store",
            "Content-Disposition": f'inline; filename="{node.id}.mp3"',
        },
    )


@app.post("/api/node/{node_id}/ask")
def ask_tutor(
    node_id: str,
    payload: AskRequest,
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Répond à une question sur le cours en utilisant Groq."""
    node = _get_node(tree, node_id)
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="La question ne peut pas être vide.")

    api_key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "La clé GROQ_API_KEY n'est pas configurée. "
                "Ajoute-la dans le fichier .env à la racine du projet "
                "(voir .env.example), puis redémarre le serveur."
            ),
        )

    lessons = load_lessons(CONTENT_DIR, {item.id for item in tree.nodes()})
    markdown = lessons.get(node.id, "").strip()
    if not markdown:
        markdown = f"{node.title}\n\n{node.description}".strip()

    context = markdown[:TUTOR_MAX_CONTEXT_CHARS]
    if len(markdown) > TUTOR_MAX_CONTEXT_CHARS:
        context += "\n\n[... cours tronqué pour respecter la fenêtre du modèle ...]"

    try:
        from groq import Groq
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Le paquet groq n'est pas installé. "
                "Lance `python -m pip install -r requirements.txt`."
            ),
        )

    requested_model = (os.environ.get("GROQ_MODEL") or GROQ_DEFAULT_MODEL).strip()
    if requested_model in GROQ_DEPRECATED_MODELS:
        requested_model = GROQ_DEFAULT_MODEL

    models: list[str] = []
    for candidate in (requested_model, GROQ_DEFAULT_MODEL, GROQ_FALLBACK_MODEL):
        if candidate and candidate not in models:
            models.append(candidate)

    system_prompt = (
        "Tu es un tuteur réseau francophone, spécialisé CCNA et administration "
        "réseau senior. Réponds en français, de façon pédagogique, précise et "
        "concise. Appuie-toi sur le cours fourni ci-dessous et n'invente pas de "
        "commandes ou de valeurs absentes. Si la réponse ne se trouve pas dans "
        "le cours, dis-le clairement puis propose une piste de vérification "
        "générale. Utilise des exemples Cisco IOS ou Linux quand c'est pertinent.\n\n"
        f"--- DÉBUT DU COURS : {node.title} ({node.category}) ---\n"
        f"{context}\n"
        "--- FIN DU COURS ---"
    )

    try:
        client = Groq(api_key=api_key)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Le client Groq n'a pas pu être initialisé : {str(error)[:500]}",
        )

    errors: list[str] = []
    answer = ""
    used_model = requested_model

    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                temperature=0.25,
                max_tokens=900,
            )
            candidate = (completion.choices[0].message.content or "").strip()
            if candidate:
                answer = candidate
                used_model = model
                break
            errors.append(f"{model} : réponse vide")
        except Exception as error:
            errors.append(f"{model} : {str(error)[:300]}")

    if not answer:
        details = " | ".join(errors[-3:]) or "aucun modèle disponible"
        raise HTTPException(
            status_code=502,
            detail=f"Le tuteur IA n'a pas pu répondre : {details}",
        )

    return {
        "node_id": node.id,
        "question": question,
        "answer": answer,
        "mock": False,
        "model": used_model,
        "fallback_used": used_model != requested_model,
    }


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


def _gamification_payload(
    tree: SkillTree,
    reward: dict | None = None,
    badges: list[dict] | None = None,
) -> dict:
    """Récompenses d'une action : XP/coins, montée de niveau et badges."""
    reward = tree.last_reward if reward is None else reward
    new_badges = tree.last_badges if badges is None else badges
    return {
        "reward": reward,
        "new_badges": new_badges or [],
        "user_stats": get_user_stats(tree.conn),
    }


def _badge_list(tree: SkillTree) -> list[dict]:
    rows = tree.conn.execute(
        "SELECT id, nom, description, icone, condition_debloquee_le FROM badges"
    ).fetchall()
    unlocked = {row["id"]: dict(row) for row in rows}
    return [
        {
            "id": badge_id,
            **definition,
            "unlocked": badge_id in unlocked,
            "condition_debloquee_le": unlocked.get(badge_id, {}).get(
                "condition_debloquee_le"
            ),
        }
        for badge_id, definition in BADGE_DEFINITIONS.items()
    ]


def _shop_payload(tree: SkillTree) -> dict:
    items = [
        dict(row)
        for row in tree.conn.execute(
            "SELECT id, nom, description, prix, type FROM shop_items ORDER BY prix, id"
        )
    ]
    inventory = {
        row["item_id"]: int(row["quantity"])
        for row in tree.conn.execute(
            "SELECT item_id, quantity FROM shop_inventory"
        )
    }
    stats = get_user_stats(tree.conn)
    return {
        "coins": stats["coins"],
        "items": [
            {**item, "quantity": inventory.get(item["id"], 0)} for item in items
        ],
        "inventory": [
            {"item_id": item_id, "quantity": quantity}
            for item_id, quantity in inventory.items()
            if quantity > 0
        ],
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


@app.get("/api/daily-plan")
def read_daily_plan(tree: SkillTree = Depends(get_tree)) -> dict:
    """Session quotidienne : travaux en cours, révisions et nœuds disponibles."""
    return get_daily_plan(tree)


@app.get("/api/flashcards")
def read_flashcards() -> dict:
    """Cartes recto-verso de mémorisation, lues depuis content/flashcards/."""
    try:
        payload = json.loads(FLASHCARDS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Fichier de flashcards introuvable : {FLASHCARDS_FILE}",
        )
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=422,
            detail=f"Fichier de flashcards invalide : {error}",
        )

    if not isinstance(payload, list):
        raise HTTPException(
            status_code=422,
            detail="Le fichier de flashcards doit contenir une liste.",
        )

    cards = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise HTTPException(status_code=422, detail=f"Carte {index} invalide.")
        front = item.get("front")
        back = item.get("back")
        if (
            not isinstance(front, str)
            or not front.strip()
            or not isinstance(back, str)
            or not back.strip()
        ):
            raise HTTPException(
                status_code=422,
                detail=f"Carte {index} : les champs front et back sont obligatoires.",
            )
        cards.append(
            {
                "id": str(item.get("id") or f"card-{index}"),
                "category": str(item.get("category") or "Général"),
                "front": front.strip(),
                "back": back.strip(),
            }
        )

    return {"count": len(cards), "cards": cards}


def _diagnostic_file(diag_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9_-]{1,64}", diag_id):
        raise HTTPException(status_code=404, detail="Diagnostic introuvable.")
    return DIAGNOSTICS_DIR / f"{diag_id}.json"


def _load_diagnostic(diag_id: str) -> dict:
    path = _diagnostic_file(diag_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Diagnostic introuvable.")
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=422,
            detail=f"Fichier de diagnostic invalide : {error}",
        )

    if not isinstance(data, dict):
        raise HTTPException(status_code=422, detail="Le diagnostic doit être un objet JSON.")
    if not isinstance(data.get("id"), str) or not isinstance(data.get("title"), str):
        raise HTTPException(status_code=422, detail="Le diagnostic doit avoir un id et un titre.")
    steps = data.get("steps")
    start = data.get("start")
    if not isinstance(steps, dict) or not steps:
        raise HTTPException(status_code=422, detail="Le diagnostic ne contient aucune étape.")
    if not isinstance(start, str) or start not in steps:
        raise HTTPException(status_code=422, detail="L'étape de départ est invalide.")

    for step_id, step in steps.items():
        if not isinstance(step, dict):
            raise HTTPException(status_code=422, detail=f"Étape invalide : {step_id}.")
        step_type = step.get("type", "choice")
        if step_type not in {"choice", "command"}:
            raise HTTPException(
                status_code=422,
                detail=f"Type d'étape inconnu dans {step_id}.",
            )
        if step_type == "command":
            command = step.get("command")
            if not isinstance(command, dict):
                raise HTTPException(
                    status_code=422,
                    detail=f"Commande invalide dans l'étape {step_id}.",
                )
            if not isinstance(command.get("next"), str) or command["next"] not in steps:
                raise HTTPException(
                    status_code=422,
                    detail=f"Étape cible inconnue dans la commande {step_id}.",
                )
            pattern = command.get("regex")
            if pattern is not None:
                try:
                    re.compile(str(pattern))
                except re.error:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Regex invalide dans l'étape {step_id}.",
                    )
            continue
        choices = step.get("choices", [])
        if not isinstance(choices, list):
            raise HTTPException(status_code=422, detail=f"Choix invalides : {step_id}.")
        for choice in choices:
            if (
                not isinstance(choice, dict)
                or not isinstance(choice.get("id"), str)
                or not isinstance(choice.get("label"), str)
                or not isinstance(choice.get("next"), str)
            ):
                raise HTTPException(
                    status_code=422,
                    detail=f"Choix incomplet dans l'étape {step_id}.",
                )
            if choice["next"] not in steps:
                raise HTTPException(
                    status_code=422,
                    detail=f"Étape cible inconnue : {choice['next']}.",
                )
        outcome = step.get("outcome")
        if outcome is not None and outcome not in {"success", "failure"}:
            raise HTTPException(
                status_code=422,
                detail=f"Résultat inconnu dans l'étape {step_id}.",
            )
    return data


def _public_diagnostic(data: dict) -> dict:
    """Retire les flags de correction avant l'envoi au navigateur."""
    steps = {}
    for step_id, step in data["steps"].items():
        step_type = step.get("type", "choice")
        command = step.get("command") if step_type == "command" else None
        steps[step_id] = {
            "type": step_type,
            "situation": str(step.get("situation") or ""),
            "choices": [
                {
                    "id": choice["id"],
                    "label": choice["label"],
                    "next": choice["next"],
                }
                for choice in step.get("choices", [])
            ],
            "command": (
                {
                    "prompt": str(command.get("prompt") or ""),
                    "placeholder": str(command.get("placeholder") or ""),
                    "regex": str(command.get("regex") or ""),
                    "next": command["next"],
                }
                if isinstance(command, dict)
                else None
            ),
            "outcome": step.get("outcome"),
            "explanation": str(step.get("explanation") or ""),
        }
    return {
        "id": data["id"],
        "title": data["title"],
        "description": str(data.get("description") or ""),
        "start": data["start"],
        "steps": steps,
    }


@app.get("/api/diagnostics/{diag_id}")
def read_diagnostic(diag_id: str) -> dict:
    """Retourne l'arbre de décision d'un diagnostic interactif."""
    return _public_diagnostic(_load_diagnostic(diag_id))


@app.post("/api/diagnostics/{diag_id}/complete")
def complete_diagnostic(
    diag_id: str,
    payload: DiagnosticCompleteRequest,
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Valide le chemin choisi et attribue les XP si le diagnostic est réussi."""
    data = _load_diagnostic(diag_id)
    elapsed = payload.elapsed_seconds
    time_expired = elapsed is not None and elapsed > payload.time_limit_seconds
    if time_expired:
        stats = get_user_stats(tree.conn)
        return {
            "success": False,
            "diagnostic_id": data["id"],
            "final_step": data["start"],
            "explanation": (
                "Temps écoulé : le diagnostic doit être résolu dans la limite "
                f"de {payload.time_limit_seconds} secondes."
            ),
            "xp_awarded": 0,
            "bonus_xp": 0,
            "time_expired": True,
            "elapsed_seconds": round(float(elapsed), 1),
            "remaining_seconds": 0,
            "user_stats": stats,
        }

    step_id = data["start"]
    all_correct = True

    for entry in payload.path:
        step = data["steps"].get(step_id)
        if not isinstance(step, dict):
            raise HTTPException(status_code=422, detail="Parcours de diagnostic invalide.")
        if step.get("type", "choice") == "command":
            command = step.get("command")
            if not isinstance(command, dict):
                raise HTTPException(status_code=422, detail="Commande de diagnostic invalide.")
            regex = command.get("regex")
            if regex:
                accepted = re.fullmatch(
                    str(regex),
                    " ".join(entry.strip().split()),
                    re.IGNORECASE,
                ) is not None
            else:
                expected = str(command.get("answer") or "").strip().lower()
                accepted = " ".join(entry.strip().split()).lower() == " ".join(
                    expected.split()
                )
            if not accepted:
                all_correct = False
            step_id = command.get("next")
            if not isinstance(step_id, str):
                raise HTTPException(status_code=422, detail="Parcours de diagnostic invalide.")
            continue

        choice = next(
            (item for item in step.get("choices", []) if item.get("id") == entry),
            None,
        )
        if choice is None:
            raise HTTPException(
                status_code=422,
                detail=f"Choix inconnu à l'étape {step_id} : {entry}.",
            )
        if not bool(choice.get("correct")):
            all_correct = False
        step_id = choice["next"]

    final_step = data["steps"].get(step_id)
    if not isinstance(final_step, dict):
        raise HTTPException(status_code=422, detail="Parcours de diagnostic invalide.")
    if final_step.get("type", "choice") == "command" or final_step.get("choices"):
        raise HTTPException(status_code=422, detail="Le diagnostic n'est pas terminé.")

    success = all_correct and final_step.get("outcome") == "success"
    base_xp = XP_REWARDS["diagnostic"]
    bonus_xp = (
        DIAGNOSTIC_FAST_BONUS_XP
        if success and elapsed is not None and elapsed < DIAGNOSTIC_FAST_BONUS_SECONDS
        else 0
    )
    xp_awarded = base_xp + bonus_xp if success else 0
    stats = get_user_stats(tree.conn)
    if xp_awarded:
        stats = add_xp(tree.conn, xp_awarded)

    return {
        "success": success,
        "diagnostic_id": data["id"],
        "final_step": step_id,
        "explanation": str(final_step.get("explanation") or ""),
        "xp_awarded": xp_awarded,
        "bonus_xp": bonus_xp,
        "time_expired": False,
        "elapsed_seconds": round(float(elapsed), 1) if elapsed is not None else None,
        "remaining_seconds": (
            max(0, payload.time_limit_seconds - int(elapsed))
            if elapsed is not None
            else None
        ),
        "user_stats": stats,
    }


@app.get("/api/user-stats")
def read_user_stats(tree: SkillTree = Depends(get_tree)) -> dict:
    """Retourne les XP, les SkillCoins et la progression vers le palier suivant."""
    return get_user_stats(tree.conn)


@app.get("/api/badges")
def read_badges(tree: SkillTree = Depends(get_tree)) -> dict:
    """Retourne les badges connus et leur état de déblocage."""
    return {"badges": _badge_list(tree)}


@app.get("/api/shop")
def read_shop(tree: SkillTree = Depends(get_tree)) -> dict:
    """Liste les objets de la boutique et l'inventaire du joueur."""
    return _shop_payload(tree)


@app.post("/api/shop/buy")
def buy_shop_item(
    payload: ShopBuyRequest,
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Achète un objet, déduit les SkillCoins et met à jour l'inventaire."""
    item_id = payload.item_id.strip()
    item = tree.conn.execute(
        "SELECT id, nom, description, prix, type FROM shop_items WHERE id = ?",
        (item_id,),
    ).fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="Objet de boutique inconnu.")

    stats = get_user_stats(tree.conn)
    price = int(item["prix"])
    if stats["coins"] < price:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Pas assez de SkillCoins : il te manque "
                f"{price - stats['coins']} pièce(s)."
            ),
        )

    try:
        with tree.conn:
            tree.conn.execute(
                "UPDATE user_stats SET coins = coins - ? WHERE id = 1",
                (price,),
            )
            tree.conn.execute(
                "INSERT INTO shop_inventory (item_id, quantity) VALUES (?, 1)"
                " ON CONFLICT(item_id) DO UPDATE SET"
                " quantity = quantity + 1",
                (item_id,),
            )
    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="Achat impossible : la boutique n'a pas pu enregistrer l'opération.",
        )

    result = _shop_payload(tree)
    result.update(
        {
            "success": True,
            "purchased": dict(item),
            "message": f"{item['nom']} acheté pour {price} SkillCoins.",
        }
    )
    return result


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
        # Chaîne rompue : le compteur repart à 1 pour la prochaine activité.
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


@app.get("/api/streak")
def read_streak(tree: SkillTree = Depends(get_tree)) -> dict:
    """Calcule les jours consécutifs d'activité et les minutes cumulées."""
    return _streak_payload(tree)


@app.get("/api/profile")
def read_profile(tree: SkillTree = Depends(get_tree)) -> dict:
    """Regroupe les accomplissements affichés dans le bandeau de profil."""
    check_badges(tree)
    nodes = tree.nodes()
    total_nodes = len(nodes)
    validated_nodes = sum(1 for node in nodes if is_validated(node))
    progress_percent = round(100 * validated_nodes / total_nodes) if total_nodes else 0

    labs_validated = int(
        tree.conn.execute(
            "SELECT COUNT(DISTINCT node_id) FROM attempts"
            " WHERE kind = 'lab' AND passed = 1"
        ).fetchone()[0]
    )
    exam_attempts = int(
        tree.conn.execute(
            "SELECT COUNT(*) FROM attempts WHERE kind = 'exam' AND passed = 1"
        ).fetchone()[0]
    )
    exam_sessions = int(
        tree.conn.execute(
            "SELECT COUNT(*) FROM exam_sessions"
            " WHERE submitted = 1 AND passed = 1"
        ).fetchone()[0]
    )
    exams_passed = exam_attempts + exam_sessions
    level = get_user_stats(tree.conn)

    return {
        "streak": _streak_payload(tree),
        "validated_nodes": validated_nodes,
        "total_nodes": total_nodes,
        "progress_percent": progress_percent,
        "labs_validated": labs_validated,
        "exams_passed": exams_passed,
        "level": level,
        "certificate": {
            "name": CERTIFICATE_NAME,
            "title": "Certificat d'Admin Réseau Senior",
            "date": date.today().strftime("%d/%m/%Y"),
        },
        "coins": level["coins"],
        "badges": _badge_list(tree),
    }


def _new_certificate_number(conn: sqlite3.Connection) -> str:
    year = date.today().year
    for _ in range(100):
        number = f"ST-{year}-{secrets.randbelow(10_000):04d}"
        if conn.execute(
            "SELECT 1 FROM certificates WHERE number = ?", (number,)
        ).fetchone() is None:
            return number
    raise HTTPException(
        status_code=503,
        detail="Impossible de générer un numéro de certificat unique.",
    )


@app.get("/api/certificate/verify/{number}")
def verify_certificate(
    number: str,
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Vérifie un numéro de certificat émis par l'application."""
    row = tree.conn.execute(
        "SELECT number, name, level, issued_at FROM certificates WHERE number = ?",
        (number,),
    ).fetchone()
    if row is None:
        return {"valid": False, "number": number}
    return {"valid": True, "certificate": dict(row)}


@app.get("/api/certificate")
def download_certificate(
    request: Request,
    tree: SkillTree = Depends(get_tree),
) -> StreamingResponse:
    """Génère un certificat PDF nominatif avec QR Code de vérification."""
    try:
        from reportlab.lib.colors import Color, HexColor
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
        import qrcode
    except ImportError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "Génération PDF indisponible : installe reportlab et qrcode "
                f"({error})."
            ),
        )

    stats = get_user_stats(tree.conn)
    number = _new_certificate_number(tree.conn)
    issued_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tree.conn.execute(
        "INSERT INTO certificates (number, name, level, issued_at)"
        " VALUES (?, ?, ?, ?)",
        (number, CERTIFICATE_NAME, stats["current_level"], issued_at),
    )
    tree.conn.commit()

    base_url = CERTIFICATE_VERIFY_BASE_URL or str(request.base_url).rstrip("/")
    verify_url = f"{base_url}/api/certificate/verify/{number}"

    qr_buffer = io.BytesIO()
    qr_image = qrcode.make(verify_url)
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
    pdf.setTitle("Certificat d'Admin Réseau Senior")
    pdf.setAuthor("Skill Tree Academy")

    pdf.setFillColor(Color(0.12, 0.09, 0.03))
    pdf.rect(0, 0, page_width, page_height, stroke=0, fill=1)

    margin = 34
    pdf.setStrokeColor(HexColor("#b45309"))
    pdf.setLineWidth(2)
    pdf.rect(margin, margin, page_width - 2 * margin, page_height - 2 * margin)
    pdf.setStrokeColor(HexColor("#d97706"))
    pdf.setLineWidth(0.6)
    pdf.rect(margin + 7, margin + 7, page_width - 2 * margin - 14, page_height - 2 * margin - 14)
    pdf.setFillColor(HexColor("#fef3c7"))
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(page_width / 2, page_height - 82, "CERTIFICAT")
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(HexColor("#fbbf24"))
    pdf.drawCentredString(page_width / 2, page_height - 105, "SKILL TREE ACADEMY")

    pdf.setFillColor(HexColor("#e5e7eb"))
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(page_width / 2, page_height - 150, "Ce certificat est décerné à")

    pdf.setFillColor(HexColor("#ffffff"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(page_width / 2, page_height - 195, CERTIFICATE_NAME)

    pdf.setFillColor(HexColor("#d1d5db"))
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 225,
        "pour avoir progressé dans le parcours Admin Réseau Senior",
    )
    pdf.drawCentredString(
        page_width / 2,
        page_height - 242,
        "et validé les compétences fondamentales du skill tree.",
    )

    pdf.setFillColor(HexColor("#fef3c7"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(90, 115, f"Niveau : {stats['level_name']}")
    pdf.drawString(90, 92, f"XP : {stats['total_xp']}")
    pdf.drawString(90, 69, f"Délivré le : {date.today().strftime('%d/%m/%Y')}")

    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(HexColor("#fcd34d"))
    pdf.drawRightString(page_width - 90, 69, f"N° {number}")
    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(HexColor("#9ca3af"))
    pdf.drawRightString(page_width - 90, 55, "Vérification :")
    pdf.drawRightString(page_width - 90, 44, verify_url)

    qr_size = 108
    qr_y = 65
    try:
        pdf.drawImage(
            ImageReader(qr_buffer),
            page_width - 90 - qr_size,
            qr_y,
            width=qr_size,
            height=qr_size,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception:
        pdf.setFillColor(HexColor("#374151"))
        pdf.rect(page_width - 90 - qr_size, qr_y, qr_size, qr_size, fill=1, stroke=0)

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(HexColor("#d1d5db"))
    pdf.drawCentredString(page_width / 2, 38, "Skill Tree — progression par preuve")
    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="certificat-{number}.pdf"',
            "Cache-Control": "no-store",
        },
    )


@app.post("/api/sandbox/check")
def check_sandbox_command(payload: SandboxCheckRequest) -> dict:
    """Vérifie une commande Cisco contre la liste blanche/noire du sandbox."""
    try:
        data = json.loads(SANDBOX_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Fichier sandbox introuvable : {SANDBOX_FILE}",
        )
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=422,
            detail=f"Fichier sandbox invalide : {error}",
        )

    if not isinstance(data, dict):
        raise HTTPException(status_code=422, detail="Le fichier sandbox doit être un objet.")

    valid_items = data.get("valid", [])
    invalid_items = data.get("invalid", [])
    if not isinstance(valid_items, list) or not isinstance(invalid_items, list):
        raise HTTPException(
            status_code=422,
            detail="Les champs valid et invalid doivent être des listes.",
        )

    valid: dict[str, dict[str, Any]] = {}
    for item in valid_items:
        if isinstance(item, dict) and isinstance(item.get("command"), str):
            valid[_normalize_cli_command(item["command"])] = item

    invalid: dict[str, dict[str, Any]] = {}
    for item in invalid_items:
        if isinstance(item, dict) and isinstance(item.get("command"), str):
            invalid[_normalize_cli_command(item["command"])] = item

    command = payload.command.strip()
    if not command:
        raise HTTPException(status_code=422, detail="La commande ne peut pas être vide.")
    normalized = _normalize_cli_command(command)

    if normalized in invalid:
        item = invalid[normalized]
        return {
            "accepted": False,
            "reason": "invalid",
            "command": command,
            "matched_command": item["command"],
            "message": str(item.get("error") or "Commande invalide."),
        }

    if normalized in valid:
        item = valid[normalized]
        return {
            "accepted": True,
            "reason": "valid",
            "command": command,
            "matched_command": item["command"],
            "message": "Commande acceptée",
            "description": str(item.get("description") or ""),
        }

    return {
        "accepted": False,
        "reason": "unknown",
        "command": command,
        "matched_command": None,
        "message": "Commande inconnue",
    }


@app.post("/api/reload-content")
def reload_content(tree: SkillTree = Depends(get_tree)) -> dict:
    """Recharge nodes.json, les exercices et les labs sans passer par la CLI."""
    try:
        report = load_content(tree.conn, CONTENT_DIR)
    except ContentError as error:
        raise HTTPException(status_code=422, detail=str(error))

    return {
        "success": True,
        "nodes": report.nodes,
        "edges": report.edges,
        "quiz_questions": report.quiz_questions,
        "exam_questions": report.exam_questions,
        "labs": report.labs,
        "lessons": report.lessons,
        "removed_nodes": list(report.removed_nodes),
    }


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


@app.get("/api/stats")
def read_stats(tree: SkillTree = Depends(get_tree)) -> dict:
    """Agrège les tentatives par catégorie et identifie les nœuds fragiles."""
    nodes = tree.nodes()
    statuses = tree.statuses()
    categories: dict[str, dict[str, Any]] = {}
    node_rows: list[dict[str, Any]] = []
    weak_points: list[dict[str, Any]] = []
    total_attempts = 0
    total_passed = 0

    for node in nodes:
        attempts = len(node.attempts)
        passed = sum(1 for attempt in node.attempts if attempt.passed)
        best_score = max((attempt.score for attempt in node.attempts), default=0)
        last_attempt_at = max(
            (attempt.created_at for attempt in node.attempts),
            default=None,
        )
        status = statuses[node.id]

        category = categories.setdefault(
            node.category,
            {
                "name": node.category,
                "attempts": 0,
                "passed": 0,
                "nodes": 0,
                "validated": 0,
                "success_rate": 0,
                "validation_rate": 0,
            },
        )
        category["attempts"] += attempts
        category["passed"] += passed
        category["nodes"] += 1
        if status is Status.VALIDATED:
            category["validated"] += 1

        total_attempts += attempts
        total_passed += passed

        row = {
            "id": node.id,
            "title": node.title,
            "category": node.category,
            "status": status.value,
            "attempts": attempts,
            "passed_attempts": passed,
            "failed_attempts": attempts - passed,
            "best_score": best_score,
            "last_attempt_at": last_attempt_at,
        }
        node_rows.append(row)
        if attempts > 3:
            weak_points.append(dict(row))

    for category in categories.values():
        if category["attempts"]:
            category["success_rate"] = round(
                100 * category["passed"] / category["attempts"]
            )
        if category["nodes"]:
            category["validation_rate"] = round(
                100 * category["validated"] / category["nodes"]
            )

    node_rows.sort(key=lambda item: (-item["attempts"], item["id"]))
    weak_points.sort(key=lambda item: (-item["attempts"], item["id"]))

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "totals": {
            "nodes": len(nodes),
            "validated": sum(1 for status in statuses.values() if status is Status.VALIDATED),
            "attempts": total_attempts,
            "passed": total_passed,
            "success_rate": round(100 * total_passed / total_attempts)
            if total_attempts
            else 0,
            "weak_points": len(weak_points),
        },
        "categories": list(categories.values()),
        "nodes": node_rows,
        "weak_points": weak_points,
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
        **_gamification_payload(tree),
    }


@app.post("/api/exam/generate")
def generate_exam(
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Tire un examen aléatoire parmi les exercices d'une catégorie."""
    category = payload.get("category")
    if not isinstance(category, str) or not category.strip():
        raise HTTPException(status_code=422, detail="Le champ category est obligatoire.")
    category = category.strip()

    nodes = [node for node in tree.nodes() if node.category == category]
    if not nodes:
        raise HTTPException(status_code=404, detail="Catégorie inconnue.")

    pool: list[tuple[Node, Question]] = []
    for node in nodes:
        for question in tree.questions(node.id, ProofKind.QUIZ):
            pool.append((node, question))
    if not pool:
        raise HTTPException(
            status_code=404,
            detail="Aucune question d'exercice dans cette catégorie.",
        )

    selected = random.sample(pool, min(EXAM_QUESTION_COUNT, len(pool)))
    question_ids = [question.id for _, question in selected]
    now = int(time.time())
    session_id = uuid.uuid4().hex

    tree.conn.execute(
        "INSERT INTO exam_sessions"
        " (session_id, category, question_ids, started_at, expires_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (
            session_id,
            category,
            json.dumps(question_ids),
            now,
            now + EXAM_DURATION_SECONDS,
        ),
    )
    tree.conn.execute(
        "DELETE FROM exam_sessions WHERE expires_at < ?",
        (now - 86400,),
    )
    tree.conn.commit()

    return {
        "session_id": session_id,
        "category": category,
        "requested": EXAM_QUESTION_COUNT,
        "available": len(pool),
        "total": len(selected),
        "duration_seconds": EXAM_DURATION_SECONDS,
        "expires_at": now + EXAM_DURATION_SECONDS,
        "questions": [
            {
                "id": question.id,
                "node_id": node.id,
                "node_title": node.title,
                "type": question.question_type,
                "prompt": question.prompt,
                "choices": list(question.choices),
            }
            for node, question in selected
        ],
    }


@app.post("/api/exam/submit")
def submit_exam(
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Corrige un examen, sans révéler les réponses avant la soumission."""
    session_id = payload.get("session_id")
    answers = payload.get("answers")
    if not isinstance(session_id, str) or not session_id.strip():
        raise HTTPException(status_code=422, detail="Le champ session_id est obligatoire.")
    if not isinstance(answers, list):
        raise HTTPException(status_code=422, detail="Le champ answers doit être une liste.")

    session = tree.conn.execute(
        "SELECT * FROM exam_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if session is None:
        raise HTTPException(status_code=404, detail="Session d'examen introuvable.")
    if session["submitted"]:
        raise HTTPException(status_code=409, detail="Cet examen a déjà été soumis.")

    try:
        question_ids = json.loads(session["question_ids"])
    except (TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=409, detail="Session d'examen invalide.")
    if not isinstance(question_ids, list) or not all(
        isinstance(question_id, int) for question_id in question_ids
    ):
        raise HTTPException(status_code=409, detail="Session d'examen invalide.")
    if len(answers) != len(question_ids):
        raise HTTPException(
            status_code=422,
            detail=f"L'examen attend exactement {len(question_ids)} réponses.",
        )

    rows = _question_rows(tree, question_ids)
    if len(rows) != len(question_ids):
        raise HTTPException(
            status_code=409,
            detail="Les questions de cet examen ne sont plus disponibles. Relance l'examen.",
        )

    results = []
    correct_count = 0
    for question_id, answer in zip(question_ids, answers):
        row = rows[question_id]
        if row["question_type"] == "qcm":
            choices = json.loads(row["choices"])
            is_correct = (
                isinstance(answer, int)
                and not isinstance(answer, bool)
                and 0 <= answer < len(choices)
                and answer == row["answer"]
            )
        else:
            is_correct = (
                isinstance(answer, str)
                and _answer_matches(
                    row["answer_regex"] or "",
                    answer,
                    terminal=row["question_type"] == "terminal",
                )
            )
        correct_count += int(is_correct)
        results.append(
            {
                "question_id": question_id,
                "correct": bool(is_correct),
                "explanation": row["explanation"],
            }
        )

    total = len(question_ids)
    score = round(100 * correct_count / total) if total else 0
    passed = score > EXAM_PASS_SCORE
    now = int(time.time())
    time_expired = now > session["expires_at"] + EXAM_SUBMIT_GRACE_SECONDS

    tree.conn.execute(
        "UPDATE exam_sessions"
        " SET submitted = 1, score = ?, passed = ?, correct = ?, total = ?,"
        " submitted_at = ?, time_expired = ?"
        " WHERE session_id = ?",
        (
            score,
            int(passed),
            correct_count,
            total,
            now,
            int(time_expired),
            session_id,
        ),
    )
    tree.conn.commit()

    reward = None
    if passed and not time_expired:
        touch_daily_streak(tree.conn)
        reward = award_attempt_xp(tree.conn, "exam", True)
        tree.last_reward = reward
    tree.last_badges = check_badges(tree)

    return {
        "success": True,
        "session_id": session_id,
        "category": session["category"],
        "score": score,
        "passed": passed,
        "threshold": EXAM_PASS_SCORE,
        "correct": correct_count,
        "total": total,
        "time_expired": time_expired,
        "elapsed_seconds": max(0, now - session["started_at"]),
        "remaining_seconds": max(0, session["expires_at"] - now),
        "xp_awarded": reward["xp"] if reward else 0,
        "coins_awarded": reward["coins"] if reward else 0,
        **(_gamification_payload(tree, reward, tree.last_badges)),
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
        **_gamification_payload(tree),
    }


# Les routes /api/lab/* exécutent des commandes dans un conteneur --privileged.
# Elles sont prévues pour un usage local ou derrière une authentification :
# ne pas exposer ce serveur directement sur Internet.
@app.post("/api/lab/start")
def start_lab(
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Démarre un conteneur de lab Docker persistant pour la session web."""
    node_id = payload.get("node_id")
    if not isinstance(node_id, str) or not node_id.strip():
        raise HTTPException(status_code=422, detail="Le champ node_id est obligatoire.")

    node = _playable(tree, node_id.strip())
    spec = tree.lab_spec(node.id)
    if spec is None or spec.kind != "docker":
        raise HTTPException(status_code=404, detail="Ce nœud n'a pas de lab Docker.")
    lab_dir = find_lab_dir(node.id)
    if lab_dir is None:
        raise HTTPException(status_code=404, detail="Dossier du lab Docker introuvable.")

    try:
        session = start_interactive_lab(node.id, lab_dir)
    except LabRunnerError as error:
        raise HTTPException(status_code=503, detail=str(error))

    return {
        "lab_id": session.lab_id,
        "container_id": session.container_id,
        "node_id": session.node_id,
        "prompt": spec.prompt,
        "hint": spec.hint,
        "setup_logs": session.setup_logs,
        "timeout_seconds": session.timeout,
    }


@app.post("/api/lab/exec")
def exec_lab(payload: dict[str, Any] = Body(...)) -> dict:
    """Exécute une commande dans un conteneur de lab actif."""
    lab_id = payload.get("lab_id")
    command = payload.get("command")
    if not isinstance(lab_id, str) or not lab_id.strip():
        raise HTTPException(status_code=422, detail="Le champ lab_id est obligatoire.")
    if not isinstance(command, str) or not command.strip():
        raise HTTPException(status_code=422, detail="Le champ command est obligatoire.")

    try:
        result = exec_in_lab(lab_id, command)
    except LabSessionError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except LabRunnerError as error:
        raise HTTPException(status_code=503, detail=str(error))

    return {
        "success": True,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "timed_out": result.timed_out,
    }


@app.post("/api/lab/validate")
def validate_lab_route(
    payload: dict[str, Any] = Body(...),
    tree: SkillTree = Depends(get_tree),
) -> dict:
    """Lance check.sh, enregistre la tentative et ferme le conteneur."""
    lab_id = payload.get("lab_id")
    if not isinstance(lab_id, str) or not lab_id.strip():
        raise HTTPException(status_code=422, detail="Le champ lab_id est obligatoire.")

    try:
        validation = validate_lab(lab_id)
    except LabSessionError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except LabRunnerError as error:
        raise HTTPException(status_code=503, detail=str(error))

    try:
        attempt, validated = tree.record_docker_lab(
            validation.node_id,
            validation.commands,
            validation.result,
        )
    except DomainError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "success": True,
        "passed": validation.result.passed,
        "score": validation.result.score,
        "detail": validation.result.detail,
        "logs": validation.result.logs,
        "validated": validated,
        "status": tree.status(validation.node_id).value,
        "attempt": _attempt_payload(attempt),
        **_gamification_payload(tree),
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
        **_gamification_payload(tree),
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
def validate_architecture(node_id: str, payload: dict, tree: SkillTree = Depends(get_tree)):
    # 1. Récupérer le défi attendu depuis la base
    challenge_row = tree.conn.execute(
        "SELECT expected_topology FROM challenges WHERE node_id = ?", (node_id,)
    ).fetchone()
    
    if not challenge_row:
        raise HTTPException(status_code=404, detail="Aucun défi configuré pour ce nœud.")
        
    expected = json.loads(challenge_row["expected_topology"])
    drawflow_data = payload.get("drawflow", {})
    
    # 2. Extraire les équipements placés par l'utilisateur
    nodes_placed = []
    for node in drawflow_data.values():
        nodes_placed.append(node.get("name")) # ex: 'router', 'switch', 'pc'
        
    # 3. Vérifier le nombre d'équipements
    from collections import Counter
    counts = Counter(nodes_placed)
    
    for req_node, req_count in expected.get("required_nodes", {}).items():
        if counts[req_node] < req_count:
            msg = f"Il te manque {req_count - counts[req_node]} équipement(s) de type '{req_node}'."
            # Chercher une conséquence spécifique
            if "missing_" + req_node in expected.get("consequences", {}):
                msg = expected["consequences"]["missing_" + req_node]
            raise HTTPException(status_code=400, detail=msg)

    # 4. Vérifier les connexions (simplifié : vérifier si les types de nœuds sont reliés entre eux)
    # Cette logique vérifie que les liens exigés existent bien
    connections = []
    for node_id_1, node in drawflow_data.items():
        for output in node.get("outputs", {}).values():
            for conn in output.get("connections", []):
                target_node_id = conn.get("node")
                if target_node_id in drawflow_data:
                    connections.append((node.get("name"), drawflow_data[target_node_id].get("name")))

    for req_link in expected.get("required_links", []):
        source_type, target_type = req_link
        found = False
        for c in connections:
            if (c[0] == source_type and c[1] == target_type) or (c[1] == source_type and c[0] == target_type):
                found = True
                break
        if not found:
            raise HTTPException(
                status_code=400, 
                detail=f"Topologie incorrecte : Il manque une connexion entre un {source_type} et un {target_type}."
            )

    # 5. Si tout est bon, on valide le nœud
    attempt, validated = tree.record(node_id, ProofKind.MANUAL, 100, True, detail="Architecture validée avec succès")
    return {"success": True, "validated": validated}


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
    new_badges = check_badges(tree)
    return {
        "success": True,
        "id": cursor.lastrowid,
        "updated_at": updated_at,
        "new_badges": new_badges,
        "user_stats": get_user_stats(tree.conn),
    }


STATIC_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)

@app.post("/api/shop/buy")
def buy_item(payload: dict = Body(...), tree: SkillTree = Depends(get_tree)):
    item_id = payload.get("item_id")
    price = payload.get("price")
    
    if not item_id or price is None:
        raise HTTPException(status_code=422, detail="Item et prix requis.")
        
    stats = get_user_stats(tree.conn)
    if stats["coins"] < price:
        raise HTTPException(status_code=400, detail="Pas assez de SkillCoins.")
        
    tree.conn.execute("UPDATE user_stats SET coins = coins - ? WHERE id = 1", (price,))
    tree.conn.execute(
        "INSERT INTO shop_inventory (item_id, quantity) VALUES (?, 1) "
        "ON CONFLICT(item_id) DO UPDATE SET quantity = quantity + 1", (item_id,)
    )
    tree.conn.commit()
    return {"success": True, "new_balance": stats["coins"] - price}

from fastapi.responses import FileResponse
import tempfile, os, qrcode, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors

@app.get("/api/certificate")
def generate_certificate(tree: SkillTree = Depends(get_tree)):
    stats = get_user_stats(tree.conn)
    user_name = os.getenv("CERTIFICATE_NAME", "Étudiant SkillTree")
    cert_id = f"ST-{datetime.now().year}-{random.randint(1000, 9999)}"
    
    # Création du PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Design
    p.setFillColor(colors.HexColor("#0f172a"))
    p.rect(0, 0, 842, 595, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(421, 450, "Certificat de Réussite")
    p.setFont("Helvetica", 20)
    p.drawCentredString(421, 380, f"Décerné à {user_name}")
    p.drawCentredString(421, 340, f"Niveau {stats['current_level']} - {stats['level_name']}")
    p.drawCentredString(421, 300, f"ID: {cert_id}")
    
    # QR Code
    qr = qrcode.make(f"http://localhost:8000/api/verify/{cert_id}")
    qr_img = io.BytesIO()
    qr.save(qr_img, format="PNG")
    qr_img.seek(0)
    from reportlab.lib.utils import ImageReader
    p.drawImage(ImageReader(qr_img), 650, 50, width=120, height=120)
    
    p.save()
    buffer.seek(0)
    
    # Sauvegarde temporaire
    temp_path = os.path.join(tempfile.gettempdir(), f"certificat_{cert_id}.pdf")
    with open(temp_path, "wb") as f:
        f.write(buffer.read())
        
    return FileResponse(temp_path, media_type="application/pdf", filename=f"Certificat_{cert_id}.pdf")