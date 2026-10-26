from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
VOICE_SIP_QUIZZES = (
    "voice-sip-debutant",
    "voice-sip-intermediaire",
    "voice-sip-expert",
)
VOICE_QOS_QUIZZES = (
    "voice-qos-debutant",
    "voice-qos-intermediaire",
    "voice-qos-expert",
)
ALL_QUIZZES = VOICE_SIP_QUIZZES + VOICE_QOS_QUIZZES
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|^\s*(?:réponse|answer)\s+[a-d]\s*$",
    re.IGNORECASE | re.MULTILINE,
)

EXPECTED_ANSWER_KEYS = (
    ("voice-sip-debutant", 0, 2, "À établir, modifier et terminer la session de communication"),
    ("voice-sip-debutant", 1, 0, "Décrire les paramètres média proposés ou acceptés, notamment les codecs, adresses et ports de média"),
    ("voice-sip-intermediaire", 1, 2, "Les paramètres de session proposés, souvent média/SDP, ne sont pas acceptés par le destinataire"),
    ("voice-sip-intermediaire", 5, 2, "Les extrémités n’utilisent pas une méthode DTMF compatible, par exemple événements RTP telephone-event ou tonalités dans le média"),
    ("voice-sip-expert", 1, 2, "À modifier les paramètres d’une session existante, par exemple le média, sans nécessairement créer un nouvel appel"),
    ("voice-sip-expert", 6, 1, "Limiter les destinations et les sources autorisées, appliquer l’authentification et le contrôle d’accès, protéger la signalisation et le média selon les capacités, et surveiller les anomalies"),
    ("voice-qos-debutant", 0, 2, "DSCP 46"),
    ("voice-qos-debutant", 5, 1, "Environ 80 kbit/s par flux"),
    ("voice-qos-intermediaire", 0, 2, "Les classer en EF et leur appliquer une file faible latence dimensionnée et contrôlée, selon la conception"),
    ("voice-qos-intermediaire", 1, 1, "CBWFQ répartit des ressources entre classes pondérées ; LLQ ajoute généralement une file à priorité stricte pour certains flux temps réel"),
    ("voice-qos-expert", 1, 1, "Le DSCP externe peut être copié, fixé ou mappé différemment du DSCP interne selon la configuration et le domaine traversé"),
    ("voice-qos-expert", 2, 3, "Estimer le débit réel par appel et le nombre maximal admis, y compris les surcharges, puis plafonner la classe et tester la capacité restante"),
)


class VoiceSipQosQuizQualityTests(unittest.TestCase):
    def test_voice_quizzes_are_complete_and_non_placeholder(self) -> None:
        for quiz_id in ALL_QUIZZES:
            with self.subTest(quiz=quiz_id):
                path = QUIZ_DIR / f"{quiz_id}.json"
                self.assertTrue(path.is_file(), f"Quiz manquant : {path.name}")
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data.get("node_id"), quiz_id)
                self.assertEqual(data.get("scope"), "quiz")
                questions = data.get("questions")
                self.assertIsInstance(questions, list)
                self.assertEqual(len(questions), 8, f"Huit QCM attendus : {quiz_id}")

                prompts = []
                answer_positions = set()
                for number, question in enumerate(questions, start=1):
                    with self.subTest(quiz=quiz_id, question=number):
                        prompt = str(question.get("prompt", "")).strip()
                        choices = question.get("choices")
                        explanation = str(question.get("explanation", "")).strip()
                        self.assertTrue(prompt, "Énoncé vide")
                        self.assertIsInstance(choices, list)
                        self.assertEqual(len(choices), 4, "Quatre choix attendus")
                        self.assertEqual(
                            len({str(choice).strip().casefold() for choice in choices}),
                            4,
                            "Les quatre choix doivent être distincts",
                        )
                        answer = question.get("answer")
                        self.assertIsInstance(answer, int)
                        self.assertNotIsInstance(answer, bool)
                        self.assertGreaterEqual(answer, 0)
                        self.assertLess(answer, len(choices))
                        self.assertTrue(explanation, "Explication absente")
                        self.assertNotRegex(prompt, PLACEHOLDER_RE)
                        for choice in choices:
                            self.assertNotRegex(str(choice), PLACEHOLDER_RE)
                        prompts.append(prompt.casefold())
                        answer_positions.add(answer)

                self.assertEqual(len(prompts), len(set(prompts)), "Énoncés dupliqués")
                self.assertEqual(
                    answer_positions,
                    {0, 1, 2, 3},
                    "Les quatre positions de réponse doivent être utilisées",
                )

    def test_reviewed_answer_keys_point_to_exact_expected_choices(self) -> None:
        for quiz_id, question_index, expected_index, expected_choice in EXPECTED_ANSWER_KEYS:
            with self.subTest(quiz=quiz_id, question=question_index + 1):
                data = json.loads((QUIZ_DIR / f"{quiz_id}.json").read_text(encoding="utf-8"))
                question = data["questions"][question_index]
                self.assertEqual(question["answer"], expected_index)
                self.assertEqual(question["choices"][question["answer"]], expected_choice)


if __name__ == "__main__":
    unittest.main()
