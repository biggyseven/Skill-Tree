from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
QOS_QUIZZES = ("qos-debutant", "qos-intermediaire", "qos-expert")
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|réponse [a-d]",
    re.IGNORECASE,
)

EXPECTED_ANSWER_KEYS = (
    ("qos-debutant", 0, 1, "Différencier le traitement du trafic selon les besoins afin de mieux gérer la congestion"),
    ("qos-debutant", 1, 3, "Six bits DSCP et deux bits ECN"),
    ("qos-debutant", 2, 0, "46"),
    ("qos-debutant", 6, 0, "Le policing mesure la conformité et peut supprimer ou re-marquer le trafic non conforme ; le shaping met en tampon les paquets pour lisser le débit"),
    ("qos-intermediaire", 1, 0, "`class-map` identifie le trafic, `policy-map` définit les actions, puis `service-policy` attache la politique à un point d’application"),
    ("qos-intermediaire", 3, 3, "Un trafic prioritaire trop abondant peut affamer les autres classes ; la classe doit être limitée, contrôlée et dimensionnée"),
    ("qos-intermediaire", 5, 2, "Limiter ou lisser le débit agrégé à la sortie, pendant que la policy enfant arbitre entre les classes, selon le support de la plateforme"),
    ("qos-expert", 0, 2, "Le parent façonne généralement le trafic agrégé tandis que la policy enfant répartit le traitement entre les classes, selon la plateforme"),
    ("qos-expert", 3, 1, "L4S s’appuie sur des mécanismes de congestion tels qu’ECN et une architecture de queues compatibles ; le marquage DSCP seul ne l’active pas"),
    ("qos-expert", 6, 3, "Elle peut lisser des pics et des microbursts ; les percentiles, les séries temporelles et les compteurs de file révèlent parfois un p99 dégradé malgré une moyenne stable"),
)


class QosQuizQualityTests(unittest.TestCase):
    def test_qos_quizzes_are_complete_and_non_placeholder(self) -> None:
        for quiz_id in QOS_QUIZZES:
            with self.subTest(quiz=quiz_id):
                path = QUIZ_DIR / f"{quiz_id}.json"
                self.assertTrue(path.is_file(), f"Quiz absent : {path.name}")
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data.get("node_id"), quiz_id)
                self.assertEqual(data.get("scope"), "quiz")
                questions = data.get("questions")
                self.assertIsInstance(questions, list)
                self.assertEqual(len(questions), 8, f"Huit QCM attendus pour {quiz_id}")

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
                        self.assertNotRegex(
                            prompt + " " + explanation + " " + " ".join(map(str, choices)),
                            PLACEHOLDER_RE,
                            "Placeholder temporaire détecté",
                        )
                        prompts.append(prompt.casefold())
                        answer_positions.add(answer)

                self.assertEqual(len(prompts), len(set(prompts)), "Énoncés dupliqués")
                self.assertEqual(
                    answer_positions,
                    {0, 1, 2, 3},
                    "Les quatre positions de réponse doivent être représentées",
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
