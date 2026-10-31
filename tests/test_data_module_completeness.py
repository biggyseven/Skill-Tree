"""Contrôles des ressources et de la progression cumulative du module Data."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

class DataModuleResourceCompletenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes = json.loads((CONTENT / "nodes.json").read_text(encoding="utf-8"))
        cls.data_nodes = [node for node in cls.nodes if node.get("module") == "Data & Bases de données"]

    def test_all_data_module_courses_have_complete_lesson_and_quiz_resources(self):
        self.assertEqual(len(self.data_nodes), 54, "Le module Data doit recenser 18 thèmes avec leurs trois niveaux.")
        for node in self.data_nodes:
            node_id = node["id"]
            lesson = CONTENT / "lessons" / f"{node_id}.md"
            quiz = CONTENT / "quiz" / f"{node_id}.json"
            with self.subTest(node_id=node_id):
                self.assertTrue(lesson.is_file(), f"Leçon manquante : {lesson.name}")
                self.assertTrue(quiz.is_file(), f"Quiz manquant : {quiz.name}")
                content = lesson.read_text(encoding="utf-8").strip()
                self.assertGreaterEqual(len(content.split()), 5000, f"Cours trop court : {lesson.name}")
                self.assertGreaterEqual(content.count("```mermaid"), 4, f"Schémas Mermaid manquants : {lesson.name}")
                self.assertNotRegex(content[:400], r"(?im)^---\s*$|^node_id:|^filename:|^language:")
                self.assertNotIn("en cours de rédaction", content.lower())
                data = json.loads(quiz.read_text(encoding="utf-8"))
                self.assertEqual(data.get("node_id"), node_id, f"{quiz.name}: node_id incohérent")
                questions = data.get("questions")
                self.assertIsInstance(questions, list, f"{quiz.name}: questions absentes")
                self.assertGreaterEqual(len(questions), 5, f"{quiz.name}: quiz trop court")
                prompts = [q.get("prompt", "").strip().lower() for q in questions]
                self.assertEqual(len(prompts), len(set(prompts)), f"{quiz.name}: énoncés dupliqués")
                positions = set()
                for index, question in enumerate(questions, 1):
                    self.assertTrue(question.get("prompt", "").strip(), f"{quiz.name} Q{index}: énoncé vide")
                    self.assertTrue(question.get("explanation", "").strip(), f"{quiz.name} Q{index}: explication absente")
                    choices = question.get("choices", [])
                    self.assertEqual(len(choices), 4, f"{quiz.name} Q{index}: quatre choix attendus")
                    self.assertEqual(len(set(choices)), 4, f"{quiz.name} Q{index}: choix dupliqués")
                    answer = question.get("answer")
                    self.assertIsInstance(answer, int, f"{quiz.name} Q{index}: réponse non entière")
                    self.assertGreaterEqual(answer, 0)
                    self.assertLess(answer, len(choices))
                    positions.add(answer)
                self.assertGreaterEqual(len(positions), 3, f"{quiz.name}: positions de réponses trop prévisibles")

    def test_relational_basics_track_has_three_cumulative_levels(self):
        by_id = {node["id"]: node for node in self.data_nodes}
        expected = {
            "data-bases-debutant": [],
            "data-bases-intermediaire": ["data-bases-debutant"],
            "data-bases-expert": ["data-bases-intermediaire"],
            "data-sql-1-debutant": ["data-bases-expert"],
        }
        for node_id, prereqs in expected.items():
            with self.subTest(node_id=node_id):
                self.assertIn(node_id, by_id)
                self.assertEqual(by_id[node_id].get("prereqs", []), prereqs)
        self.assertLess(by_id["data-bases-debutant"]["order"],
                        by_id["data-bases-intermediaire"]["order"])
        self.assertLess(by_id["data-bases-intermediaire"]["order"],
                        by_id["data-bases-expert"]["order"])
        self.assertLess(by_id["data-bases-expert"]["order"],
                        by_id["data-sql-1-debutant"]["order"])

    def test_all_data_tracks_have_three_cumulative_levels(self):
        roots = ["data-bases","data-sql-1","data-modelisation","data-sql-2","data-normalisation","data-sql-pratique","data-dba-role","data-sql-avance","data-optimisation","data-sauvegarde","data-nosql","data-warehouse","data-bigdata","data-streaming","data-datalake","data-securite","data-gouvernance","data-ingestion"]
        by_id = {node["id"]: node for node in self.data_nodes}
        expected = [f"{root}-{level}" for root in roots
                    for level in ("debutant", "intermediaire", "expert")]
        self.assertEqual(len(expected), 54)
        for index, node_id in enumerate(expected):
            with self.subTest(node_id=node_id):
                expected_prereqs = [] if index == 0 else [expected[index - 1]]
                self.assertIn(node_id, by_id)
                self.assertEqual(by_id[node_id].get("prereqs", []), expected_prereqs)
                self.assertEqual(by_id[node_id].get("order"), 4340 + index)

if __name__ == "__main__":
    unittest.main()
