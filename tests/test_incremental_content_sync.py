from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.db import connect, initialize
from app.loader import sync_content_additions


class IncrementalContentSyncTests(unittest.TestCase):
    def _write_content(self, root: Path) -> None:
        (root / "quiz").mkdir(parents=True)
        (root / "exam").mkdir()
        (root / "labs").mkdir()
        (root / "terminal").mkdir()
        nodes = [
            {
                "id": "existing-course",
                "title": "Cours existant mis à jour",
                "description": "Description issue du catalogue canonique.",
                "module": "Cybersécurité",
                "category": "Cybersécurité",
                "order": 10,
                "prereqs": [],
                "requirements": [{"kind": "quiz", "min_score": 80}],
            },
            {
                "id": "new-course",
                "title": "Nouveau cours",
                "description": "Un nouveau cours doit devenir visible.",
                "module": "Cybersécurité",
                "category": "Cybersécurité",
                "order": 11,
                "prereqs": ["existing-course"],
                "requirements": [{"kind": "quiz", "min_score": 85}],
            },
        ]
        (root / "nodes.json").write_text(
            json.dumps(nodes, ensure_ascii=False), encoding="utf-8"
        )
        questions = {
            "existing-course": {
                "node_id": "existing-course",
                "scope": "quiz",
                "questions": [
                    {
                        "type": "qcm",
                        "prompt": "Quel contrôle limite le privilège excessif ?",
                        "choices": [
                            "Le moindre privilège",
                            "La suppression des journaux",
                            "Un mot de passe partagé",
                            "La désactivation de l’audit",
                        ],
                        "answer": 0,
                        "explanation": "Le moindre privilège limite les droits au besoin.",
                    }
                ],
            },
            "new-course": {
                "node_id": "new-course",
                "scope": "quiz",
                "questions": [
                    {
                        "type": "qcm",
                        "prompt": "Que doit contenir une hypothèse testable ?",
                        "choices": [
                            "Une conclusion fixée d’avance",
                            "Une précondition et un résultat observable",
                            "Un outil sans objectif",
                            "Une requête non documentée",
                        ],
                        "answer": 1,
                        "explanation": "Une hypothèse décrit les conditions et les observations attendues.",
                    }
                ],
            },
        }
        for node_id, payload in questions.items():
            (root / "quiz" / f"{node_id}.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )

    def test_adds_new_course_and_replaces_only_temporary_quiz_without_losing_progress(self) -> None:
        with TemporaryDirectory() as temporary:
            content_root = Path(temporary) / "content"
            content_root.mkdir()
            self._write_content(content_root)

            conn = connect(":memory:")
            try:
                initialize(conn)
                conn.execute(
                    "INSERT INTO nodes (id, title, description, category, module, sort_order)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    ("existing-course", "Ancien titre", "Ancienne description", "Général", "Général", 1),
                )
                conn.execute(
                    "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
                    ("existing-course", "quiz", 80),
                )
                conn.execute(
                    "INSERT INTO questions"
                    " (node_id, scope, prompt, choices, answer, question_type, explanation, position)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        "existing-course",
                        "quiz",
                        "Question placeholder pour un cours à rédiger.",
                        json.dumps(["Option A (placeholder)", "Option B", "Option C", "Option D"]),
                        0,
                        "qcm",
                        "Question temporaire à remplacer.",
                        0,
                    ),
                )
                conn.execute(
                    "INSERT INTO attempts (node_id, kind, score, passed, evidence, detail, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        "existing-course",
                        "quiz",
                        100,
                        1,
                        "preuve-validée",
                        "Tentative historique à préserver",
                        "2026-10-27T00:00:00Z",
                    ),
                )
                conn.execute(
                    "INSERT INTO exam_sessions"
                    " (session_id, category, question_ids, started_at, expires_at, node_id, exam_type)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("session-active", "Cybersécurité", "[]", 100, 200, "existing-course", "course"),
                )
                conn.commit()

                report = sync_content_additions(conn, content_root)

                new_node = conn.execute(
                    "SELECT title, description FROM nodes WHERE id = 'new-course'"
                ).fetchone()
                existing_node = conn.execute(
                    "SELECT title, description FROM nodes WHERE id = 'existing-course'"
                ).fetchone()
                edges = conn.execute(
                    "SELECT node_id, prereq_id FROM edges WHERE node_id = 'new-course'"
                ).fetchall()
                old_quiz = conn.execute(
                    "SELECT prompt, answer FROM questions"
                    " WHERE node_id = 'existing-course' AND scope = 'quiz' ORDER BY position"
                ).fetchall()
                new_quiz = conn.execute(
                    "SELECT prompt, answer FROM questions"
                    " WHERE node_id = 'new-course' AND scope = 'quiz' ORDER BY position"
                ).fetchall()
                attempt = conn.execute(
                    "SELECT detail, passed FROM attempts WHERE node_id = 'existing-course'"
                ).fetchone()
                active_session = conn.execute(
                    "SELECT session_id FROM exam_sessions WHERE session_id = 'session-active'"
                ).fetchone()

                self.assertEqual(report["nodes_added"], 1)
                self.assertEqual(report["quiz_banks_added"], 1)
                self.assertEqual(report["quiz_banks_refreshed"], 1)
                self.assertEqual(new_node["title"], "Nouveau cours")
                self.assertEqual(existing_node["title"], "Cours existant mis à jour")
                self.assertEqual(edges[0]["prereq_id"], "existing-course")
                self.assertEqual(old_quiz[0]["prompt"], "Quel contrôle limite le privilège excessif ?")
                self.assertEqual(old_quiz[0]["answer"], 0)
                self.assertEqual(new_quiz[0]["prompt"], "Que doit contenir une hypothèse testable ?")
                self.assertEqual(new_quiz[0]["answer"], 1)
                self.assertEqual(attempt["detail"], "Tentative historique à préserver")
                self.assertEqual(attempt["passed"], 1)
                self.assertIsNotNone(active_session)

                second_report = sync_content_additions(conn, content_root)
                self.assertEqual(second_report["nodes_added"], 0)
                self.assertEqual(second_report["quiz_banks_added"], 0)
                self.assertEqual(second_report["quiz_banks_refreshed"], 0)
                self.assertEqual(
                    conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 1
                )
                self.assertEqual(
                    conn.execute(
                        "SELECT COUNT(*) FROM questions WHERE node_id = 'new-course' AND scope = 'quiz'"
                    ).fetchone()[0],
                    1,
                )
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
