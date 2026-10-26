from __future__ import annotations

import json

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


ROOT = Path(__file__).resolve().parents[1]


class QuizReadRouteTests(unittest.TestCase):
    def test_get_quiz_returns_questions_without_expected_answers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            with patch.object(api, "DB_PATH", database_path):
                with TestClient(api.app) as client:
                    response = client.get("/api/node/intro-reseau-intermediaire/quiz")

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["node_id"], "intro-reseau-intermediaire")
        self.assertGreater(len(payload["questions"]), 0)
        question = payload["questions"][0]
        self.assertTrue(question["prompt"])
        self.assertIsInstance(question["choices"], list)
        self.assertNotIn("answer", question)
        self.assertNotIn("answer_regex", question)
        self.assertNotIn("explanation", question)



    def test_post_quiz_returns_correct_answer_feedback_after_submission(self) -> None:
        quiz_path = ROOT / "content" / "quiz" / "intro-reseau-debutant.json"
        quiz_data = json.loads(quiz_path.read_text(encoding="utf-8"))
        questions = quiz_data["questions"]
        answers = [
            (question["answer"] + 1) % len(question["choices"])
            if index == 0
            else question["answer"]
            for index, question in enumerate(questions)
        ]

        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            with patch.object(api, "DB_PATH", database_path):
                with TestClient(api.app) as client:
                    response = client.post(
                        "/api/node/intro-reseau-debutant/quiz",
                        json={"answers": answers},
                    )

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertLess(payload["score"], 100)
        self.assertEqual(len(payload["results"]), len(questions))
        feedback = payload["results"][0]
        source_question = questions[0]
        self.assertEqual(feedback["prompt"], source_question["prompt"])
        self.assertEqual(
            feedback["correct_answer"],
            source_question["choices"][source_question["answer"]],
        )
        self.assertEqual(
            feedback["selected_answer"],
            source_question["choices"][(source_question["answer"] + 1) % len(source_question["choices"])],
        )
        self.assertNotEqual(feedback["selected_answer"], feedback["correct_answer"])
        self.assertFalse(feedback["correct"])


if __name__ == "__main__":
    unittest.main()
