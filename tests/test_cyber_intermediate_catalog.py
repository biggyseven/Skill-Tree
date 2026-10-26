from __future__ import annotations

import json
import unittest
from pathlib import Path

from app.api import _configured_node_labs

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
TRACK = [
    ("secu-cia-debutant", "La Triade CIA", None),
    ("secu-menaces-debutant", "Panorama des menaces", "secu-cia-debutant"),
    ("secu-crypto-debutant", "Cryptographie", "secu-menaces-debutant"),
    ("secu-hachage-debutant", "Hachage et signatures", "secu-crypto-debutant"),
    ("secu-auth-debutant", "Authentification et MFA", "secu-hachage-debutant"),
    ("secu-endpoint-debutant", "Sécurité des Endpoints", "secu-auth-debutant"),
    ("secu-wifi-debutant", "Sécurité Wi-Fi", "secu-endpoint-debutant"),
    ("secu-firewall-debutant", "Introduction aux pare-feu", "secu-wifi-debutant"),
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
    ("secu-zero-trust-expert", "Architecture Zero Trust", "secu-web-intermediaire"),
    ("secu-cloud-expert", "Sécurité du Cloud (AWS/Azure/GCP)", "secu-zero-trust-expert"),
    ("secu-k8s-expert", "Sécurité des conteneurs (Docker/K8s)", "secu-cloud-expert"),
    ("secu-devsecops-expert", "DevSecOps", "secu-k8s-expert"),
    ("secu-iam-expert", "Gestion des identités et des accès avancée", "secu-devsecops-expert"),
    ("secu-pentest-expert", "Pentest et Hacking Éthique", "secu-iam-expert"),
    ("secu-malware-expert", "Analyse de malwares", "secu-pentest-expert"),
    ("secu-forensique-expert", "Forensique réseau et système", "secu-malware-expert"),
    ("secu-dfir-expert", "Réponse à incident (DFIR)", "secu-forensique-expert"),
    ("secu-gouvernance-expert", "Gouvernance et Conformité", "secu-dfir-expert"),
    ("secu-routing-secu-expert", "Sécurité des protocoles de routage", "secu-gouvernance-expert"),
    ("secu-vuln-expert", "Gestion des vulnérabilités", "secu-routing-secu-expert"),
    ("secu-supply-chain-expert", "Sécurité de la supply chain", "secu-vuln-expert"),
    ("secu-ot-ics-expert", "Architecture de sécurité sur les réseaux OT/ICS", "secu-supply-chain-expert"),
    ("secu-redteam-expert", "Red Team vs Blue Team vs Purple Team", "secu-ot-ics-expert"),
]


class CyberCatalogScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.nodes = json.loads((CONTENT / "nodes.json").read_text(encoding="utf-8"))
        cls.node_by_id = {node["id"]: node for node in cls.nodes}

    def test_35_lessons_and_quizzes_are_present_without_bom(self) -> None:
        for node_id, title, _prereq in TRACK:
            lesson_path = CONTENT / "lessons" / f"{node_id}.md"
            quiz_path = CONTENT / "quiz" / f"{node_id}.json"
            self.assertTrue(lesson_path.is_file(), f"Markdown manquant : {lesson_path.name}")
            self.assertTrue(quiz_path.is_file(), f"Quiz manquant : {quiz_path.name}")
            lesson_bytes = lesson_path.read_bytes()
            quiz_bytes = quiz_path.read_bytes()
            bom = bytes((239, 187, 191))
            self.assertFalse(lesson_bytes.startswith(bom), f"BOM du cours {node_id}")
            self.assertFalse(quiz_bytes.startswith(bom), f"BOM du quiz {node_id}")
            lesson = lesson_bytes.decode("utf-8")
            quiz = json.loads(quiz_bytes.decode("utf-8"))
            self.assertEqual(quiz["node_id"], node_id)
            if node_id in {"secu-cia-debutant", "secu-menaces-debutant", "secu-crypto-debutant", "secu-hachage-debutant", "secu-auth-debutant", "secu-endpoint-debutant", "secu-wifi-debutant", "secu-firewall-debutant", "secu-acl-intermediaire", "secu-nat-intermediaire", "secu-vpn-intermediaire", "secu-switch-secu-intermediaire"}:
                self.assertTrue(
                    lesson.startswith(f"# {title}\n\n> **Mise en contexte**")
                    or lesson.startswith(f"# {title}\n\n> **Encadré de mise en contexte**")
                    or lesson.startswith(f"# {title}\n\n## Encadré de mise en contexte\n\n")
                )
                self.assertNotIn("[Contenu de 5000 mots à rédiger]", lesson)
                self.assertGreaterEqual(len(lesson.split()), 5000, f"Le cours {node_id} doit contenir au moins 5000 mots.")
                self.assertGreaterEqual(len(quiz["questions"]), 10)
                for question in quiz["questions"]:
                    self.assertEqual(question["type"], "qcm")
                    self.assertNotIn("placeholder", question["prompt"].lower())
                    self.assertEqual(len(question["choices"]), 4)
                    self.assertGreaterEqual(question["answer"], 0)
                    self.assertLess(question["answer"], len(question["choices"]))
                    self.assertTrue(question["explanation"].strip())
            else:
                self.assertEqual(lesson.splitlines(), [f"# {title}", "", "[Contenu de 5000 mots à rédiger]"])
                self.assertEqual(len(quiz["questions"]), 1)
                question = quiz["questions"][0]
                self.assertEqual(question["type"], "qcm")
                self.assertIn("placeholder", question["prompt"].lower())
                self.assertEqual(len(question["choices"]), 4)
                self.assertEqual(question["answer"], 0)

    def test_node_titles_modules_and_exact_prerequisites(self) -> None:
        self.assertEqual(len(self.node_by_id), len(self.nodes), "Des identifiants sont dupliqués.")
        for node_id, title, prereq in TRACK:
            node = self.node_by_id[node_id]
            self.assertEqual(node["title"], title)
            self.assertEqual(node["module"], "Cybersécurité")
            self.assertEqual(node["category"], "Cybersécurité")
            self.assertEqual(node["prereqs"], [prereq] if prereq else [])
        known = set(self.node_by_id)
        missing = [(node["id"], prereq) for node in self.nodes for prereq in node.get("prereqs", []) if prereq not in known]
        self.assertEqual(missing, [], f"Prérequis invalides : {missing}")

    def test_acl_lab_link_is_kept_in_the_catalog(self) -> None:
        expected = {
            "kind": "security",
            "prompt": "Configurez une ACL étendue sur R1 pour bloquer le trafic du PC Attaquant vers le Serveur.",
        }
        self.assertEqual(self.node_by_id["secu-acl-intermediaire"]["lab"], expected)
        self.assertEqual(_configured_node_labs()["secu-acl-intermediaire"], expected)
        self.assertTrue((ROOT / "labs_v2" / "secu-acl-intermediaire.json").is_file())

    def test_roadmap_contains_both_completed_levels(self) -> None:
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        cyber = html[html.index("{ id: 'cybersecurite'"):]
        for title in ("ACL Avancées", "NAT & Périmètre", "VPN & IPsec", "Sécurité Web"):
            self.assertIn(title, cyber)
        for title in ("Zero Trust", "Cloud Security", "K8s Security", "DevSecOps", "IAM Avancé", "Pentest", "Analyse Malwares", "Forensique", "DFIR", "Gouvernance", "Routing Secu", "Vulnérabilités", "Supply Chain", "OT/ICS", "Red Team"):
            self.assertIn(title, cyber)


if __name__ == "__main__":
    unittest.main()
