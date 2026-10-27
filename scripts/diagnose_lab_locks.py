"""Diagnostic local du Lab Workspace, strictement en lecture seule.

Compare content/nodes.json au graphe SQLite et explique les cours prérequis
qui maintiennent les laboratoires du parcours verrouillés.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "skilltree.db"
DEFAULT_NODES = PROJECT_ROOT / "content" / "nodes.json"


class DiagnosticError(RuntimeError):
    """Erreur lisible empêchant d'effectuer le diagnostic."""


def _read_nodes(nodes_path: Path) -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(nodes_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise DiagnosticError(f"Lecture de {nodes_path} impossible : {error}") from error

    if not isinstance(payload, list):
        raise DiagnosticError(f"{nodes_path} : une liste de cours est attendue.")

    nodes: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise DiagnosticError(f"{nodes_path} : nœud invalide à la position {index}.")
        node_id = item["id"].strip()
        if not node_id or node_id in nodes:
            raise DiagnosticError(f"{nodes_path} : identifiant de cours vide ou dupliqué ({node_id!r}).")
        prereqs = item.get("prereqs", [])
        requirements = item.get("requirements", [])
        if not isinstance(prereqs, list) or not isinstance(requirements, list):
            raise DiagnosticError(f"{nodes_path} : prérequis/exigences invalides pour {node_id}.")
        normalized_requirements = []
        for requirement in requirements:
            if not isinstance(requirement, dict) or not isinstance(requirement.get("kind"), str):
                raise DiagnosticError(f"{nodes_path} : exigence invalide pour {node_id}.")
            try:
                min_score = int(requirement.get("min_score", 80))
            except (TypeError, ValueError) as error:
                raise DiagnosticError(f"{nodes_path} : seuil invalide pour {node_id}.") from error
            normalized_requirements.append(
                {"kind": requirement["kind"], "min_score": min_score}
            )
        nodes[node_id] = {
            "id": node_id,
            "title": str(item.get("title") or node_id),
            "module": str(item.get("module") or item.get("category") or ""),
            "prereqs": [str(value) for value in prereqs if isinstance(value, str)],
            "requirements": normalized_requirements,
        }
    return nodes


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    path = db_path.expanduser().resolve()
    if not path.is_file():
        raise DiagnosticError(f"Base SQLite introuvable : {path}")
    # URI mode=ro et query_only protègent la base contre toute écriture.
    uri = f"file:{quote(path.as_posix(), safe='/:')}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        return conn
    except sqlite3.Error as error:
        raise DiagnosticError(f"Ouverture en lecture seule impossible : {error}") from error


def _requirement_met(requirement: dict[str, Any], attempts: list[dict[str, Any]]) -> bool:
    return any(
        attempt["kind"] == requirement["kind"]
        and attempt["passed"]
        and attempt["score"] >= requirement["min_score"]
        for attempt in attempts
    )


def _unmet_requirements(node: dict[str, Any], attempts: list[dict[str, Any]]) -> list[str]:
    unmet = []
    for requirement in node["requirements"]:
        if not _requirement_met(requirement, attempts):
            unmet.append(f"{requirement['kind']} ≥ {requirement['min_score']}/100")
    return unmet


def audit_database(db_path: Path, nodes_path: Path) -> dict[str, Any]:
    """Analyse la progression courante sans modifier la base."""
    source_nodes = _read_nodes(nodes_path)
    source_ids = set(source_nodes)
    source_edges = {
        (node_id, prereq)
        for node_id, node in source_nodes.items()
        for prereq in node["prereqs"]
        if prereq in source_ids
    }
    invalid_source_prereqs = [
        (node_id, prereq)
        for node_id, node in source_nodes.items()
        for prereq in node["prereqs"]
        if prereq not in source_ids
    ]
    source_requirements = {
        (node_id, req["kind"], req["min_score"])
        for node_id, node in source_nodes.items()
        for req in node["requirements"]
    }

    conn = _connect_readonly(db_path)
    try:
        tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        required_tables = {"nodes", "edges", "requirements", "attempts"}
        missing_tables = sorted(required_tables - tables)
        if missing_tables:
            raise DiagnosticError(
                "Schéma incomplet : tables manquantes : " + ", ".join(missing_tables)
            )

        db_nodes = {
            str(row["id"]): str(row["title"] or row["id"])
            for row in conn.execute("SELECT id, title FROM nodes")
        }
        db_edges = {
            (str(row["node_id"]), str(row["prereq_id"]))
            for row in conn.execute("SELECT node_id, prereq_id FROM edges")
        }
        db_requirements = {
            (str(row["node_id"]), str(row["kind"]), int(row["min_score"]))
            for row in conn.execute("SELECT node_id, kind, min_score FROM requirements")
        }
        attempts_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
        attempt_count = 0
        for row in conn.execute("SELECT node_id, kind, score, passed FROM attempts"):
            attempts_by_node[str(row["node_id"])].append({
                "kind": str(row["kind"]),
                "score": int(row["score"] or 0),
                "passed": bool(row["passed"]),
            })
            attempt_count += 1

        if "lab_attempts" in tables:
            lab_attempt_count = int(conn.execute("SELECT COUNT(*) FROM lab_attempts").fetchone()[0])
        else:
            lab_attempt_count = None
        if "labs" in tables:
            lab_catalog_count = int(conn.execute("SELECT COUNT(*) FROM labs").fetchone()[0])
        else:
            lab_catalog_count = None

        missing_nodes = sorted(source_ids - set(db_nodes))
        stale_nodes = sorted(set(db_nodes) - source_ids)
        missing_edges = sorted(source_edges - db_edges)
        extra_edges = sorted(db_edges - source_edges)
        missing_requirements = sorted(source_requirements - db_requirements)
        extra_requirements = sorted(db_requirements - source_requirements)

        validated: set[str] = set()
        for node_id, node in source_nodes.items():
            node_attempts = attempts_by_node.get(node_id, [])
            requirements = node["requirements"]
            if requirements and all(
                _requirement_met(requirement, node_attempts)
                for requirement in requirements
            ):
                validated.add(node_id)

        statuses: dict[str, str] = {}
        for node_id, node in source_nodes.items():
            if node_id in validated:
                statuses[node_id] = "validé"
            elif any(prereq not in validated for prereq in node["prereqs"]):
                statuses[node_id] = "verrouillé"
            elif attempts_by_node.get(node_id):
                statuses[node_id] = "en cours"
            else:
                statuses[node_id] = "disponible"

        lab_nodes = [
            node for node in source_nodes.values()
            if any(req["kind"] == "lab" for req in node["requirements"])
        ]
        locked_labs = []
        accessible_labs = 0
        for node in lab_nodes:
            node_id = node["id"]
            if statuses[node_id] != "verrouillé":
                accessible_labs += 1
                continue
            blockers = []
            for prereq in node["prereqs"]:
                if prereq in validated:
                    continue
                prereq_node = source_nodes.get(prereq)
                title = prereq_node["title"] if prereq_node else db_nodes.get(prereq, prereq)
                unmet = _unmet_requirements(
                    prereq_node or {"requirements": []},
                    attempts_by_node.get(prereq, []),
                )
                blockers.append({
                    "id": prereq,
                    "title": title,
                    "status": statuses.get(prereq, "absent du catalogue source"),
                    "unmet_requirements": unmet,
                })
            locked_labs.append({
                "id": node_id,
                "title": node["title"],
                "module": node.get("module", ""),
                "blockers": blockers,
            })

        root_available = [
            {"id": node_id, "title": node["title"]}
            for node_id, node in source_nodes.items()
            if not node["prereqs"] and statuses[node_id] == "disponible"
        ]
        status_counts = Counter(statuses.values())
        db_graph_mismatch = bool(
            missing_nodes or stale_nodes or missing_edges or extra_edges
            or missing_requirements or extra_requirements
        )
        return {
            "database": str(db_path.expanduser().resolve()),
            "nodes_file": str(nodes_path.expanduser().resolve()),
            "source_node_count": len(source_nodes),
            "database_node_count": len(db_nodes),
            "source_edge_count": len(source_edges),
            "database_edge_count": len(db_edges),
            "source_requirement_count": len(source_requirements),
            "database_requirement_count": len(db_requirements),
            "db_graph_mismatch": db_graph_mismatch,
            "missing_nodes": missing_nodes,
            "stale_nodes": stale_nodes,
            "missing_edges": missing_edges,
            "extra_edges": extra_edges,
            "missing_requirements": missing_requirements,
            "extra_requirements": extra_requirements,
            "invalid_source_prereqs": invalid_source_prereqs,
            "attempt_count": attempt_count,
            "lab_attempt_count": lab_attempt_count,
            "lab_catalog_count": lab_catalog_count,
            "validated_node_count": len(validated),
            "status_counts": dict(status_counts),
            "node_statuses": statuses,
            "lab_required_node_count": len(lab_nodes),
            "accessible_lab_count": accessible_labs,
            "locked_lab_count": len(locked_labs),
            "locked_labs": locked_labs,
            "available_root_nodes": root_available,
        }
    except sqlite3.Error as error:
        raise DiagnosticError(f"Lecture SQLite impossible : {error}") from error
    finally:
        conn.close()


def _display_pairs(title: str, values: list[tuple[Any, ...]], limit: int) -> list[str]:
    lines = [f"{title} : {len(values)}"]
    for item in values[:limit]:
        lines.append("  - " + " -> ".join(str(value) for value in item))
    if len(values) > limit:
        lines.append(f"  … {len(values) - limit} autre(s), utiliser --all pour tout afficher")
    return lines


def print_report(report: dict[str, Any], *, show_all: bool = False) -> None:
    limit = None if show_all else 20
    print("DIAGNOSTIC LAB WORKSPACE — LECTURE SEULE")
    print(f"Base : {report['database']}")
    print(f"Catalogue source : {report['nodes_file']}")
    print()
    print(
        f"Cours : {report['source_node_count']} dans content/ ; "
        f"{report['database_node_count']} en SQLite"
    )
    print(
        f"Arêtes de prérequis : {report['source_edge_count']} dans content/ ; "
        f"{report['database_edge_count']} en SQLite"
    )
    print(
        f"Exigences : {report['source_requirement_count']} dans content/ ; "
        f"{report['database_requirement_count']} en SQLite"
    )
    print(
        f"Progression enregistrée : {report['attempt_count']} tentative(s) de cours ; "
        f"{report['lab_attempt_count'] if report['lab_attempt_count'] is not None else 'table absente'} "
        "tentative(s) Lab Workspace"
    )
    print(
        "Entrées dans le catalogue Lab Workspace : "
        f"{report['lab_catalog_count'] if report['lab_catalog_count'] is not None else 'table absente'}"
    )
    counts = report["status_counts"]
    print(
        "Statuts calculés depuis content/ et les tentatives : "
        f"{counts.get('validé', 0)} validés ; "
        f"{counts.get('disponible', 0)} disponibles ; "
        f"{counts.get('en cours', 0)} en cours ; "
        f"{counts.get('verrouillé', 0)} verrouillés"
    )
    print(
        "Nœuds validés selon les exigences actuelles : "
        f"{report['validated_node_count']} / {report['source_node_count']}"
    )
    print(
        "Labs liés au parcours : "
        f"{report['accessible_lab_count']} accessibles ; {report['locked_lab_count']} verrouillés "
        f"sur {report['lab_required_node_count']}"
    )
    print()
    if report["db_graph_mismatch"]:
        print("ALERTE : le graphe SQLite diffère de content/nodes.json.")
    else:
        print("Graphe SQLite : cohérent avec content/nodes.json.")
    if report["invalid_source_prereqs"]:
        print("Références de prérequis absentes du catalogue source :")
        for node_id, prereq in report["invalid_source_prereqs"][: (limit or len(report["invalid_source_prereqs"]))]:
            print(f"  - {node_id} -> {prereq}")

    diff_sections = [
        ("Cours présents dans content/ mais absents de SQLite", report["missing_nodes"]),
        ("Cours SQLite absents du catalogue source", report["stale_nodes"]),
        ("Prérequis attendus mais absents de SQLite", report["missing_edges"]),
        ("Prérequis SQLite qui ne correspondent plus à content/", report["extra_edges"]),
        ("Exigences attendues mais absentes de SQLite", report["missing_requirements"]),
        ("Exigences SQLite qui ne correspondent plus à content/", report["extra_requirements"]),
    ]
    for title, values in diff_sections:
        lines = _display_pairs(
            title, values, len(values) if limit is None else limit
        )
        if len(values) or title.startswith("Cours présents"):
            print("\n".join(lines))

    print()
    roots = report["available_root_nodes"]
    print(f"Premiers cours racines disponibles : {len(roots)}")
    for node in roots[: (limit or len(roots))]:
        print(f"  - {node['title']} [{node['id']}]")

    locked = report["locked_labs"]
    if locked:
        print()
        print(f"Pourquoi les labs du parcours sont verrouillés ({len(locked)}) :")
        for lab in locked[: (limit or len(locked))]:
            print(f"  - {lab['title']} [{lab['id']}]")
            if not lab["blockers"]:
                print("      cause : prérequis non déterminé à partir du catalogue")
            for blocker in lab["blockers"]:
                unmet = (
                    "; exigences à valider : " + ", ".join(blocker["unmet_requirements"])
                    if blocker["unmet_requirements"] else ""
                )
                print(
                    f"      ↳ {blocker['title']} [{blocker['id']}] — "
                    f"{blocker['status']}{unmet}"
                )
        if limit is not None and len(locked) > limit:
            print(f"  … {len(locked) - limit} autre(s), utiliser --all pour tout afficher")

    if report["db_graph_mismatch"]:
        print()
        print(
            "Action prudente : fais d'abord une sauvegarde. La commande "
            "python main.py import resynchronise le contenu, mais elle ne doit "
            "pas être lancée sans sauvegarde car le retrait d'un ancien nœud peut "
            "supprimer les tentatives qui lui sont rattachées."
        )
    elif report["locked_lab_count"] and report["attempt_count"] == 0:
        print()
        print(
            "Le graphe est cohérent et aucune tentative de cours n'est enregistrée : "
            "le verrouillage est expliqué par la progression non encore validée. "
            "Commence par l'un des cours racines disponibles ci-dessus."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare le graphe de prérequis du Lab Workspace sans écrire dans SQLite."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="chemin de la base SQLite")
    parser.add_argument(
        "--nodes", type=Path, default=DEFAULT_NODES, help="chemin vers content/nodes.json"
    )
    parser.add_argument("--all", action="store_true", help="affiche tous les labs verrouillés et toutes les différences")
    args = parser.parse_args(argv)

    try:
        report = audit_database(args.db, args.nodes)
        print_report(report, show_all=args.all)
    except DiagnosticError as error:
        print(f"Diagnostic impossible : {error}", file=sys.stderr)
        return 2
    return 1 if report["db_graph_mismatch"] or report["invalid_source_prereqs"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
