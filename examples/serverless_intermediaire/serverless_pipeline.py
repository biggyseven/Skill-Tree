"""Simulation pédagogique d'un pipeline serverless pour Skill-Tree.

Le script utilise une base SQLite locale dédiée. Il ne se connecte pas à
l'application réelle et ne touche jamais au fichier skilltree.db.
"""
from __future__ import annotations

import json
import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).with_name("skilltree_serverless_demo.db")


class PermanentProcessingError(Exception):
    """Erreur qui ne sera pas résolue par une nouvelle tentative."""


@contextmanager
def open_db(db_path: str | Path = DB_PATH) -> Iterator[sqlite3.Connection]:
    """Ouvre puis ferme une connexion SQLite, même en cas d'exception."""
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def now_utc() -> str:
    """Renvoie un horodatage ISO 8601 en UTC."""
    return datetime.now(timezone.utc).isoformat()


def init_db(db_path: str | Path = DB_PATH) -> None:
    """Crée les tables du TP dans la base dédiée à la démonstration."""
    with open_db(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS lab_attempts (
                attempt_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lab_id TEXT NOT NULL,
                passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
                authorized_xp INTEGER NOT NULL CHECK (authorized_xp BETWEEN 0 AND 1000),
                xp_awarded INTEGER NOT NULL DEFAULT 0 CHECK (xp_awarded >= 0),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS outbox_events (
                event_id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'published')),
                created_at TEXT NOT NULL,
                published_at TEXT
            );
            CREATE TABLE IF NOT EXISTS queue_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'retry', 'processed', 'dead_letter')),
                attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
                available_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                processed_at TEXT,
                last_error TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_queue_ready
                ON queue_messages(status, available_at, created_at);
            CREATE TABLE IF NOT EXISTS processed_events (
                event_id TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS xp_rewards (
                user_id TEXT NOT NULL,
                lab_id TEXT NOT NULL,
                xp_awarded INTEGER NOT NULL CHECK (xp_awarded >= 0),
                source_attempt_id TEXT NOT NULL UNIQUE,
                awarded_at TEXT NOT NULL,
                PRIMARY KEY (user_id, lab_id)
            );
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                xp_total INTEGER NOT NULL DEFAULT 0 CHECK (xp_total >= 0)
            );
        """)


def validate_submission(
    attempt_id: str, user_id: str, lab_id: str, passed: bool, xp_reward: int
) -> None:
    """Valide les données calculées par le backend avant leur stockage."""
    for name, value in (("attempt_id", attempt_id), ("user_id", user_id), ("lab_id", lab_id)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} doit être une chaîne non vide.")
    if not isinstance(passed, bool):
        raise ValueError("passed doit être calculé côté serveur et être booléen.")
    if isinstance(xp_reward, bool) or not isinstance(xp_reward, int):
        raise ValueError("xp_reward doit être un entier.")
    if not 0 <= xp_reward <= 1000:
        raise ValueError("xp_reward doit être compris entre 0 et 1000.")


def submit_lab_attempt(
    attempt_id: str,
    user_id: str,
    lab_id: str,
    passed: bool,
    xp_reward: int,
    db_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    """Enregistre tentative + événement outbox dans une transaction atomique.

    passed et xp_reward doivent être calculés par le backend après vérification
    du lab ; le navigateur ne doit pas pouvoir choisir ces valeurs.
    """
    validate_submission(attempt_id, user_id, lab_id, passed, xp_reward)
    attempt_id, user_id, lab_id = attempt_id.strip(), user_id.strip(), lab_id.strip()
    event_id = f"lab.submitted:{attempt_id}"
    created_at = now_utc()
    payload = {
        "event_id": event_id,
        "event_type": "lab.submitted",
        "event_version": 1,
        "occurred_at": created_at,
        "data": {
            "attempt_id": attempt_id,
            "user_id": user_id,
            "lab_id": lab_id,
            "passed": passed,
            "xp_reward": xp_reward,
        },
    }

    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            existing = conn.execute(
                "SELECT user_id, lab_id, passed, authorized_xp FROM lab_attempts WHERE attempt_id = ?",
                (attempt_id,),
            ).fetchone()
            if existing is not None:
                same = (
                    existing["user_id"] == user_id
                    and existing["lab_id"] == lab_id
                    and existing["passed"] == int(passed)
                    and existing["authorized_xp"] == xp_reward
                )
                conn.rollback()
                return (
                    {"status": "duplicate_submission", "attempt_id": attempt_id, "event_id": event_id}
                    if same else {"status": "id_conflict", "message": "attempt_id existe avec d'autres données."}
                )

            conn.execute(
                """INSERT INTO lab_attempts
                (attempt_id, user_id, lab_id, passed, authorized_xp, xp_awarded, created_at)
                VALUES (?, ?, ?, ?, ?, 0, ?)""",
                (attempt_id, user_id, lab_id, int(passed), xp_reward, created_at),
            )
            conn.execute(
                "INSERT INTO outbox_events(event_id, payload_json, status, created_at) VALUES (?, ?, 'pending', ?)",
                (event_id, json.dumps(payload, separators=(",", ":")), created_at),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    return {"status": "accepted", "attempt_id": attempt_id, "event_id": event_id}


def publish_outbox(db_path: str | Path = DB_PATH, limit: int = 100) -> dict[str, int | str]:
    """Copie les événements outbox vers la file SQLite simulée.

    Ici la file et l'outbox partagent SQLite. Un vrai broker externe ne partage
    normalement pas cette transaction : le relais réel doit donc gérer les
    reprises de publication et tolérer les doublons.
    """
    if limit < 1:
        raise ValueError("limit doit être supérieur à zéro.")
    published = 0
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            events = conn.execute(
                "SELECT event_id, payload_json FROM outbox_events WHERE status = 'pending' ORDER BY created_at LIMIT ?",
                (limit,),
            ).fetchall()
            for event in events:
                ts = now_utc()
                conn.execute(
                    """INSERT INTO queue_messages
                    (event_id, payload_json, status, attempts, available_at, created_at)
                    VALUES (?, ?, 'pending', 0, ?, ?)""",
                    (event["event_id"], event["payload_json"], ts, ts),
                )
                conn.execute(
                    "UPDATE outbox_events SET status = 'published', published_at = ? WHERE event_id = ? AND status = 'pending'",
                    (ts, event["event_id"]),
                )
                published += 1
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return {"status": "ok", "published": published}


def simulate_redelivery(event_id: str, db_path: str | Path = DB_PATH) -> dict[str, Any]:
    """Crée un deuxième message portant le même événement pour tester les doublons."""
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            source = conn.execute(
                "SELECT payload_json FROM outbox_events WHERE event_id = ?", (event_id,)
            ).fetchone()
            if source is None:
                conn.rollback()
                return {"status": "not_found", "event_id": event_id}
            ts = now_utc()
            cursor = conn.execute(
                """INSERT INTO queue_messages
                (event_id, payload_json, status, attempts, available_at, created_at)
                VALUES (?, ?, 'pending', 0, ?, ?)""",
                (event_id, source["payload_json"], ts, ts),
            )
            message_id = cursor.lastrowid
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return {"status": "redelivery_created", "event_id": event_id, "message_id": message_id}


def _read_event(payload: Any, expected_event_id: str) -> dict[str, Any]:
    """Valide le contrat d'événement et retourne son champ data."""
    if not isinstance(payload, dict):
        raise PermanentProcessingError("Le payload doit être un objet JSON.")
    if payload.get("event_id") != expected_event_id:
        raise PermanentProcessingError("event_id ne correspond pas au message.")
    if payload.get("event_type") != "lab.submitted" or payload.get("event_version") != 1:
        raise PermanentProcessingError("Type ou version d'événement non pris en charge.")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise PermanentProcessingError("Le champ data doit être un objet.")
    for name in ("attempt_id", "user_id", "lab_id"):
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise PermanentProcessingError(f"Champ invalide : {name}.")
    if not isinstance(data.get("passed"), bool):
        raise PermanentProcessingError("passed doit être un booléen.")
    xp = data.get("xp_reward")
    if isinstance(xp, bool) or not isinstance(xp, int) or not 0 <= xp <= 1000:
        raise PermanentProcessingError("xp_reward est invalide.")
    return data


