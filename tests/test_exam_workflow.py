from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


class ExamWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary.name) / "skilltree.sqlite3"
        self.db_patch = patch.object(api, "DB_PATH", self.database_path)
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        self.client = TestClient(api.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

        tree = self.client.get("/api/tree")
        self.assertEqual(tree.status_code, 200, tree.text)
        self.nodes = tree.json()["nodes"]
        self.node = next(node for node in self.nodes if node["id"] == "intro-reseau-debutant")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _answers(self, question_ids: list[int]) -> list[int | str]:
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            answers: list[int | str] = []
            for question_id in question_ids:
                row = connection.execute(
                    "SELECT question_type, answer, answer_text FROM questions WHERE id = ?",
                    (question_id,),
                ).fetchone()
                self.assertIsNotNone(row, f"Question absente de la session : {question_id}")
                if row["question_type"] == "qcm":
                    answers.append(int(row["answer"]))
                else:
                    answers.append(str(row["answer_text"] or ""))
            return answers

    def test_build_and_submit_exam_is_server_scored_and_idempotent(self) -> None:
        response = self.client.post(
            "/api/exam/build",
            json={
                "node_ids": ["intro-reseau-debutant"],
                "levels": ["debutant"],
                "count": 5,
                "time_limit": 600,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        exam = response.json()
        self.assertTrue(exam["id"])
        self.assertEqual(exam["time_limit"], 600)
        self.assertEqual(exam["pass_score"], 80)
        self.assertGreater(len(exam["questions"]), 0)
        self.assertLessEqual(len(exam["questions"]), 5)

        for question in exam["questions"]:
            self.assertTrue(question["prompt"])
            for secret_field in ("answer", "answer_text", "answer_regex", "explanation", "correct"):
                self.assertNotIn(secret_field, question)

        ids = [int(question["id"]) for question in exam["questions"]]
        result_response = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": self._answers(ids)},
        )
        self.assertEqual(result_response.status_code, 200, result_response.text)
        result = result_response.json()
        self.assertTrue(result["success"])
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["correct"], len(ids))
        self.assertEqual(result["total"], len(ids))
        self.assertEqual(len(result["details"]), len(ids))
        self.assertFalse(result["offline"])

        replay = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": [None] * len(ids)},
        )
        self.assertEqual(replay.status_code, 200, replay.text)
        self.assertEqual(replay.json(), result)

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT submitted, score, passed, result_json FROM exam_sessions WHERE session_id = ?",
                (exam["id"],),
            ).fetchone()
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], 100)
        self.assertEqual(row[2], 1)
        self.assertTrue(json.loads(row[3])["success"])

    def test_invalid_exam_selection_and_limits_are_rejected(self) -> None:
        unknown = self.client.post(
            "/api/exam/build",
            json={"node_ids": ["cours-inexistant"], "count": 10, "time_limit": 900},
        )
        self.assertEqual(unknown.status_code, 422, unknown.text)

        invalid_count = self.client.post(
            "/api/exam/build",
            json={"node_ids": ["intro-reseau-debutant"], "count": 0, "time_limit": 900},
        )
        self.assertEqual(invalid_count.status_code, 422, invalid_count.text)

        invalid_duration = self.client.post(
            "/api/exam/build",
            json={"node_ids": ["intro-reseau-debutant"], "count": 1, "time_limit": 1},
        )
        self.assertEqual(invalid_duration.status_code, 422, invalid_duration.text)

    def test_legacy_exam_start_can_also_be_submitted(self) -> None:
        response = self.client.post(
            "/api/exam/start",
            json={"category": self.node["category"]},
        )
        self.assertEqual(response.status_code, 200, response.text)
        exam = response.json()
        self.assertGreater(len(exam["questions"]), 0)
        ids = [int(question["id"]) for question in exam["questions"]]

        submitted = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": self._answers(ids)},
        )
        self.assertEqual(submitted.status_code, 200, submitted.text)
        self.assertEqual(submitted.json()["score"], 100)
        self.assertTrue(submitted.json()["passed"])


if __name__ == "__main__":
    unittest.main()
