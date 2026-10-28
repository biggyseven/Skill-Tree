from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api
from app.scenario_loader import list_scenarios, load_scenario


class WarRoomApiTests(unittest.TestCase):
    """Tests d'intégration War Room sur une base jetable."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "war-room.sqlite3"
        self.db_patch = patch.object(api, "DB_PATH", self.db_path)
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

    def _client(self) -> TestClient:
        return TestClient(api.app)

    def test_pilot_scenarios_are_valid_and_every_link_has_both_ports(self) -> None:
        scenarios = list_scenarios()
        self.assertEqual(
            {scenario["id"] for scenario in scenarios},
            {"INC-001", "CHG-001", "PRB-001"},
        )
        for scenario in scenarios:
            self.assertEqual(scenario["initial_topology"]["schema_version"], 2)
            nodes = {node["id"]: node for node in scenario["initial_topology"]["nodes"]}
            self.assertTrue(scenario["resolution_check"]["rules"])
            for link in scenario["initial_topology"]["links"]:
                self.assertIn(link["from"]["node"], nodes)
                self.assertIn(link["to"]["node"], nodes)
                from_ports = {port["id"] for port in nodes[link["from"]["node"]].get("ports", [])}
                to_ports = {port["id"] for port in nodes[link["to"]["node"]].get("ports", [])}
                self.assertIn(link["from"]["port"], from_ports)
                self.assertIn(link["to"]["port"], to_ports)

        self.assertEqual(load_scenario("INC-001")["hidden_faults"][0]["actual_vlan"], 1)
        self.assertIsNone(load_scenario("PRB-001")["sla_minutes"])

    def test_incident_resolution_requires_the_vlan_fix_and_a_postmortem(self) -> None:
        with self._client() as client:
            inbox = client.get("/api/tickets")
            self.assertEqual(inbox.status_code, 200, inbox.text)
            self.assertEqual({item["id"] for item in inbox.json()}, {"INC-001", "CHG-001", "PRB-001"})
            ticket_response = client.get("/api/tickets/INC-001")
            self.assertEqual(ticket_response.status_code, 200, ticket_response.text)
            scenario = ticket_response.json()["scenario"]
            topology = scenario["initial_topology"]

            failed = client.post(
                "/api/tickets/INC-001/resolve",
                json={"topology": topology, "elapsed_seconds": 10},
            )
            self.assertEqual(failed.status_code, 200, failed.text)
            self.assertFalse(failed.json()["passed"])

            sw1 = next(node for node in topology["nodes"] if node["id"] == "SW1")
            fa07 = next(port for port in sw1["ports"] if port["id"] == "Fa0/7")
            fa07["vlan"] = 20
            resolved_config = client.post(
                "/api/tickets/INC-001/resolve",
                json={"topology": topology, "elapsed_seconds": 20},
            )
            self.assertEqual(resolved_config.status_code, 200, resolved_config.text)
            self.assertTrue(resolved_config.json()["passed"])

            incomplete = client.post(
                "/api/tickets/INC-001/post-mortem",
                json={"root_cause": "VLAN incorrect", "impact": "", "corrective_action": "Port corrigé"},
            )
            self.assertEqual(incomplete.status_code, 422)

            closed = client.post(
                "/api/tickets/INC-001/post-mortem",
                json={
                    "root_cause": "Le port SW1 Fa0/7 était resté dans le VLAN 1 au lieu du VLAN 20.",
                    "impact": "Les utilisateurs concernés ne pouvaient plus joindre le serveur ERP.",
                    "corrective_action": "Port remis dans le VLAN 20 et contrôle de connectivité ajouté à la checklist.",
                },
            )
            self.assertEqual(closed.status_code, 200, closed.text)
            self.assertEqual(closed.json()["status"], "resolved")
            self.assertEqual(closed.json()["xp_earned"], 150)

            detail = client.get("/api/tickets/INC-001")
            self.assertEqual(detail.json()["ticket"]["status"], "resolved")
            saved = detail.json()["ticket"]["resolution_data"]
            self.assertIn("post_mortem", saved)
            with sqlite3.connect(self.db_path) as conn:
                self.assertEqual(conn.execute("SELECT total_xp FROM user_stats WHERE id = 1").fetchone()[0], 150)
                actions = conn.execute(
                    "SELECT action_type FROM ticket_actions WHERE ticket_id = ? ORDER BY id",
                    ("INC-001",),
                ).fetchall()
            self.assertIn("configuration_verified", {row[0] for row in actions})
            self.assertIn("post_mortem_submitted", {row[0] for row in actions})
            self.assertNotIn("INC-001", {item["id"] for item in client.get("/api/tickets").json()})

    def test_change_acl_assertion_and_problem_root_cause_validation(self) -> None:
        with self._client() as client:
            change_detail = client.get("/api/tickets/CHG-001")
            self.assertEqual(change_detail.status_code, 200, change_detail.text)
            change_topology = change_detail.json()["scenario"]["initial_topology"]
            r1 = next(node for node in change_topology["nodes"] if node["id"] == "R1")
            r1["config"]["acls"] = ["101 permit tcp any host 10.0.0.5 eq 443"]
            change_check = client.post(
                "/api/tickets/CHG-001/resolve",
                json={"topology": change_topology, "elapsed_seconds": 10},
            )
            self.assertEqual(change_check.status_code, 200, change_check.text)
            self.assertTrue(change_check.json()["passed"])

            problem_detail = client.get("/api/tickets/PRB-001")
            self.assertEqual(problem_detail.status_code, 200, problem_detail.text)
            problem_topology = problem_detail.json()["scenario"]["initial_topology"]
            problem_check = client.post(
                "/api/tickets/PRB-001/resolve",
                json={"topology": problem_topology, "elapsed_seconds": 30},
            )
            self.assertEqual(problem_check.status_code, 200, problem_check.text)
            self.assertTrue(problem_check.json()["passed"])
            rejected = client.post(
                "/api/tickets/PRB-001/post-mortem",
                json={
                    "root_cause": "Un défaut d'alimentation a été suspecté.",
                    "impact": "Le switch était indisponible pendant plusieurs minutes.",
                    "corrective_action": "Une supervision supplémentaire a été planifiée.",
                },
            )
            self.assertEqual(rejected.status_code, 422)
            accepted = client.post(
                "/api/tickets/PRB-001/post-mortem",
                json={
                    "root_cause": "Une boucle STP non bloquée a déclenché une tempête de broadcast.",
                    "impact": "La saturation a perturbé SW1 et interrompu la supervision autour de 02:00.",
                    "corrective_action": "Rétablir STP, supprimer la boucle et ajouter une alerte sur les broadcasts.",
                },
            )
            self.assertEqual(accepted.status_code, 200, accepted.text)
            self.assertEqual(accepted.json()["xp_earned"], 200)


if __name__ == "__main__":
    unittest.main()
