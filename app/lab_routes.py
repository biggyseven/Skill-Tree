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
from fastapi.responses import JSONResponse

from .db import DEFAULT_DB, add_xp, connect
from .lab_schema_v2 import (
    CheckDefinition,
    CheckRequest,
    LabDefinition,
    SubmitRequest,
    Topology,
    model_to_dict,
)

class UTF8JSONResponse(JSONResponse):
    """Réponse JSON avec charset explicite pour les clients Windows/PowerShell."""

    media_type = "application/json; charset=utf-8"


router = APIRouter(tags=["Lab Workspace v2"])
DB_PATH = Path(os.environ.get("SKILLTREE_DB", DEFAULT_DB))
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LABS_V2_DIR = PROJECT_ROOT / "labs_v2"


def _database_connection() -> sqlite3.Connection:
    # Résolu à chaque requête : app.api charge .env après l'import de ce module.
    db_path = Path(os.environ.get("SKILLTREE_DB", str(DEFAULT_DB))).expanduser()
    try:
        return connect(db_path)
    except sqlite3.Error as error:
        raise HTTPException(status_code=503, detail=f"Base SQLite indisponible : {error}")


def _lab_payload_from_definition(
    lab_id: str,
    definition: LabDefinition,
    *,
    schema_version: int = 2,
) -> dict[str, Any]:
    """Normalise la réponse du lab pour les clients du Lab Workspace."""
    return {
        "id": lab_id,
        "schema_version": schema_version,
        "definition": definition,
        "initial_topology": definition.initial_topology,
    }


def _load_lab_file(lab_id: str) -> dict[str, Any] | None:
    """Charge un lab v2 depuis labs_v2/ quand SQLite ne fournit pas de définition exploitable."""
    labs_root = LABS_V2_DIR.resolve()
    lab_path = (labs_root / f"{lab_id}.json").resolve()

    # Empêche un lab_id malveillant de sortir du répertoire labs_v2.
    if lab_path.parent != labs_root:
        return None
    if not lab_path.is_file():
        return None

    try:
        raw_payload = json.loads(lab_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Fichier JSON du lab '{lab_id}' illisible ({lab_path.name}) : {error}",
        )

    if not isinstance(raw_payload, dict):
        raise HTTPException(
            status_code=500,
            detail=f"Définition du lab '{lab_id}' invalide : un objet JSON était attendu.",
        )

    file_lab_id = str(raw_payload.get("id") or lab_id)
    if file_lab_id != lab_id:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Identifiant incohérent dans {lab_path.name} : "
                f"'{file_lab_id}' au lieu de '{lab_id}'."
            ),
        )

    try:
        definition = LabDefinition(**raw_payload)
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Définition v2 invalide dans {lab_path.name} : {error}",
        )

    return _lab_payload_from_definition(
        lab_id,
        definition,
        schema_version=int(raw_payload.get("schema_version") or definition.schema_version or 2),
    )


def _fetch_lab(lab_id: str) -> dict[str, Any]:
    """Cherche d'abord SQLite, puis le fichier JSON local en solution de repli."""
    db_issue: str | None = None
    invalid_db_definition: str | None = None
    conn: sqlite3.Connection | None = None

    try:
        conn = _database_connection()
    except HTTPException as error:
        # Une DB absente/indisponible ne doit pas empêcher un lab fichier de s'ouvrir.
        db_issue = str(error.detail)
    except sqlite3.Error as error:
        db_issue = str(error)

    if conn is not None:
        try:
            columns = {row["name"] for row in conn.execute('PRAGMA table_info("labs")')}
            if columns and "id" in columns:
                row = conn.execute("SELECT * FROM labs WHERE id = ?", (lab_id,)).fetchone()
                if row is not None:
                    data = dict(row)
                    raw_definition = data.get("definition_json")
                    if raw_definition:
                        try:
                            payload = json.loads(raw_definition)
                            definition = LabDefinition(**payload)
                        except (json.JSONDecodeError, TypeError, ValueError) as error:
                            invalid_db_definition = str(error)
                        else:
                            db_payload = _lab_payload_from_definition(
                                str(data["id"]),
                                definition,
                                schema_version=int(data.get("schema_version") or 1),
                            )

                            # Une ancienne ligne SQLite peut contenir une définition valide
                            # mais une topologie vide (aucun noeud ni lien). Dans ce cas,
                            # préférer le JSON du dépôt s'il fournit une vraie topologie.
                            if definition.initial_topology.nodes:
                                return db_payload

                            try:
                                file_payload = _load_lab_file(lab_id)
                            except HTTPException:
                                # Ne pas rendre la ligne SQLite inutilisable si le fichier
                                # de repli existe mais est invalide.
                                file_payload = None

                            if file_payload is not None:
                                file_topology = file_payload.get("initial_topology")
                                if file_topology is not None and getattr(file_topology, "nodes", None):
                                    return file_payload

                            return db_payload
                    else:
                        invalid_db_definition = (
                            "la ligne existe mais le champ definition_json est vide"
                        )
            else:
                db_issue = "la table labs n'existe pas ou ne contient pas de colonne id"
        except sqlite3.Error as error:
            db_issue = str(error)
        finally:
            conn.close()

    file_payload = _load_lab_file(lab_id)
    if file_payload is not None:
        return file_payload

    details = [
        f"Lab '{lab_id}' introuvable : aucune définition exploitable en SQLite",
        f"et le fichier '{LABS_V2_DIR / (lab_id + '.json')}' est absent.",
    ]
    if invalid_db_definition:
        details.append(f"Détail SQLite : {invalid_db_definition}.")
    elif db_issue:
        details.append(f"Détail SQLite : {db_issue}.")
    raise HTTPException(status_code=404, detail=" ".join(details))


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


