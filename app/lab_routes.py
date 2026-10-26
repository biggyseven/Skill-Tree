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

from .db import DEFAULT_DB, add_xp, connect, touch_daily_streak
from .domain import ProofKind, Status
from .engine import BADGE_DEFINITIONS, DomainError, SkillTree
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

# Les scénarios v2 sont parfois nommés selon le scénario plutôt que l'identifiant du cours.
# Ces alias relient uniquement les cours dont le niveau et le contenu correspondent réellement.
LAB_FILE_ALIASES = {
    "ipv4-debutant": "ipv4",
    "vlan-debutant": "vlan-trunk",
    "vlan-intermediaire": "inter-vlan",
    "ospf-debutant": "ospf-3-routers",
    "nat-intermediaire": "dhcp-nat",
}

# Métadonnées des badges spécifiques aux scénarios v2. Les identifiants canoniques
# (first-blood, war-machine, architect, flawless) viennent de app.engine.
LAB_BADGE_DEFINITIONS: dict[str, dict[str, str]] = {
    "dhcp-nat-master": {
        "nom": "Maître DHCP/NAT",
        "description": "Réussir le laboratoire « DHCP et préparation NAT ».",
        "icone": "🌐",
    },
    "inter-vlan": {
        "nom": "Spécialiste inter-VLAN",
        "description": "Réussir le laboratoire de routage inter-VLAN.",
        "icone": "🔀",
    },
    "vlan-basics": {
        "nom": "Fondations VLAN",
        "description": "Réussir le laboratoire VLAN 10 et trunk entre deux switches.",
        "icone": "🔗",
    },
}
LAB_BADGE_ID_ALIASES = {
    "first_blood": "first-blood",
    "war_machine": "war-machine",
}


def _resolve_badge_definition(badge_id: Any) -> tuple[str, dict[str, str]] | None:
    """Résout les anciens alias et les badges v2 sans annoncer de badge inconnu."""
    if not isinstance(badge_id, str) or not badge_id.strip():
        return None
    canonical_id = LAB_BADGE_ID_ALIASES.get(badge_id, badge_id)
    definition = BADGE_DEFINITIONS.get(canonical_id) or LAB_BADGE_DEFINITIONS.get(canonical_id)
    if definition is None:
        return None
    return canonical_id, definition


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
    """Charge un lab v2, en résolvant les alias de cours sans perdre son identifiant."""
    source_lab_id = LAB_FILE_ALIASES.get(lab_id, lab_id)
    labs_root = LABS_V2_DIR.resolve()
    lab_path = (labs_root / f"{source_lab_id}.json").resolve()

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

    file_lab_id = str(raw_payload.get("id") or source_lab_id)
    if file_lab_id != source_lab_id:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Identifiant incohérent dans {lab_path.name} : "
                f"'{file_lab_id}' au lieu de '{source_lab_id}'."
            ),
        )

    try:
        definition = LabDefinition(**raw_payload)
        if lab_id != source_lab_id:
            # Garder l'identifiant du cours pour l'historique et la progression,
            # même si le JSON de scénario possède son propre identifiant canonique.
            if hasattr(definition, "model_copy"):
                definition = definition.model_copy(update={"id": lab_id})
            else:
                definition = definition.copy(update={"id": lab_id})
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
    """Charge d'abord un scénario v2 explicite, puis SQLite et les replis historiques."""
    # Un scénario pédagogique complet prévaut sur une ancienne ligne SQLite de compatibilité
    # (souvent migrée avec une topologie vide et une règle temporaire « ok »).
    if lab_id in LAB_FILE_ALIASES:
        curated_payload = _load_lab_file(lab_id)
        if curated_payload is not None:
            return curated_payload

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

                            # Une définition de compatibilité avec une topologie vide ne constitue
                            # pas un véritable lab V2 noté. Le tableau de bord la traitera comme bac à sable.
                            db_payload["sandbox"] = True
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

    # Ne jamais remplacer silencieusement un laboratoire de cours manquant par
    # une topologie vide : cela donne l'impression que le scénario a été chargé.
    # L'atelier libre s'ouvre séparément via /lab.html sans paramètre id.
    details = [
        f"Lab '{lab_id}' introuvable : aucune définition exploitable en SQLite "
        f"et aucun fichier JSON correspondant à '{lab_id}.json' dans '{LABS_V2_DIR}'.",
    ]
    if invalid_db_definition:
        details.append(f"Détail SQLite : {invalid_db_definition}.")
    elif db_issue:
        details.append(f"Détail SQLite : {db_issue}.")
    raise HTTPException(status_code=404, detail=" ".join(details))


