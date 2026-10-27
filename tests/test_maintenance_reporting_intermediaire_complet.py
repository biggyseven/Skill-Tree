# Validate after removing orphan empty lesson stubs from feature/lab-workspace.
# Re-run catalog and content validation after branch-base cleanup.
# Regression checks for the complete intermediate Maintenance & Reporting path.
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "content" / "lessons"
QUIZZES = ROOT / "content" / "quiz"
NODES = ROOT / "content" / "nodes.json"

COURSES = {
    "maint-monitoring-intermediaire": ("Supervision réseau (Nagios, Zabbix)", "maint-securite-bases-debutant"),
    "maint-sauvegarde-intermediaire": ("Stratégies de sauvegarde (3-2-1)", "maint-monitoring-intermediaire"),
    "maint-maintenance-preventive-intermediaire": ("Planifier la maintenance préventive", "maint-sauvegarde-intermediaire"),
    "maint-gestion-parc-intermediaire": ("Gestion de parc (GLPI, OCS)", "maint-maintenance-preventive-intermediaire"),
    "maint-procedure-intermediaire": ("Rédiger des procédures et checklists", "maint-gestion-parc-intermediaire"),
    "maint-escalade-intermediaire": ("Gestion de l'escalade (N1/N2/N3)", "maint-procedure-intermediaire"),
    "maint-itil-intermediaire": ("Frameworks ITIL (incidents, changements)", "maint-escalade-intermediaire"),
    "maint-rca-intermediaire": ("Analyse de cause racine (5 Pourquoi, Ishikawa)", "maint-itil-intermediaire"),
    "maint-sla-intermediaire": ("SLA, OLA et satisfaction utilisateur", "maint-rca-intermediaire"),
    "maint-reporting-technique-intermediaire": ("Rédiger un rapport d'incident", "maint-sla-intermediaire"),
    "maint-reporting-mensuel-intermediaire": ("Rédiger un reporting mensuel", "maint-reporting-technique-intermediaire"),
    "maint-automatisation-intermediaire": ("Automatiser les tâches (scripts, Ansible)", "maint-reporting-mensuel-intermediaire"),
}

def word_count(value):
    return len(re.findall(r"\b[\w’'-]+\b", value, flags=re.UNICODE))

def diagram_count(value):
    return len(re.findall(r"(?m)^\s*(?:~~~|\x60\x60\x60)\s*mermaid\s*$", value))

class IntermediateMaintenanceCourseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with NODES.open(encoding="utf-8") as stream:
            cls.nodes = {item["id"]: item for item in json.load(stream)}

    def test_courses_match_catalog_and_have_enough_content(self):
        for node_id, (title, prereq) in COURSES.items():
            with self.subTest(node=node_id):
                content = (LESSONS / f"{node_id}.md").read_text(encoding="utf-8")
                node = self.nodes[node_id]
                self.assertGreaterEqual(word_count(content), 3000)
                self.assertGreaterEqual(diagram_count(content), 4)
                self.assertEqual(node["title"], title)
                self.assertEqual(node["module"], "Maintenance & Reporting")
                self.assertEqual(node["prereqs"], [prereq])
                self.assertTrue(content.startswith("# " + title))
                self.assertIn("**Mise en contexte**", content)
                self.assertRegex(content, r"(?mi)^## .*Objectifs")
                self.assertRegex(content, r"(?mi)^## .*?(Mise en pratique|Travaux pratiques)")
                self.assertRegex(content, r"(?mi)^## .*Exercices.*(corrigés|corrections)")
                self.assertRegex(content, r"(?mi)^## .*Défi final")
                self.assertNotIn("[Contenu à rédiger]", content)
                self.assertNotIn("Question temporaire", content)

    def test_each_course_has_eight_valid_qcm_questions(self):
        for node_id in COURSES:
            with self.subTest(node=node_id):
                with (QUIZZES / f"{node_id}.json").open(encoding="utf-8") as stream:
                    quiz = json.load(stream)
                self.assertEqual(quiz["node_id"], node_id)
                self.assertEqual(quiz["scope"], "quiz")
                self.assertEqual(len(quiz["questions"]), 8)
                for question in quiz["questions"]:
                    self.assertEqual(question["type"], "qcm")
                    self.assertGreaterEqual(len(question["choices"]), 4)
                    self.assertIsInstance(question["answer"], int)
                    self.assertGreaterEqual(question["answer"], 0)
                    self.assertLess(question["answer"], len(question["choices"]))
                    self.assertTrue(question.get("prompt", "").strip())
                    self.assertTrue(question.get("explanation", "").strip())
                    self.assertNotIn("Question temporaire", question["prompt"])

if __name__ == "__main__":
    unittest.main()
