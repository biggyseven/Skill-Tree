from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
HA_QUIZZES = ("ha-debutant", "ha-intermediaire", "ha-expert")
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|réponse [a-d]",
    re.IGNORECASE,
)

# Clés de correction choisies lors de la revue technique du lot HA.
EXPECTED_ANSWER_KEYS = (
    ("ha-debutant", 0, 0, "Haute disponibilité (High Availability) : réduire l’interruption du service lors de certaines pannes"),
    ("ha-debutant", 3, 3, "Pour utiliser une adresse logique stable dont le routeur responsable peut changer lors d’une bascule"),
    ("ha-debutant", 6, 3, "LACP agrège des liens physiques compatibles ; STP garde son rôle de prévention des boucles de couche 2"),
    ("ha-intermediaire", 0, 2, "VRRP emploie Active Router et Backup Router ; HSRP utilise les états Active et Standby dans sa terminologie Cisco"),
    ("ha-intermediaire", 1, 1, "Elle n’est généralement pas activée par défaut ; un routeur de priorité supérieure ne reprend donc pas forcément le rôle Active sans configuration de préemption"),
    ("ha-intermediaire", 3, 0, "La négociation ne démarre pas, car aucun côté n’initie l’envoi des paquets LACP"),
    ("ha-expert", 0, 2, "BFD détecte certaines défaillances du chemin de forwarding ; les temps dépendent des intervalles, de la négociation et des capacités de la plateforme"),
    ("ha-expert", 1, 1, "Deux nœuds ou groupes séparés pensent chacun être autorisés à assurer la même fonction active"),
    ("ha-expert", 3, 0, "MLAG/vPC fournit un modèle de multi-attachement entre deux switches compatibles, mais ne signifie pas que STP peut être supprimé de toute la topologie"),
    ("ha-expert", 5, 3, "Mesurer depuis un client la perte de paquets, le délai de convergence et le succès d’une transaction représentative, tout en corrélant les états réseau"),
)


class HighAvailabilityQuizQualityTests(unittest.TestCase):
    def test_ha_quizzes_are_complete_and_answer_positions_are_balanced(self) -> None:
        for quiz_id in HA_QUIZZES:
            with self.subTest(quiz=quiz_id):
                path = QUIZ_DIR / f"{quiz_id}.json"
                self.assertTrue(path.is_file(), f"Quiz manquant : {path.name}")
                data = json.loads(path.read_text(encoding="utf-8"))
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
                        self.assertTrue(explanation, "Explication manquante")
                        self.assertNotRegex(
                            prompt + " " + explanation + " " + " ".join(map(str, choices)),
                            PLACEHOLDER_RE,
                        )
                        prompts.append(prompt.casefold())
                        answer_positions.add(answer)

                self.assertEqual(len(prompts), len(set(prompts)), "Énoncés dupliqués")
                self.assertEqual(
                    answer_positions,
                    {0, 1, 2, 3},
                    "Les quatre positions de réponse doivent être utilisées",
                )

    def test_reviewed_ha_answer_keys_point_to_expected_choices(self) -> None:
        for quiz_id, question_index, expected_index, expected_choice in EXPECTED_ANSWER_KEYS:
            with self.subTest(quiz=quiz_id, question=question_index + 1):
                data = json.loads((QUIZ_DIR / f"{quiz_id}.json").read_text(encoding="utf-8"))
                question = data["questions"][question_index]
                self.assertEqual(question["answer"], expected_index)
                self.assertEqual(question["choices"][question["answer"]], expected_choice)


if __name__ == "__main__":
    unittest.main()
