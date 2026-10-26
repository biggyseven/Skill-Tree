from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PRIORITY_TRACKS = {
    "db": ("db-debutant", "db-intermediaire", "db-expert"),
    "dhcp-dns": ("dhcp-dns-debutant", "dhcp-dns-intermediaire", "dhcp-dns-expert"),
    "equipment": ("equipment-debutant", "equipment-intermediaire", "equipment-expert"),
    "ddos-mitigation": ("ddos-mitigation-debutant", "ddos-mitigation-intermediaire", "ddos-mitigation-expert"),
    "docker": ("docker-debutant", "docker-intermediaire", "docker-expert"),
    "ethernet": ("ethernet-debutant", "ethernet-intermediaire", "ethernet-expert"),
    "etherchannel": ("etherchannel-debutant", "etherchannel-intermediaire", "etherchannel-expert"),
    "firewall": ("firewall-debutant", "firewall-intermediaire", "firewall-expert"),
    "devsecops": ("devsecops-debutant", "devsecops-intermediaire", "devsecops-expert"),
    "git": ("git-debutant", "git-intermediaire", "git-expert"),
    "ha-sys": ("ha-sys-debutant", "ha-sys-intermediaire", "ha-sys-expert"),
    "ids-ips": ("ids-ips-debutant", "ids-ips-intermediaire", "ids-ips-expert"),
    "intro-reseau": ("intro-reseau-debutant", "intro-reseau-intermediaire", "intro-reseau-expert"),
    "iac": ("iac-debutant", "iac-intermediaire", "iac-expert"),
    "terraform": ("terraform-debutant", "terraform-intermediaire", "terraform-expert"),
    "ipsec": ("ipsec-debutant", "ipsec-intermediaire", "ipsec-expert"),
    "ipv6": ("ipv6-debutant", "ipv6-intermediaire", "ipv6-expert"),
    "isis": ("isis-debutant", "isis-intermediaire", "isis-expert"),
    "itil-rca": ("itil-rca-debutant", "itil-rca-intermediaire", "itil-rca-expert"),
    "k8s": ("k8s-debutant", "k8s-intermediaire", "k8s-expert"),
    "linux": ("linux-debutant", "linux-intermediaire", "linux-expert"),
    "materiel-reseau": ("materiel-reseau-debutant", "materiel-reseau-intermediaire", "materiel-reseau-expert"),
    "mesh": ("mesh-debutant", "mesh-intermediaire", "mesh-expert"),
    "monitoring": ("monitoring-debutant", "monitoring-intermediaire", "monitoring-expert"),
    "mpls": ("mpls-debutant", "mpls-intermediaire", "mpls-expert"),
    "mtu-pmtud": ("mtu-pmtud-debutant", "mtu-pmtud-intermediaire", "mtu-pmtud-expert"),
    "multicast": ("multicast-debutant", "multicast-intermediaire", "multicast-expert"),
    "napalm": ("napalm-debutant", "napalm-intermediaire", "napalm-expert"),
    "netconf-yang": ("netconf-yang-debutant", "netconf-yang-intermediaire", "netconf-yang-expert"),
    "netflow": ("netflow-debutant", "netflow-intermediaire", "netflow-expert"),
    "netmiko": ("netmiko-debutant", "netmiko-intermediaire", "netmiko-expert"),
    "ntp-syslog": ("ntp-syslog-debutant", "ntp-syslog-intermediaire", "ntp-syslog-expert"),
    "scripting": ("scripting-debutant", "scripting-intermediaire", "scripting-expert"),
    "users": ("users-debutant", "users-intermediaire", "users-expert"),
    "virt": ("virt-debutant", "virt-intermediaire", "virt-expert"),
    "web-server": ("web-server-debutant", "web-server-intermediaire", "web-server-expert"),
}
PRIORITY_STANDALONE_QUIZZES = (
    "incident-ospf",
    "lab_bridge",
    "lab_netns",
    "lab_troubleshoot_vlan",
    "lab_tshoot_dns",
    "lab_tshoot_mtu",
    "lab_tshoot_route",
)
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours",
    re.IGNORECASE,
)
GENERIC_ANSWER_LABELS = {"réponse a", "réponse b", "réponse c", "réponse d"}
GENERIC_BINARY_CHOICES = {"oui", "non", "peut-être", "je ne sais pas"}


class PriorityQuizQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.nodes = json.loads((CONTENT / "nodes.json").read_text(encoding="utf-8"))
        cls.node_by_id = {node["id"]: node for node in cls.nodes}
        cls.quiz_paths = {
            path.stem: path for path in (CONTENT / "quiz").glob("*.json")
        }

    def test_priority_tracks_have_real_level_specific_quizzes(self) -> None:
        for topic, levels in PRIORITY_TRACKS.items():
            with self.subTest(topic=topic):
                self.assertEqual(len(levels), 3)
                for index, quiz_id in enumerate(levels):
                    with self.subTest(quiz=quiz_id):
                        self.assertIn(quiz_id, self.node_by_id, f"Nœud absent : {quiz_id}")
                        self.assertIn(quiz_id, self.quiz_paths, f"Quiz absent : {quiz_id}")
                        data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                        self.assertEqual(data.get("node_id"), quiz_id)
                        self.assertEqual(data.get("scope"), "quiz")
                        questions = data.get("questions")
                        self.assertIsInstance(questions, list)
                        self.assertGreaterEqual(len(questions), 8, f"Quiz trop court : {quiz_id}")

                        prompts = []
                        answer_positions = set()
                        for number, question in enumerate(questions, 1):
                            with self.subTest(question=number):
                                prompt = str(question.get("prompt", "")).strip()
                                choices = question.get("choices")
                                explanation = str(question.get("explanation", "")).strip()
                                self.assertTrue(prompt, f"Question sans énoncé : {quiz_id} #{number}")
                                self.assertNotRegex(
                                    prompt + " " + explanation,
                                    PLACEHOLDER_RE,
                                    f"Placeholder : {quiz_id} #{number}",
                                )
                                self.assertIsInstance(choices, list)
                                self.assertEqual(len(choices), 4, f"Quatre choix attendus : {quiz_id} #{number}")
                                normalized_choices = {str(c).strip().casefold() for c in choices}
                                self.assertEqual(len(normalized_choices), 4,
                                                 f"Choix répétés : {quiz_id} #{number}")
                                self.assertFalse(
                                    normalized_choices & GENERIC_ANSWER_LABELS,
                                    f"Choix générique Réponse A/B/C/D : {quiz_id} #{number}",
                                )
                                self.assertNotEqual(
                                    normalized_choices, GENERIC_BINARY_CHOICES,
                                    f"Choix génériques Oui/Non/Peut-être/Je ne sais pas : {quiz_id} #{number}",
                                )
                                answer = question.get("answer")
                                self.assertIsInstance(answer, int)
                                self.assertNotIsInstance(answer, bool)
                                self.assertGreaterEqual(answer, 0)
                                self.assertLess(answer, len(choices))
                                self.assertTrue(explanation, f"Explication absente : {quiz_id} #{number}")
                                self.assertEqual(question.get("type", "qcm"), "qcm")
                                prompts.append(prompt.casefold())
                                answer_positions.add(answer)

                        self.assertEqual(len(prompts), len(set(prompts)), f"Énoncés dupliqués : {quiz_id}")
                        self.assertGreaterEqual(
                            len(answer_positions), 3,
                            f"Position des bonnes réponses trop prévisible : {quiz_id}",
                        )

    def test_intermediate_and_expert_levels_depend_on_previous_level(self) -> None:
        for topic, levels in PRIORITY_TRACKS.items():
            beginner, intermediate, expert = levels
            self.assertIn(beginner, self.node_by_id)
            self.assertIn(beginner, self.node_by_id[intermediate].get("prereqs", []),
                          f"{intermediate} doit dépendre de {beginner}")
            self.assertIn(intermediate, self.node_by_id[expert].get("prereqs", []),
                          f"{expert} doit dépendre de {intermediate}")


    def test_standalone_lab_quizzes_are_contextual_and_complete(self) -> None:
        for quiz_id in PRIORITY_STANDALONE_QUIZZES:
            with self.subTest(quiz=quiz_id):
                self.assertIn(quiz_id, self.node_by_id, f"Nœud absent : {quiz_id}")
                self.assertIn(quiz_id, self.quiz_paths, f"Quiz absent : {quiz_id}")
                node = self.node_by_id[quiz_id]
                self.assertIn(
                    "lab",
                    {req.get("kind") for req in node.get("requirements", [])},
                    f"Le nœud {quiz_id} n'est pas déclaré comme prérequis de lab",
                )
                data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                self.assertEqual(data.get("node_id"), quiz_id)
                self.assertEqual(data.get("scope"), "quiz")
                questions = data.get("questions")
                self.assertIsInstance(questions, list)
                self.assertGreaterEqual(len(questions), 8, f"Quiz trop court : {quiz_id}")

                prompts = []
                answer_positions = set()
                for number, question in enumerate(questions, 1):
                    with self.subTest(quiz=quiz_id, question=number):
                        prompt = str(question.get("prompt", "")).strip()
                        choices = question.get("choices")
                        explanation = str(question.get("explanation", "")).strip()
                        self.assertTrue(prompt, f"Question sans énoncé : {quiz_id} #{number}")
                        self.assertNotRegex(
                            prompt + " " + explanation,
                            PLACEHOLDER_RE,
                            f"Placeholder : {quiz_id} #{number}",
                        )
                        self.assertIsInstance(choices, list)
                        self.assertEqual(len(choices), 4, f"Quatre choix attendus : {quiz_id} #{number}")
                        normalized_choices = {str(choice).strip().casefold() for choice in choices}
                        self.assertEqual(len(normalized_choices), 4, f"Choix répétés : {quiz_id} #{number}")
                        self.assertFalse(
                            normalized_choices & GENERIC_ANSWER_LABELS,
                            f"Choix générique Réponse A/B/C/D : {quiz_id} #{number}",
                        )
                        self.assertNotEqual(
                            normalized_choices, GENERIC_BINARY_CHOICES,
                            f"Choix génériques Oui/Non/Peut-être/Je ne sais pas : {quiz_id} #{number}",
                        )
                        answer = question.get("answer")
                        self.assertIsInstance(answer, int)
                        self.assertNotIsInstance(answer, bool)
                        self.assertGreaterEqual(answer, 0)
                        self.assertLess(answer, len(choices))
                        self.assertTrue(explanation, f"Explication absente : {quiz_id} #{number}")
                        self.assertEqual(question.get("type", "qcm"), "qcm")
                        prompts.append(prompt.casefold())
                        answer_positions.add(answer)

                self.assertEqual(len(prompts), len(set(prompts)), f"Énoncés dupliqués : {quiz_id}")
                self.assertGreaterEqual(
                    len(answer_positions), 3,
                    f"Position des bonnes réponses trop prévisible : {quiz_id}",
                )


    def test_reviewed_correct_answers_point_to_expected_options(self) -> None:
        cases = (
            (
                "db-intermediaire",
                6,
                0,
                "Une sauvegarde de base exploitable et l’archivage continu des WAL nécessaires",
            ),
            (
                "db-intermediaire",
                7,
                3,
                "Accorder uniquement les droits requis, avec un rôle et des secrets propres à l’application",
            ),
            (
                "equipment-expert",
                1,
                1,
                "Mesurer/estimer les pertes de la liaison et vérifier la puissance reçue par rapport aux limites du transceiver, avec marge",
            ),
        )
        for quiz_id, question_index, expected_index, expected_choice in cases:
            with self.subTest(quiz=quiz_id, question=question_index + 1):
                data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                question = data["questions"][question_index]
                self.assertEqual(question["answer"], expected_index)
                self.assertEqual(
                    question["choices"][question["answer"]],
                    expected_choice,
                    f"La correction désignée doit être l’option correcte : {quiz_id} #{question_index + 1}",
                )


    def test_new_system_quiz_answer_keys_match_reviewed_options(self) -> None:
        cases = (
            ("users-debutant", 0, 1, "`/etc/passwd`"),
            ("users-intermediaire", 1, 0, "Le DN qui identifie une entrée dans l’arborescence de l’annuaire"),
            ("users-expert", 0, 2, "Des clés secrètes associées à un ou plusieurs principaux Kerberos du service"),
            ("scripting-debutant", 0, 0, "`#!/usr/bin/env bash`"),
            ("scripting-intermediaire", 5, 0, "Le relancer sans changement d’entrée ne provoque pas de modifications supplémentaires inutiles"),
            ("scripting-expert", 0, 2, "Ansible Core fournit l’automatisation en ligne de commande ; AWX ajoute notamment une interface, une API, des inventaires, des identifiants et la planification des jobs"),
            ("web-server-debutant", 1, 1, "`nginx -t`"),
            ("web-server-intermediaire", 2, 3, "Lorsque l’en-tête est posé/normalisé par un proxy de confiance et que la chaîne de proxies est interprétée selon une politique définie"),
            ("web-server-expert", 1, 1, "20 requêtes"),
            ("virt-debutant", 0, 0, "Un hyperviseur de type 1 fonctionne sur la plateforme physique sans nécessiter un système d’exploitation généraliste hôte de type bureau comme dans le modèle 2."),
            ("virt-intermediaire", 0, 1, "La compatibilité CPU/versions, la connectivité, l’accès aux disques ou leur migration et les contraintes de la plateforme"),
            ("virt-expert", 1, 0, "Keystone"),
        )
        for quiz_id, question_index, expected_index, expected_choice in cases:
            with self.subTest(quiz=quiz_id, question=question_index + 1):
                data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                question = data["questions"][question_index]
                self.assertEqual(question["answer"], expected_index)
                self.assertEqual(
                    question["choices"][question["answer"]],
                    expected_choice,
                    f"Clé de réponse incorrecte : {quiz_id} #{question_index + 1}",
                )

if __name__ == "__main__":
    unittest.main()
