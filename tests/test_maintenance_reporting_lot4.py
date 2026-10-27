import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "content" / "lessons"
QUIZZES = ROOT / "content" / "quiz"
NODES = ROOT / "content" / "nodes.json"

LOT4 = {
    "maint-escalade-intermediaire": "Gestion de l'escalade (N1/N2/N3)",
    "maint-itil-intermediaire": "Frameworks ITIL (incidents, changements)",
    "maint-rca-intermediaire": "Analyse de cause racine (5 Pourquoi, Ishikawa)",
    "maint-sla-intermediaire": "SLA, OLA et satisfaction utilisateur",
    "maint-reporting-technique-intermediaire": "Rédiger un rapport d'incident",
}


class MaintenanceReportingLot4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with NODES.open(encoding="utf-8") as stream:
            cls.nodes = {node["id"]: node for node in json.load(stream)}

    def test_lessons_are_complete_and_match_the_curriculum(self):
        for node_id, title in LOT4.items():
            with self.subTest(node_id=node_id):
                lesson = (LESSONS / f"{node_id}.md").read_text(encoding="utf-8")
                node = self.nodes[node_id]
                self.assertGreater(len(lesson), 5000)
                self.assertEqual(node["title"], title)
                self.assertEqual(node["module"], "Maintenance & Reporting")
                self.assertIn("**Mise en contexte**", lesson)
                self.assertIn("## Mise en pratique", lesson)
                self.assertIn("## Exercices corrigés", lesson)
                self.assertIn("## Défi final corrigé", lesson)
                self.assertIn("~~~mermaid", lesson)
                self.assertNotIn("[Contenu à rédiger]", lesson)
                self.assertNotIn("node_id:", lesson)
                self.assertNotRegex(lesson, r"(?m)^---\s*$")

    def test_quizzes_have_real_questions_valid_answers_and_explanations(self):
        for node_id in LOT4:
            with self.subTest(node_id=node_id):
                with (QUIZZES / f"{node_id}.json").open(encoding="utf-8") as stream:
                    quiz = json.load(stream)
                self.assertEqual(quiz["node_id"], node_id)
                self.assertEqual(quiz["scope"], "quiz")
                self.assertGreaterEqual(len(quiz["questions"]), 8)
                for q in quiz["questions"]:
                    self.assertEqual(q["type"], "qcm")
                    self.assertGreaterEqual(len(q["choices"]), 4)
                    self.assertGreaterEqual(q["answer"], 0)
                    self.assertLess(q["answer"], len(q["choices"]))
                    self.assertTrue(q.get("explanation", "").strip())
                    self.assertNotIn("Question temporaire", q.get("prompt", ""))


if __name__ == "__main__":
    unittest.main()
