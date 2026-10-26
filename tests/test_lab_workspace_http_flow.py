from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


class LabWorkspaceHttpFlowTests(unittest.TestCase):
    """Parcours API complet sur une base éphémère, sans modifier la DB de production."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "workspace-http.sqlite3"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE labs (
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
                    schema_version INTEGER NOT NULL DEFAULT 2,
                    definition_json TEXT,
                    migration_note TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE lab_attempts (
                    id TEXT PRIMARY KEY,
                    lab_id TEXT NOT NULL REFERENCES labs(id),
                    user_id TEXT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    passed INTEGER NOT NULL DEFAULT 0,
                    config_snapshot TEXT,
                    check_result_json TEXT
                )
                """
            )
        self.db_path_patch = patch.object(api, "DB_PATH", self.db_path)
        self.db_path_patch.start()
        self.addCleanup(self.db_path_patch.stop)
        self.env_patch = patch.dict(os.environ, {"SKILLTREE_DB": str(self.db_path)})
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_open_save_reload_check_and_submit_real_ipv4_scenario_over_http(self) -> None:
        with TestClient(api.app) as client:
            opened = client.get("/api/lab/v2/ipv4-debutant")
            self.assertEqual(opened.status_code, 200, opened.text)
            payload = opened.json()
            self.assertFalse(payload.get("sandbox", False))
            self.assertEqual(payload["id"], "ipv4-debutant")
            topology = payload["initial_topology"]
            self.assertEqual(
                [node["id"] for node in topology["nodes"]],
                ["PC-A", "SW1", "PC-B"],
            )
            self.assertEqual(len(topology["links"]), 2)

            saved = client.post(
                "/api/lab/v2/ipv4-debutant/save",
                json={"topology": topology},
            )
            self.assertEqual(saved.status_code, 200, saved.text)
            self.assertTrue(saved.json()["success"])

            reloaded = client.get("/api/lab/v2/ipv4-debutant/load")
            self.assertEqual(reloaded.status_code, 200, reloaded.text)
            self.assertEqual(reloaded.json()["topology"], topology)

            checked = client.post(
                "/api/lab/v2/ipv4-debutant/check",
                json={"topology": topology},
            )
            self.assertEqual(checked.status_code, 200, checked.text)
            self.assertIn("passed", checked.json())
            self.assertIsInstance(checked.json().get("results"), list)

            # Le client ment volontairement : la soumission doit recalculer le score.
            submitted = client.post(
                "/api/lab/v2/ipv4-debutant/submit",
                json={
                    "topology": topology,
                    "check_result": {"passed": True, "score": 1.0, "results": []},
                },
            )
            self.assertEqual(submitted.status_code, 200, submitted.text)
            result = submitted.json()
            self.assertTrue(result["attempt_recorded"])
            self.assertFalse(result["passed"])
            self.assertEqual(result["xp_gained"], 0)

        with sqlite3.connect(self.db_path) as conn:
            attempt = conn.execute(
                "SELECT lab_id, passed, check_result_json FROM lab_attempts"
            ).fetchone()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt[0], "ipv4-debutant")
        self.assertEqual(attempt[1], 0)
        self.assertFalse(__import__("json").loads(attempt[2])["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