def _ensure_lab_catalog_row(
    conn: sqlite3.Connection,
    lab_id: str,
    definition: LabDefinition,
) -> None:
    """Crée l'entrée minimale du catalogue si un lab JSON doit être soumis pour la première fois."""
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if "labs" not in tables:
        raise HTTPException(
            status_code=503,
            detail="La table labs n'existe pas. Exécute la migration M1 avant de soumettre ce laboratoire.",
        )

    columns = {
        row["name"] for row in conn.execute('PRAGMA table_info("labs")')
    }
    if "id" not in columns:
        raise HTTPException(status_code=503, detail="La table labs ne contient pas de colonne id.")

    existing = conn.execute("SELECT 1 FROM labs WHERE id = ?", (lab_id,)).fetchone()
    if existing:
        return

    definition_payload = model_to_dict(definition, by_alias=True)
    definition_payload["id"] = lab_id
    row_values: dict[str, Any] = {
        "id": lab_id,
        "title": definition.title or lab_id,
        "level": definition.level,
        "module": definition.module,
        "prompt": definition.prompt,
        "objectives": json.dumps(definition.objectives, ensure_ascii=False),
        "hints": json.dumps(definition.hints, ensure_ascii=False),
        "duration_min": definition.duration_min,
        "difficulty": definition.difficulty,
        "xp_reward": definition.xp_reward,
        "badges": json.dumps(definition.badges, ensure_ascii=False),
        "schema_version": definition.schema_version,
        "definition_json": json.dumps(definition_payload, ensure_ascii=False),
        "migration_note": "Catalogue synchronisé depuis la définition labs_v2 lors de la première soumission.",
    }
    available = [(name, value) for name, value in row_values.items() if name in columns]
    quoted_columns = ", ".join('"' + name.replace('"', '""') + '"' for name, _ in available)
    placeholders = ", ".join("?" for _ in available)
    conn.execute(
        f"INSERT INTO labs ({quoted_columns}) VALUES ({placeholders})",
        tuple(value for _, value in available),
    )


def seed_lab_v2_catalog(conn: sqlite3.Connection) -> int:
    """Insère sans écraser les scénarios v2 distribués avec le code source.

    La base SQLite est volontairement ignorée par Git : un déploiement neuf doit
    reconstruire le catalogue depuis les fichiers versionnés, pas depuis la base
    personnelle d'un développeur.
    """
    inserted = 0
    for lab_path in sorted(LABS_V2_DIR.glob("*.json")):
        payload = _load_lab_file(lab_path.stem)
        if payload is None:
            continue
        existed = conn.execute(
            "SELECT 1 FROM labs WHERE id = ?", (lab_path.stem,)
        ).fetchone()
        _ensure_lab_catalog_row(conn, lab_path.stem, payload["definition"])
        if existed is None:
            inserted += 1
    conn.commit()
    return inserted


def _course_lab_context(conn: sqlite3.Connection, lab_id: str) -> dict[str, Any] | None:
    """Retourne le lien vers une exigence de lab du parcours, si les schémas le permettent."""
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if not {"nodes", "edges", "requirements", "attempts"}.issubset(tables):
        return None

    try:
        tree = SkillTree(conn)
        node = tree.node(lab_id)
        requirement = node.requirement(ProofKind.LAB)
        if requirement is None:
            return None
        status = tree.status(lab_id)
        validated_ids = tree.validated_ids()
        missing_prerequisites = [
            prerequisite for prerequisite in node.prereqs
            if prerequisite not in validated_ids
        ]
        return {
            "min_score": int(requirement.min_score),
            "unlocked": status is not Status.LOCKED,
            "missing_prerequisites": missing_prerequisites,
        }
    except (sqlite3.Error, DomainError, KeyError, TypeError, ValueError):
        # Un lab autonome reste utilisable même si aucune correspondance de parcours
        # n'existe ou si la base ne possède pas le schéma complet du skill tree.
        return None


def _course_lock_message(course_context: dict[str, Any]) -> str:
    """Explique pourquoi un scénario du parcours n'est pas encore accessible."""
    missing = [str(item) for item in course_context.get("missing_prerequisites", [])]
    if missing:
        return (
            "Ce laboratoire est verrouillé par le parcours. Validez d'abord les "
            f"prérequis suivants : {', '.join(missing)}."
        )
    return (
        "Ce laboratoire est verrouillé par le parcours. Validez ses prérequis "
        "avant de continuer."
    )


