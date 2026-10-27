import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "content" / "lessons"
QUIZZES = ROOT / "content" / "quiz"
NODES = ROOT / "content" / "nodes.json"

FOUNDATIONS = {
    "maint-glossaire-debutant": {
        "title": "Vocabulaire technique et communication",
        "prereq": "maint-tickets-debutant",
    },
    "maint-documentation-debutant": {
        "title": "Rédiger une fiche d'intervention",
        "prereq": "maint-glossaire-debutant",
    },
    "maint-securite-bases-debutant": {
        "title": "Sécurité de base pour les interventions",
        "prereq": "maint-documentation-debutant",
    },
}


def count_words(text):
    return len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE))


def count_mermaid_diagrams(text):
    return len(re.findall(r"(?m)^\s*(?:```|~~~)mermaid\s*$", text))


class MaintenanceReportingFoundationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with NODES.open(encoding="utf-8") as stream:
            cls.nodes = {node["id"]: node for node in json.load(stream)}

    def test_lessons_meet_word_diagram_and_curriculum_requirements(self):
        for node_id, expected in FOUNDATIONS.items():
            with self.subTest(node_id=node_id):
                lesson = (LESSONS / f"{node_id}.md").read_text(encoding="utf-8")
                node = self.nodes[node_id]
                self.assertGreaterEqual(count_words(lesson), 5000)
                self.assertGreaterEqual(count_mermaid_diagrams(lesson), 3)
                self.assertEqual(node["title"], expected["title"])
                self.assertEqual(node["module"], "Maintenance & Reporting")
                self.assertEqual(node["prereqs"], [expected["prereq"]])
                self.assertIn("**Mise en contexte**", lesson)
                self.assertRegex(lesson, r"(?m)^## .*Objectifs pédagogiques")
                self.assertRegex(lesson, r"(?mi)^## .*Travaux pratiques")
                self.assertRegex(lesson, r"(?mi)^## .*Exercices avec corrections")
                self.assertRegex(lesson, r"(?mi)^## .*Défi final")
                self.assertRegex(lesson, r"(?mi)^## .*Synthèse du cours")
                self.assertNotIn("[Contenu à rédiger]", lesson)
                self.assertNotIn("node_id:", lesson)
                self.assertNotRegex(lesson, r"(?m)^---\s*$")

    def test_quizzes_have_eight_complete_qcm_items(self):
        for node_id in FOUNDATIONS:
            with self.subTest(node_id=node_id):
                with (QUIZZES / f"{node_id}.json").open(encoding="utf-8") as stream:
                    quiz = json.load(stream)
                self.assertEqual(quiz["node_id"], node_id)
                self.assertEqual(quiz["scope"], "quiz")
                self.assertEqual(len(quiz["questions"]), 8)
                for question in quiz["questions"]:
                    self.assertEqual(question["type"], "qcm")
                    self.assertGreaterEqual(len(question["choices"]), 4)
                    self.assertGreaterEqual(question["answer"], 0)
                    self.assertLess(question["answer"], len(question["choices"]))
                    self.assertTrue(question.get("prompt", "").strip())
                    self.assertTrue(question.get("explanation", "").strip())
                    self.assertNotIn("Question temporaire", question["prompt"])


if __name__ == "__main__":
    unittest.main()
