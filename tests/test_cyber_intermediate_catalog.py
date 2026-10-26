from __future__ import annotations

import json
import unittest
from pathlib import Path

from app.api import _configured_node_labs

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
TRACK = [
    ("secu-acl-intermediaire", "ACL et filtrage avancé", "secu-firewall-debutant"),
    ("secu-nat-intermediaire", "NAT et sécurité du périmètre", "secu-acl-intermediaire"),
    ("secu-vpn-intermediaire", "VPN Site-to-Site et d'accès distant", "secu-nat-intermediaire"),
    ("secu-switch-secu-intermediaire", "Sécurité des commutateurs (Couche 2)", "secu-vpn-intermediaire"),
    ("secu-ngfw-intermediaire", "Architecture de pare-feu (NGFW)", "secu-switch-secu-intermediaire"),
    ("secu-ids-intermediaire", "IDS/IPS et détection d'intrusion", "secu-ngfw-intermediaire"),
    ("secu-segmentation-intermediaire", "Segmentation réseau", "secu-ids-intermediaire"),
    ("secu-linux-intermediaire", "Sécurité des systèmes Linux", "secu-segmentation-intermediaire"),
    ("secu-ad-intermediaire", "Sécurité Active Directory", "secu-linux-intermediaire"),
    ("secu-siem-intermediaire", "Introduction aux SIEM", "secu-ad-intermediaire"),
    ("secu-services-intermediaire", "Sécurité des services réseau", "secu-siem-intermediaire"),
    ("secu-web-intermediaire", "Sécurité Web de base", "secu-services-intermediaire"),
]


class CyberIntermediateCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.nodes = json.loads((CONTENT / "nodes.json").read_text(encoding="utf-8"))
        cls.node_by_id = {node["id"]: node for node in cls.nodes}

    def test_all_courses_have_three_intro_paragraphs_and_two_qcms(self) -> None:
        for node_id, _title, _prereq in TRACK:
            lesson_path = CONTENT / "lessons" / f"{node_id}.md"
            quiz_path = CONTENT / "quiz" / f"{node_id}.json"
            self.assertTrue(lesson_path.is_file(), f"Cours manquant : {lesson_path.name}")
            self.assertTrue(quiz_path.is_file(), f"Quiz manquant : {quiz_path.name}")
            self.assertFalse(lesson_path.read_bytes().startswith(bytes((239, 187, 191))))
            raw_quiz = quiz_path.read_bytes()
            self.assertFalse(raw_quiz.startswith(bytes((239, 187, 191))), f"BOM détecté : {quiz_path.name}")
            quiz = json.loads(raw_quiz.decode("utf-8"))
            self.assertEqual(quiz.get("node_id"), node_id)
            self.assertEqual(len(quiz.get("questions", [])), 2)
            for question in quiz["questions"]:
                self.assertEqual(question.get("type"), "qcm")
                self.assertEqual(len(question.get("choices", [])), 4)
                self.assertIsInstance(question.get("answer"), int)
                self.assertGreaterEqual(question["answer"], 0)
                self.assertLess(question["answer"], 4)
                self.assertTrue(question.get("explanation", "").strip())
            lesson = lesson_path.read_text(encoding="utf-8")
            self.assertTrue(lesson.startswith("# "))
            introduction = lesson.split("## Introduction", 1)[1].split("## Concepts clés", 1)[0]
            paragraphs = [part.strip() for part in introduction.strip().split("\n\n") if part.strip()]
            self.assertEqual(len(paragraphs), 3, f"Introduction incorrecte : {lesson_path.name}")

    def test_exact_pre_requisite_chain_and_unique_ids(self) -> None:
        self.assertEqual(len(self.node_by_id), len(self.nodes), "Identifiants de nœuds dupliqués.")
        for node_id, title, prereq in TRACK:
            node = self.node_by_id[node_id]
            self.assertEqual(node["module"], "Cybersécurité")
            self.assertEqual(node["title"], f"{title} - Intermédiaire")
            self.assertEqual(node["prereqs"], [prereq])

    def test_acl_lab_metadata_is_visible_to_the_labs_catalog(self) -> None:
        expected = {
            "kind": "security",
            "prompt": "Configurez une ACL étendue sur R1 pour bloquer le trafic du PC Attaquant vers le Serveur.",
        }
        self.assertEqual(self.node_by_id["secu-acl-intermediaire"]["lab"], expected)
        self.assertEqual(_configured_node_labs()["secu-acl-intermediaire"], expected)


if __name__ == "__main__":
    unittest.main()