def _evaluate_lab_check(
    definition: LabDefinition,
    topology: Topology,
) -> dict[str, Any]:
    """Évalue un lab côté serveur et refuse une réussite sans preuve automatique."""
    check = definition.check
    if check.type == "manual_review":
        return {
            "passed": False,
            "score": 0.0,
            "results": [],
            "manual_review_required": True,
            "message": "Ce laboratoire nécessite une validation manuelle.",
        }
    if not check.rules:
        return {
            "passed": False,
            "score": 0.0,
            "results": [],
            "message": "Aucune règle de contrôle n'est configurée ; validation automatique refusée.",
        }
    results = evaluate_rules(topology, check.rules)
    score = sum(1 for result in results if result["passed"]) / len(results)
    return {"passed": score >= check.pass_threshold, "score": round(score, 4), "results": results}


@router.get("/lab/v2/{lab_id}", response_class=UTF8JSONResponse)
def get_lab_v2(lab_id: str) -> dict[str, Any]:
    return _fetch_lab(lab_id)


@router.post("/lab/v2/{lab_id}/check", response_class=UTF8JSONResponse)
def check_lab_v2(lab_id: str, body: CheckRequest) -> dict[str, Any]:
    payload = _fetch_lab(lab_id)
    definition: LabDefinition = payload["definition"]
    return _evaluate_lab_check(definition, body.topology)


@router.post("/lab/v2/{lab_id}/submit", response_class=UTF8JSONResponse)
def submit_lab_v2(lab_id: str, body: SubmitRequest) -> dict[str, Any]:
    payload = _fetch_lab(lab_id)
    definition: LabDefinition = payload["definition"]

    # Le résultat envoyé par le client n'est jamais la source de vérité.
    check_result = _evaluate_lab_check(definition, body.topology)
    passed = bool(check_result["passed"])
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    attempt_id = str(uuid.uuid4())
    snapshot = json.dumps(model_to_dict(body.topology, by_alias=True), ensure_ascii=False)
    result_json = json.dumps(check_result, ensure_ascii=False)

    conn = _database_connection()
    try:
        if "lab_attempts" not in {
            row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }:
            raise HTTPException(status_code=503, detail="La table lab_attempts n'existe pas. Exécute la migration M1.")

        conn.execute("BEGIN IMMEDIATE")
        previous_success = conn.execute(
            "SELECT 1 FROM lab_attempts WHERE lab_id = ? AND passed = 1 LIMIT 1", (lab_id,)
        ).fetchone()
        first_success = passed and previous_success is None
        xp_gained = int(definition.xp_reward) if first_success else 0
        badges_unlocked = list(definition.badges) if first_success else []

        conn.execute(
            "INSERT INTO lab_attempts "
            "(id, lab_id, user_id, started_at, finished_at, passed, config_snapshot, check_result_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (attempt_id, lab_id, None, now, now, int(passed), snapshot, result_json),
        )
        if xp_gained:
            # add_xp committe aussi la tentative ; les deux changements restent atomiques.
            add_xp(conn, xp_gained)
        else:
            conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except sqlite3.IntegrityError as error:
        conn.rollback()
        raise HTTPException(status_code=409, detail=f"Impossible d'enregistrer la tentative : {error}")
    except sqlite3.Error as error:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur SQLite pendant la soumission : {error}")
    finally:
        conn.close()

    return {"ok": True, **check_result, "xp_gained": xp_gained, "badges_unlocked": badges_unlocked}

@router.get("/lab/v2")
def list_labs_v2() -> list[dict[str, Any]]:
    """Catalogue des labs V2 disponibles dans la base SQLite."""
    conn = _database_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, title, level, module, schema_version
            FROM labs
            ORDER BY module, title
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
