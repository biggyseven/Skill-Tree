from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABS_DIR = ROOT / "labs_v2"


class LabV2CatalogIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payloads = {
            path.stem: (path, json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(LABS_DIR.glob("*.json"))
        }

    def test_primary_lab_json_files_parse_and_have_unique_ids(self) -> None:
        ids = [payload.get("id") for _, payload in self.payloads.values()]
        self.assertTrue(self.payloads, "Aucun laboratoire v2 trouvé.")
        self.assertTrue(all(ids), "Un laboratoire v2 ne possède pas d’identifiant.")
        self.assertEqual(len(ids), len(set(ids)), "Des identifiants de lab v2 sont dupliqués.")
        for filename, (path, payload) in self.payloads.items():
            with self.subTest(file=path.name):
                self.assertEqual(payload.get("schema_version"), 2, f"{path.name}: schéma v2 attendu.")
                self.assertTrue(payload.get("title"), f"{path.name}: titre manquant.")
                self.assertIn("initial_topology", payload, f"{path.name}: topologie initiale manquante.")
                self.assertTrue(payload.get("check", {}).get("rules"), f"{path.name}: contrôles absents.")

    def test_all_links_reference_existing_ports_and_match_endpoint_states(self) -> None:
        for filename, (path, payload) in self.payloads.items():
            topology = payload.get("initial_topology") or {}
            nodes = topology.get("nodes") or []
            nodes_by_id = {str(node.get("id", "")): node for node in nodes}
            nodes_by_name = {}
            for node in nodes:
                for name in (node.get("label"), (node.get("config") or {}).get("hostname")):
                    if name:
                        nodes_by_name[str(name)] = node

            with self.subTest(file=path.name):
                for link in topology.get("links") or []:
                    source = link.get("from") or link.get("from_endpoint") or {}
                    target = link.get("to") or link.get("to_endpoint") or {}
                    source_node = nodes_by_id.get(str(source.get("node", ""))) or nodes_by_name.get(str(source.get("node", "")))
                    target_node = nodes_by_id.get(str(target.get("node", ""))) or nodes_by_name.get(str(target.get("node", "")))
                    self.assertIsNotNone(source_node, f"{path.name}/{link.get('id')}: source inconnue {source.get('node')!r}.")
                    self.assertIsNotNone(target_node, f"{path.name}/{link.get('id')}: destination inconnue {target.get('node')!r}.")
                    source_port = next((p for p in (source_node or {}).get("ports", []) if p.get("id") == source.get("port") or p.get("name") == source.get("port")), None)
                    target_port = next((p for p in (target_node or {}).get("ports", []) if p.get("id") == target.get("port") or p.get("name") == target.get("port")), None)
                    self.assertIsNotNone(source_port, f"{path.name}/{link.get('id')}: source port inconnu {source.get('node')}.{source.get('port')}.")
                    self.assertIsNotNone(target_port, f"{path.name}/{link.get('id')}: port destination inconnu {target.get('node')}.{target.get('port')}.")
                    source_up = (source_port or {}).get("state", "down") == "up"
                    target_up = (target_port or {}).get("state", "down") == "up"
                    expected_state = "up" if source_up and target_up else "down"
                    self.assertEqual(
                        link.get("state", "up"),
                        expected_state,
                        f"{path.name}/{link.get('id')}: l’état du câble doit être {expected_state} "
                        "selon les états de ses deux ports d’extrémité.",
                    )

    def test_dhcp_nat_checks_the_structured_state_written_by_cli(self) -> None:
        _, payload = self.payloads["dhcp-nat"]
        rules = payload.get("check", {}).get("rules", [])
        pool_rule = next((rule for rule in rules if rule.get("path") == "config.protocols.dhcp.pools"), None)
        self.assertIsNotNone(pool_rule, "Le contrôle DHCP doit cibler les pools structurés écrits par la CLI.")
        self.assertEqual((pool_rule or {}).get("operator"), "contains")
        expected = (pool_rule or {}).get("expected") or {}
        self.assertEqual(expected.get("name"), "LAN-CLIENTS")
        self.assertEqual(expected.get("network"), "192.168.1.0")
        self.assertEqual(expected.get("mask"), "255.255.255.0")
        self.assertEqual(expected.get("default_router"), "192.168.1.1")
        self.assertEqual(expected.get("dns_server"), "192.168.1.53")
        self.assertEqual(expected.get("lease_days"), 7)
        self.assertFalse(any("pas prises en charge" in hint for hint in payload.get("hints", [])))

    def test_cli_trunk_lab_has_two_switches_and_checks_both_ends(self) -> None:
        _, payload = self.payloads["cli-vlan-trunk"]
        topology = payload.get("initial_topology") or {}
        switches = {node.get("id") for node in topology.get("nodes", []) if node.get("type") == "switch"}
        self.assertTrue({"SW1", "SW2"} <= switches, "Le scénario de trunk doit représenter les deux commutateurs.")
        links = topology.get("links") or []
        self.assertTrue(any(
            {((link.get("from") or {}).get("node")), ((link.get("to") or {}).get("node"))} == {"SW1", "SW2"}
            for link in links
        ), "Aucun câble inter-switch entre SW1 et SW2.")
        rules = payload.get("check", {}).get("rules", [])
        self.assertTrue(any(r.get("device") == "SW1" and r.get("path") == "ports[1].mode" and r.get("expected") == "trunk" for r in rules))
        self.assertTrue(any(r.get("device") == "SW2" and r.get("path") == "ports[1].mode" and r.get("expected") == "trunk" for r in rules))


if __name__ == "__main__":
    unittest.main()
