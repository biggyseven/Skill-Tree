import json
import re
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db import connect, ensure_ready
from app.loader import sync_content_additions
EXPECTED = {
    "data-bases-debutant", "data-sql-1-debutant", "data-modelisation-debutant",
    "data-sql-2-debutant", "data-normalisation-debutant", "data-sql-pratique-debutant",
    "data-dba-role-intermediaire", "data-sql-avance-intermediaire",
    "data-optimisation-intermediaire", "data-sauvegarde-intermediaire",
    "data-nosql-intermediaire", "data-warehouse-intermediaire",
    "data-bigdata-expert", "data-streaming-expert", "data-datalake-expert",
    "data-securite-expert", "data-gouvernance-expert", "data-ingestion-expert",
}

class DataModuleIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes = json.loads((ROOT / "content" / "nodes.json").read_text(encoding="utf-8"))
        cls.by_id = {node["id"]: node for node in cls.nodes}
        cls.data_nodes = {key: cls.by_id[key] for key in EXPECTED if key in cls.by_id}

    def test_catalog_contains_all_eighteen_data_courses(self):
        self.assertEqual(EXPECTED, set(self.data_nodes))
        for node in self.data_nodes.values():
            self.assertEqual("Data & Bases de données", node.get("module"))
            self.assertEqual("Data & Bases de données", node.get("category"))

    def test_prerequisites_resolve_inside_catalog(self):
        for node in self.data_nodes.values():
            for prerequisite in node.get("prereqs", []):
                self.assertIn(prerequisite, self.by_id, f"{node['id']} -> {prerequisite}")

    def test_each_lesson_exists_and_has_at_least_five_thousand_words(self):
        for node_id in sorted(EXPECTED):
            path = ROOT / "content" / "lessons" / f"{node_id}.md"
            self.assertTrue(path.is_file(), f"Missing lesson: {path.name}")
            content = path.read_text(encoding="utf-8")
            word_count = len(re.findall(r"\S+", content))
            self.assertGreaterEqual(word_count, 5000, f"{path.name}: only {word_count} words")
            self.assertIn("Mise en contexte", content)

    def test_each_quiz_has_at_least_five_distinct_well_formed_questions(self):
        for node_id in sorted(EXPECTED):
            path = ROOT / "content" / "quiz" / f"{node_id}.json"
            self.assertTrue(path.is_file(), f"Missing quiz: {path.name}")
            quiz = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(node_id, quiz.get("node_id"), path.name)
            questions = quiz.get("questions", [])
            self.assertGreaterEqual(len(questions), 5, path.name)
            self.assertLessEqual(len(questions), 8, path.name)
            prompts = [q.get("prompt", "").strip() for q in questions]
            self.assertTrue(all(prompts), f"Empty prompt in {path.name}")
            self.assertEqual(len(questions), len(set(prompts)), f"Duplicated question in {path.name}")
            for index, question in enumerate(questions, start=1):
                self.assertEqual("qcm", question.get("type"), f"{path.name}, Q{index}")
                choices = question.get("choices")
                self.assertIsInstance(choices, list, f"{path.name}, Q{index}")
                self.assertEqual(4, len(choices), f"{path.name}, Q{index}")
                self.assertIsInstance(question.get("answer"), int, f"{path.name}, Q{index}")
                self.assertGreaterEqual(question["answer"], 0, f"{path.name}, Q{index}")
                self.assertLess(question["answer"], len(choices), f"{path.name}, Q{index}")
                self.assertGreaterEqual(len(question.get("explanation", "").strip()), 10,
                                        f"{path.name}, Q{index}")

    def test_fresh_sqlite_database_loads_forward_prerequisites(self):
        conn = connect(":memory:")
        try:
            ensure_ready(conn)
            loaded_ids = {row["id"] for row in conn.execute("SELECT id FROM nodes")}
            self.assertEqual(set(self.by_id), loaded_ids)
            self.assertEqual(18, sum(node_id.startswith("data-") for node_id in loaded_ids))
            for node in self.data_nodes.values():
                for prerequisite in node.get("prereqs", []):
                    self.assertIn(prerequisite, loaded_ids)
        finally:
            conn.close()


    def test_existing_database_adds_data_module_without_losing_progress(self):
        conn = connect(":memory:")
        try:
            ensure_ready(conn)
            with conn:
                conn.execute("DELETE FROM nodes WHERE id LIKE 'data-%'")
                conn.execute(
                    "INSERT INTO attempts "
                    "(node_id, kind, score, passed, evidence, detail, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("intro-reseau-debutant", "quiz", 100, 1, "fixture", "keep", "2026-01-01T00:00:00Z"),
                )

            report = sync_content_additions(conn)
            self.assertEqual(18, report["nodes_added"])
            data_ids = {
                row["id"] for row in conn.execute(
                    "SELECT id FROM nodes WHERE id LIKE 'data-%'"
                ).fetchall()
            }
            self.assertEqual(EXPECTED, data_ids)

            for node_id in EXPECTED:
                question_count = conn.execute(
                    "SELECT COUNT(*) FROM questions WHERE node_id = ? AND scope = 'quiz'",
                    (node_id,),
                ).fetchone()[0]
                self.assertGreaterEqual(question_count, 5, node_id)

            preserved = conn.execute(
                "SELECT detail FROM attempts WHERE node_id = 'intro-reseau-debutant'"
            ).fetchone()
            self.assertIsNotNone(preserved)
            self.assertEqual("keep", preserved["detail"])
        finally:
            conn.close()

    def test_dashboard_exposes_and_routes_the_data_module(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("id: 'data'", html)
        self.assertIn("icon: '📊'", html)
        self.assertIn("raw.startsWith('data')", html)
        self.assertIn("cat.startsWith('data')", html)

if __name__ == "__main__":
    unittest.main()
