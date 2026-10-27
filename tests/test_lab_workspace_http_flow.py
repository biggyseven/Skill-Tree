from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
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
            conn.execute(
                """
                CREATE TABLE topologies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    updated_at TEXT NOT NULL
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

    def test_unknown_lab_id_returns_404_instead_of_a_fictitious_sandbox(self) -> None:
        with TestClient(api.app) as client:
            response = client.get("/api/lab/v2/lab-id-that-does-not-exist")

        self.assertEqual(response.status_code, 404, response.text)
        self.assertIn("introuvable", response.json()["detail"].lower())

    def test_node_detail_exposes_v2_lab_when_legacy_metadata_is_missing(self) -> None:
        node_id = "test-v2-course-without-legacy-lab"
        definition = SimpleNamespace(
            prompt="Configurez le trunk entre les deux commutateurs.",
            hints=["Créez le VLAN 10.", "Vérifiez le mode trunk."],
            duration_min=20,
            difficulty="intermédiaire",
            level="intermédiaire",
            initial_topology=SimpleNamespace(nodes=[SimpleNamespace(id="SW1")]),
        )

        with TestClient(api.app) as client:
            conn = api.connect(self.db_path)
            try:
                conn.execute(
                    "INSERT INTO nodes (id, title, description, category, module, sort_order) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (node_id, "Lab V2 sans métadonnées historiques", "Description de test", "Réseaux", "Test", 9999),
                )
                conn.execute(
                    "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
                    (node_id, "lab", 100),
                )
                conn.commit()
            finally:
                conn.close()

            with patch(
                "app.api._fetch_lab",
                return_value={"id": node_id, "definition": definition},
            ):
                response = client.get(f"/api/node/{node_id}")

        self.assertEqual(response.status_code, 200, response.text)
        lab = response.json()["lab"]
        self.assertIsNotNone(lab)
        self.assertEqual(lab["kind"], "workspace-v2")
        self.assertEqual(lab["prompt"], definition.prompt)
        self.assertEqual(lab["hint"], "\n".join(definition.hints))
        self.assertEqual(lab["duration"], "20 min")
        self.assertEqual(lab["difficulty"], "intermédiaire")
        self.assertTrue(lab["workspace_v2"])

    def test_open_save_reload_check_and_submit_real_ipv4_scenario_over_http(self) -> None:
        unlocked_course = {
            "min_score": 100,
            "unlocked": True,
            "missing_prerequisites": [],
        }
        with patch("app.lab_routes._course_lab_context", return_value=unlocked_course), TestClient(api.app) as client:
            opened = client.get("/api/lab/v2/ipv4-debutant")
            self.assertEqual(opened.status_code, 200, opened.text)
            payload = opened.json()
            self.assertFalse(payload.get("sandbox", False))
            self.assertEqual(payload["id"], "ipv4-debutant")
            topology = payload["initial_topology"]
            node_ids = {node["id"] for node in topology["nodes"]}
            self.assertTrue({"PC-A", "SW1", "PC-B"}.issubset(node_ids))
            self.assertEqual(len(topology["nodes"]), 3)
            self.assertEqual(len(topology["links"]), 2)
            self.assertFalse(any(node_id.startswith("EXT-") for node_id in node_ids))
            self.assertFalse(any(link["id"].startswith("EXT-LINK-") for link in topology["links"]))

            saved = client.post(
                "/api/lab/v2/ipv4-debutant/save",
                json={"topology": topology},
            )
            self.assertEqual(saved.status_code, 200, saved.text)
            self.assertTrue(saved.json()["success"])

            # Une simple réouverture doit reprendre la sauvegarde sans action manuelle
            # sur le bouton « Charger ».
            reopened = client.get("/api/lab/v2/ipv4-debutant")
            self.assertEqual(reopened.status_code, 200, reopened.text)
            self.assertTrue(reopened.json()["has_saved_topology"])
            self.assertEqual(reopened.json()["initial_topology"], topology)

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


    def test_valid_ipv4_configuration_passes_and_rewards_only_once_over_http(self) -> None:
        unlocked_course = {
            "min_score": 100,
            "unlocked": True,
            "missing_prerequisites": [],
        }
        with patch("app.lab_routes._course_lab_context", return_value=unlocked_course), TestClient(api.app) as client:
            opened = client.get("/api/lab/v2/ipv4-debutant")
            self.assertEqual(opened.status_code, 200, opened.text)
            payload = opened.json()
            self.assertFalse(payload.get("sandbox", False))
            topology = payload["initial_topology"]
            nodes = {node["id"]: node for node in topology["nodes"]}

            # Reproduire les modifications attendues de l'onglet Hardware :
            # IP + masque sur les deux PC, puis activation des quatre interfaces.
            for device_id, address in (
                ("PC-A", "192.168.10.10"),
                ("PC-B", "192.168.10.20"),
            ):
                port = nodes[device_id]["ports"][0]
                port["ip"] = address
                port["mask"] = "255.255.255.0"
                port["state"] = "up"
            for port in nodes["SW1"]["ports"]:
                port["state"] = "up"

            checked = client.post(
                "/api/lab/v2/ipv4-debutant/check",
                json={"topology": topology},
            )
            self.assertEqual(checked.status_code, 200, checked.text)
            check_result = checked.json()
            self.assertTrue(check_result["passed"], check_result)
            self.assertEqual(check_result["score"], 1.0)
            self.assertEqual(len(check_result["results"]), 8)
            self.assertTrue(all(item["passed"] for item in check_result["results"]))

            first_response = client.post(
                "/api/lab/v2/ipv4-debutant/submit",
                json={"topology": topology, "check_result": check_result},
            )
            self.assertEqual(first_response.status_code, 200, first_response.text)
            first = first_response.json()
            self.assertTrue(first["passed"], first)
            self.assertTrue(first["attempt_recorded"])
            self.assertTrue(first["first_success"])
            self.assertEqual(first["xp_gained"], 25)
            self.assertEqual(first["coins_gained"], 20)

            # Une deuxième soumission doit être enregistrée, sans doubler les primes.
            second_response = client.post(
                "/api/lab/v2/ipv4-debutant/submit",
                json={"topology": topology, "check_result": check_result},
            )
            self.assertEqual(second_response.status_code, 200, second_response.text)
            second = second_response.json()
            self.assertTrue(second["passed"], second)
            self.assertTrue(second["attempt_recorded"])
            self.assertFalse(second["first_success"])
            self.assertEqual(second["xp_gained"], 0)
            self.assertEqual(second["coins_gained"], 0)

        with sqlite3.connect(self.db_path) as conn:
            attempts = conn.execute(
                "SELECT passed FROM lab_attempts WHERE lab_id = 'ipv4-debutant' ORDER BY started_at, id"
            ).fetchall()
            stats = conn.execute(
                "SELECT total_xp, coins FROM user_stats WHERE id = 1"
            ).fetchone()
        self.assertEqual([row[0] for row in attempts], [1, 1])
        self.assertEqual(tuple(stats), (25, 20))


if __name__ == "__main__":
    unittest.main(verbosity=2)
