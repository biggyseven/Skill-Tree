"""Badges spécifiques à la War Room ITSM.

Le déblocage est calculé à partir de l'historique conservé dans les tables
tickets et ticket_actions ; aucune table ni dépendance supplémentaire n'est requise.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any


WAR_BADGE_DEFINITIONS: tuple[dict[str, str], ...] = (
    {"id": "first_blood", "name": "First Blood", "icon": "🩸", "description": "Résoudre ton premier ticket War Room."},
    {"id": "speedrunner", "name": "Speedrunner", "icon": "⚡", "description": "Résoudre un ticket en moins de 5 minutes."},
    {"id": "sla_master", "name": "SLA Master", "icon": "🎯", "description": "Réussir 10 résolutions dans le délai SLA."},
    {"id": "night_owl", "name": "Night Owl", "icon": "🌙", "description": "Résoudre un ticket entre 22 h et 6 h."},
    {"id": "comeback_kid", "name": "Comeback Kid", "icon": "🔁", "description": "Réussir un ticket rejoué après un échec."},
    {"id": "root_cause_expert", "name": "Root Cause Expert", "icon": "🧠", "description": "Valider 5 post-mortem complets."},
    {"id": "stress_test", "name": "Stress Test", "icon": "🔥", "description": "Résoudre 3 tickets dans une fenêtre de 30 minutes."},
    {"id": "noc_veteran", "name": "NOC Veteran", "icon": "🏆", "description": "Résoudre 50 tickets au total."},
)


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def _duration_seconds(ticket: dict[str, Any]) -> float | None:
    data = _json_object(ticket.get("resolution_data"))
    opened = _parse_time(ticket.get("opened_at"))
    ended = _parse_time(ticket.get("resolved_at"))
    if not opened or not ended:
        return None
    paused = max(0.0, float(data.get("paused_total_seconds") or 0))
    return max(0.0, (ended - opened).total_seconds() - paused)


def _sla_met(ticket: dict[str, Any]) -> bool:
    if ticket.get("status") != "resolved":
        return False
    data = _json_object(ticket.get("resolution_data"))
    if isinstance(data.get("sla_met"), bool):
        return data["sla_met"]
    deadline = _parse_time(ticket.get("sla_deadline"))
    resolved = _parse_time(ticket.get("resolved_at"))
    return resolved is not None and (deadline is None or resolved <= deadline)


def build_war_badges(conn: Any) -> list[dict[str, Any]]:
    """Retourne les 8 badges, avec leur statut de déblocage calculé."""
    tickets = [dict(row) for row in conn.execute("SELECT * FROM tickets ORDER BY opened_at ASC").fetchall()]
    resolved = sorted(
        [ticket for ticket in tickets if ticket.get("status") == "resolved" and _parse_time(ticket.get("resolved_at"))],
        key=lambda ticket: _parse_time(ticket.get("resolved_at")) or datetime.min.replace(tzinfo=timezone.utc),
    )
    durations = {str(ticket.get("id")): _duration_seconds(ticket) for ticket in resolved}
    sla_successes = sum(1 for ticket in resolved if _sla_met(ticket))
    night_owl = False
    try:
        local_zone = ZoneInfo(os.environ.get("SKILLTREE_TIMEZONE", "Africa/Douala"))
    except (ZoneInfoNotFoundError, ValueError):
        local_zone = timezone.utc
    for ticket in resolved:
        ended = _parse_time(ticket.get("resolved_at"))
        if ended:
            hour = ended.astimezone(local_zone).hour
            if hour >= 22 or hour < 6:
                night_owl = True
                break

    resolved_ids = {str(ticket.get("id")) for ticket in resolved}
    tickets_by_id = {str(ticket.get("id")): ticket for ticket in tickets}
    comeback_kid = False
    try:
        replay_actions = conn.execute(
            "SELECT ticket_id, payload FROM ticket_actions WHERE action_type = 'opened' ORDER BY at ASC"
        ).fetchall()
    except Exception:
        replay_actions = []
    for action in replay_actions:
        payload = _json_object(action["payload"])
        replayed_id = str(payload.get("replayed_ticket_id") or "")
        new_id = str(action["ticket_id"])
        if payload.get("source") != "replay" or not replayed_id or new_id not in resolved_ids:
            continue
        prior = tickets_by_id.get(replayed_id)
        if prior and prior.get("status") == "failed":
            comeback_kid = True
            break

    postmortems = 0
    for ticket in resolved:
        data = _json_object(ticket.get("resolution_data"))
        pm = data.get("post_mortem")
        if isinstance(pm, dict) and all(str(pm.get(key) or "").strip() for key in ("root_cause", "impact", "corrective_action")):
            postmortems += 1

    stress_test = False
    for start in range(max(0, len(resolved) - 2)):
        group = resolved[start:start + 3]
        if len(group) != 3:
            continue
        times = [_parse_time(ticket.get("resolved_at")) for ticket in group]
        if all(times) and (times[-1] - times[0]).total_seconds() < 1800:
            stress_test = True
            break

    unlocked = {
        "first_blood": len(resolved) >= 1,
        "speedrunner": any(value is not None and value < 300 for value in durations.values()),
        "sla_master": sla_successes >= 10,
        "night_owl": night_owl,
        "comeback_kid": comeback_kid,
        "root_cause_expert": postmortems >= 5,
        "stress_test": stress_test,
        "noc_veteran": len(resolved) >= 50,
    }
    return [
        {**definition, "unlocked": bool(unlocked.get(definition["id"], False))}
        for definition in WAR_BADGE_DEFINITIONS
    ]
