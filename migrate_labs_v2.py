#!/usr/bin/env python3
"""Migration incrémentale des labs Skill-Tree vers le schéma v2.

Usage:
    python migrate_labs_v2.py --dry-run
    python migrate_labs_v2.py
    python migrate_labs_v2.py --lab=ospf-3-routers

Le script conserve les tables legacy. Si labs n'existe pas encore, les données
sont reprises de lab_specs et des définitions de content/labs/.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "skilltree.db"
DB_PATH = Path(os.environ.get("SKILLTREE_DB", str(DEFAULT_DB))).expanduser()
LABS_V2_DIR = ROOT / "labs_v2"
LEGACY_LABS_DIR = ROOT / "content" / "labs"

PILOT_LABS = (
    "ospf-3-routers",
    "vlan-trunk-2-switches",
    "inter-vlan-routing",
    "dhcp-nat",
    "acl-filtering",
)

LABS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS labs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    level TEXT NOT NULL DEFAULT 'débutant',
    module TEXT NOT NULL DEFAULT 'Général',
    prompt TEXT NOT NULL DEFAULT '',
    objectives TEXT NOT NULL DEFAULT '[]',
    hints TEXT NOT NULL DEFAULT '[]',
    duration_min INTEGER NOT NULL DEFAULT 15,
    difficulty TEXT NOT NULL DEFAULT 'débutant',
    xp_reward INTEGER NOT NULL DEFAULT 0,
    badges TEXT NOT NULL DEFAULT '[]',
    schema_version INTEGER DEFAULT 1,
    definition_json TEXT,
    migration_note TEXT
)
"""

LAB_ATTEMPTS_SQL = """
CREATE TABLE IF NOT EXISTS lab_attempts (
    id TEXT PRIMARY KEY,
    lab_id TEXT NOT NULL,
    user_id TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    passed INTEGER DEFAULT 0,
    config_snapshot TEXT,
    check_result_json TEXT,
    FOREIGN KEY (lab_id) REFERENCES labs(id)
)
"""


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone() is not None


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    if not table_exists(conn, table):
        return set()
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}


def decode_list(value: Any, fallback: list[Any] | None = None) -> list[Any]:
    fallback = fallback or []
    if value is None or value == "":
        return list(fallback)
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return [value] if value.strip() else list(fallback)
        if isinstance(decoded, list):
            return decoded
        return [decoded] if decoded is not None else list(fallback)
    return list(fallback)


def decode_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}
    return {}


def infer_level(lab_id: str, title: str = "", existing: str = "") -> str:
    if existing and str(existing).strip():
        return str(existing).strip()
    value = f"{lab_id} {title}".lower()
    if "intermediaire" in value or "intermédiaire" in value:
        return "intermédiaire"
    if "expert" in value:
        return "expert"
    if "debutant" in value or "débutant" in value:
        return "débutant"
    return "débutant"


def normalize_legacy_row(row: dict[str, Any]) -> dict[str, Any]:
    lab_id = row.get("id") or row.get("lab_id") or row.get("node_id")
    if lab_id is None or not str(lab_id).strip():
        raise ValueError("Un lab legacy ne possède ni id, ni lab_id, ni node_id.")
    lab_id = str(lab_id).strip()
    title = str(row.get("title") or row.get("name") or lab_id)
    hint_value = row.get("hints")
    if hint_value in (None, ""):
        hint_value = row.get("hint")
    hints = decode_list(hint_value)
    objectives = decode_list(row.get("objectives"))
    return {
        **row,
        "id": lab_id,
        "title": title,
        "level": infer_level(lab_id, title, str(row.get("level") or "")),
        "module": str(row.get("module") or row.get("category") or "Général"),
        "prompt": str(row.get("prompt") or row.get("description") or title),
        "objectives": objectives,
        "hints": hints,
        "duration_min": _safe_int(row.get("duration_min"), 15),
        "difficulty": str(row.get("difficulty") or infer_level(lab_id, title)),
        "xp_reward": _safe_int(row.get("xp_reward"), 0),
        "badges": decode_list(row.get("badges")),
    }


def _safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def load_lab_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"[AVERTISSEMENT] JSON ignoré {path.relative_to(ROOT)} : {error}")
        return None
    if not isinstance(payload, dict):
        print(f"[AVERTISSEMENT] JSON ignoré {path.relative_to(ROOT)} : objet attendu.")
        return None
    return payload


