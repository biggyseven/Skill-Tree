from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from app import api


class LabTopologyPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "workspace.sqlite3"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE topologies (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
        self.db_patch = patch.object(api, "DB_PATH", self.db_path)
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _topology(topology_id: str = "topology-test", node_id: str = "R1") -> dict:
        return {
            "schema_version": 2,
            "topology_id": topology_id,
            "metadata": {
                "name": "Test",
                "author": "test",
                "created_at": "2026-01-01T00:00:00Z",
                "mode": "lab",
            },
            "nodes": [
                {
                    "id": node_id,
                    "type": "router",
                    "x": 120,
                    "y": 180,
                    "label": node_id,
                    "ports": [
                        {
                            "id": "Fa0/0",
                            "name": "Fa0/0",
                            "state": "up",
                            "ip": "10.0.0.1",
                            "mask": "255.255.255.252",
                        }
                    ],
                    "config": {"hostname": node_id},
                }
            ],
            "links": [],
            "simulation": {"state": "idle", "event_log": []},
        }

    def _save(self, lab_id: str, topology: dict) -> dict:
        return api.save_lab_topology_v2(lab_id, {"topology": topology})

    def _load(self, lab_id: str) -> dict:
        return api.load_lab_topology_v2(lab_id)

    def test_save_and_load_round_trip_preserves_topology(self) -> None:
        topology = self._topology()
        result = self._save("ospf-3-routers", topology)
        loaded = self._load("ospf-3-routers")

        self.assertTrue(result["success"])
        self.assertEqual(loaded["topology"], topology)
        self.assertEqual(loaded["lab_id"], "ospf-3-routers")
        self.assertEqual(loaded["name"], "lab_ospf-3-routers")
        self.assertTrue(loaded["updated_at"])

    def test_saving_again_replaces_the_previous_snapshot_for_same_lab(self) -> None:
        first = self._topology(topology_id="first", node_id="R1")
        second = self._topology(topology_id="second", node_id="R2")
        self._save("lab-a", first)
        self._save("lab-a", second)

        loaded = self._load("lab-a")
        with sqlite3.connect(self.db_path) as conn:
            row_count = conn.execute(
                "SELECT COUNT(*) FROM topologies WHERE name = 'lab_lab-a'"
            ).fetchone()[0]

        self.assertEqual(row_count, 1)
        self.assertEqual(loaded["topology"], second)

    def test_saved_topologies_are_isolated_by_lab_id(self) -> None:
        topology_a = self._topology(topology_id="a", node_id="R1")
        topology_b = self._topology(topology_id="b", node_id="R2")
        self._save("lab-a", topology_a)
        self._save("lab-b", topology_b)

        self.assertEqual(self._load("lab-a")["topology"], topology_a)
        self.assertEqual(self._load("lab-b")["topology"], topology_b)

    def test_rejects_incompatible_or_malformed_topology_before_saving(self) -> None:
        invalid_values = [
            {"schema_version": 1, "nodes": [], "links": []},
            {"schema_version": 2, "nodes": {}, "links": []},
            {
                "schema_version": 2,
                "nodes": [{"id": "bad", "type": "unknown-device"}],
                "links": [],
            },
        ]
        for topology in invalid_values:
            with self.subTest(topology=topology):
                with self.assertRaises(HTTPException) as raised:
                    self._save("lab-invalid", topology)
                self.assertEqual(raised.exception.status_code, 422)

        with sqlite3.connect(self.db_path) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM topologies").fetchone()[0], 0)

    def test_missing_snapshot_returns_not_found(self) -> None:
        with self.assertRaises(HTTPException) as raised:
            self._load("lab-without-save")
        self.assertEqual(raised.exception.status_code, 404)

    def test_corrupt_or_invalid_saved_snapshot_returns_server_error(self) -> None:
        valid_json_but_invalid_topology = json.dumps(
            {"schema_version": 2, "nodes": "not-a-list", "links": []}
        )
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO topologies (name, data, updated_at) VALUES (?, ?, ?)",
                ("lab-broken", valid_json_but_invalid_topology, "2026-01-01T00:00:00Z"),
            )
            conn.execute(
                "INSERT INTO topologies (name, data, updated_at) VALUES (?, ?, ?)",
                ("lab-json-broken", "{not-json", "2026-01-01T00:00:00Z"),
            )

        with self.assertRaises(HTTPException) as invalid:
            self._load("broken")
        self.assertEqual(invalid.exception.status_code, 500)
        self.assertIn("invalide", invalid.exception.detail.lower())

        with self.assertRaises(HTTPException) as corrupt:
            self._load("json-broken")
        self.assertEqual(corrupt.exception.status_code, 500)
        self.assertIn("invalide", corrupt.exception.detail.lower())


