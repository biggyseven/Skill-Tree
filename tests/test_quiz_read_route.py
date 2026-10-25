from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


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


if __name__ == "__main__":
    unittest.main()
