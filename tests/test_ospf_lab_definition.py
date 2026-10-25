from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from app.lab_routes import _evaluate_lab_check
from app.lab_schema_v2 import LabDefinition


ROOT = Path(__file__).resolve().parents[1]
LAB_PATH = ROOT / "labs_v2" / "ospf-3-routers.json"


class OspfLabDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        raw = json.loads(LAB_PATH.read_text(encoding="utf-8-sig"))
        cls.definition = LabDefinition(**raw)

    def configured_topology(self):
        topology = copy.deepcopy(self.definition.initial_topology)
        devices = {node.id: node for node in topology.nodes}
        devices["R1"].config.hostname = "Routeur-Paris"
        addresses = {
            ("R1", "Fa0/0"): "10.0.12.1",
            ("R2", "Fa0/0"): "10.0.12.2",
            ("R2", "Fa0/1"): "10.0.23.1",
            ("R3", "Fa0/0"): "10.0.23.2",
        }
        for (device_id, port_id), address in addresses.items():
            port = next(port for port in devices[device_id].ports if port.id == port_id)
            port.ip = address
            port.mask = "255.255.255.252"
            port.state = "up"
        networks = {
            "R1": ["10.0.12.0/30"],
            "R2": ["10.0.12.0/30", "10.0.23.0/30"],
            "R3": ["10.0.23.0/30"],
        }
        for device_id, declared_networks in networks.items():
            ospf = devices[device_id].config.ospf
            ospf.enabled = True
            ospf.areas = [{"area": 0, "network": network} for network in declared_networks]
        return topology

    def test_complete_ospf_configuration_passes(self) -> None:
        result = _evaluate_lab_check(self.definition, self.configured_topology())
        self.assertTrue(result["passed"], result["results"])
        self.assertEqual(result["score"], 1.0)

    def test_every_routed_interface_must_be_up(self) -> None:
        targets = [
            ("R1", "Fa0/0", "r1_fa00_state"),
            ("R2", "Fa0/0", "r2_fa00_state"),
            ("R2", "Fa0/1", "r2_fa01_state"),
            ("R3", "Fa0/0", "r3_fa00_state"),
        ]
        for device_id, port_id, rule_id in targets:
            with self.subTest(device=device_id, port=port_id):
                topology = self.configured_topology()
                device = next(node for node in topology.nodes if node.id == device_id)
                next(port for port in device.ports if port.id == port_id).state = "down"
                result = _evaluate_lab_check(self.definition, topology)
                self.assertFalse(result["passed"])
                failed_rules = {rule["rule_id"] for rule in result["results"] if not rule["passed"]}
                self.assertIn(rule_id, failed_rules)

    def test_each_router_must_advertise_its_required_ospf_networks(self) -> None:
        topology = self.configured_topology()
        r2 = next(node for node in topology.nodes if node.id == "R2")
        r2.config.ospf.areas = [{"area": 0, "network": "10.0.12.0/30"}]
        result = _evaluate_lab_check(self.definition, topology)
        self.assertFalse(result["passed"])
        failed_rules = {rule["rule_id"] for rule in result["results"] if not rule["passed"]}
        self.assertIn("r2_ospf_10_0_23_0_30_area0", failed_rules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
