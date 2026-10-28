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
        self.assertEqual(54, len(data_nodes), "Le catalogue Data doit compter 18 thèmes sur trois niveaux.")
        self.assertTrue(all(node.get("module") == "Data & Bases de données" for node in data_nodes))
        self.assertTrue(all(node.get("category") == "Data & Bases de données" for node in data_nodes))

    def test_data_category_heading_displays_the_chart_icon(self):
        self.assertIn("category.name === 'Data &amp; Bases de données' ? '📊 ' + category.name", self.html)


if __name__ == "__main__":
    unittest.main()