def _locked_course_check(course_context: dict[str, Any]) -> dict[str, Any]:
    message = _course_lock_message(course_context)
    return {
        "passed": False,
        "score": 0.0,
        "locked": True,
        "results": [{
            "rule_id": "course-locked",
            "passed": False,
            "message": message,
        }],
        "message": message,
    }


def _enforce_course_lab_score(
    result: dict[str, Any],
    course_context: dict[str, Any] | None,
) -> dict[str, Any]:
    """Aligne le succès du lab sur le seuil défini pour valider le cours."""
    if course_context is None:
        return result

    try:
        score_percent = round(max(0.0, min(1.0, float(result.get("score", 0)))) * 100)
    except (TypeError, ValueError):
        score_percent = 0

    minimum = int(course_context["min_score"])
    if score_percent < minimum and result.get("passed"):
        result = dict(result)
        result["passed"] = False
        results = list(result.get("results") or [])
        results.append({
            "rule_id": "course-min-score",
            "passed": False,
            "message": (
                f"Le parcours exige au moins {minimum}/100 pour valider ce lab ; "
                f"score obtenu : {score_percent}/100."
            ),
        })
        result["results"] = results
        result["message"] = results[-1]["message"]
    return result


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
    # OSPF stocke les déclarations sous forme de liste d'objets {area, network}.
    # Autoriser l'opérateur sur cette liste, tout en conservant son usage sur une IP
    # ou un préfixe isolé pour les autres laboratoires.
    if isinstance(actual, (list, tuple)):
        return any(
            _contains_network(item.get("network") if isinstance(item, dict) else item, expected)
            for item in actual
        )

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
    payload = _fetch_lab(lab_id)
    if payload.get("sandbox"):
        return payload

    conn: sqlite3.Connection | None = None
    try:
        conn = _database_connection()
        course_context = _course_lab_context(conn, lab_id)
    except HTTPException:
        # La définition JSON reste consultable si SQLite est temporairement indisponible.
        return payload
    finally:
        if conn is not None:
            conn.close()

    if course_context is not None:
        payload = dict(payload)
        payload["course_locked"] = not course_context["unlocked"]
        if not course_context["unlocked"]:
            payload["course_lock_message"] = _course_lock_message(course_context)
    return payload


@router.post("/lab/v2/{lab_id}/check", response_class=UTF8JSONResponse)
def check_lab_v2(lab_id: str, body: CheckRequest) -> dict[str, Any]:
    payload = _fetch_lab(lab_id)
    if payload.get("sandbox"):
        return {
            "passed": False,
            "score": 0.0,
            "sandbox": True,
            "manual_review_required": True,
            "results": [{
                "rule_id": "sandbox",
                "passed": False,
                "message": "Bac à sable : ce workspace n'a pas de règles de validation et ne peut pas valider un cours.",
            }],
        }
    definition: LabDefinition = payload["definition"]
    result = _evaluate_lab_check(definition, body.topology)
    conn = None
    try:
        try:
            conn = _database_connection()
        except HTTPException:
            # La vérification pédagogique du JSON peut rester disponible même si
            # SQLite est temporairement indisponible ; la soumission, elle, exige DB.
            return result
        course_context = _course_lab_context(conn, lab_id)
        if course_context is not None and not course_context["unlocked"]:
            return _locked_course_check(course_context)
        return _enforce_course_lab_score(result, course_context)
    finally:
        if conn is not None:
            conn.close()


