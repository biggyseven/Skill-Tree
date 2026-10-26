from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.responses import Response

from app import lab_routes


class LabLockDiagnosticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db_path = self.root / "skilltree.sqlite3"
        self.nodes_path = self.root / "nodes.json"
        self.nodes_path.write_text(
            json.dumps(
                [
                    {
                        "id": "foundation",
                        "title": "Fondamentaux",
                        "prereqs": [],
                        "requirements": [{"kind": "quiz", "min_score": 80}],
                    },
                    {
                        "id": "lab-network",
                        "title": "Lab réseau",
                        "prereqs": ["foundation"],
                        "requirements": [{"kind": "lab", "min_score": 100}],
                    },
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(
                """
                CREATE TABLE nodes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    category TEXT NOT NULL DEFAULT '',
                    module TEXT NOT NULL DEFAULT '',
                    sort_order INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE edges (
                    node_id TEXT NOT NULL,
                    prereq_id TEXT NOT NULL
                );
                CREATE TABLE requirements (
                    node_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    min_score INTEGER NOT NULL
                );
                CREATE TABLE attempts (
                    id INTEGER PRIMARY KEY,
                    node_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    passed INTEGER NOT NULL,
                    evidence TEXT NOT NULL DEFAULT 'PRIVATE_EVIDENCE',
                    detail TEXT NOT NULL DEFAULT 'PRIVATE_DETAIL',
                    created_at TEXT NOT NULL DEFAULT '2026-01-01'
                );
                CREATE TABLE lab_attempts (
                    id TEXT PRIMARY KEY,
                    lab_id TEXT NOT NULL,
                    user_id TEXT,
                    passed INTEGER DEFAULT 0
                );
                CREATE TABLE labs (id TEXT PRIMARY KEY, title TEXT);
                INSERT INTO nodes (id, title) VALUES
                    ('foundation', 'Fondamentaux'),
                    ('lab-network', 'Lab réseau');
                INSERT INTO edges (node_id, prereq_id)
                    VALUES ('lab-network', 'foundation');
                INSERT INTO requirements (node_id, kind, min_score) VALUES
                    ('foundation', 'quiz', 80),
                    ('lab-network', 'lab', 100);
                INSERT INTO attempts (id, node_id, kind, score, passed, evidence, detail)
                    VALUES (1, 'foundation', 'quiz', 40, 0, 'SECRET_ANSWER', 'SECRET_DETAIL');
                """
            )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_reports_blocking_prerequisite_without_exposing_attempt_details(self) -> None:
        before = sqlite3.connect(self.db_path).execute(
            "SELECT COUNT(*) FROM attempts"
        ).fetchone()[0]

        report = lab_routes._build_lab_lock_diagnostic(self.db_path, self.nodes_path)

        self.assertEqual(report["mode"], "lecture_seule")
        self.assertEqual(report["progression"]["course_labs_total"], 1)
        self.assertEqual(report["progression"]["course_labs_locked"], 1)
        blocked_lab = report["locked_labs"][0]
        self.assertEqual(blocked_lab["id"], "lab-network")
        self.assertEqual(blocked_lab["blocking_prerequisites"][0]["id"], "foundation")
        self.assertEqual(
            blocked_lab["blocking_prerequisites"][0]["unmet_requirements"],
            ["quiz ≥ 80/100"],
        )
        serialized = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("SECRET_ANSWER", serialized)
        self.assertNotIn("SECRET_DETAIL", serialized)
        self.assertNotIn("PRIVATE_EVIDENCE", serialized)
        after = sqlite3.connect(self.db_path).execute(
            "SELECT COUNT(*) FROM attempts"
        ).fetchone()[0]
        self.assertEqual(before, after)

    def test_reports_database_catalogue_drift(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
                ("foundation", "exam", 85),
            )
        report = lab_routes._build_lab_lock_diagnostic(self.db_path, self.nodes_path)
        self.assertFalse(report["catalogue"]["consistent_with_deployed_source"])
        self.assertEqual(
            report["catalogue"]["differences"]["requirements_only_in_sqlite"]["count"],
            1,
        )

    def test_route_is_closed_when_secret_is_not_configured(self) -> None:
        response = Response()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as raised:
                lab_routes.get_lab_lock_diagnostic(
                    response=response,
                    authorization="Bearer " + ("x" * 40),
                )
        self.assertEqual(raised.exception.status_code, 404)

    def test_route_requires_bearer_secret_and_disables_caching(self) -> None:
        token = "diagnostic-secret-" + ("x" * 40)
        with patch.dict(os.environ, {"SKILLTREE_DIAGNOSTIC_TOKEN": token}):
            with self.assertRaises(HTTPException) as raised:
                lab_routes.get_lab_lock_diagnostic(
                    response=Response(),
                    authorization="Bearer wrong",
                )
            self.assertEqual(raised.exception.status_code, 404)

        with patch.dict(
            os.environ,
            {
                "SKILLTREE_DIAGNOSTIC_TOKEN": token,
                "SKILLTREE_DB": str(self.db_path),
            },
        ), patch.object(lab_routes, "DIAGNOSTIC_NODES_PATH", self.nodes_path):
            response = Response()
            report = lab_routes.get_lab_lock_diagnostic(
                response=response,
                authorization="Bearer " + token,
            )
        self.assertEqual(report["status"], "ok")
        self.assertEqual(response.headers["cache-control"], "no-store, private, max-age=0")
        self.assertEqual(response.headers["pragma"], "no-cache")


if __name__ == "__main__":
    unittest.main()
