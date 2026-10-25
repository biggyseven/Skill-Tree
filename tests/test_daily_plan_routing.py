"""Regression tests for routing daily-plan recommendations to the right activity."""

from datetime import datetime
import json
import sqlite3
import unittest

from app.db import initialize
from app.engine import SkillTree, get_daily_plan


class DailyPlanRoutingTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        initialize(self.conn)

        nodes = [
            ("lab-legacy", "Lab historique", "Lab classique", "Réseaux", "Réseaux", 1),
            ("lab-v2", "Lab Workspace", "Laboratoire v2", "Réseaux", "Réseaux", 2),
            ("challenge-node", "Défi réseau", "Défi d'architecture", "Réseaux", "Réseaux", 3),
            ("lesson-node", "Cours normal", "Leçon", "Réseaux", "Réseaux", 4),
        ]
        self.conn.executemany(
            """
            INSERT INTO nodes (id, title, description, category, module, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            nodes,
        )
        self.conn.executemany(
            "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
            [
                ("lab-legacy", "lab", 80),
                ("lab-v2", "lab", 80),
                ("challenge-node", "manual", 80),
                ("lesson-node", "quiz", 80),
            ],
        )
        self.conn.execute(
            """
            INSERT INTO lab_specs (node_id, kind, mode, pattern, prompt, hint)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("lab-legacy", "text", "contains", "verified", "Configure le lab", "Contrôle la configuration"),
        )
        expected_topology = {
            "nodes": {"router": 2},
            "connections": [{"from": "router", "to": "router"}],
        }
        self.conn.execute(
            "INSERT INTO challenges (node_id, expected_topology, time_limit) VALUES (?, ?, ?)",
            ("challenge-node", json.dumps(expected_topology), 300),
        )
        self.conn.commit()
        self.tree = SkillTree(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_available_lab_requirements_route_to_the_lab_action(self):
        plan = get_daily_plan(
            self.tree,
            limit=10,
            now=datetime(2026, 10, 25, 12, 0, 0),
        )
        actions = {item["node_id"]: item for item in plan["actions"]}

        self.assertEqual(actions["lab-legacy"]["action"], "lab")
        self.assertEqual(actions["lab-legacy"]["label"], "Commencer le lab Lab historique")
        self.assertEqual(actions["lab-v2"]["action"], "lab")
        self.assertEqual(actions["lab-v2"]["reason"], "Laboratoire disponible")

    def test_challenges_and_regular_lessons_keep_their_own_actions(self):
        plan = get_daily_plan(
            self.tree,
            limit=10,
            now=datetime(2026, 10, 25, 12, 0, 0),
        )
        actions = {item["node_id"]: item for item in plan["actions"]}

        self.assertEqual(actions["challenge-node"]["action"], "challenge")
        self.assertEqual(actions["lesson-node"]["action"], "start")


if __name__ == "__main__":
    unittest.main()
