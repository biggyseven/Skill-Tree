from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
PRIORITY_QUIZZES = (
    "stp-debutant", "stp-intermediaire", "stp-expert",
    "ospf-debutant", "ospf-intermediaire", "ospf-expert",
    "bgp-debutant", "bgp-intermediaire", "bgp-expert",
    "eigrp-debutant", "eigrp-intermediaire", "eigrp-expert",
)
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|réponse [a-d]",
    re.IGNORECASE,
)

# Clés pédagogiques exactes vérifiées durant la revue du lot.
EXPECTED_ANSWER_KEYS = (
    ("stp-debutant", 1, 2, "Le switch dont le Bridge ID est le plus faible, en tenant compte de la priorité puis des éléments de départage comme l’adresse MAC"),
    ("stp-intermediaire", 1, 2, "Max Age de 20 s + deux étapes Forward Delay de 15 s, soit environ 50 s avec les valeurs par défaut usuelles"),
    ("stp-expert", 2, 0, "À empêcher qu’une BPDU supérieure reçue sur cette interface ne fasse élire un nouveau Root Bridge en passant le port dans un état root-inconsistent selon la plateforme"),
    ("ospf-debutant", 5, 2, "Le numéro de protocole IP 89"),
    ("ospf-intermediaire", 1, 0, "Le routeur dont l’interface a la priorité OSPF la plus élevée ; en cas d’égalité, le Router ID le plus élevé départage, et priorité 0 est inéligible"),
    ("ospf-expert", 0, 1, "Il représente une route externe annoncée à l’intérieur de la NSSA ; un ABR traducteur peut convertir un Type 7 éligible en Type 5 pour l’extérieur"),
    ("bgp-debutant", 3, 3, "eBGP relie des pairs dans des AS différents ; iBGP relie des pairs à l’intérieur du même AS"),
    ("bgp-intermediaire", 1, 2, "BGP effectue ou retente l’établissement d’une connexion TCP ; l’état seul ne prouve pas la cause du problème"),
    ("bgp-expert", 0, 2, "Weight"),
    ("eigrp-debutant", 1, 0, "La bande passante et le délai"),
    ("eigrp-intermediaire", 0, 2, "La Reported Distance (RD) du voisin doit être strictement inférieure à la Feasible Distance (FD) locale"),
    ("eigrp-expert", 1, 1, "Le routeur participe à une computation diffusante pour chercher un nouveau chemin sans boucle, généralement après la perte du Successor ou une information qui nécessite de recalculer"),
)


class ShortRoutingQuizQualityTests(unittest.TestCase):
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
                            f"Placeholder détecté : {quiz_id} #{number}",
                        )
                        self.assertEqual(question.get("type", "qcm"), "qcm")
                        self.assertIsInstance(choices, list)
                        self.assertEqual(len(choices), 4, f"Quatre choix attendus : {quiz_id} #{number}")
                        normalized = {str(choice).strip().casefold() for choice in choices}
                        self.assertEqual(len(normalized), 4, f"Choix répétés : {quiz_id} #{number}")
                        answer = question.get("answer")
                        self.assertIsInstance(answer, int)
                        self.assertNotIsInstance(answer, bool)
                        self.assertGreaterEqual(answer, 0)
                        self.assertLess(answer, len(choices))
                        self.assertTrue(explanation, f"Explication absente : {quiz_id} #{number}")
                        prompts.append(prompt.casefold())
                        answer_positions.add(answer)

                self.assertEqual(len(prompts), len(set(prompts)), f"Énoncés dupliqués : {quiz_id}")
                self.assertGreaterEqual(
                    len(answer_positions), 3,
                    f"Positions de réponse trop prévisibles : {quiz_id}",
                )

    def test_reviewed_answer_keys_point_to_exact_expected_choices(self) -> None:
        for quiz_id, question_index, expected_index, expected_choice in EXPECTED_ANSWER_KEYS:
            with self.subTest(quiz=quiz_id, question=question_index + 1):
                data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                question = data["questions"][question_index]
                self.assertEqual(question["answer"], expected_index)
                self.assertEqual(question["choices"][question["answer"]], expected_choice)


if __name__ == "__main__":
    unittest.main()
