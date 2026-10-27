from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


class CertificateApiTests(unittest.TestCase):
    MODULE = "Administration Réseaux"
    MODULE_ID = "admin-reseaux"
    LEVEL = "debutant"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary.name) / "skilltree.sqlite3"
        self.db_patch = patch.object(api, "DB_PATH", self.database_path)
        self.db_patch.start()
        self.client = TestClient(api.app)
        self.client.__enter__()
        response = self.client.get("/api/tree")
        self.assertEqual(response.status_code, 200, response.text)
        self.nodes = response.json()["nodes"]
        self.scope = [
            node for node in self.nodes
            if node["module"] == self.MODULE
            and api._exam_level(node["id"], node["title"]) == self.LEVEL
        ]
        self.assertGreater(len(self.scope), 0)

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.db_patch.stop()
        self.temporary.cleanup()

    def _validate_scope_courses(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            for node in self.scope:
                requirements = connection.execute(
                    "SELECT kind FROM requirements WHERE node_id = ?",
                    (node["id"],),
                ).fetchall()
                for (kind,) in requirements:
                    connection.execute(
                        "INSERT INTO attempts "
                        "(node_id, kind, score, passed, evidence, detail, created_at) "
                        "VALUES (?, ?, 100, 1, '', 'certificate test fixture', '2026-10-27 10:00:00')",
                        (node["id"], kind),
                    )
            connection.commit()

    def _answer_key(self, exam: dict) -> list[int | str | None]:
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT question_ids FROM exam_sessions WHERE session_id = ?",
                (exam["id"],),
            ).fetchone()
            self.assertIsNotNone(row)
            question_ids = json.loads(row["question_ids"])
            answers: list[int | str | None] = []
            for question_id in question_ids:
                question = connection.execute(
                    "SELECT question_type, answer, answer_text FROM questions WHERE id = ?",
                    (question_id,),
                ).fetchone()
                self.assertIsNotNone(question)
                if question["question_type"] == "qcm":
                    answers.append(int(question["answer"]))
                else:
                    answers.append(str(question["answer_text"] or ""))
            return answers

    def _start_official_exam(self) -> dict:
        response = self.client.post(
            "/api/certificate/exam/start",
            json={"module": self.MODULE, "module_id": self.MODULE_ID, "level": self.LEVEL},
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["exam_type"], "certification")
        self.assertEqual(result["passing_score"], 80)
        self.assertEqual(result["module_scope"], self.MODULE)
        self.assertEqual(result["level_scope"], self.LEVEL)
        self.assertEqual(set(result["scope_node_ids"]), {node["id"] for node in self.scope})
        return result

    def test_official_exam_is_blocked_until_every_course_is_validated(self) -> None:
        response = self.client.post(
            "/api/certificate/exam/start",
            json={"module": self.MODULE, "module_id": self.MODULE_ID, "level": self.LEVEL},
        )
        self.assertEqual(response.status_code, 409, response.text)
        self.assertIn("Tous les cours du niveau", response.json()["detail"])

    def test_practice_exam_cannot_issue_an_official_certificate(self) -> None:
        self._validate_scope_courses()
        response = self.client.post(
            "/api/exam/build",
            json={
                "node_ids": [node["id"] for node in self.scope],
                "levels": [self.LEVEL],
                "count": 20,
                "time_limit": 1800,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        exam = response.json()
        submitted = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": self._answer_key(exam)},
        )
        self.assertEqual(submitted.status_code, 200, submitted.text)
        self.assertTrue(submitted.json()["passed"])

        issue = self.client.post(
            "/api/certificate/issue",
            json={
                "module": self.MODULE,
                "module_id": self.MODULE_ID,
                "level": self.LEVEL,
                "exam_session_id": exam["id"],
                "name": "Test Learner",
            },
        )
        self.assertEqual(issue.status_code, 409, issue.text)
        self.assertIn("examen officiel", issue.json()["detail"])

    def test_official_exam_issues_one_persistent_certificate_and_a_valid_pdf(self) -> None:
        self._validate_scope_courses()
        exam = self._start_official_exam()
        submitted = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": self._answer_key(exam)},
        )
        self.assertEqual(submitted.status_code, 200, submitted.text)
        self.assertTrue(submitted.json()["passed"])
        self.assertEqual(submitted.json()["score"], 100)

        payload = {
            "module": self.MODULE,
            "module_id": self.MODULE_ID,
            "level": self.LEVEL,
            "exam_session_id": exam["id"],
            "name": "Élodie Réseau",
        }
        issued = self.client.post("/api/certificate/issue", json=payload)
        self.assertEqual(issued.status_code, 200, issued.text)
        self.assertTrue(issued.json()["success"])
        self.assertFalse(issued.json()["already_issued"])
        certificate = issued.json()["certificate"]
        self.assertEqual(certificate["module"], self.MODULE_ID)
        self.assertEqual(certificate["module_label"], self.MODULE)
        self.assertEqual(certificate["level"], self.LEVEL)
        self.assertEqual(certificate["score"], 100)
        self.assertEqual(certificate["courses"], len(self.scope))

        duplicate = self.client.post("/api/certificate/issue", json=payload)
        self.assertEqual(duplicate.status_code, 200, duplicate.text)
        self.assertTrue(duplicate.json()["already_issued"])
        self.assertEqual(duplicate.json()["certificate"]["number"], certificate["number"])

        listing = self.client.get("/api/certificates")
        self.assertEqual(listing.status_code, 200, listing.text)
        matching = [
            item for item in listing.json()["items"]
            if item["module"] == self.MODULE_ID and item["level"] == self.LEVEL
        ]
        self.assertEqual(len(matching), 1)
        self.assertEqual(len(listing.json()["exams"]), 1)

        pdf = self.client.get("/api/certificate", params={"number": certificate["number"]})
        self.assertEqual(pdf.status_code, 200, pdf.text)
        self.assertEqual(pdf.headers["content-type"], "application/pdf")
        self.assertTrue(pdf.content.startswith(b"%PDF-1.4"))
        self.assertIn(b"%%EOF", pdf.content)
        self.assertNotEqual(pdf.content, b"PDF EXEMPLE")

        missing = self.client.get("/api/certificate", params={"number": "UNKNOWN"})
        self.assertEqual(missing.status_code, 404)

    def test_failed_official_exam_cannot_issue_a_certificate(self) -> None:
        self._validate_scope_courses()
        exam = self._start_official_exam()
        submitted = self.client.post(
            "/api/exam/submit",
            json={"session_id": exam["id"], "answers": [None] * len(exam["questions"])},
        )
        self.assertEqual(submitted.status_code, 200, submitted.text)
        self.assertFalse(submitted.json()["passed"])
        issue = self.client.post(
            "/api/certificate/issue",
            json={
                "module": self.MODULE,
                "module_id": self.MODULE_ID,
                "level": self.LEVEL,
                "exam_session_id": exam["id"],
                "name": "Test Learner",
            },
        )
        self.assertEqual(issue.status_code, 409, issue.text)
        listing = self.client.get("/api/certificates")
        self.assertEqual(listing.json()["items"], [])


if __name__ == "__main__":
    unittest.main()