def collect_legacy_sources(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    """Récupère les labs déjà connus de SQLite et des fichiers v1."""
    sources: dict[str, dict[str, Any]] = {}

    if table_exists(conn, "lab_specs"):
        columns = table_columns(conn, "lab_specs")
        if "node_id" in columns:
            has_nodes = table_exists(conn, "nodes")
            if has_nodes:
                node_columns = table_columns(conn, "nodes")
                title_expr = "n.title" if "title" in node_columns else "ls.node_id"
                module_expr = "n.category" if "category" in node_columns else "'Général'"
                description_expr = "n.description" if "description" in node_columns else "''"
                rows = conn.execute(
                    "SELECT ls.node_id AS id, "
                    f"{title_expr} AS title, {module_expr} AS module, "
                    f"{description_expr} AS description, "
                    "ls.prompt AS prompt, ls.hint AS hint "
                    "FROM lab_specs ls LEFT JOIN nodes n ON n.id = ls.node_id"
                ).fetchall()
            else:
                select_cols = ["node_id AS id"]
                for name in ("prompt", "hint"):
                    select_cols.append(name if name in columns else f"'' AS {name}")
                rows = conn.execute(
                    "SELECT " + ", ".join(select_cols) + " FROM lab_specs"
                ).fetchall()
            for row in rows:
                item = normalize_legacy_row(dict(row))
                sources.setdefault(item["id"], item)

    if LEGACY_LABS_DIR.exists():
        paths = sorted(LEGACY_LABS_DIR.glob("*.json"))
        paths += sorted(LEGACY_LABS_DIR.glob("*/lab.json"))
        for path in paths:
            payload = load_lab_json(path)
            if payload is None:
                continue
            raw_id = payload.get("id") or payload.get("lab_id") or payload.get("node_id")
            if not raw_id:
                raw_id = path.parent.name if path.name == "lab.json" else path.stem
            item = normalize_legacy_row({**payload, "id": str(raw_id)})
            # Les valeurs SQLite restent prioritaires ; les fichiers complètent les manques.
            if item["id"] not in sources:
                sources[item["id"]] = item
            else:
                current = sources[item["id"]]
                for field in ("title", "module", "prompt", "objectives", "hints",
                              "duration_min", "difficulty", "xp_reward", "badges"):
                    if current.get(field) in (None, "", [], 0) and item.get(field) not in (None, "", [], 0):
                        current[field] = item[field]

    return sources


def read_pilot_definition(lab_id: str) -> dict[str, Any] | None:
    path = LABS_V2_DIR / f"{lab_id}.json"
    if not path.is_file():
        return None
    payload = load_lab_json(path)
    if payload is None:
        raise ValueError(f"Le JSON pilote {path.relative_to(ROOT)} est illisible.")
    return payload


def row_from_pilot_json(lab_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    initial = payload.get("initial_topology") or {}
    metadata = initial.get("metadata") or {}
    return normalize_legacy_row({
        "id": lab_id,
        "title": payload.get("title") or metadata.get("name") or lab_id,
        "level": payload.get("level"),
        "module": payload.get("module"),
        "prompt": payload.get("prompt"),
        "objectives": payload.get("objectives", []),
        "hints": payload.get("hints", []),
        "duration_min": payload.get("duration_min", 15),
        "difficulty": payload.get("difficulty"),
        "xp_reward": payload.get("xp_reward", 0),
        "badges": payload.get("badges", []),
    })


def migration_targets(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    targets: dict[str, dict[str, Any]] = {}
    if table_exists(conn, "labs"):
        for raw in conn.execute("SELECT * FROM labs ORDER BY id").fetchall():
            item = normalize_legacy_row(dict(raw))
            targets[item["id"]] = item

    for lab_id, item in collect_legacy_sources(conn).items():
        targets.setdefault(lab_id, item)

    # Un JSON pilote existant est une définition source même si aucun enregistrement
    # legacy n'a encore été créé en base.
    for lab_id in PILOT_LABS:
        payload = read_pilot_definition(lab_id)
        if payload is not None:
            targets.setdefault(lab_id, row_from_pilot_json(lab_id, payload))
    return targets


def minimal_v1_compat(row: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_legacy_row(row)
    return {
        "id": normalized["id"],
        "title": normalized["title"],
        "level": normalized["level"],
        "module": normalized["module"],
        "duration_min": normalized["duration_min"],
        "difficulty": normalized["difficulty"],
        "prompt": normalized["prompt"],
        "objectives": normalized["objectives"],
        "hints": normalized["hints"],
        "initial_topology": {
            "schema_version": 2,
            "nodes": [],
            "links": [],
            "simulation": {"state": "idle", "event_log": []},
        },
        "device_locks": decode_mapping(normalized.get("device_locks")),
        "check": {
            "type": "manual_review",
            "rules": [],
            "pass_threshold": 1.0,
            "time_bonus": {},
        },
        "schema_version": 2,
        "xp_reward": normalized["xp_reward"],
        "badges": normalized["badges"],
    }


def print_plan(targets: dict[str, dict[str, Any]], lab_filter: str | None) -> None:
    selected = {lab_filter} if lab_filter else set(targets)
    print(f"Base ciblée : {DB_PATH}")
    print(f"Mode : {'DRY-RUN (aucune écriture)' if DRY_RUN else 'MIGRATION'}")
    print("-" * 92)
    print(f"{'LAB ID':34} {'ACTION':30} DÉTAIL")
    print("-" * 92)

    for pilot in PILOT_LABS:
        if lab_filter and pilot != lab_filter:
            continue
        payload = read_pilot_definition(pilot)
        if pilot in targets and payload is not None:
            print(f"{pilot:34} {'would migrate from JSON':30} labs_v2/{pilot}.json")
        elif pilot in targets and payload is None:
            print(f"{pilot:34} {'missing, skipped':30} JSON pilote absent")
        elif payload is not None:
            print(f"{pilot:34} {'would migrate from JSON':30} nouvel enregistrement depuis labs_v2/{pilot}.json")
        else:
            print(f"{pilot:34} {'missing, skipped':30} absent de la base et de labs_v2/")
    for lab_id in sorted(selected - set(PILOT_LABS)):
        if lab_id not in targets:
            print(f"{lab_id:34} {'missing, skipped':30} aucun lab legacy trouvé")
        else:
            print(f"{lab_id:34} {'auto v1-compat':30} conversion vers schema_version=2")
    print("-" * 92)
    count = sum(1 for lab_id in selected if lab_id in targets and
                (lab_id not in PILOT_LABS or (LABS_V2_DIR / f"{lab_id}.json").is_file()))
    print(f"Labs qui seraient migrés : {count}")


def backup_database(db_path: Path) -> Path:
    backup_dir = ROOT / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = backup_dir / f"lab_migration_{stamp}.db"
    suffix = 1
    while target.exists():
        target = backup_dir / f"lab_migration_{stamp}_{suffix}.db"
        suffix += 1
    with sqlite3.connect(str(db_path)) as source, sqlite3.connect(str(target)) as dest:
        source.backup(dest)
    print(f"[BACKUP] Sauvegarde SQLite créée : {target.relative_to(ROOT)}")
    return target


def ensure_v2_columns(conn: sqlite3.Connection) -> None:
    columns = table_columns(conn, "labs")
    declarations = (
        ("schema_version", "INTEGER DEFAULT 1"),
        ("definition_json", "TEXT"),
        ("migration_note", "TEXT"),
    )
    for name, declaration in declarations:
        if name not in columns:
            conn.execute(f'ALTER TABLE labs ADD COLUMN "{name}" {declaration}')
            print(f"[DB] Colonne labs.{name} ajoutée.")


def insert_lab_if_missing(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    columns = table_columns(conn, "labs")
    values = {
        "id": row["id"],
        "title": row["title"],
        "level": row["level"],
        "module": row["module"],
        "prompt": row["prompt"],
        "objectives": json.dumps(row["objectives"], ensure_ascii=False),
        "hints": json.dumps(row["hints"], ensure_ascii=False),
        "duration_min": row["duration_min"],
        "difficulty": row["difficulty"],
        "xp_reward": row["xp_reward"],
        "badges": json.dumps(row["badges"], ensure_ascii=False),
        "schema_version": _safe_int(row.get("schema_version"), 1),
        "definition_json": row.get("definition_json"),
        "migration_note": row.get("migration_note"),
    }
    selected = [(key, value) for key, value in values.items() if key in columns]
    if not any(key == "id" for key, _ in selected):
        raise RuntimeError("La table labs doit posséder une colonne id.")
    names = ", ".join(f'"{key}"' for key, _ in selected)
    placeholders = ", ".join("?" for _ in selected)
    conn.execute(
        f"INSERT OR IGNORE INTO labs ({names}) VALUES ({placeholders})",
        tuple(value for _, value in selected),
    )


def main() -> int:
    global DRY_RUN
    parser = argparse.ArgumentParser(description="Migration des labs Skill-Tree vers le schéma v2.")
    parser.add_argument("--dry-run", action="store_true", help="affiche le plan sans écrire en base")
    parser.add_argument("--lab", metavar="ID", help="limite la migration à un seul lab")
    parser.add_argument("--db", type=Path, help="chemin explicite vers skilltree.db")
    args = parser.parse_args()
    DRY_RUN = args.dry_run
    db_path = args.db.expanduser().resolve() if args.db else DB_PATH.resolve()
    globals()["DB_PATH"] = db_path

    if not db_path.is_file():
        print(f"[ERREUR] Base SQLite introuvable : {db_path}")
        for pilot in PILOT_LABS:
            if not args.lab or args.lab == pilot:
                print(f"{pilot:34} {'missing, skipped':30} base absente et pilote non vérifié")
        if args.dry_run:
            print("DRY-RUN terminé : aucune base ni aucun fichier n'a été créé.")
        return 1

    connect_uri = f"file:{quote(str(db_path))}?mode=ro" if args.dry_run else str(db_path)
    try:
        conn = sqlite3.connect(connect_uri, uri=args.dry_run)
        conn.row_factory = sqlite3.Row
        try:
            targets = migration_targets(conn)
            print_plan(targets, args.lab)
            if args.dry_run:
                return 0

            if args.lab and args.lab not in targets and args.lab not in PILOT_LABS:
                print(f"[ERREUR] Lab introuvable : {args.lab}")
                return 1

            selected_ids = [args.lab] if args.lab else sorted(targets)
            pilot_json = {
                lab_id: read_pilot_definition(lab_id)
                for lab_id in PILOT_LABS
                if lab_id in selected_ids
            }
        finally:
            conn.close()
    except (sqlite3.Error, ValueError, RuntimeError) as error:
        print(f"[ERREUR] Inspection de la base impossible : {error}")
        return 1

    try:
        backup_database(db_path)
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(LABS_TABLE_SQL)
            ensure_v2_columns(conn)
            conn.execute(LAB_ATTEMPTS_SQL)

            # Réconcilie les labs legacy ou les JSON pilotes absents de la table cible.
            for lab_id in selected_ids:
                row = targets.get(lab_id)
                if row is None and lab_id in pilot_json and pilot_json[lab_id] is not None:
                    row = row_from_pilot_json(lab_id, pilot_json[lab_id])
                if row is not None:
                    insert_lab_if_missing(conn, row)

            for lab_id in selected_ids:
                row = targets.get(lab_id)
                payload = pilot_json.get(lab_id) if lab_id in PILOT_LABS else None
                if lab_id in PILOT_LABS and payload is None:
                    print(f"[SKIP] {lab_id} : JSON pilote absent, enregistrement non modifié.")
                    continue
                if payload is not None:
                    definition = payload
                    note = f"M1: définition pilote chargée depuis labs_v2/{lab_id}.json"
                    source = f"labs_v2/{lab_id}.json"
                else:
                    if row is None:
                        print(f"[SKIP] {lab_id} : aucun enregistrement legacy.")
                        continue
                    definition = minimal_v1_compat(row)
                    note = "M1: définition minimale v1-compat générée automatiquement"
                    source = "v1-compat"
                now_iso = datetime.now(timezone.utc).isoformat()
                if not table_exists(conn, "labs"):
                    raise RuntimeError("La table labs n'a pas pu être créée.")
                columns = table_columns(conn, "labs")
                id_column = "id" if "id" in columns else None
                if id_column is None:
                    raise RuntimeError("La table labs ne possède pas de colonne id.")
                conn.execute(
                    "UPDATE labs SET schema_version = 2, definition_json = ?, migration_note = ? "
                    "WHERE id = ?",
                    (json.dumps(definition, ensure_ascii=False, indent=2), f"{note} — {now_iso}", lab_id),
                )
                print(f"[OK] {lab_id}: schema_version=2 ({source})")
            conn.commit()
        print("[TERMINE] Migration M1 effectuée.")
        return 0
    except Exception as error:
        print(f"[ERREUR] Migration annulée : {error}")
        return 1


DRY_RUN = False

if __name__ == "__main__":
    raise SystemExit(main())
