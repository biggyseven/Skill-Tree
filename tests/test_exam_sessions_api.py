from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


class ExamSessionApiTests(unittest.TestCase):
    def _client(self, directory: str):
        database_path = Path(directory) / "skilltree.db"
        patcher = patch.object(api, "DB_PATH", database_path)
        patcher.start()
        client = TestClient(api.app)
        client.__enter__()
        self.addCleanup(client.__exit__, None, None, None)
        self.addCleanup(patcher.stop)
        return client, database_path

    def _correct_answers(self, database_path: Path, question_ids: list[int]) -> list[int | str]:
        with api.connect(database_path) as conn:
            answers = []
            for question_id in question_ids:
                row = conn.execute(
                    "SELECT question_type, answer, answer_text FROM questions WHERE id = ?",
                    (question_id,),
                ).fetchone()
                self.assertIsNotNone(row)
                if row["question_type"] == "qcm":
                    answers.append(int(row["answer"]))
                else:
                    answers.append(str(row["answer_text"] or ""))
            return answers

    def test_exam_build_hides_answers_and_submit_grades_on_server_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client, database_path = self._client(temporary)
            response = client.post(
                "/api/exam/build",
                json={"node_ids": ["bgp-expert"], "levels": ["expert"], "count": 3, "time_limit": 600},
            )

            self.assertEqual(response.status_code, 200, response.text)
            session = response.json()
            self.assertTrue(session["id"])
            self.assertEqual(session["time_limit"], 600)
            self.assertEqual(session["pass_score"], api.EXAM_PASS_SCORE)
            self.assertGreater(len(session["questions"]), 0)
            self.assertLessEqual(len(session["questions"]), 3)
            for question in session["questions"]:
                self.assertTrue(question["prompt"])
                self.assertIsInstance(question["choices"], list)
                self.assertNotIn("answer", question)
                self.assertNotIn("answer_regex", question)
                self.assertNotIn("explanation", question)

            ids = [int(question["id"]) for question in session["questions"]]
            placeholders = ",".join("?" for _ in ids)
            with api.connect(database_path) as conn:
                rows = conn.execute(
                    f"SELECT id, scope FROM questions WHERE id IN ({placeholders})", ids
                ).fetchall()
            self.assertTrue(rows)
            self.assertTrue(all(row["scope"] == "exam" for row in rows))

            answers = self._correct_answers(database_path, ids)
            submitted = client.post(
                "/api/exam/submit",
                json={"session_id": session["id"], "answers": answers},
            )
            self.assertEqual(submitted.status_code, 200, submitted.text)
            result = submitted.json()
            self.assertEqual(result["score"], 100)
            self.assertTrue(result["passed"])
            self.assertEqual(result["correct"], len(ids))
            self.assertEqual(result["total"], len(ids))
            self.assertTrue(all(item["correct"] for item in result["details"]))
            self.assertFalse(result["offline"])

            # Une double soumission ne doit jamais permettre de remplacer la note.
            repeated = client.post(
                "/api/exam/submit",
                json={"session_id": session["id"], "answers": [None] * len(ids)},
            )
            self.assertEqual(repeated.status_code, 200, repeated.text)
            self.assertEqual(repeated.json()["score"], 100)
            self.assertEqual(repeated.json()["answers"], answers)

            with api.connect(database_path) as conn:
                saved = conn.execute(
                    "SELECT submitted, score, passed, answers_json, details_json "
                    "FROM exam_sessions WHERE session_id = ?",
                    (session["id"],),
                ).fetchone()
            self.assertEqual(saved["submitted"], 1)
            self.assertEqual(saved["score"], 100)
            self.assertEqual(saved["passed"], 1)
            self.assertEqual(json.loads(saved["answers_json"]), answers)
            self.assertEqual(len(json.loads(saved["details_json"])), len(ids))

    def test_exam_uses_quiz_bank_only_when_a_course_has_no_exam_bank(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client, database_path = self._client(temporary)
            response = client.post(
                "/api/exam/build",
                json={"node_ids": ["intro-reseau-debutant"], "levels": ["debutant"], "count": 2, "time_limit": 900},
            )
            self.assertEqual(response.status_code, 200, response.text)
            session = response.json()
            self.assertGreater(len(session["questions"]), 0)
            ids = [int(question["id"]) for question in session["questions"]]
            placeholders = ",".join("?" for _ in ids)
            with api.connect(database_path) as conn:
                rows = conn.execute(
                    f"SELECT id, scope FROM questions WHERE id IN ({placeholders})", ids
                ).fetchall()
            self.assertTrue(rows)
            self.assertTrue(all(row["scope"] == "quiz" for row in rows))
            # Les questions réutilisées depuis les quiz ne révèlent pas leur corrigé.
            self.assertTrue(all("answer" not in question for question in session["questions"]))

    def test_exam_rejects_unknown_courses_and_invalid_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client, _ = self._client(temporary)
            unknown = client.post(
                "/api/exam/build",
                json={"node_ids": ["cours-inexistant"], "count": 10, "time_limit": 900},
            )
            self.assertEqual(unknown.status_code, 422)

            invalid_count = client.post(
                "/api/exam/build",
                json={"node_ids": ["intro-reseau-debutant"], "count": 0, "time_limit": 900},
            )
            self.assertEqual(invalid_count.status_code, 422)

            invalid_time = client.post(
                "/api/exam/build",
                json={"node_ids": ["intro-reseau-debutant"], "count": 1, "time_limit": 1},
            )
            self.assertEqual(invalid_time.status_code, 422)

    def test_late_submission_after_grace_discards_client_answers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client, database_path = self._client(temporary)
            response = client.post(
                "/api/exam/build",
                json={"node_ids": ["intro-reseau-debutant"], "count": 1, "time_limit": 60},
            )
            self.assertEqual(response.status_code, 200, response.text)
            session = response.json()
            ids = [int(question["id"]) for question in session["questions"]]
            answers = self._correct_answers(database_path, ids)

            with api.connect(database_path) as conn:
                conn.execute(
                    "UPDATE exam_sessions SET expires_at = ? WHERE session_id = ?",
                    (int(time.time()) - api.EXAM_SUBMIT_GRACE_SECONDS - 2, session["id"]),
                )
                conn.commit()

            response = client.post(
                "/api/exam/submit",
                json={"session_id": session["id"], "answers": answers},
            )
            self.assertEqual(response.status_code, 200, response.text)
            result = response.json()
            self.assertTrue(result["time_expired"])
            self.assertEqual(result["score"], 0)
            self.assertEqual(result["answers"], [None] * len(ids))

    def test_pause_and_resume_extend_server_deadline_by_paused_duration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client, database_path = self._client(temporary)
            response = client.post(
                "/api/exam/build",
                json={"node_ids": ["intro-reseau-debutant"], "count": 1, "time_limit": 60},
            )
            self.assertEqual(response.status_code, 200, response.text)
            session_id = response.json()["id"]
            with api.connect(database_path) as conn:
                row = conn.execute(
                    "SELECT started_at, expires_at FROM exam_sessions WHERE session_id = ?",
                    (session_id,),
                ).fetchone()
            started_at = int(row["started_at"])
            initial_expiry = int(row["expires_at"])

            with patch("app.api.time.time", return_value=started_at + 10):
                paused = client.post("/api/exam/pause", json={"session_id": session_id})
            self.assertEqual(paused.status_code, 200, paused.text)
            self.assertTrue(paused.json()["paused"])

            forbidden_submit = client.post(
                "/api/exam/submit", json={"session_id": session_id, "answers": [None]}
            )
            self.assertEqual(forbidden_submit.status_code, 409)

            with patch("app.api.time.time", return_value=started_at + 100):
                resumed = client.post("/api/exam/resume", json={"session_id": session_id})
            self.assertEqual(resumed.status_code, 200, resumed.text)
            self.assertFalse(resumed.json()["paused"])
            self.assertEqual(resumed.json()["resumed_seconds"], 90)

            with api.connect(database_path) as conn:
                row = conn.execute(
                    "SELECT expires_at, paused_at, paused_seconds FROM exam_sessions WHERE session_id = ?",
                    (session_id,),
                ).fetchone()
            self.assertEqual(int(row["expires_at"]), initial_expiry + 90)
            self.assertIsNone(row["paused_at"])
            self.assertEqual(int(row["paused_seconds"]), 90)


if __name__ == "__main__":
    unittest.main()
