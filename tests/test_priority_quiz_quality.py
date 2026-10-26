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
    "ipsec": ("ipsec-debutant", "ipsec-intermediaire", "ipsec-expert"),
    "ipv6": ("ipv6-debutant", "ipv6-intermediaire", "ipv6-expert"),
    "isis": ("isis-debutant", "isis-intermediaire", "isis-expert"),
    "itil-rca": ("itil-rca-debutant", "itil-rca-intermediaire", "itil-rca-expert"),
    "k8s": ("k8s-debutant", "k8s-intermediaire", "k8s-expert"),
}
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


if __name__ == "__main__":
    unittest.main()
