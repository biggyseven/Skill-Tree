from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from app.loader import _parse_nodes


ROOT = Path(__file__).resolve().parents[1]
MODULE_NAME = "Commandes & Aide-mémoire"
EXPECTED = {
    "cmd-base": "Configuration de base (Hostname, SSH, Mots de passe, NTP)",
    "cmd-interfaces": "Interfaces & VLANs (Switchport, Trunk, Router-on-a-stick)",
    "cmd-routage": "Routage & OSPF (Routes statiques, OSPF, EIGRP)",
    "cmd-securite": "Sécurité & ACL (Access-lists, Port-security, DHCP Snooping)",
    "cmd-verification": "Vérification & Diagnostic (Show, Debug, Ping, Traceroute)",
}


def _word_count(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    return len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", content, flags=re.UNICODE))


class CiscoCommandReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes = json.loads((ROOT / "content" / "nodes.json").read_text(encoding="utf-8"))
        cls.node_by_id = {node["id"]: node for node in cls.nodes}

    def test_module_is_registered_in_catalog_source(self):
        catalog = (ROOT / "app" / "main_ui" / "skilltree-catalog.js").read_text(encoding="utf-8")
        self.assertIn("id: 'commandes', label: 'Commandes & Aide-mémoire'", catalog)
        self.assertIn("icon: '⌨️'", catalog)
        for item in (
            "Config de base",
            "Interfaces & VLANs",
            "Routage & OSPF",
            "Sécurité & ACL",
            "Vérification & Diagnostic",
        ):
            self.assertIn(item, catalog)
        self.assertIn("if (id.startsWith('cmd-')) return 'commandes';", catalog)
        for node_id in EXPECTED:
            self.assertIn(f"'{node_id}': 'intermediaire'", catalog)

    def test_loader_accepts_requirement_free_reference_nodes(self):
        parsed = _parse_nodes(ROOT / "content" / "nodes.json")
        by_id = {node.id: node for node in parsed}
        for node_id in EXPECTED:
            self.assertIn(node_id, by_id)
            self.assertEqual(by_id[node_id].requirements, ())

    def test_nodes_are_immediately_available_and_not_quiz_driven(self):
        self.assertEqual(len(self.node_by_id), len(self.nodes), "Les identifiants de nœuds doivent être uniques.")
        for node_id, title in EXPECTED.items():
            node = self.node_by_id[node_id]
            self.assertEqual(node["module"], MODULE_NAME)
            self.assertEqual(node["title"], title)
            self.assertEqual(node.get("prereqs", []), [])
            self.assertEqual(node.get("requirements", []), [])

            lesson = ROOT / "content" / "lessons" / f"{node_id}.md"
            self.assertTrue(lesson.is_file(), f"Fiche manquante : {lesson.name}")
            self.assertGreaterEqual(_word_count(lesson), 800, f"Fiche trop courte : {lesson.name}")
            self.assertLessEqual(_word_count(lesson), 1200, f"Fiche trop longue : {lesson.name}")
            quiz = ROOT / "content" / "quiz" / f"{node_id}.json"
            self.assertFalse(quiz.exists(), f"Quiz individuel inattendu : {quiz.name}")


if __name__ == "__main__":
    unittest.main()