@router.post("/lab/v2/{lab_id}/submit", response_class=UTF8JSONResponse)
def submit_lab_v2(lab_id: str, body: SubmitRequest) -> dict[str, Any]:
    payload = _fetch_lab(lab_id)
    definition: LabDefinition = payload["definition"]

    # Un bac à sable est utilisable librement, mais n'est jamais une validation.
    if payload.get("sandbox"):
        return {
            "ok": True,
            "lab_id": lab_id,
            "passed": False,
            "score": 0.0,
            "sandbox": True,
            "attempt_recorded": False,
            "course_attempt_recorded": False,
            "results": [{
                "rule_id": "sandbox",
                "passed": False,
                "message": "Bac à sable : aucune règle de validation n'est configurée. Aucune progression ni récompense n'est attribuée.",
            }],
            "xp_gained": 0,
            "badges_unlocked": [],
        }

    # Le résultat envoyé par le client n'est jamais la source de vérité.
    check_result = _evaluate_lab_check(definition, body.topology)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    attempt_id = str(uuid.uuid4())
    snapshot = json.dumps(model_to_dict(body.topology, by_alias=True), ensure_ascii=False)
    result_json = ""

    conn = _database_connection()
    course_attempt_recorded = False
    try:
        if "lab_attempts" not in {
            row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }:
            raise HTTPException(status_code=503, detail="La table lab_attempts n'existe pas. Exécute la migration M1.")

        conn.execute("BEGIN IMMEDIATE")
        # Un lab servi depuis labs_v2/*.json peut ne pas encore avoir été versé
        # dans la table labs ; il faut créer la ligne référencée par lab_attempts.
        _ensure_lab_catalog_row(conn, lab_id, definition)
        course_context = _course_lab_context(conn, lab_id)
        if course_context is not None and not course_context["unlocked"]:
            # Une réussite avant déblocage ne doit pas consommer la première
            # récompense ni créer une tentative de progression.
            raise HTTPException(status_code=423, detail=_course_lock_message(course_context))
        check_result = _enforce_course_lab_score(check_result, course_context)
        passed = bool(check_result["passed"])
        score_percent = round(max(0.0, min(1.0, float(check_result.get("score", 0)))) * 100)
        result_json = json.dumps(check_result, ensure_ascii=False)

        previous_success = conn.execute(
            "SELECT 1 FROM lab_attempts WHERE lab_id = ? AND passed = 1 LIMIT 1", (lab_id,)
        ).fetchone()
        first_success = passed and previous_success is None
        xp_gained = int(definition.xp_reward) if first_success else 0
        badge_candidates = list(definition.badges) if passed else []
        badges_unlocked: list[dict[str, str]] = []

        conn.execute(
            "INSERT INTO lab_attempts "
            "(id, lab_id, user_id, started_at, finished_at, passed, config_snapshot, check_result_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (attempt_id, lab_id, None, now, now, int(passed), snapshot, result_json),
        )

        # Les statistiques du skill tree lisent la table canonique attempts, pas
        # lab_attempts. Synchroniser les deux uniquement si le lab est bien lié à
        # une exigence LAB du même nœud et que les prérequis sont déjà déverrouillés.
        if course_context and course_context["unlocked"]:
            canonical_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO attempts "
                "(node_id, kind, score, passed, evidence, detail, created_at) "
                "VALUES (?, 'lab', ?, ?, ?, ?, ?)",
                (
                    lab_id,
                    score_percent,
                    int(passed),
                    snapshot[:4000],
                    f"Lab Workspace v2 : {'réussi' if passed else 'à reprendre'} ({score_percent}/100)",
                    canonical_created,
                ),
            )
            course_attempt_recorded = True

        # Comme les autres validations du moteur Skill-Tree, une vraie tentative
        # compte dans la série quotidienne, même pour un lab autonome hors parcours.
        # Les sandboxes sortent plus haut et les cours verrouillés sont rejetés avant
        # l'insertion : aucun de ces deux cas ne peut créditer une série.
        touch_daily_streak(conn, commit=False)

        # Récompenses du Lab Workspace : une prime de pièces à la première réussite
        # uniquement, comme pour les labs du parcours classique.
        coins_gained = 20 if first_success else 0
        # Les badges sont attribués lorsqu'un lab est réussi, indépendamment de
        # la prime XP : cela permet aussi de réparer une récompense manquante sur
        # une ancienne réussite. INSERT OR IGNORE garantit l'idempotence.
        for requested_badge_id in badge_candidates:
            resolved = _resolve_badge_definition(requested_badge_id)
            if resolved is None:
                continue
            badge_id, badge_info = resolved
            cursor = conn.execute(
                "INSERT OR IGNORE INTO badges (id, nom, description, icone, condition_debloquee_le) "
                "VALUES (?, ?, ?, ?, ?)",
                (badge_id, badge_info["nom"], badge_info["description"], badge_info["icone"], now),
            )
            if cursor.rowcount == 1:
                badges_unlocked.append({"id": badge_id, **badge_info})

        if xp_gained or coins_gained:
            # add_xp committe aussi les tentatives, la série et les récompenses.
            add_xp(conn, xp_gained, coins=coins_gained)
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

    return {
        "ok": True,
        "lab_id": lab_id,
        **check_result,
        "xp_gained": xp_gained,
        "coins_gained": coins_gained,
        "badges_unlocked": badges_unlocked,
        "first_success": bool(first_success),
        "sandbox": False,
        "attempt_recorded": True,
        "course_attempt_recorded": course_attempt_recorded,
    }