def _record_failure(
    message_id: int, attempt_no: int, error: Exception, db_path: str | Path,
    max_attempts: int, permanent: bool,
) -> dict[str, Any]:
    """Enregistre un délai de reprise ou place le message en échec définitif."""
    dead = permanent or attempt_no >= max_attempts
    status = "dead_letter" if dead else "retry"
    if dead:
        available_at = now_utc()
    else:
        seconds = min(300.0, 2.0 ** (attempt_no - 1)) * random.uniform(0.8, 1.2)
        available_at = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
    # En production, expurger les secrets des erreurs avant de les journaliser.
    safe_error = f"{type(error).__name__}: {str(error)[:300]}"
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute(
                "UPDATE queue_messages SET status = ?, attempts = ?, available_at = ?, last_error = ? WHERE message_id = ? AND status != 'processed'",
                (status, attempt_no, available_at, safe_error, message_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return {"status": status, "message_id": message_id, "attempts": attempt_no, "error": safe_error}


def consume_message(
    message_id: int,
    db_path: str | Path = DB_PATH,
    max_attempts: int = 3,
    simulate_failure: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Traite un message ; les écritures métier et le statut sont atomiques.

    force=True est uniquement destiné aux tests locaux pour ne pas attendre
    le délai de reprise. Un worker réel doit respecter available_at.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts doit être au moins égal à 1.")
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            message = conn.execute(
                "SELECT * FROM queue_messages WHERE message_id = ?", (message_id,)
            ).fetchone()
            if message is None:
                conn.rollback()
                return {"status": "not_found", "message_id": message_id}
            event_id = message["event_id"]
            if message["status"] == "processed":
                conn.rollback()
                return {"status": "already_processed", "message_id": message_id, "xp_gained": 0}
            if message["status"] == "dead_letter":
                conn.rollback()
                return {"status": "dead_letter", "message_id": message_id, "event_id": event_id}
            if not force and message["available_at"] > now_utc():
                conn.rollback()
                return {"status": "not_due", "message_id": message_id, "event_id": event_id}

            attempt_no = message["attempts"] + 1
            try:
                try:
                    payload = json.loads(message["payload_json"])
                except (json.JSONDecodeError, TypeError) as exc:
                    raise PermanentProcessingError("Le payload JSON est illisible.") from exc
                data = _read_event(payload, event_id)
                source = conn.execute(
                    "SELECT user_id, lab_id, passed, authorized_xp FROM lab_attempts WHERE attempt_id = ?",
                    (data["attempt_id"],),
                ).fetchone()
                if source is None:
                    raise PermanentProcessingError("La tentative source est introuvable.")
                if (source["user_id"] != data["user_id"] or source["lab_id"] != data["lab_id"]
                        or source["passed"] != int(data["passed"]) or source["authorized_xp"] != data["xp_reward"]):
                    raise PermanentProcessingError("L'événement ne correspond pas à la tentative source.")
                if simulate_failure:
                    raise RuntimeError("Panne temporaire simulée par le TP.")

                if conn.execute("SELECT 1 FROM processed_events WHERE event_id = ?", (event_id,)).fetchone():
                    conn.execute(
                        "UPDATE queue_messages SET status = 'processed', attempts = ?, processed_at = ?, last_error = NULL WHERE message_id = ?",
                        (attempt_no, now_utc(), message_id),
                    )
                    conn.commit()
                    return {"status": "duplicate_ignored", "event_id": event_id, "message_id": message_id, "xp_gained": 0}

                gained = 0
                outcome = "processed_no_reward"
                if data["passed"]:
                    reward = conn.execute(
                        "SELECT 1 FROM xp_rewards WHERE user_id = ? AND lab_id = ?",
                        (data["user_id"], data["lab_id"]),
                    ).fetchone()
                    if reward is None:
                        gained = data["xp_reward"]
                        conn.execute(
                            "INSERT INTO xp_rewards(user_id, lab_id, xp_awarded, source_attempt_id, awarded_at) VALUES (?, ?, ?, ?, ?)",
                            (data["user_id"], data["lab_id"], gained, data["attempt_id"], now_utc()),
                        )
                        conn.execute(
                            "INSERT INTO user_stats(user_id, xp_total) VALUES (?, 0) ON CONFLICT(user_id) DO NOTHING",
                            (data["user_id"],),
                        )
                        conn.execute("UPDATE user_stats SET xp_total = xp_total + ? WHERE user_id = ?", (gained, data["user_id"]))
                        conn.execute("UPDATE lab_attempts SET xp_awarded = ? WHERE attempt_id = ?", (gained, data["attempt_id"]))
                        outcome = "rewarded"
                    else:
                        outcome = "already_rewarded"

                conn.execute("INSERT INTO processed_events(event_id, processed_at) VALUES (?, ?)", (event_id, now_utc()))
                conn.execute(
                    "UPDATE queue_messages SET status = 'processed', attempts = ?, processed_at = ?, last_error = NULL WHERE message_id = ?",
                    (attempt_no, now_utc(), message_id),
                )
                conn.commit()
                return {
                    "status": outcome, "event_id": event_id, "message_id": message_id,
                    "user_id": data["user_id"], "lab_id": data["lab_id"],
                    "xp_gained": gained, "attempts": attempt_no,
                }
            except PermanentProcessingError as exc:
                conn.rollback()
                return _record_failure(message_id, attempt_no, exc, db_path, max_attempts, permanent=True)
            except Exception as exc:
                conn.rollback()
                return _record_failure(message_id, attempt_no, exc, db_path, max_attempts, permanent=False)
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise


def process_pending(db_path: str | Path = DB_PATH, limit: int = 100) -> list[dict[str, Any]]:
    """Traite un lot de messages dont le délai de reprise est écoulé."""
    if limit < 1:
        raise ValueError("limit doit être supérieur à zéro.")
    with open_db(db_path) as conn:
        ids = conn.execute(
            "SELECT message_id FROM queue_messages WHERE status IN ('pending', 'retry') AND available_at <= ? ORDER BY created_at, message_id LIMIT ?",
            (now_utc(), limit),
        ).fetchall()
    return [consume_message(row["message_id"], db_path) for row in ids]


def get_user_xp(user_id: str, db_path: str | Path = DB_PATH) -> int:
    with open_db(db_path) as conn:
        row = conn.execute("SELECT xp_total FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
    return int(row["xp_total"]) if row else 0


def reset_demo_data(db_path: str | Path = DB_PATH) -> None:
    """Efface uniquement les tables du TP dans la base fournie explicitement."""
    tables = ("processed_events", "xp_rewards", "user_stats", "queue_messages", "outbox_events", "lab_attempts")
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            for table in tables:  # Liste fixe, non fournie par l'utilisateur.
                conn.execute(f"DELETE FROM {table}")
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def demo() -> None:
    """Exécute un scénario local simple sur la base de démonstration."""
    init_db(DB_PATH)
    reset_demo_data(DB_PATH)
    result = submit_lab_attempt("attempt-001", "user-42", "ospf-3-routers", True, 100)
    print("1. Soumission :", result)
    print("2. Publication outbox :", publish_outbox())
    with open_db() as conn:
        message = conn.execute("SELECT message_id FROM queue_messages WHERE event_id = ?", (result["event_id"],)).fetchone()
    message_id = int(message["message_id"])
    print("3. Erreur temporaire :", consume_message(message_id, simulate_failure=True))
    print("4. Reprise forcée pour le TP :", consume_message(message_id, force=True))
    duplicate = simulate_redelivery(result["event_id"])
    print("5. Livraison répétée :", consume_message(duplicate["message_id"], force=True))
    second = submit_lab_attempt("attempt-002", "user-42", "ospf-3-routers", True, 100)
    publish_outbox()
    with open_db() as conn:
        second_message = conn.execute("SELECT message_id FROM queue_messages WHERE event_id = ?", (second["event_id"],)).fetchone()
    print("6. Nouvelle réussite du même lab :", consume_message(int(second_message["message_id"]), force=True))
    print("XP final :", get_user_xp("user-42"), "(attendu : 100)")


if __name__ == "__main__":
    demo()
