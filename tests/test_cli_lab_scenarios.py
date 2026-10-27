from __future__ import annotations

import json
import sqlite3
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from app import lab_routes
from app.lab_routes import _path_tokens, evaluate_rules
from app.lab_schema_v2 import LabDefinition, model_to_dict

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "cli-ipv4-interfaces", "cli-vlan-access", "cli-vlan-trunk", "cli-static-routing",
    "cli-ospf-area", "cli-bgp-neighbor", "cli-eigrp-network", "cli-acl-interface",
    "cli-dhcp-pool", "cli-dns-host-records", "cli-nat-overload", "cli-ipv6-interface",
    "cli-stp-hardening", "cli-hsrp-gateway", "cli-port-security", "cli-ntp-syslog",
    "cli-qos-voice-policy",
)

def _set_path(root: dict[str, Any], device: str, path: str, value: Any) -> None:
    current: Any = root
    if device:
        current = next(item for item in root["nodes"] if item["id"] == device)
    tokens = _path_tokens(path)
    for index, token in enumerate(tokens[:-1]):
        next_token = tokens[index + 1]
        if isinstance(token, int):
            while len(current) <= token:
                current.append({} if not isinstance(next_token, int) else [])
            current = current[token]
        else:
            if token not in current or current[token] is None:
                current[token] = [] if isinstance(next_token, int) else {}
            current = current[token]
    last = tokens[-1]
    if isinstance(last, int):
        while len(current) <= last:
            current.append({})
        current[last] = value
    else:
        current[last] = value

def _append_path(root: dict[str, Any], device: str, path: str, value: Any) -> None:
    current: Any = root
    if device:
        current = next(item for item in root["nodes"] if item["id"] == device)
    tokens = _path_tokens(path)
    for index, token in enumerate(tokens):
        if isinstance(token, int):
            while len(current) <= token:
                current.append({})
            current = current[token]
        elif index == len(tokens) - 1:
            if token not in current or current[token] is None:
                current[token] = []
            current = current[token]
        else:
            if token not in current or current[token] is None:
                current[token] = [] if isinstance(tokens[index + 1], int) else {}
            current = current[token]
    if not isinstance(current, list):
        raise AssertionError(f"{path} should resolve to a list")
    current.append(value)

class CLIScenarioServerCheckTests(unittest.TestCase):
    def test_cli_scenarios_appear_in_the_catalog_without_course_nodes(self) -> None:
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        with patch.object(lab_routes, "_database_connection", return_value=conn):
            catalog = lab_routes.list_labs_v2()
        visible_ids = {item["id"] for item in catalog}
        self.assertTrue(set(SCENARIOS).issubset(visible_ids),
                        f"Scénarios CLI absents du catalogue : {sorted(set(SCENARIOS) - visible_ids)}")

    def test_all_seventeen_scenarios_use_automatic_structured_assertions(self) -> None:
        self.assertEqual(len(SCENARIOS), 17)
        for scenario_id in SCENARIOS:
            with self.subTest(scenario=scenario_id):
                payload = json.loads((ROOT / "labs_v2" / f"{scenario_id}.json").read_text(encoding="utf-8"))
                definition = LabDefinition(**payload)
                self.assertEqual(definition.id, scenario_id)
                self.assertEqual(definition.check.type, "config_assertions")
                self.assertGreater(len(definition.initial_topology.nodes), 0)
                self.assertGreater(len(definition.check.rules), 0)

                initial = model_to_dict(definition.initial_topology, by_alias=True)
                baseline = evaluate_rules(initial, definition.check.rules)
                self.assertFalse(all(item["passed"] for item in baseline), "un état initial ne doit pas valider le lab")

                expected_state = json.loads(json.dumps(initial))
                for rule in definition.check.rules:
                    item = model_to_dict(rule) if hasattr(rule, "model_dump") or hasattr(rule, "dict") else dict(rule)
                    if item["operator"] == "contains":
                        _append_path(expected_state, item["device"], item["path"], item["expected"])
                    elif item["operator"] == "equals":
                        _set_path(expected_state, item["device"], item["path"], item["expected"])
                    else:
                        self.fail(f"{scenario_id}: opérateur non testé {item['operator']}")

                results = evaluate_rules(expected_state, definition.check.rules)
                failures = [item for item in results if not item["passed"]]
                self.assertEqual(failures, [], f"{scenario_id}: {failures}")

if __name__ == "__main__":
    unittest.main()
