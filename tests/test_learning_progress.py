from __future__ import annotations

import json
import unittest

from fastapi import HTTPException
from datetime import datetime, timedelta

from app.api import read_node, read_profile, read_tree, submit_challenge
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

    def add_requirement(self, node_id: str, kind: str, min_score: int = 80) -> None:
        self.conn.execute(
            "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
            (node_id, kind, min_score),
        )

    def add_quiz_requirement(self, node_id: str, min_score: int = 80) -> None:
        self.add_requirement(node_id, "quiz", min_score)

    def add_challenge(self, node_id: str, expected: dict | None = None, min_score: int = 100) -> dict:
        expected = expected or {
            "nodes": {"router": 1, "switch": 1},
            "connections": [{"from": "router", "to": "switch"}],
        }
        self.conn.execute(
            "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, 'manual', ?)",
            (node_id, min_score),
        )
        self.conn.execute(
            "INSERT INTO challenges (node_id, expected_topology, time_limit) VALUES (?, ?, ?)",
            (node_id, json.dumps(expected), 300),
        )
        return expected

    @staticmethod
    def drawflow_topology(*, extra_server: bool = False) -> dict:
        topology = {
            "1": {"name": "router", "outputs": {"output_1": {"connections": [{"node": "2", "output": "input_1"}]}}},
            "2": {"name": "switch", "outputs": {"output_1": {"connections": []}}},
        }
        if extra_server:
            topology["3"] = {"name": "server", "outputs": {"output_1": {"connections": []}}}
        return topology

    def add_attempt(
        self, node_id: str, score: int, passed: bool, created_at: datetime, kind: str = "quiz"
    ) -> None:
        self.conn.execute(
            "INSERT INTO attempts (node_id, kind, score, passed, evidence, detail, created_at) "
            "VALUES (?, ?, ?, ?, '', 'test', ?)",
            (node_id, kind, score, int(passed), created_at.strftime("%Y-%m-%d %H:%M:%S")),
        )

    def test_tree_and_detail_apis_expose_canonical_module(self) -> None:
        self.add_node("cloud-aws-debutant", "AWS débutant", "Cloud Computing", 1)
        payload = read_tree(self.tree)

        course = next(node for node in payload["nodes"] if node["id"] == "cloud-aws-debutant")
        detail = read_node("cloud-aws-debutant", self.tree)
        self.assertEqual(course["module"], "Cloud Computing")
        self.assertEqual(detail["module"], "Cloud Computing")
        self.assertEqual(course["status"], "available")
        self.assertEqual(payload["progress_percent"], 0)

    def test_progress_percentage_is_consistent_between_tree_and_profile(self) -> None:
        now = datetime(2026, 10, 25, 12, 0, 0)
        for index in range(1, 4):
            node_id = f"course-{index}"
            self.add_node(node_id, f"Cours {index}", "Administration Réseaux", index)
            if index < 3:
                self.add_quiz_requirement(node_id)
                self.add_attempt(node_id, 90, True, now - timedelta(days=1))

        tree_payload = read_tree(self.tree)
        profile_payload = read_profile(self.tree)
        expected_percent = round(tree_payload["validated"] / tree_payload["total"] * 100)

        self.assertEqual(tree_payload["validated"], 2)
        self.assertEqual(tree_payload["progress_percent"], 67)
        self.assertEqual(profile_payload["progress_percent"], expected_percent)

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

    def test_failed_quiz_is_recommended_before_the_lab_on_a_multi_requirement_course(self) -> None:
        now = datetime(2026, 10, 25, 12, 0, 0)
        self.add_node("multi-proof-course", "Cours avec quiz et lab", "Administration Réseaux", 1)
        self.add_requirement("multi-proof-course", "quiz")
        self.add_requirement("multi-proof-course", "lab")
        self.conn.execute(
            "INSERT INTO lab_specs (node_id, kind, mode, pattern, prompt, hint) "
            "VALUES (?, 'text', 'contains', 'validated', 'Établir la configuration', '')",
            ("multi-proof-course",),
        )
        self.add_attempt("multi-proof-course", 45, False, now - timedelta(minutes=5), kind="quiz")

        plan = get_daily_plan(self.tree, now=now)
        action = plan["actions"][0]

        self.assertEqual(action["node_id"], "multi-proof-course")
        self.assertEqual(action["action"], "continue")
        self.assertEqual(action["status"], "in_progress")
        self.assertEqual(action["last_attempt_kind"], "quiz")
        self.assertEqual(action["next_requirement_kind"], "quiz")

    def test_passed_terminal_does_not_hide_an_unmet_quiz_requirement(self) -> None:
        now = datetime(2026, 10, 25, 12, 0, 0)
        self.add_node("wifi-course", "Wi-Fi avec quiz et terminal", "Administration Réseaux", 1)
        self.add_requirement("wifi-course", "quiz")
        self.add_requirement("wifi-course", "terminal")
        self.conn.execute(
            "INSERT INTO terminal_specs (node_id, prompt, answer, pattern, explanation) "
            "VALUES (?, 'Saisir la commande', 'show ip interface brief', 'show ip interface brief', '')",
            ("wifi-course",),
        )
        self.add_attempt("wifi-course", 100, True, now - timedelta(minutes=5), kind="terminal")

        plan = get_daily_plan(self.tree, now=now)
        action = plan["actions"][0]

        self.assertEqual(action["action"], "continue")
        self.assertEqual(action["last_attempt_kind"], "terminal")
        self.assertEqual(action["next_requirement_kind"], "quiz")

    def test_validating_prerequisite_unlocks_multiple_courses_and_daily_plan(self) -> None:
        now = datetime(2026, 10, 25, 12, 0, 0)
        self.add_node("intro-course", "Introduction", "Administration Réseaux", 1)
        self.add_quiz_requirement("intro-course")
        self.add_node("next-course", "Étape suivante", "Administration Réseaux", 2)
        self.add_node("parallel-course", "Autre étape accessible", "Administration Réseaux", 3)
        self.conn.execute(
            "INSERT INTO edges (node_id, prereq_id) VALUES (?, ?)",
            ("next-course", "intro-course"),
        )
        self.conn.execute(
            "INSERT INTO edges (node_id, prereq_id) VALUES (?, ?)",
            ("parallel-course", "intro-course"),
        )
        self.add_attempt("intro-course", 100, True, now)

        statuses = self.tree.statuses()
        self.assertEqual(statuses["intro-course"].value, "validated")
        self.assertEqual(statuses["next-course"].value, "available")
        self.assertEqual(statuses["parallel-course"].value, "available")

        tree_payload = read_tree(self.tree)
        tree_statuses = {node["id"]: node["status"] for node in tree_payload["nodes"]}
        self.assertEqual(tree_statuses["next-course"], "available")
        self.assertEqual(tree_statuses["parallel-course"], "available")

        plan = get_daily_plan(self.tree, now=now)
        self.assertEqual(
            [(action["node_id"], action["action"], action["status"]) for action in plan["actions"]],
            [
                ("next-course", "start", "available"),
                ("parallel-course", "start", "available"),
            ],
        )

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

    def test_challenge_detail_exposes_expected_topology_and_server_records_success(self) -> None:
        self.add_node("challenge-network", "Défi réseau", "Administration Réseaux", 1)
        expected = self.add_challenge("challenge-network")

        detail = read_node("challenge-network", self.tree)
        self.assertEqual(detail["challenge"]["expected_summary"], {
            "nodes": expected["nodes"],
            "connections": len(expected["connections"]),
        })
        self.assertNotIn("expected_topology", detail["challenge"])
        self.assertEqual(detail["challenge"]["time_limit"], 300)

        result = submit_challenge(
            "challenge-network",
            {"topology": self.drawflow_topology()},
            self.tree,
        )

        self.assertEqual(result["score"], 100)
        self.assertTrue(result["passed"])
        self.assertTrue(result["validated"])
        self.assertEqual(result["status"], "validated")
        self.assertTrue(result["attempt_recorded"])
        attempt = self.conn.execute(
            "SELECT kind, score, passed FROM attempts WHERE node_id = ?",
            ("challenge-network",),
        ).fetchone()
        self.assertEqual(tuple(attempt), ("manual", 100, 1))

    def test_failed_and_timed_out_challenges_are_recorded_and_retryable(self) -> None:
        self.add_node("challenge-network", "Défi réseau", "Administration Réseaux", 1)
        self.add_challenge("challenge-network")

        failed = submit_challenge(
            "challenge-network",
            {
                "topology": self.drawflow_topology(extra_server=True),
                # Ces champs ne doivent jamais influencer le résultat calculé.
                "score": 100,
                "passed": True,
            },
            self.tree,
        )
        self.assertEqual(failed["score"], 83)
        self.assertFalse(failed["passed"])
        self.assertEqual(failed["status"], "in_progress")
        self.assertTrue(failed["attempt_recorded"])

        plan = get_daily_plan(self.tree, now=datetime(2026, 10, 25, 12, 0, 0))
        self.assertEqual(plan["actions"][0]["node_id"], "challenge-network")
        self.assertEqual(plan["actions"][0]["action"], "challenge")

        timed_out = submit_challenge(
            "challenge-network",
            {"topology": self.drawflow_topology(), "timeout": True},
            self.tree,
        )
        self.assertEqual(timed_out["score"], 100)
        self.assertFalse(timed_out["passed"])
        self.assertEqual(timed_out["status"], "in_progress")

        passed = submit_challenge(
            "challenge-network",
            {"topology": self.drawflow_topology()},
            self.tree,
        )
        self.assertTrue(passed["passed"])
        self.assertTrue(passed["validated"])
        self.assertEqual(passed["status"], "validated")

    def test_replaying_validated_challenge_does_not_record_a_second_reward_attempt(self) -> None:
        self.add_node("challenge-network", "Défi réseau", "Administration Réseaux", 1)
        self.add_challenge("challenge-network")
        first = submit_challenge("challenge-network", {"topology": self.drawflow_topology()}, self.tree)
        second = submit_challenge("challenge-network", {"topology": self.drawflow_topology()}, self.tree)

        self.assertTrue(first["attempt_recorded"])
        self.assertFalse(second["attempt_recorded"])
        self.assertTrue(second["passed"])
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM attempts WHERE node_id = ?", ("challenge-network",)).fetchone()[0],
            1,
        )

    def test_challenge_with_no_required_links_can_be_validated(self) -> None:
        self.add_node("challenge-single-router", "Défi routeur isolé", "Administration Réseaux", 1)
        expected = {
            "nodes": {"router": 1},
            "connections": [],
        }
        self.add_challenge("challenge-single-router", expected=expected)
        topology = {
            "1": {"name": "router", "outputs": {"output_1": {"connections": []}}},
        }

        detail = read_node("challenge-single-router", self.tree)
        self.assertEqual(detail["challenge"]["expected_summary"]["connections"], 0)
        result = submit_challenge("challenge-single-router", {"topology": topology}, self.tree)

        self.assertEqual(result["score"], 100)
        self.assertTrue(result["passed"])
        self.assertTrue(result["validated"])

    def test_locked_challenge_is_rejected_by_server(self) -> None:
        self.add_node("prerequisite", "Prérequis", "Administration Réseaux", 1)
        self.add_node("challenge-network", "Défi réseau", "Administration Réseaux", 2)
        self.conn.execute(
            "INSERT INTO edges (node_id, prereq_id) VALUES ('challenge-network', 'prerequisite')"
        )
        self.add_challenge("challenge-network")

        with self.assertRaises(HTTPException) as context:
            submit_challenge(
                "challenge-network",
                {"topology": self.drawflow_topology()},
                self.tree,
            )
        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(
            self.conn.execute("SELECT COUNT(*) FROM attempts WHERE node_id = 'challenge-network'").fetchone()[0],
            0,
        )

    def test_newly_available_challenge_appears_as_a_challenge_action(self) -> None:
        self.add_node("challenge-network", "Défi réseau", "Administration Réseaux", 1)
        self.add_challenge("challenge-network")

        plan = get_daily_plan(self.tree, now=datetime(2026, 10, 25, 12, 0, 0))

        self.assertEqual(len(plan["actions"]), 1)
        self.assertEqual(plan["actions"][0]["node_id"], "challenge-network")
        self.assertEqual(plan["actions"][0]["action"], "challenge")

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
