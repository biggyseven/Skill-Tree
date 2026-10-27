from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api, db, lab_routes


ROOT = Path(__file__).resolve().parents[1]
CLI_SCENARIOS = sorted((ROOT / "labs_v2").glob("cli-*.json"))


def _path_tokens(path: str) -> list[str | int]:
    tokens: list[str | int] = []
    for segment in path.split("."):
        import re
        match = re.fullmatch(r"([^\[\]]+)?(?:\[(\d+)\])?", segment)
        if not match:
            raise AssertionError(f"Chemin de règle non pris en charge: {path}")
        name, index = match.groups()
        if name:
            tokens.append(name)
        if index is not None:
            tokens.append(int(index))
    return tokens


def _root_for_device(topology: dict, device_name: str) -> dict:
    if not device_name:
        return topology
    return next(
        (node for node in topology.get("nodes", [])
         if node.get("id") == device_name
         or node.get("label") == device_name
         or (node.get("config") or {}).get("hostname") == device_name),
        None,
    )


def _resolve_parent(topology: dict, device: str, path: str):
    current = _root_for_device(topology, device)
    if current is None:
        raise AssertionError(f"Périphérique absent: {device}")
    tokens = _path_tokens(path)
    for token in tokens[:-1]:
        if isinstance(token, int):
            while len(current) <= token:
                current.append({})
            current = current[token]
        else:
            if token not in current or current[token] is None:
                next_token = tokens[tokens.index(token) + 1]
                current[token] = [] if isinstance(next_token, int) else {}
            current = current[token]
    return current, tokens[-1]


def _set_rule_value(topology: dict, rule: dict, value) -> None:
    parent, key = _resolve_parent(topology, rule.get("device", ""), rule["path"])
    if isinstance(key, int):
        while len(parent) <= key:
            parent.append({})
        parent[key] = value
    else:
        parent[key] = value


def _append_rule_value(topology: dict, rule: dict, value) -> None:
    parent, key = _resolve_parent(topology, rule.get("device", ""), rule["path"])
    if isinstance(key, int):
        raise AssertionError("contains ne doit pas terminer par un index dans ces scénarios")
    if not isinstance(parent.get(key), list):
        parent[key] = []
    parent[key].append(value)


def _build_passing_topology(initial: dict, rules: list[dict]) -> dict:
    result = copy.deepcopy(initial)
    for rule in rules:
        operator = rule["operator"]
        if operator == "equals":
            _set_rule_value(result, rule, rule.get("expected"))
        elif operator == "contains":
            _append_rule_value(result, rule, rule.get("expected"))
        else:
            raise AssertionError(
                f"Opérateur CLI non couvert par ce test : {rule.get('id')} ({operator})"
            )
    return result


def _make_one_rule_fail(topology: dict, rule: dict) -> dict:
    result = copy.deepcopy(topology)
    expected = rule.get("expected")
    if rule["operator"] == "equals":
        if isinstance(expected, bool):
            wrong = not expected
        elif isinstance(expected, (int, float)):
            wrong = expected + 1
        elif isinstance(expected, str) and rule["path"].endswith(".state"):
            # Reste dans l'énumération Pydantic : le contrôle doit échouer sur la règle,
            # pas sur la validation structurelle du corps HTTP.
            wrong = "down" if expected == "up" else "up"
        elif isinstance(expected, str) and rule["path"].endswith(".mode"):
            valid_modes = ("routed", "access", "trunk", "down")
            wrong = next(mode for mode in valid_modes if mode != expected)
        elif isinstance(expected, str) and len(expected.split(".")) == 4 and all(
            part.isdigit() and 0 <= int(part) <= 255 for part in expected.split(".")
        ):
            octets = expected.split(".")
            octets[-1] = str((int(octets[-1]) + 1) % 256)
            wrong = ".".join(octets)
        elif isinstance(expected, str):
            wrong = expected + "-incorrect"
        else:
            wrong = "__valeur_incorrecte__"
        _set_rule_value(result, rule, wrong)
    elif rule["operator"] == "contains":
        parent, key = _resolve_parent(result, rule.get("device", ""), rule["path"])
        values = parent.get(key, []) if not isinstance(key, int) else parent
        if not isinstance(values, list):
            raise AssertionError(f"{rule['path']} devrait être une liste")
        for index, value in enumerate(values):
            if value == expected:
                del values[index]
                break
        else:
            raise AssertionError(f"Valeur attendue absente de {rule['path']}: {expected!r}")
    else:
        raise AssertionError(f"Opérateur non testé: {rule['operator']}")
    return result


class CLILabCheckHttpTests(unittest.TestCase):
    """Contrôle serveur HTTP pour chaque scénario CLI, sur une base jetable."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="skilltree-cli-check-")
        self.db_path = Path(self.temp_dir.name) / "cli-check.sqlite3"
        connection = db.connect(self.db_path)
        try:
            db.initialize(connection)
        finally:
            connection.close()

        self.db_patch = patch.object(
            lab_routes, "_database_connection",
            side_effect=lambda: db.connect(self.db_path),
        )
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        self.env_patch = patch.dict(
            os.environ,
            {"SKILLTREE_DB": str(self.db_path), "RENDER_SERVICE_ID": ""},
        )
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_every_cli_lab_fails_initial_state_passes_correct_state_and_rejects_wrong_state(self) -> None:
        self.assertEqual(len(CLI_SCENARIOS), 17, "Le nombre de scénarios CLI a changé")

        with TestClient(api.app) as client:
            for scenario_path in CLI_SCENARIOS:
                with self.subTest(scenario=scenario_path.stem):
                    scenario = json.loads(scenario_path.read_text(encoding="utf-8-sig"))
                    lab_id = scenario["id"]
                    initial = scenario["initial_topology"]
                    rules = scenario["check"]["rules"]
                    self.assertEqual(scenario["check"]["type"], "config_assertions")
                    self.assertGreater(len(rules), 0)

                    baseline = client.post(
                        f"/api/lab/v2/{lab_id}/check",
                        json={"topology": initial},
                    )
                    self.assertEqual(baseline.status_code, 200, baseline.text)
                    self.assertFalse(
                        baseline.json()["passed"],
                        f"{lab_id}: le scénario initial ne doit pas réussir",
                    )

                    configured = _build_passing_topology(initial, rules)
                    passed = client.post(
                        f"/api/lab/v2/{lab_id}/check",
                        json={"topology": configured},
                    )
                    self.assertEqual(passed.status_code, 200, passed.text)
                    result = passed.json()
                    self.assertTrue(result["passed"], f"{lab_id}: {result}")
                    self.assertEqual(result["score"], 1.0, result)
                    self.assertEqual(len(result["results"]), len(rules), result)
                    self.assertTrue(all(item["passed"] for item in result["results"]), result)

                    broken = _make_one_rule_fail(configured, rules[-1])
                    rejected = client.post(
                        f"/api/lab/v2/{lab_id}/check",
                        json={"topology": broken},
                    )
                    self.assertEqual(rejected.status_code, 200, rejected.text)
                    negative_result = rejected.json()
                    self.assertFalse(
                        negative_result["passed"],
                        f"{lab_id}: le serveur a accepté une règle volontairement incorrecte",
                    )
                    self.assertTrue(
                        any(not item["passed"] for item in negative_result["results"]),
                        negative_result,
                    )

        # Les opérations /check doivent rester sans effet de bord.
        connection = db.connect(self.db_path)
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM lab_attempts").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM topologies").fetchone()[0], 0)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
