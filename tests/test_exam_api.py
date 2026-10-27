from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, local
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api, db as db_module
from app.domain import Attempt, Node, ProofKind, Requirement
from app.engine import requirement_met


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

    def _start_category_exam(self) -> dict:
        response = self.client.post("/api/exam/start", json={"category": self.category})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def _answer_key(self, exam: dict) -> list[int | str | None]:
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            session = connection.execute(
                "SELECT question_ids FROM exam_sessions WHERE session_id = ?",
                (exam["id"],),
            ).fetchone()
            self.assertIsNotNone(session)
            question_ids = json.loads(session["question_ids"])
            answers: list[int | str | None] = []
            for question_id in question_ids:
                row = connection.execute(
                    "SELECT question_type, answer, answer_text FROM questions WHERE id = ?",
                    (question_id,),
                ).fetchone()
                self.assertIsNotNone(row, f"Question de session absente : {question_id}")
                if row["question_type"] == "qcm":
                    answers.append(int(row["answer"]))
                else:
                    answers.append(str(row["answer_text"] or ""))
            return answers

    def _unlock_ipv6_exam_prerequisite(self) -> None:
        # Le cours IPv6 Expert dépend d'IPv6 Intermédiaire, lui-même validé par quiz + lab.
        with sqlite3.connect(self.database_path) as connection:
            for kind, score in (("quiz", 100), ("lab", 100)):
                connection.execute(
                    "INSERT INTO attempts (node_id, kind, score, passed, evidence, detail, created_at) "
                    "VALUES (?, ?, ?, 1, '', 'test prerequisite', '2026-10-26 12:00:00')",
                    ("ipv6-intermediaire", kind, score),
                )
            connection.commit()

    def test_start_returns_questions_without_answer_key_leaks(self) -> None:
        exam = self._start_category_exam()
        self.assertTrue(exam["id"])
        self.assertEqual(exam["exam_type"], "category")
        self.assertEqual(exam["category"], self.category)
        self.assertGreater(len(exam["questions"]), 0)
        self.assertLessEqual(len(exam["questions"]), api.EXAM_QUESTION_COUNT)

        for question in exam["questions"]:
            self.assertEqual(question["type"], "qcm")
            self.assertTrue(question["prompt"])
            self.assertEqual(len(question["choices"]), 4)
            for secret_key in ("answer", "answer_text", "answer_regex", "explanation", "correct"):
                self.assertNotIn(secret_key, question)

    def test_submit_is_server_scored_and_idempotent(self) -> None:
        exam = self._start_category_exam()
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

    def test_expired_submission_after_grace_discards_late_answers(self) -> None:
        exam = self._start_category_exam()
        answers = self._answer_key(exam)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE exam_sessions SET expires_at = 1000 WHERE session_id = ?",
                (exam["id"],),
            )
            connection.commit()

        with patch.object(api.time, "time", return_value=1000 + api.EXAM_SUBMIT_GRACE_SECONDS + 1):
            response = self.client.post(
                "/api/exam/submit",
                json={"session_id": exam["id"], "answers": answers},
            )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertTrue(result["time_expired"])
        self.assertEqual(result["correct"], 0)
        self.assertEqual(result["score"], 0)
        self.assertFalse(result["passed"])
        self.assertTrue(all(answer is None for answer in result["answers"]))

    def test_pause_blocks_submission_and_resume_extends_expiry(self) -> None:
        with patch.object(api.time, "time", return_value=10000):
            exam_response = self.client.post("/api/exam/start", json={"category": self.category})
        self.assertEqual(exam_response.status_code, 200, exam_response.text)
        exam = exam_response.json()
        with sqlite3.connect(self.database_path) as connection:
            original_expiry = connection.execute(
                "SELECT expires_at FROM exam_sessions WHERE session_id = ?",
                (exam["id"],),
            ).fetchone()[0]

        with patch.object(api.time, "time", return_value=10010):
            pause = self.client.post("/api/exam/pause", json={"session_id": exam["id"]})
        self.assertEqual(pause.status_code, 200, pause.text)
        self.assertTrue(pause.json()["paused"])

        blocked_submit = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": self._answer_key(exam)},
        )
        self.assertEqual(blocked_submit.status_code, 409, blocked_submit.text)

        with patch.object(api.time, "time", return_value=10040):
            resume = self.client.post("/api/exam/resume", json={"session_id": exam["id"]})
        self.assertEqual(resume.status_code, 200, resume.text)
        self.assertFalse(resume.json()["paused"])
        self.assertEqual(resume.json()["resumed_seconds"], 30)

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT expires_at, paused_seconds, paused_at FROM exam_sessions WHERE session_id = ?",
                (exam["id"],),
            ).fetchone()
        self.assertEqual(row[0], original_expiry + 30)
        self.assertEqual(row[1], 30)
        self.assertIsNone(row[2])

        with patch.object(api.time, "time", return_value=10041):
            submitted = self.client.post(
                "/api/exam/submit",
                json={"session_id": exam["id"], "answers": self._answer_key(exam)},
            )
        self.assertEqual(submitted.status_code, 200, submitted.text)
        self.assertTrue(submitted.json()["passed"])

    def test_course_exam_uses_dedicated_bank_and_records_exam_proof(self) -> None:
        self._unlock_ipv6_exam_prerequisite()
        response = self.client.post("/api/exam/start", json={"node_id": "ipv6-expert"})
        self.assertEqual(response.status_code, 200, response.text)
        exam = response.json()
        self.assertEqual(exam["exam_type"], "course")
        self.assertEqual(exam["node_id"], "ipv6-expert")
        self.assertEqual(exam["passing_score"], 80)
        self.assertEqual(exam["category"], "IPv6 - Expert")
        self.assertGreater(len(exam["questions"]), 0)
        self.assertTrue(all(question["type"] == "qcm" for question in exam["questions"]))
        self.assertTrue(all("answer" not in question for question in exam["questions"]))

        with sqlite3.connect(self.database_path) as connection:
            question_ids = json.loads(
                connection.execute(
                    "SELECT question_ids FROM exam_sessions WHERE session_id = ?",
                    (exam["id"],),
                ).fetchone()[0]
            )
            for question_id in question_ids:
                question = connection.execute(
                    "SELECT node_id, scope FROM questions WHERE id = ?",
                    (question_id,),
                ).fetchone()
                self.assertEqual(question[0], "ipv6-expert")
                self.assertEqual(question[1], "exam")

        answers = self._answer_key(exam)
        result_response = self.client.post(
            "/api/exam/submit", json={"session_id": exam["id"], "answers": answers}
        )
        self.assertEqual(result_response.status_code, 200, result_response.text)
        result = result_response.json()
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["node_id"], "ipv6-expert")
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
        self.assertEqual(attempts, 1)

        profile = self.client.get("/api/profile")
        self.assertEqual(profile.status_code, 200, profile.text)
        self.assertEqual(profile.json()["exams_passed"], 1)

    def test_concurrent_course_exam_submissions_record_one_attempt_and_one_reward(self) -> None:
        self._unlock_ipv6_exam_prerequisite()
        exam_response = self.client.post("/api/exam/start", json={"node_id": "ipv6-expert"})
        self.assertEqual(exam_response.status_code, 200, exam_response.text)
        exam = exam_response.json()
        answers = self._answer_key(exam)

        second_client = TestClient(api.app)
        second_client.__enter__()
        self.addCleanup(second_client.__exit__, None, None, None)

        barrier = Barrier(2)
        thread_state = local()
        original_grade = api._grade_exam_question

        def synchronized_grade(question, answer):
            if not getattr(thread_state, "waited", False):
                thread_state.waited = True
                barrier.wait(timeout=10)
            return original_grade(question, answer)

        payload = {"session_id": exam["id"], "answers": answers}
        with patch.object(api, "_grade_exam_question", side_effect=synchronized_grade):
            with ThreadPoolExecutor(max_workers=2) as executor:
                first = executor.submit(self.client.post, "/api/exam/submit", json=payload)
                second = executor.submit(second_client.post, "/api/exam/submit", json=payload)
                responses = [first.result(timeout=20), second.result(timeout=20)]

        self.assertEqual([response.status_code for response in responses], [200, 200])
        self.assertEqual(responses[0].json(), responses[1].json())
        self.assertTrue(responses[0].json()["passed"])

        with sqlite3.connect(self.database_path) as connection:
            attempt_count = connection.execute(
                "SELECT COUNT(*) FROM attempts WHERE node_id = 'ipv6-expert' AND kind = 'exam'"
            ).fetchone()[0]
            total_xp, coins = connection.execute(
                "SELECT total_xp, coins FROM user_stats WHERE id = 1"
            ).fetchone()
            streak_minutes = connection.execute(
                "SELECT COALESCE(SUM(minutes_etudiees), 0) FROM daily_streak"
            ).fetchone()[0]
            session = connection.execute(
                "SELECT submitted, score, passed FROM exam_sessions WHERE session_id = ?",
                (exam["id"],),
            ).fetchone()

        self.assertEqual(attempt_count, 1)
        self.assertEqual(total_xp, 100)
        self.assertEqual(coins, 50)
        self.assertEqual(streak_minutes, 5)
        self.assertEqual(tuple(session), (1, 100, 1))

    def test_course_exam_accepts_80_percent_even_if_legacy_threshold_is_85(self) -> None:
        self._unlock_ipv6_exam_prerequisite()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE requirements SET min_score = 85 WHERE node_id = 'ipv6-expert' AND kind = 'exam'"
            )
            connection.commit()

        response = self.client.post("/api/exam/start", json={"node_id": "ipv6-expert"})
        self.assertEqual(response.status_code, 200, response.text)
        exam = response.json()
        self.assertEqual(exam["passing_score"], 80)
        correct_answers = self._answer_key(exam)
        self.assertEqual(len(correct_answers), 10)

        # Huit bonnes réponses sur dix donnent exactement 80 %.
        answers = [
            correct_answers[index] if index < 8 else None
            for index in range(len(correct_answers))
        ]
        submitted = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": answers},
        )
        self.assertEqual(submitted.status_code, 200, submitted.text)
        result = submitted.json()
        self.assertEqual(result["score"], 80)
        self.assertTrue(result["passed"])
        self.assertEqual(result["pass_score"], 80)

        with sqlite3.connect(self.database_path) as connection:
            attempt = connection.execute(
                "SELECT score, passed FROM attempts "
                "WHERE node_id = 'ipv6-expert' AND kind = 'exam' ORDER BY id DESC LIMIT 1"
            ).fetchone()
        self.assertEqual(tuple(attempt), (80, 1))

    def test_course_exam_rejects_missing_prerequisites_and_missing_requirement(self) -> None:
        blocked = self.client.post("/api/exam/start", json={"node_id": "ipv6-expert"})
        self.assertEqual(blocked.status_code, 409, blocked.text)

        no_requirement = self.client.post(
            "/api/exam/start", json={"node_id": "intro-reseau-debutant"}
        )
        self.assertEqual(no_requirement.status_code, 409, no_requirement.text)

    def test_all_exam_types_share_the_80_percent_threshold(self) -> None:
        for should_pass in (False, True):
            exam = self._start_category_exam()
            self.assertEqual(exam["pass_score"], 80)
            self.assertEqual(exam["passing_score"], 80)

            correct_answers = self._answer_key(exam)
            total = len(correct_answers)
            passing_count = next(
                count for count in range(total + 1)
                if round(100 * count / total) >= api.EXAM_PASS_SCORE
            )
            chosen_correct = passing_count if should_pass else passing_count - 1
            answers = [
                correct_answers[index] if index < chosen_correct else None
                for index in range(total)
            ]

            response = self.client.post(
                "/api/exam/submit",
                json={"session_id": exam["id"], "answers": answers},
            )
            self.assertEqual(response.status_code, 200, response.text)
            result = response.json()
            self.assertEqual(result["passed"], should_pass)
            self.assertEqual(result["passed"], result["score"] >= 80)
            self.assertEqual(result["pass_score"], 80)

    def test_exam_requirement_uses_80_even_if_legacy_data_says_85(self) -> None:
        requirement = Requirement(kind=ProofKind.EXAM, min_score=85)
        attempt = Attempt(
            id=1,
            node_id="ipv6-expert",
            kind=ProofKind.EXAM,
            score=80,
            passed=True,
            evidence="",
            detail="test",
            created_at="2026-10-27 10:00:00",
        )
        node = Node(
            id="ipv6-expert",
            title="IPv6 - Expert",
            description="",
            module="Administration Réseaux",
            category="IPv6",
            sort_order=1,
            requirements=(requirement,),
            attempts=(attempt,),
        )

        self.assertEqual(api.effective_requirement_score(ProofKind.EXAM, 85), 80)
        self.assertEqual(api.effective_requirement_score(ProofKind.QUIZ, 85), 85)
        self.assertTrue(requirement_met(requirement, node))

    def test_exam_threshold_is_displayed_as_80_even_if_database_has_85(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE requirements SET min_score = 85 WHERE node_id = 'ipv6-expert' AND kind = 'exam'"
            )
            connection.commit()

        response = self.client.get("/api/tree")
        self.assertEqual(response.status_code, 200, response.text)
        node = next(item for item in response.json()["nodes"] if item["id"] == "ipv6-expert")
        exam_requirement = next(
            requirement for requirement in node["requirements_detail"]
            if requirement["kind"] == "exam"
        )
        self.assertEqual(exam_requirement["min_score"], 80)

    def test_invalid_payloads_and_unknown_sessions_are_rejected(self) -> None:
        invalid_category = self.client.post("/api/exam/start", json={"category": " "})
        self.assertEqual(invalid_category.status_code, 422, invalid_category.text)

        unknown_category = self.client.post(
            "/api/exam/start", json={"category": "Catégorie inexistante"}
        )
        self.assertEqual(unknown_category.status_code, 404, unknown_category.text)

        unknown_session = self.client.post(
            "/api/exam/submit", json={"session_id": "absent", "answers": []}
        )
        self.assertEqual(unknown_session.status_code, 404, unknown_session.text)

    
    def test_postgres_migration_adds_exam_session_columns(self) -> None:
        class RecordingPostgresConnection:
            is_postgres = True

            def __init__(self):
                self.statements: list[str] = []

            def executescript(self, script: str) -> None:
                self.statements.append("SCHEMA SCRIPT")

            def execute(self, sql: str, params=None):
                self.statements.append(sql)
                return self

            def commit(self) -> None:
                return None

        connection = RecordingPostgresConnection()
        db_module.initialize(connection)
        sql = "\\n".join(connection.statements)
        for column in (
            "node_id TEXT REFERENCES nodes(id) ON DELETE SET NULL",
            "exam_type TEXT NOT NULL DEFAULT 'category'",
            "passing_score INTEGER NOT NULL DEFAULT 80",
            "result_json TEXT NOT NULL DEFAULT ''",
        ):
            self.assertIn(column, sql)


if __name__ == "__main__":
    unittest.main()
