from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
ZERO_TRUST_QUIZZES = (
    "zero-trust-debutant",
    "zero-trust-intermediaire",
    "zero-trust-expert",
)
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|réponse [a-d]",
    re.IGNORECASE,
)

EXPECTED_ANSWER_KEYS = (
    ("zero-trust-debutant", 0, 1, "Vérifier explicitement les demandes d’accès plutôt que de considérer le réseau interne comme automatiquement fiable"),
    ("zero-trust-debutant", 2, 0, "Appliquer la décision d’accès sur le chemin entre le sujet et la ressource, notamment en permettant, surveillant ou terminant la connexion"),
    ("zero-trust-debutant", 4, 1, "Un VPN peut fournir un chemin d’accès chiffré, mais l’autorisation Zero Trust doit encore contrôler les ressources et les actions accessibles"),
    ("zero-trust-intermediaire", 1, 0, "Le PDP évalue la politique et les informations de contexte ; le PA exécute la décision en pilotant notamment le PEP qui établit ou termine le chemin d’accès"),
    ("zero-trust-intermediaire", 3, 1, "Une authentification cryptographique liée au site et au protocole, par exemple une clé de sécurité FIDO2/WebAuthn lorsque le déploiement le prend en charge"),
    ("zero-trust-intermediaire", 4, 3, "La limiter à un besoin et un périmètre, définir un propriétaire et une expiration, puis la surveiller et la réexaminer"),
    ("zero-trust-expert", 0, 2, "Fournir une identité cryptographique de charge de travail vérifiable, par exemple via des SVID à durée limitée, que d’autres contrôles peuvent utiliser"),
    ("zero-trust-expert", 2, 3, "Aucun chemin ne doit permettre d’atteindre la ressource en contournant les points d’application et les décisions de politique prévus"),
    ("zero-trust-expert", 5, 0, "Définir à l’avance une stratégie proportionnée au risque, avec les limites du cache éventuel, la durée, la journalisation et un test de dégradation ; il n’existe pas de réponse universelle"),
    ("zero-trust-expert", 7, 1, "Les mots de passe, secrets privés et jetons d’accès complets, sauf exigence exceptionnelle strictement contrôlée — généralement à exclure"),
)


class ZeroTrustQuizQualityTests(unittest.TestCase):
    def test_zero_trust_quizzes_are_complete_and_non_placeholder(self) -> None:
        for quiz_id in ZERO_TRUST_QUIZZES:
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
                            "Les choix doivent être distincts",
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
