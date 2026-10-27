"""Tests ciblés : visibilité du module Data dans le site servi par FastAPI."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DataModuleVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        cls.nodes = json.loads((ROOT / "content" / "nodes.json").read_text(encoding="utf-8"))

    def test_data_module_is_registered_in_the_module_cards(self):
        self.assertIn("{ id: 'data', label: 'Data & Bases de données', short: 'Data', icon: '📊'", self.html)
        self.assertIn("raw.toLowerCase().startsWith('data')", self.html)
        self.assertIn("id.startsWith('data-')", self.html)

    def test_data_courses_are_mapped_to_the_data_module(self):
        data_nodes = [node for node in self.nodes if node.get("id", "").startswith("data-")]
        self.assertEqual(18, len(data_nodes))
        self.assertTrue(all(node.get("module") == "Data & Bases de données" for node in data_nodes))
        self.assertTrue(all(node.get("category") == "Data & Bases de données" for node in data_nodes))

    def test_all_data_lessons_are_complete_and_not_placeholders(self):
        placeholder_markers = (
            "contenu pédagogique en préparation",
            "emplacement provisoire",
            "le cours complet sera rédigé dans une étape ultérieure",
        )
        for node in self.nodes:
            node_id = node.get("id", "")
            if not node_id.startswith("data-"):
                continue
            lesson_path = ROOT / "content" / "lessons" / f"{node_id}.md"
            self.assertTrue(lesson_path.is_file(), f"Leçon Data absente : {lesson_path.name}")
            lesson = lesson_path.read_text(encoding="utf-8")
            words = len(lesson.split())
            self.assertGreaterEqual(
                words,
                5000,
                f"{lesson_path.name} est trop court : {words} mots (minimum : 5000)",
            )
            lowered = lesson.lower()
            for marker in placeholder_markers:
                self.assertNotIn(marker, lowered, f"Placeholder détecté dans {lesson_path.name}: {marker}")

    def test_data_category_heading_displays_the_chart_icon(self):
        self.assertIn("category.name === 'Data &amp; Bases de données' ? '📊 ' + category.name", self.html)


if __name__ == "__main__":
    unittest.main()
