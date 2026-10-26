from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


class ExamApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary.name) / "skilltree.sqlite3"
        self.db_patch = patch.object(api, "DB_PATH", self.database_path)
        self.db_patch.start()
        self.client = TestClient(api.app)
        self.client.__enter__()

        tree_response = self.client.get("/api/tree")
        self.assertEqual(tree_response.status_code, 200, tree_response.text)
        nodes = tree_response.json()["nodes"]
        ipv6_node = next(node for node in nodes if node["id"] == "ipv6-expert")
        self.category = ipv6_node["category"]

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.db_patch.stop()
        self.temporary.cleanup()

    def _start_exam(self) -> dict:
        response = self.client.post("/api/exam/start", json={"category": self.category})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def _answer_key(self, exam: dict) -> list[int]:
        with sqlite3.connect(self.database_path) as connection:
            session = connection.execute(
                "SELECT question_ids FROM exam_sessions WHERE session_id = ?",
                (exam["id"],),
            ).fetchone()
            self.assertIsNotNone(session)
            refs = json.loads(session[0])
            answers = []
            for ref in refs:
                self.assertIsInstance(ref, dict)
                row = connection.execute(
                    "SELECT answer FROM questions WHERE id = ? AND node_id = ? AND scope = ?",
                    (ref["question_id"], ref["node_id"], ref.get("scope", "quiz")),
                ).fetchone()
                self.assertIsNotNone(row, f"Question de session absente : {ref}")
                answers.append(row[0])
            return answers

    def test_start_returns_qcm_without_leaking_answer_keys(self) -> None:
        exam = self._start_exam()
        self.assertTrue(exam["id"])
        self.assertEqual(exam["category"], self.category)
        self.assertGreater(len(exam["questions"]), 0)
        self.assertLessEqual(len(exam["questions"]), api.EXAM_QUESTION_COUNT)

        for question in exam["questions"]:
            self.assertEqual(question["type"], "qcm")
            self.assertTrue(question["prompt"])
            self.assertEqual(len(question["choices"]), 4)
            self.assertNotIn("answer", question)
            self.assertNotIn("answer_regex", question)
            self.assertNotIn("explanation", question)

        with sqlite3.connect(self.database_path) as connection:
            refs = json.loads(connection.execute(
                "SELECT question_ids FROM exam_sessions WHERE session_id = ?", (exam["id"],)
            ).fetchone()[0])
        self.assertTrue(refs)
        self.assertTrue(all(isinstance(ref, dict) for ref in refs))
        self.assertTrue(all(type(ref["question_id"]) is int for ref in refs))

    def test_submit_scores_server_side_and_is_idempotent(self) -> None:
        exam = self._start_exam()
        answers = self._answer_key(exam)

        response = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": answers},
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertTrue(result["success"])
        self.assertEqual(result["correct"], len(answers))
        self.assertEqual(result["total"], len(answers))
        self.assertEqual(result["score"], 100)
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["details"]), len(answers))
        self.assertTrue(all(detail["correct"] for detail in result["details"]))

        replay = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": [None] * len(answers)},
        )
        self.assertEqual(replay.status_code, 200, replay.text)
        self.assertEqual(replay.json(), result)

        profile = self.client.get("/api/profile")
        self.assertEqual(profile.status_code, 200, profile.text)
        self.assertEqual(profile.json()["exams_passed"], 1)

    def _unlock_ipv6_exam_prerequisite(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "INSERT INTO attempts (node_id, kind, score, passed, evidence, detail, created_at) "
                "VALUES (?, 'quiz', 100, 1, '', 'test prerequisite', '2026-10-26 12:00:00')",
                ("ipv6-intermediaire",),
            )
            connection.commit()

    def test_course_exam_uses_dedicated_bank_and_records_exam_requirement(self) -> None:
        self._unlock_ipv6_exam_prerequisite()
        response = self.client.post("/api/exam/start", json={"node_id": "ipv6-expert"})
        self.assertEqual(response.status_code, 200, response.text)
        exam = response.json()
        self.assertEqual(exam["exam_type"], "course")
        self.assertEqual(exam["node_id"], "ipv6-expert")
        self.assertEqual(exam["passing_score"], 85)
        self.assertEqual(exam["category"], "IPv6 - Expert")
        self.assertGreater(len(exam["questions"]), 0)
        self.assertTrue(all("answer" not in question for question in exam["questions"]))

        with sqlite3.connect(self.database_path) as connection:
            refs = json.loads(connection.execute(
                "SELECT question_ids FROM exam_sessions WHERE session_id = ?", (exam["id"],)
            ).fetchone()[0])
        self.assertTrue(all(ref["scope"] == "exam" for ref in refs))
        answers = self._answer_key(exam)
        result_response = self.client.post(
            "/api/exam/submit", json={"session_id": exam["id"], "answers": answers}
        )
        self.assertEqual(result_response.status_code, 200, result_response.text)
        result = result_response.json()
        self.assertEqual(result["score"], 100)
        self.assertTrue(result["passed"])
        self.assertEqual(result["node_id"], "ipv6-expert")
        # Le cours conserve aussi son exigence de quiz : réussir l'examen ne la contourne pas.
        self.assertFalse(result["validated"])

        replay = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": [None] * len(answers)},
        )
        self.assertEqual(replay.status_code, 200, replay.text)
        self.assertEqual(replay.json(), result)

        with sqlite3.connect(self.database_path) as connection:
            attempts = connection.execute(
                "SELECT COUNT(*) FROM attempts WHERE node_id = 'ipv6-expert' AND kind = 'exam' AND passed = 1"
            ).fetchone()[0]
            saved_node_id = connection.execute(
                "SELECT node_id FROM exam_submissions WHERE session_id = ?", (exam["id"],)
            ).fetchone()[0]
        self.assertEqual(attempts, 1)
        self.assertEqual(saved_node_id, "ipv6-expert")

        profile = self.client.get("/api/profile")
        self.assertEqual(profile.status_code, 200, profile.text)
        self.assertEqual(profile.json()["exams_passed"], 1)

    def test_course_exam_requires_prerequisites_and_exam_requirement(self) -> None:
        blocked = self.client.post("/api/exam/start", json={"node_id": "ipv6-expert"})
        self.assertEqual(blocked.status_code, 409, blocked.text)

        no_requirement = self.client.post("/api/exam/start", json={"node_id": "intro-reseau-debutant"})
        self.assertEqual(no_requirement.status_code, 409, no_requirement.text)

    def test_submit_rejects_answer_count_mismatch(self) -> None:
        exam = self._start_exam()
        response = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": []},
        )
        self.assertEqual(response.status_code, 422, response.text)

    def test_submit_scores_missing_answers_as_incorrect(self) -> None:
        exam = self._start_exam()
        answers = [None] * len(exam["questions"])
        response = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": answers},
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["correct"], 0)
        self.assertEqual(result["score"], 0)
        self.assertFalse(result["passed"])

    def test_expired_and_unknown_sessions_are_rejected(self) -> None:
        unknown = self.client.post(
            "/api/exam/submit",
            json={"session_id": "not-a-session", "answers": []},
        )
        self.assertEqual(unknown.status_code, 404, unknown.text)

        exam = self._start_exam()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE exam_sessions SET expires_at = 0 WHERE session_id = ?",
                (exam["id"],),
            )
            connection.commit()
        expired = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": [None] * len(exam["questions"])},
        )
        self.assertEqual(expired.status_code, 409, expired.text)

    def test_start_and_submit_validate_payloads_and_category(self) -> None:
        missing_category = self.client.post("/api/exam/start", json={"category": "  "})
        self.assertEqual(missing_category.status_code, 422, missing_category.text)

        unknown_category = self.client.post("/api/exam/start", json={"category": "Catégorie inexistante"})
        self.assertEqual(unknown_category.status_code, 404, unknown_category.text)

        missing_answers = self.client.post(
            "/api/exam/submit",
            json={"session_id": "some-session"},
        )
        self.assertEqual(missing_answers.status_code, 422, missing_answers.text)


if __name__ == "__main__":
    unittest.main()
