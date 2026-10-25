from __future__ import annotations

import sqlite3
import unittest
from datetime import datetime, timedelta

from app.api import read_tree
from app.db import connect, initialize
from app.engine import SkillTree, get_daily_plan


class LearningProgressConsistencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = connect(":memory:")
        initialize(self.conn)
        self.tree = SkillTree(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def add_node(self, node_id: str, title: str, module: str, sort_order: int) -> None:
        self.conn.execute(
            "INSERT INTO nodes (id, title, description, category, module, sort_order) "
            "VALUES (?, ?, '', 'Réseaux', ?, ?)",
            (node_id, title, module, sort_order),
        )

    def add_quiz_requirement(self, node_id: str, min_score: int = 80) -> None:
        self.conn.execute(
            "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, 'quiz', ?)",
            (node_id, min_score),
        )

    def add_attempt(self, node_id: str, score: int, passed: bool, created_at: datetime) -> None:
        self.conn.execute(
            "INSERT INTO attempts (node_id, kind, score, passed, evidence, detail, created_at) "
            "VALUES (?, 'quiz', ?, ?, '', 'test', ?)",
            (node_id, score, int(passed), created_at.strftime("%Y-%m-%d %H:%M:%S")),
        )

    def test_tree_api_exposes_canonical_module(self) -> None:
        self.add_node("cloud-aws-debutant", "AWS débutant", "Cloud Computing", 1)
        payload = read_tree(self.tree)

        course = next(node for node in payload["nodes"] if node["id"] == "cloud-aws-debutant")
        self.assertEqual(course["module"], "Cloud Computing")
        self.assertEqual(course["status"], "available")

    def test_incomplete_non_lab_course_is_recommended_before_new_content(self) -> None:
        now = datetime(2026, 10, 25, 12, 0, 0)
        self.add_node("routing-started", "Routage en cours", "Administration Réseaux", 1)
        self.add_quiz_requirement("routing-started")
        self.add_attempt("routing-started", 45, False, now - timedelta(hours=2))
        self.add_node("next-course", "Cours suivant", "Administration Réseaux", 2)

        plan = get_daily_plan(self.tree, now=now)

        self.assertGreaterEqual(len(plan["actions"]), 2)
        first = plan["actions"][0]
        self.assertEqual(first["node_id"], "routing-started")
        self.assertEqual(first["action"], "continue")
        self.assertEqual(first["status"], "in_progress")
        self.assertEqual(first["last_attempt_kind"], "quiz")
        self.assertEqual(plan["counts"]["in_progress"], 1)

    def test_review_recommendation_uses_the_real_validation_date(self) -> None:
        now = datetime(2026, 10, 25, 12, 0, 0)
        self.add_node("validated-course", "Cours validé", "Administration Réseaux", 1)
        self.add_quiz_requirement("validated-course")
        self.add_attempt("validated-course", 95, True, now - timedelta(days=5))

        plan = get_daily_plan(self.tree, now=now)

        self.assertEqual(len(plan["actions"]), 1)
        self.assertEqual(plan["actions"][0]["node_id"], "validated-course")
        self.assertEqual(plan["actions"][0]["action"], "review")
        self.assertEqual(plan["actions"][0]["days_since"], 5)

    def test_locked_course_is_not_presented_as_a_new_step(self) -> None:
        self.add_node("first-step", "Première étape", "Administration Réseaux", 1)
        self.add_node("locked-step", "Étape verrouillée", "Administration Réseaux", 2)
        self.conn.execute(
            "INSERT INTO edges (node_id, prereq_id) VALUES ('locked-step', 'first-step')"
        )

        plan = get_daily_plan(self.tree, now=datetime(2026, 10, 25, 12, 0, 0))

        planned_ids = {action["node_id"] for action in plan["actions"]}
        self.assertIn("first-step", planned_ids)
        self.assertNotIn("locked-step", planned_ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
