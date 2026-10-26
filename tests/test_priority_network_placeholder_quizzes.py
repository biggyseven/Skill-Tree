from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
PRIORITY_QUIZZES = (
    "wifi-debutant", "wifi-intermediaire", "wifi-expert",
    "vtp-debutant", "vtp-intermediaire", "vtp-expert",
    "routing-debutant", "routing-intermediaire", "routing-expert",
)
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|réponse [a-d]",
    re.IGNORECASE,
)
GENERIC_BINARY_CHOICES = {"oui", "non", "peut-être", "je ne sais pas"}

# Assertions de régression sur des clés pédagogiques relues manuellement.
EXPECTED_ANSWER_KEYS = (
    ("wifi-debutant", 0, 0, "Le SSID est le nom logique du réseau ; le BSSID identifie généralement une cellule radio d’un point d’accès"),
    ("wifi-intermediaire", 1, 3, "Les stations consomment du temps de transmission ; les débits PHY, les retransmissions et la contention influencent la part de temps disponible pour chaque flux"),
    ("wifi-expert", 2, 2, "La liaison montante du client peut rester limitée par sa propre puissance, son antenne, le bruit ou les obstacles, ce qui crée une liaison asymétrique"),
    ("vtp-debutant", 4, 1, "Sa base VLAN ou son numéro de révision peuvent influencer la base diffusée, selon le protocole et la configuration"),
    ("vtp-intermediaire", 1, 2, "À autoriser l’administration des changements de base VLAN selon les règles VTPv3, plutôt que de laisser chaque équipement modifier librement cette base"),
    ("vtp-expert", 2, 0, "Parce qu’il renseigne sur l’état/version de la base dans le protocole, pas sur l’adéquation métier de chaque VLAN au plan validé"),
    ("routing-debutant", 0, 2, "La route `10.20.30.0/24`, car elle correspond au préfixe le plus spécifique"),
    ("routing-intermediaire", 0, 1, "La route OSPF /16 car la correspondance au préfixe le plus long est prioritaire pour cette destination"),
    ("routing-expert", 3, 3, "Maintenir des contextes de routage distincts, permettant notamment des espaces d’adressage séparés sur une même infrastructure"),
)


class PriorityNetworkPlaceholderQuizTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.quiz_paths = {path.stem: path for path in QUIZ_DIR.glob("*.json")}

    def test_priority_quizzes_are_complete_and_contextual(self) -> None:
        for quiz_id in PRIORITY_QUIZZES:
            with self.subTest(quiz=quiz_id):
                self.assertIn(quiz_id, self.quiz_paths, f"Quiz manquant : {quiz_id}")
                data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                self.assertEqual(data.get("node_id"), quiz_id)
                self.assertEqual(data.get("scope"), "quiz")
                questions = data.get("questions")
                self.assertIsInstance(questions, list)
                self.assertEqual(len(questions), 8, f"Huit questions attendues : {quiz_id}")

                prompts = []
                answer_positions = set()
                for number, question in enumerate(questions, 1):
                    with self.subTest(quiz=quiz_id, question=number):
                        prompt = str(question.get("prompt", "")).strip()
                        choices = question.get("choices")
                        explanation = str(question.get("explanation", "")).strip()
                        self.assertTrue(prompt, f"Énoncé vide : {quiz_id} #{number}")
                        self.assertNotRegex(
                            prompt + " " + explanation + " " + " ".join(map(str, choices or [])),
                            PLACEHOLDER_RE,
                            f"Placeholder : {quiz_id} #{number}",
                        )
                        self.assertEqual(question.get("type", "qcm"), "qcm")
                        self.assertIsInstance(choices, list)
                        self.assertEqual(len(choices), 4, f"Quatre choix attendus : {quiz_id} #{number}")
                        normalized = {str(choice).strip().casefold() for choice in choices}
                        self.assertEqual(len(normalized), 4, f"Choix dupliqués : {quiz_id} #{number}")
                        self.assertNotEqual(normalized, GENERIC_BINARY_CHOICES,
                                            f"Choix génériques : {quiz_id} #{number}")
                        answer = question.get("answer")
                        self.assertIsInstance(answer, int)
                        self.assertNotIsInstance(answer, bool)
                        self.assertGreaterEqual(answer, 0)
                        self.assertLess(answer, len(choices))
                        self.assertTrue(explanation, f"Explication absente : {quiz_id} #{number}")
                        prompts.append(prompt.casefold())
                        answer_positions.add(answer)

                self.assertEqual(len(prompts), len(set(prompts)), f"Énoncés dupliqués : {quiz_id}")
                self.assertGreaterEqual(len(answer_positions), 3,
                                        f"Positions de réponse trop prévisibles : {quiz_id}")

    def test_reviewed_answer_keys_point_to_exact_expected_choices(self) -> None:
        for quiz_id, question_index, expected_index, expected_choice in EXPECTED_ANSWER_KEYS:
            with self.subTest(quiz=quiz_id, question=question_index + 1):
                data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                question = data["questions"][question_index]
                self.assertEqual(question["answer"], expected_index)
                self.assertEqual(question["choices"][question["answer"]], expected_choice)


if __name__ == "__main__":
    unittest.main()
