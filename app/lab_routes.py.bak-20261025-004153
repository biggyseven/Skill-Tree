"""Routes API du Lab Workspace v2."""
from __future__ import annotations

import ipaddress
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from .db import DEFAULT_DB, connect
from .lab_schema_v2 import (
    CheckDefinition,
    CheckRequest,
    LabDefinition,
    SubmitRequest,
    Topology,
    model_to_dict,
)

router = APIRouter(tags=["Lab Workspace v2"])
DB_PATH = Path(os.environ.get("SKILLTREE_DB", DEFAULT_DB))


def _database_connection() -> sqlite3.Connection:
    # Résolu à chaque requête : app.api charge .env après l'import de ce module.
    db_path = Path(os.environ.get("SKILLTREE_DB", str(DEFAULT_DB))).expanduser()
    try:
        return connect(db_path)
    except sqlite3.Error as error:
        raise HTTPException(status_code=503, detail=f"Base SQLite indisponible : {error}")


def _fetch_lab(lab_id: str) -> dict[str, Any]:
    conn = _database_connection()
    try:
        columns = {row["name"] for row in conn.execute('PRAGMA table_info("labs")')}
        if not columns or "id" not in columns:
            raise HTTPException(status_code=404, detail="Lab introuvable")
        row = conn.execute("SELECT * FROM labs WHERE id = ?", (lab_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Lab introuvable")
        data = dict(row)
        raw_definition = data.get("definition_json")
        if not raw_definition:
            raise HTTPException(
                status_code=409,
                detail="La définition v2 de ce lab n'est pas encore disponible. Exécute la migration M1.",
            )
        try:
            payload = json.loads(raw_definition)
            definition = LabDefinition(**payload)
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise HTTPException(
                status_code=500,
                detail=f"Définition v2 invalide pour le lab {lab_id} : {error}",
            )
        return {
            "id": str(data["id"]),
            "schema_version": int(data.get("schema_version") or 1),
            "definition": definition,
            "initial_topology": definition.initial_topology,
        }
    finally:
        conn.close()


def _path_tokens(path: str) -> list[str | int]:
    """Accepte des chemins tels que config.ports[0].ip."""
    if not path:
        return []
    tokens: list[str | int] = []
    for segment in path.split("."):
        match = re.fullmatch(r"([^\[\]]+)?(?:\[(\d+)\])?", segment)
        if not match:
            raise ValueError(f"syntaxe de chemin invalide près de {segment!r}")
        name, index = match.groups()
        if name:
            tokens.append(name)
        if index is not None:
            tokens.append(int(index))
    return tokens


def _resolve_rule_path(
    topology_data: dict[str, Any], device_name: str, path: str
) -> tuple[bool, Any, str]:
    if device_name:
        nodes = topology_data.get("nodes", [])
        device = next(
            (
                item for item in nodes
                if str(item.get("id", "")) == device_name
                or str(item.get("label", "")) == device_name
                or str((item.get("config") or {}).get("hostname", "")) == device_name
            ),
            None,
        )
        if device is None:
            return False, None, f"périphérique {device_name!r} introuvable"
        current: Any = device
    else:
        current = topology_data

    try:
        tokens = _path_tokens(path)
    except ValueError as error:
        return False, None, str(error)
    if not tokens:
        return False, None, "le chemin est vide"

    for token in tokens:
        if isinstance(token, int):
            if not isinstance(current, list) or token >= len(current):
                return False, None, f"index [{token}] absent ou non applicable"
            current = current[token]
        else:
            if not isinstance(current, dict) or token not in current:
                return False, None, f"champ {token!r} absent"
            current = current[token]
    return True, current, ""


def _contains_network(actual: Any, expected: Any) -> bool:
    try:
        expected_net = ipaddress.ip_network(str(expected), strict=False)
        actual_text = str(actual)
        if "/" in actual_text:
            actual_net = ipaddress.ip_network(actual_text, strict=False)
            if actual_net.version != expected_net.version:
                return False
            return expected_net.subnet_of(actual_net)
        actual_ip = ipaddress.ip_address(actual_text)
        return actual_ip.version == expected_net.version and actual_ip in expected_net
    except (TypeError, ValueError):
        return False


def _apply_operator(actual: Any, operator: str, expected: Any, exists: bool) -> bool:
    if operator == "exists":
        return exists
    if operator == "equals":
        return actual == expected
    if operator == "not_equals":
        return actual != expected
    if operator == "contains":
        if isinstance(actual, (list, tuple, set, dict, str)):
            return expected in actual
        return False
    if operator == "contains_network":
        return _contains_network(actual, expected)
    if operator in {"gt", "lt"}:
        try:
            actual_num = float(actual)
            expected_num = float(expected)
        except (TypeError, ValueError):
            return False
        return actual_num > expected_num if operator == "gt" else actual_num < expected_num
    return False


def evaluate_rules(topology: Topology | dict[str, Any], rules: list[Any]) -> list[dict[str, Any]]:
    """Évalue chaque règle et retourne un résultat explicite par règle."""
    topology_data = (
        model_to_dict(topology, by_alias=True)
        if hasattr(topology, "model_dump") or hasattr(topology, "dict")
        else topology
    )
    results: list[dict[str, Any]] = []
    for index, raw_rule in enumerate(rules):
        rule = model_to_dict(raw_rule) if hasattr(raw_rule, "model_dump") or hasattr(raw_rule, "dict") else dict(raw_rule)
        rule_id = str(rule.get("id") or f"rule-{index + 1}")
        operator = str(rule.get("operator") or "")
        device_name = str(rule.get("device") or "")
        path = str(rule.get("path") or "")
        expected = rule.get("expected")
        exists, actual, error = _resolve_rule_path(topology_data, device_name, path)
        if not exists:
            results.append({
                "rule_id": rule_id,
                "passed": False,
                "message": f"Chemin invalide ({device_name or 'topologie'}.{path}) : {error}.",
            })
            continue
        if operator not in {
            "equals", "not_equals", "contains", "contains_network",
            "exists", "gt", "lt",
        }:
            results.append({
                "rule_id": rule_id,
                "passed": False,
                "message": f"Opérateur non pris en charge : {operator!r}.",
            })
            continue
        passed = _apply_operator(actual, operator, expected, exists)
        if passed:
            message = str(rule.get("description") or f"Règle {rule_id} satisfaite.")
        else:
            message = (
                f"Règle {rule_id} non satisfaite : opérateur {operator}, "
                f"valeur obtenue {actual!r}, valeur attendue {expected!r}."
            )
        results.append({"rule_id": rule_id, "passed": passed, "message": message})
    return results


@router.get("/lab/v2/{lab_id}")
def get_lab_v2(lab_id: str) -> dict[str, Any]:
    return _fetch_lab(lab_id)


@router.post("/lab/v2/{lab_id}/check")
def check_lab_v2(lab_id: str, body: CheckRequest) -> dict[str, Any]:
    payload = _fetch_lab(lab_id)
    definition: LabDefinition = payload["definition"]
    rules = definition.check.rules
    results = evaluate_rules(body.topology, rules)
    score = (
        sum(1 for result in results if result["passed"]) / len(results)
        if results else 1.0
    )
    passed = score >= definition.check.pass_threshold
    return {"passed": passed, "score": round(score, 4), "results": results}


@router.post("/lab/v2/{lab_id}/submit")
def submit_lab_v2(lab_id: str, body: SubmitRequest) -> dict[str, Any]:
    payload = _fetch_lab(lab_id)
    definition: LabDefinition = payload["definition"]
    passed = bool(body.check_result.get("passed", False))
    xp_gained = int(definition.xp_reward) if passed else 0
    badges_unlocked = list(definition.badges) if passed else []
    now = datetime.now(timezone.utc).isoformat()
    attempt_id = str(uuid.uuid4())
    snapshot = json.dumps(
        model_to_dict(body.topology, by_alias=True),
        ensure_ascii=False,
    )
    result_json = json.dumps(body.check_result, ensure_ascii=False)

    conn = _database_connection()
    try:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "lab_attempts" not in tables:
            raise HTTPException(
                status_code=503,
                detail="La table lab_attempts n'existe pas. Exécute la migration M1.",
            )
        conn.execute(
            "INSERT INTO lab_attempts "
            "(id, lab_id, user_id, started_at, finished_at, passed, config_snapshot, check_result_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                attempt_id, lab_id, None, now, now, int(passed), snapshot, result_json,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as error:
        conn.rollback()
        raise HTTPException(status_code=409, detail=f"Impossible d'enregistrer la tentative : {error}")
    except sqlite3.Error as error:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur SQLite pendant la soumission : {error}")
    finally:
        conn.close()

    return {"ok": True, "xp_gained": xp_gained, "badges_unlocked": badges_unlocked}