@router.get("/lab/v2")
def list_labs_v2() -> list[dict[str, Any]]:
    """Liste les labs v2 réellement ouvrables associés au catalogue de cours.

    Certaines migrations historiques ont créé des entrées schema_version=2
    avec une topologie vide pour préserver un ancien exercice texte. Elles ne
    doivent pas être présentées comme des labs Workspace jouables.
    """
    conn = _database_connection()
    try:
        tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        db_rows: dict[str, dict[str, Any]] = {}
        if "labs" in tables:
            lab_columns = {row["name"] for row in conn.execute('PRAGMA table_info("labs")')}
            if "id" in lab_columns:
                fields = ["id"] + [
                    f'"{name}"' if name in lab_columns else f"NULL AS {name}"
                    for name in (
                        "title", "level", "module", "duration_min", "difficulty",
                        "schema_version", "definition_json",
                    )
                ]
                for row in conn.execute("SELECT " + ", ".join(fields) + " FROM labs").fetchall():
                    if row["id"]:
                        db_rows[str(row["id"])] = dict(row)

        # Le contenu versionné reste la source de vérité quand SQLite n'a pas
        # encore été synchronisé avec les nouveaux nœuds du catalogue.
        course_metadata: dict[str, dict[str, Any]] = {}
        course_ids: set[str] = set()
        if "nodes" in tables:
            node_columns = {row["name"] for row in conn.execute('PRAGMA table_info("nodes")')}
            if "id" in node_columns:
                fields = ["id"]
                fields.append('"title"' if "title" in node_columns else "'' AS title")
                fields.append('"module"' if "module" in node_columns else "'' AS module")
                fields.append('"category"' if "category" in node_columns else "'' AS category")
                for row in conn.execute("SELECT " + ", ".join(fields) + " FROM nodes").fetchall():
                    if not row["id"]:
                        continue
                    node_id = str(row["id"])
                    course_ids.add(node_id)
                    course_metadata[node_id] = {
                        "title": str(row["title"] or ""),
                        "module": str(row["module"] or row["category"] or ""),
                    }

        nodes_path = PROJECT_ROOT / "content" / "nodes.json"
        try:
            configured_nodes = json.loads(nodes_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            configured_nodes = []
        if isinstance(configured_nodes, list):
            for node in configured_nodes:
                if not isinstance(node, dict) or not isinstance(node.get("id"), str):
                    continue
                node_id = node["id"].strip()
                if not node_id:
                    continue
                course_ids.add(node_id)
                course_metadata[node_id] = {
                    "title": str(node.get("title") or ""),
                    "module": str(node.get("module") or node.get("category") or ""),
                }

        catalog: list[dict[str, Any]] = []
        for lab_id in sorted(course_ids):
            row = db_rows.get(lab_id, {})
            definition: LabDefinition | None = None
            raw_definition = row.get("definition_json")
            if raw_definition:
                try:
                    raw_payload = json.loads(raw_definition)
                    if isinstance(raw_payload, dict):
                        candidate = LabDefinition(**raw_payload)
                        if candidate.initial_topology.nodes and int(candidate.schema_version or 2) >= 2:
                            definition = candidate
                except (json.JSONDecodeError, TypeError, ValueError):
                    definition = None

            # Une ancienne entrée SQLite vide ne doit masquer un vrai scénario
            # versionné sous le même identifiant ou un alias de cours.
            if definition is None:
                try:
                    file_payload = _load_lab_file(lab_id)
                except HTTPException:
                    file_payload = None
                if file_payload is not None:
                    candidate = file_payload["definition"]
                    if candidate.initial_topology.nodes and int(candidate.schema_version or 2) >= 2:
                        definition = candidate

            if definition is None:
                continue

            metadata = course_metadata.get(lab_id, {})
            catalog.append({
                "id": lab_id,
                "title": str(metadata.get("title") or definition.title or row.get("title") or lab_id),
                "level": str(definition.level or row.get("level") or "débutant"),
                "module": str(metadata.get("module") or definition.module or row.get("module") or "Général"),
                "duration_min": int(definition.duration_min or row.get("duration_min") or 15),
                "difficulty": str(definition.difficulty or row.get("difficulty") or definition.level or "débutant"),
                "schema_version": int(definition.schema_version or row.get("schema_version") or 2),
            })

        return sorted(catalog, key=lambda item: (item["module"].casefold(), item["title"].casefold()))
    finally:
        conn.close()
