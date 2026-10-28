from __future__ import annotations

import json
import sqlite3
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api
import app.scenario_loader as scenario_loader
from app.scenario_loader import list_scenarios, load_scenario


class WarRoomApiTests(unittest.TestCase):
    """Tests d'intégration War Room sur une base jetable."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "war-room.sqlite3"
        self.scenario_dir = Path(self.temp_dir.name) / "scenarios"
        self.scenario_dir.mkdir()
        source_scenarios = scenario_loader.SCENARIO_DIR
        for source in source_scenarios.glob("*.json"):
            shutil.copy2(source, self.scenario_dir / source.name)

        self.db_patch = patch.object(api, "DB_PATH", self.db_path)
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        self.loader_scenarios_patch = patch.object(scenario_loader, "SCENARIO_DIR", self.scenario_dir)
        self.loader_scenarios_patch.start()
        self.addCleanup(self.loader_scenarios_patch.stop)
        self.api_scenarios_patch = patch.object(api, "SCENARIO_DIR", self.scenario_dir)
        self.api_scenarios_patch.start()
        self.addCleanup(self.api_scenarios_patch.stop)

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
            self.assertEqual(failed.json()["reason"], "config_incorrect")

            # Un échec est désormais terminal : le workflow de récupération passe par Rejouer.
            replay = client.post("/api/tickets/INC-001/replay")
            self.assertEqual(replay.status_code, 200, replay.text)
            ticket_id = replay.json()["new_ticket_id"]
            self.assertNotEqual(ticket_id, "INC-001")

            sw1 = next(node for node in topology["nodes"] if node["id"] == "SW1")
            fa07 = next(port for port in sw1["ports"] if port["id"] == "Fa0/7")
            fa07["vlan"] = 20
            resolved_config = client.post(
                f"/api/tickets/{ticket_id}/resolve",
                json={"topology": topology, "elapsed_seconds": 20},
            )
            self.assertEqual(resolved_config.status_code, 200, resolved_config.text)
            self.assertTrue(resolved_config.json()["passed"])

            incomplete = client.post(
                f"/api/tickets/{ticket_id}/post-mortem",
                json={"root_cause": "VLAN incorrect", "impact": "", "corrective_action": "Port corrigé"},
            )
            self.assertEqual(incomplete.status_code, 422)

            closed = client.post(
                f"/api/tickets/{ticket_id}/post-mortem",
                json={
                    "root_cause": "Le port SW1 Fa0/7 était resté dans le VLAN 1 au lieu du VLAN 20.",
                    "impact": "Les utilisateurs concernés ne pouvaient plus joindre le serveur ERP.",
                    "corrective_action": "Port remis dans le VLAN 20 et contrôle de connectivité ajouté à la checklist.",
                },
            )
            self.assertEqual(closed.status_code, 200, closed.text)
            self.assertEqual(closed.json()["status"], "resolved")
            self.assertEqual(closed.json()["xp_earned"], 150)

            detail = client.get(f"/api/tickets/{ticket_id}")
            self.assertEqual(detail.json()["ticket"]["status"], "resolved")
            saved = detail.json()["ticket"]["resolution_data"]
            self.assertIn("post_mortem", saved)
            with sqlite3.connect(self.db_path) as conn:
                self.assertEqual(conn.execute("SELECT total_xp FROM user_stats WHERE id = 1").fetchone()[0], 150)
                actions = conn.execute(
                    "SELECT action_type FROM ticket_actions WHERE ticket_id = ? ORDER BY id",
                    (ticket_id,),
                ).fetchall()
            self.assertIn("configuration_verified", {row[0] for row in actions})
            self.assertIn("post_mortem_submitted", {row[0] for row in actions})
            self.assertNotIn(ticket_id, {item["id"] for item in client.get("/api/tickets").json()})

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


    def test_itms_stats_archive_and_replay_create_a_fresh_ticket(self) -> None:
        with self._client() as client:
            detail = client.get("/api/tickets/INC-001")
            self.assertEqual(detail.status_code, 200, detail.text)
            topology = detail.json()["scenario"]["initial_topology"]
            sw1 = next(node for node in topology["nodes"] if node["id"] == "SW1")
            next(port for port in sw1["ports"] if port["id"] == "Fa0/7")["vlan"] = 20

            checked = client.post(
                "/api/tickets/INC-001/resolve",
                json={"topology": topology, "elapsed_seconds": 12},
            )
            self.assertEqual(checked.status_code, 200, checked.text)
            self.assertTrue(checked.json()["passed"], checked.json())

            closed = client.post(
                "/api/tickets/INC-001/post-mortem",
                json={
                    "root_cause": "Le port SW1 Fa0/7 était dans le VLAN 1 au lieu du VLAN 20.",
                    "impact": "Les utilisateurs ne pouvaient plus joindre le serveur ERP.",
                    "corrective_action": "Port remis dans le VLAN 20 et contrôle de connectivité ajouté.",
                },
            )
            self.assertEqual(closed.status_code, 200, closed.text)

            stats_response = client.get("/api/itsm/stats")
            self.assertEqual(stats_response.status_code, 200, stats_response.text)
            stats = stats_response.json()
            self.assertEqual(stats["total_resolved"], 1)
            self.assertEqual(stats["total_failed"], 0)
            self.assertGreaterEqual(stats["mttr_minutes"], 0)
            self.assertEqual(stats["sla_compliance_pct"], 100.0)
            self.assertGreaterEqual(stats["incidents_today"], 3)
            self.assertEqual(stats["recent_resolved"][0]["id"], "INC-001")
            self.assertIsNotNone(stats["recent_resolved"][0]["duration_seconds"])

            archive_response = client.get("/api/tickets/archive")
            self.assertEqual(archive_response.status_code, 200, archive_response.text)
            archived = next(item for item in archive_response.json() if item["id"] == "INC-001")
            self.assertEqual(archived["status"], "resolved")
            self.assertEqual(archived["title"], "VLAN 20 injoignable depuis 08:05")

            replay = client.post("/api/tickets/INC-001/replay")
            self.assertEqual(replay.status_code, 200, replay.text)
            self.assertTrue(replay.json()["success"])
            new_ticket_id = replay.json()["new_ticket_id"]
            self.assertNotEqual(new_ticket_id, "INC-001")
            new_detail = client.get(f"/api/tickets/{new_ticket_id}")
            self.assertEqual(new_detail.status_code, 200, new_detail.text)
            new_ticket = new_detail.json()["ticket"]
            self.assertEqual(new_ticket["status"], "open")
            self.assertIsNotNone(new_ticket["sla_deadline"])
            self.assertNotEqual(new_ticket["opened_at"], detail.json()["ticket"]["opened_at"])
            inbox_ids = {item["id"] for item in client.get("/api/tickets").json()}
            self.assertIn(new_ticket_id, inbox_ids)
            self.assertNotIn("INC-001", {item["id"] for item in client.get("/api/tickets/archive").json()})

    def test_resolution_failures_and_expired_sla_are_archived_as_failed(self) -> None:
        with self._client() as client:
            # Une configuration incorrecte doit clôturer le ticket en échec.
            incident = client.get("/api/tickets/INC-001").json()
            rejected = client.post(
                "/api/tickets/INC-001/resolve",
                json={"topology": incident["scenario"]["initial_topology"], "elapsed_seconds": 10},
            )
            self.assertEqual(rejected.status_code, 200, rejected.text)
            self.assertFalse(rejected.json()["passed"])
            self.assertEqual(rejected.json()["reason"], "config_incorrect")
            with sqlite3.connect(self.db_path) as conn:
                self.assertEqual(conn.execute("SELECT status FROM tickets WHERE id = 'INC-001'").fetchone()[0], "failed")

            # L'expiration est matérialisée lors de la prochaine lecture de l'inbox/archive.
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE tickets SET sla_deadline = ? WHERE id = 'CHG-001'",
                    ("2000-01-01T00:00:00Z",),
                )
                conn.commit()
            archive = client.get("/api/tickets/archive")
            self.assertEqual(archive.status_code, 200, archive.text)
            expired = next(item for item in archive.json() if item["id"] == "CHG-001")
            self.assertEqual(expired["status"], "failed")
            with sqlite3.connect(self.db_path) as conn:
                status, resolution_data = conn.execute(
                    "SELECT status, resolution_data FROM tickets WHERE id = 'CHG-001'"
                ).fetchone()
            self.assertEqual(status, "failed")
            self.assertEqual(json.loads(resolution_data)["reason"], "sla_exceeded")

    def test_resolve_after_deadline_returns_sla_exceeded_reason(self) -> None:
        with self._client() as client:
            detail = client.get("/api/tickets/CHG-001")
            self.assertEqual(detail.status_code, 200, detail.text)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE tickets SET sla_deadline = ? WHERE id = 'CHG-001'",
                    ("2000-01-01T00:00:00Z",),
                )
                conn.commit()
            response = client.post(
                "/api/tickets/CHG-001/resolve",
                json={"topology": detail.json()["scenario"]["initial_topology"], "elapsed_seconds": 10},
            )
            self.assertEqual(response.status_code, 200, response.text)
            self.assertFalse(response.json()["passed"])
            self.assertEqual(response.json()["reason"], "sla_exceeded")
            with sqlite3.connect(self.db_path) as conn:
                self.assertEqual(conn.execute("SELECT status FROM tickets WHERE id = 'CHG-001'").fetchone()[0], "failed")



    def test_random_ticket_is_persisted_in_database_without_a_scenario_file(self) -> None:
        with self._client() as client:
            response = client.post("/api/tickets/random")
            self.assertEqual(response.status_code, 200, response.text)
            payload = response.json()
            ticket_id = payload["ticket_id"]
            scenario = payload["scenario"]
            self.assertTrue(ticket_id.startswith("RND-"))
            self.assertEqual(scenario["id"], ticket_id)
            self.assertGreaterEqual(scenario["sla_minutes"], 20)
            self.assertLessEqual(scenario["sla_minutes"], 45)
            self.assertGreaterEqual(scenario["reward_xp"], 100)
            self.assertLessEqual(scenario["reward_xp"], 200)
            self.assertEqual(len(scenario["diagnostic_steps"]), 3)
            self.assertEqual(
                set(scenario["post_mortem_template"]),
                {"root_cause", "impact", "corrective_action"},
            )
            self.assertFalse((self.scenario_dir / f"{ticket_id}.json").exists())

            with sqlite3.connect(self.db_path) as conn:
                stored = conn.execute(
                    "SELECT scenario_json FROM war_room_scenarios WHERE scenario_id = ?",
                    (ticket_id,),
                ).fetchone()
            self.assertIsNotNone(stored)
            self.assertEqual(json.loads(stored[0])["id"], ticket_id)

            detail = client.get(f"/api/tickets/{ticket_id}")
            self.assertEqual(detail.status_code, 200, detail.text)
            self.assertEqual(detail.json()["scenario"]["fault_id"], scenario["fault_id"])
            opened = client.post(f"/api/tickets/{ticket_id}/open")
            self.assertEqual(opened.status_code, 200, opened.text)
            self.assertTrue(opened.json()["existing"])

    def test_scenario_creation_shutdown_fix_export_and_import(self) -> None:
        request_body = {
            "name": "SW1 Fa0/7 désactivé après maintenance",
            "type": "incident",
            "severity": "normal",
            "topology": "lan_simple",
            "fault_id": "port_shutdown",
            "target_device": "SW1",
            "target_port": "Fa0/7",
            "sla_minutes": 30,
        }
        with self._client() as client:
            saved = client.post("/api/scenarios/save", json=request_body)
            self.assertEqual(saved.status_code, 200, saved.text)
            saved_payload = saved.json()
            scenario_id = saved_payload["scenario_id"]
            self.assertTrue(scenario_id.startswith("USER-"))
            self.assertTrue((self.scenario_dir / f"{scenario_id}.json").is_file())
            file_content = json.loads((self.scenario_dir / f"{scenario_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(file_content["id"], scenario_id)

            listed = client.get("/api/scenarios/list")
            self.assertEqual(listed.status_code, 200, listed.text)
            personal = next(item for item in listed.json() if item["id"] == scenario_id)
            self.assertTrue(personal["is_user_created"])

            opened = client.post(f"/api/tickets/{scenario_id}/open")
            self.assertEqual(opened.status_code, 200, opened.text)
            ticket_id = opened.json()["ticket"]["id"]
            topology = opened.json()["scenario"]["initial_topology"]
            sw1 = next(node for node in topology["nodes"] if node["id"] == "SW1")
            fa07 = next(port for port in sw1["ports"] if port["id"] == "Fa0/7")
            self.assertEqual(fa07["state"], "down")
            fa07["state"] = "up"  # Même résultat que la commande CLI « no shutdown ».
            resolved = client.post(
                f"/api/tickets/{ticket_id}/resolve",
                json={"topology": topology, "elapsed_seconds": 1},
            )
            self.assertEqual(resolved.status_code, 200, resolved.text)
            self.assertTrue(resolved.json()["passed"], resolved.json())

            exported = client.get(f"/api/scenarios/{scenario_id}/export")
            self.assertEqual(exported.status_code, 200, exported.text)
            self.assertIn(f'filename="{scenario_id}.json"', exported.headers.get("content-disposition", ""))
            exported_scenario = exported.json()
            self.assertEqual(exported_scenario["id"], scenario_id)

            imported = client.post("/api/scenarios/import", json=exported_scenario)
            self.assertEqual(imported.status_code, 200, imported.text)
            imported_id = imported.json()["scenario_id"]
            self.assertTrue(imported_id.startswith("USER-"))
            self.assertNotEqual(imported_id, scenario_id)
            self.assertTrue((self.scenario_dir / f"{imported_id}.json").is_file())
            listed_after_import = client.get("/api/scenarios/list").json()
            self.assertTrue(next(item for item in listed_after_import if item["id"] == imported_id)["is_user_created"])

    def test_fault_options_are_filtered_by_topology_and_keep_the_eight_faults(self) -> None:
        with self._client() as client:
            response = client.get("/api/scenarios/options")
            self.assertEqual(response.status_code, 200, response.text)
            options = response.json()
            self.assertEqual(len(options["faults"]), 8)
            faults = {item["id"]: item for item in options["faults"]}
            self.assertNotIn("lan_simple", faults["trunk_missing"]["topologies"])
            self.assertNotIn("lan_wan", faults["trunk_missing"]["topologies"])
            self.assertEqual(faults["trunk_missing"]["topologies"], ["multi_vlan"])
            self.assertIn(
                {"id": "Fa0/7", "label": "Fa0/7"},
                next(target for target in options["targets"]["lan_simple"]["port_shutdown"] if target["id"] == "SW1")["ports"],
            )


    def test_base_topologies_do_not_reuse_a_physical_port_for_multiple_links(self) -> None:
        from app.scenario_loader import BASE_TOPOLOGIES

        for topology_id, model in BASE_TOPOLOGIES.items():
            used_ports = []
            for link in model["topology"]["links"]:
                used_ports.append((link["from"]["node"], link["from"]["port"]))
                used_ports.append((link["to"]["node"], link["to"]["port"]))
            self.assertEqual(
                len(used_ports),
                len(set(used_ports)),
                f"La topologie {topology_id} réutilise un port physique sur plusieurs liaisons.",
            )

    def test_all_eight_faults_start_broken_and_have_a_repairable_rule(self) -> None:
        from app.scenario_faults import SCENARIO_FAULTS
        from app.scenario_loader import BASE_TOPOLOGIES, build_scenario, get_scenario_options

        options = get_scenario_options()
        self.assertEqual(len(SCENARIO_FAULTS), 8)
        for fault_id in SCENARIO_FAULTS:
            compatible_topology = next(
                topology_id for topology_id, faults in options["targets"].items()
                if faults.get(fault_id)
            )
            target = options["targets"][compatible_topology][fault_id][0]
            target_port = target["ports"][0]["id"]
            scenario = build_scenario(
                scenario_id="RND-UNIT-TEST",
                title=f"Test {fault_id}",
                scenario_type="incident",
                severity="normal",
                topology_id=compatible_topology,
                fault_id=fault_id,
                target_device=target["id"],
                target_port=target_port,
                sla_minutes=30,
            )
            device = next(node for node in scenario["initial_topology"]["nodes"] if node["id"] == target["id"])
            port = next(port for port in device["ports"] if port["id"] == target_port)
            self.assertFalse(
                SCENARIO_FAULTS[fault_id]["fix_validator"](device, port),
                f"{fault_id} doit être réellement injectée",
            )
            rule = scenario["resolution_check"]["rules"][0]
            if fault_id == "vlan_mismatch":
                port["vlan"] = rule["value"]
            elif fault_id == "port_shutdown":
                port["state"] = "up"
            elif fault_id == "ip_wrong":
                port["ip"] = rule["value"]
            elif fault_id == "acl_missing":
                device["config"].setdefault("acls", []).append(f"101 {rule['value']}")
            elif fault_id == "trunk_missing":
                device["config"]["interfaces"][target_port]["mode"] = "trunk"
                port["mode"] = "trunk"
            elif fault_id == "ospf_down":
                device["config"]["interfaces"][target_port]["ospf_enabled"] = True
            elif fault_id == "default_gateway_missing":
                device["config"]["gateway"] = rule["value"]
            elif fault_id == "dhcp_off":
                device["config"]["dhcp_enabled"] = True

            checks = api._scenario_topology_checks(scenario, scenario["initial_topology"])
            self.assertTrue(all(item["passed"] for item in checks), f"{fault_id}: {checks}")
            self.assertIn(compatible_topology, BASE_TOPOLOGIES)

if __name__ == "__main__":
    unittest.main()
