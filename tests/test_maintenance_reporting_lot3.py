import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "content" / "lessons"
QUIZZES = ROOT / "content" / "quiz"
NODES = ROOT / "content" / "nodes.json"

LOT3 = {
    "maint-monitoring-intermediaire": "Supervision réseau (Nagios, Zabbix)",
    "maint-sauvegarde-intermediaire": "Stratégies de sauvegarde (3-2-1)",
    "maint-maintenance-preventive-intermediaire": "Planifier la maintenance préventive",
    "maint-gestion-parc-intermediaire": "Gestion de parc (GLPI, OCS)",
    "maint-procedure-intermediaire": "Rédiger des procédures et checklists",
}


class MaintenanceReportingLot3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with NODES.open(encoding="utf-8") as stream:
            cls.nodes = json.load(stream)
        cls.nodes_by_id = {node["id"]: node for node in cls.nodes}

    def test_every_lesson_is_complete_and_matches_its_node(self):
        for node_id, title in LOT3.items():
            with self.subTest(node_id=node_id):
                path = LESSONS / f"{node_id}.md"
                self.assertTrue(path.is_file(), f"Lesson missing: {path}")
                lesson = path.read_text(encoding="utf-8")
                self.assertGreater(len(lesson), 5000)
                self.assertIn(title, lesson)
                self.assertIn("**Mise en contexte**", lesson)
                self.assertIn("## Mise en pratique", lesson)
                self.assertIn("## Exercices corrigés", lesson)
                self.assertIn("## Défi final corrigé", lesson)
                self.assertIn("~~~mermaid", lesson)
                self.assertNotIn("[Contenu à rédiger]", lesson)
                self.assertNotIn("node_id:", lesson)
                self.assertNotRegex(lesson, r"(?m)^---\s*$")
                self.assertIn(node_id, self.nodes_by_id)
                self.assertEqual(self.nodes_by_id[node_id]["module"], "Maintenance & Reporting")

    def test_each_quiz_has_real_questions_and_valid_answers(self):
        for node_id in LOT3:
            with self.subTest(node_id=node_id):
                path = QUIZZES / f"{node_id}.json"
                self.assertTrue(path.is_file(), f"Quiz missing: {path}")
                with path.open(encoding="utf-8") as stream:
                    quiz = json.load(stream)
                self.assertEqual(quiz.get("node_id"), node_id)
                self.assertEqual(quiz.get("scope"), "quiz")
                questions = quiz.get("questions", [])
                self.assertGreaterEqual(len(questions), 8)
                for question in questions:
                    self.assertEqual(question.get("type"), "qcm")
                    self.assertGreaterEqual(len(question.get("choices", [])), 4)
                    self.assertGreaterEqual(question.get("answer", -1), 0)
                    self.assertLess(question["answer"], len(question["choices"]))
                    self.assertTrue(question.get("explanation", "").strip())
                    self.assertNotIn("Question temporaire", question.get("prompt", ""))

    def test_lesson_titles_match_the_node_titles(self):
        for node_id, title in LOT3.items():
            with self.subTest(node_id=node_id):
                self.assertEqual(self.nodes_by_id[node_id]["title"], title)


if __name__ == "__main__":
    unittest.main()
