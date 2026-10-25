from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import lab_routes
from app.api import app
from app.lab_schema_v2 import CheckDefinition, CheckRequest, CheckRule, Device, DeviceConfig, Link, Port, SubmitRequest, Topology


class LabValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "labs.sqlite3"
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("CREATE TABLE labs (id TEXT PRIMARY KEY, title TEXT NOT NULL DEFAULT '')")
            conn.execute("INSERT INTO labs (id, title) VALUES (?, ?)", ("lab-1", "Lab de test"))
            conn.execute(
                """
                CREATE TABLE lab_attempts (
                    id TEXT PRIMARY KEY, lab_id TEXT NOT NULL, user_id TEXT,
                    started_at TEXT NOT NULL, finished_at TEXT, passed INTEGER DEFAULT 0,
                    config_snapshot TEXT, check_result_json TEXT,
                    FOREIGN KEY (lab_id) REFERENCES labs(id)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def _rule() -> CheckRule:
        return CheckRule(
            id="hostname", description="Le nom attendu est configuré",
            device="R1", path="config.hostname", operator="equals", expected="edge-1",
        )

    def _definition(self, *, check_type: str = "config_assertions", rules=None):
        if rules is None:
            rules = [self._rule()]
        return lab_routes.LabDefinition(
            id="lab-1", title="Lab de test", xp_reward=25, badges=["lab-validated"],
            check=CheckDefinition(type=check_type, rules=rules, pass_threshold=1.0),
        )

    @staticmethod
    def _topology(hostname: str) -> Topology:
        return Topology(nodes=[Device(
            id="R1", label="R1", config=DeviceConfig(hostname=hostname),
            ports=[Port(id="Fa0/0", name="Fa0/0", state="up", vlan=20)],
        )])

    def _mock_lab(self, definition):
        return patch.object(lab_routes, "_fetch_lab", return_value={"id": "lab-1", "definition": definition})

    def test_matching_server_rules_can_pass(self) -> None:
        with self._mock_lab(self._definition()):
            result = lab_routes.check_lab_v2("lab-1", CheckRequest(topology=self._topology("edge-1")))
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 1.0)

    def test_manual_review_cannot_pass_automatically(self) -> None:
        with self._mock_lab(self._definition(check_type="manual_review")):
            result = lab_routes.check_lab_v2("lab-1", CheckRequest(topology=self._topology("edge-1")))
        self.assertFalse(result["passed"])
        self.assertTrue(result["manual_review_required"])

    def test_empty_rule_set_fails_closed(self) -> None:
        with self._mock_lab(self._definition(rules=[])):
            result = lab_routes.check_lab_v2("lab-1", CheckRequest(topology=self._topology("edge-1")))
        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 0.0)

    def test_submit_ignores_forged_client_success(self) -> None:
        request = SubmitRequest(
            topology=self._topology("attacker-value"),
            check_result={"passed": True, "score": 1.0, "results": [{"passed": True}]},
        )
        with self._mock_lab(self._definition()), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            result = lab_routes.submit_lab_v2("lab-1", request)
        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["xp_gained"], 0)
        self.assertEqual(result["badges_unlocked"], [])
        conn = sqlite3.connect(str(self.db_path))
        try:
            passed, result_json = conn.execute("SELECT passed, check_result_json FROM lab_attempts").fetchone()
        finally:
            conn.close()
        self.assertEqual(passed, 0)
        self.assertFalse(json.loads(result_json)["passed"])

    def test_success_reward_is_persisted_once_per_lab(self) -> None:
        request = SubmitRequest(topology=self._topology("edge-1"), check_result={"passed": False})
        with self._mock_lab(self._definition()), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            first = lab_routes.submit_lab_v2("lab-1", request)
            second = lab_routes.submit_lab_v2("lab-1", request)
        self.assertTrue(first["passed"])
        self.assertEqual(first["xp_gained"], 25)
        self.assertEqual(second["xp_gained"], 0)
        conn = sqlite3.connect(str(self.db_path))
        try:
            stats = conn.execute("SELECT total_xp FROM user_stats WHERE id = 1").fetchone()
        finally:
            conn.close()
        self.assertEqual(stats[0], 25)

    def test_vlan_and_cross_cable_survive_schema_validation(self) -> None:
        topology = self._topology("edge-1")
        topology.links.append(Link(
            id="L1",
            **{"from": {"node": "R1", "port": "Fa0/0"}, "to": {"node": "R2", "port": "Fa0/0"}},
            cable_type="copper_crossover",
        ))
        payload = lab_routes.model_to_dict(topology, by_alias=True)
        self.assertEqual(payload["nodes"][0]["ports"][0]["vlan"], 20)
        self.assertEqual(payload["links"][0]["cable_type"], "copper_crossover")

    def test_lab_api_routes_are_not_duplicated(self) -> None:
        endpoints = [
            (method, getattr(route, "path", ""))
            for route in app.routes
            for method in (getattr(route, "methods", set()) or set())
            if getattr(route, "path", "") in {
                "/api/lab/v2/{lab_id}",
                "/api/lab/v2/{lab_id}/check",
                "/api/lab/v2/{lab_id}/submit",
            }
        ]
        self.assertEqual(len(endpoints), 3)
        self.assertEqual(len(set(endpoints)), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
