from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.diagnose_lab_locks import audit_database


class LabLockDiagnosticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.db_path = root / "skilltree.sqlite3"
        self.nodes_path = root / "nodes.json"
        self.nodes = [
            {
                "id": "osi-debutant",
                "title": "Modèle OSI & TCP/IP - Débutant",
                "module": "Administration Réseaux",
                "prereqs": [],
                "requirements": [{"kind": "quiz", "min_score": 80}],
            },
            {
                "id": "routing-debutant",
                "title": "Routage statique - Débutant",
                "module": "Administration Réseaux",
                "prereqs": ["osi-debutant"],
                "requirements": [
                    {"kind": "quiz", "min_score": 80},
                    {"kind": "lab", "min_score": 100},
                ],
            },
            {
                "id": "acl-debutant",
                "title": "ACL & filtrage - Débutant",
                "module": "Cybersécurité",
                "prereqs": ["routing-debutant"],
                "requirements": [{"kind": "lab", "min_score": 100}],
            },
        ]
        self.nodes_path.write_text(json.dumps(self.nodes), encoding="utf-8")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE nodes (id TEXT PRIMARY KEY, title TEXT NOT NULL)")
            conn.execute("CREATE TABLE edges (node_id TEXT NOT NULL, prereq_id TEXT NOT NULL)")
            conn.execute(
                "CREATE TABLE requirements (node_id TEXT NOT NULL, kind TEXT NOT NULL, min_score INTEGER NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT NOT NULL, kind TEXT NOT NULL, score INTEGER NOT NULL, passed INTEGER NOT NULL)"
            )
            conn.execute("CREATE TABLE labs (id TEXT PRIMARY KEY)")
            conn.execute("CREATE TABLE lab_attempts (id TEXT PRIMARY KEY)")
            for node in self.nodes:
                conn.execute("INSERT INTO nodes (id, title) VALUES (?, ?)", (node["id"], node["title"]))
                for req in node["requirements"]:
                    conn.execute(
                        "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
                        (node["id"], req["kind"], req["min_score"]),
                    )
                for prereq in node["prereqs"]:
                    conn.execute(
                        "INSERT INTO edges (node_id, prereq_id) VALUES (?, ?)",
                        (node["id"], prereq),
                    )
            conn.execute(
                "INSERT INTO attempts (node_id, kind, score, passed) VALUES (?, ?, ?, ?)",
                ("osi-debutant", "quiz", 80, 1),
            )
            conn.execute(
                "INSERT INTO attempts (node_id, kind, score, passed) VALUES (?, ?, ?, ?)",
                ("routing-debutant", "quiz", 90, 1),
            )
            conn.commit()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_reports_the_course_that_blocks_a_lab_without_writing(self) -> None:
        report = audit_database(self.db_path, self.nodes_path)

        self.assertFalse(report["db_graph_mismatch"])
        self.assertEqual(report["lab_required_node_count"], 2)
        self.assertEqual(report["accessible_lab_count"], 1)
        self.assertEqual(report["locked_lab_count"], 1)
        locked = report["locked_labs"][0]
        self.assertEqual(locked["id"], "acl-debutant")
        self.assertEqual(locked["blockers"][0]["title"], "Routage statique - Débutant")
        self.assertEqual(locked["blockers"][0]["unmet_requirements"], ["lab ≥ 100/100"])
        self.assertEqual(report["attempt_count"], 2)

        # Le diagnostic ouvre SQLite en lecture seule : les tentatives ne changent pas.
        with sqlite3.connect(self.db_path) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 2)

    def test_detects_a_stale_sqlite_prerequisite_graph(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM edges WHERE node_id = ? AND prereq_id = ?",
                ("acl-debutant", "routing-debutant"),
            )
            conn.commit()

        report = audit_database(self.db_path, self.nodes_path)

        self.assertTrue(report["db_graph_mismatch"])
        self.assertIn(("acl-debutant", "routing-debutant"), report["missing_edges"])

    def test_does_not_mark_a_node_validated_when_a_required_proof_is_missing(self) -> None:
        report = audit_database(self.db_path, self.nodes_path)

        self.assertEqual(report["node_statuses"]["osi-debutant"], "validé")
        self.assertEqual(report["node_statuses"]["routing-debutant"], "en cours")
        self.assertEqual(report["node_statuses"]["acl-debutant"], "verrouillé")


if __name__ == "__main__":
    unittest.main()
