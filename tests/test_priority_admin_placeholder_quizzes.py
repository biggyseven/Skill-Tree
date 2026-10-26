from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
PRIORITY_QUIZZES = (
    "process-debutant", "process-intermediaire", "process-expert",
    "packages-debutant", "packages-intermediaire", "packages-expert",
    "windows-server-debutant", "windows-server-intermediaire", "windows-server-expert",
    "storage-debutant", "storage-intermediaire", "storage-expert",
)
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|réponse [a-d]",
    re.IGNORECASE,
)

# Clés ancrées sur des options exactes : elles détectent une dérive accidentelle
# de l'index de réponse sur des notions de diagnostic et d'administration.
EXPECTED_ANSWER_KEYS = (
    ("process-debutant", 0, 0, "`ps -eo pid,comm`"),
    ("process-intermediaire", 1, 1, "Que le PID existe ou est visible et que l’appelant dispose des permissions nécessaires, au moment du contrôle"),
    ("process-expert", 4, 2, "À limiter le nombre de tâches/processus dans le cgroup et sa hiérarchie concernée"),
    ("packages-debutant", 0, 1, "Il actualise les index locaux des dépôts configurés"),
    ("packages-intermediaire", 0, 3, "`apt-cache policy nginx`"),
    ("packages-expert", 0, 2, "`dpkg --audit`"),
    ("windows-server-debutant", 2, 1, "`Get-Service`"),
    ("windows-server-intermediaire", 0, 2, "Local, site, domaine, puis unités d’organisation de la plus haute à la plus basse"),
    ("windows-server-expert", 0, 1, "Il contribue au vote/quorum afin de réduire le risque de décisions concurrentes lors d’une partition du cluster"),
    ("storage-debutant", 3, 2, "Le propriétaire a lecture/écriture/exécution, le groupe lecture/exécution, les autres aucun droit"),
    ("storage-intermediaire", 1, 2, "Les données sont écrites en miroir sur les deux membres, ce qui peut tolérer la panne de l’un des deux selon l’état du miroir"),
    ("storage-expert", 1, 0, "`iostat -xz 1`"),
)


class PriorityAdminPlaceholderQuizTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.quiz_paths = {path.stem: path for path in QUIZ_DIR.glob("*.json")}

    def test_priority_quizzes_are_complete_and_contextual(self) -> None:
        for quiz_id in PRIORITY_QUIZZES:
            with self.subTest(quiz=quiz_id):
                self.assertIn(quiz_id, self.quiz_paths, f"Quiz manquant : {quiz_id}")
                path = self.quiz_paths[quiz_id]
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data.get("node_id"), quiz_id)
                self.assertEqual(data.get("scope"), "quiz")
                questions = data.get("questions")
                self.assertIsInstance(questions, list)
                self.assertEqual(len(questions), 8, f"8 questions attendues : {quiz_id}")

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
                        normalized_choices = {str(choice).strip().casefold() for choice in choices}
                        self.assertEqual(len(normalized_choices), 4, f"Choix dupliqués : {quiz_id} #{number}")
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
                    f"Positions de réponses trop prévisibles : {quiz_id}",
                )

    def test_reviewed_answer_keys_point_to_the_exact_expected_choices(self) -> None:
        for quiz_id, question_index, expected_index, expected_choice in EXPECTED_ANSWER_KEYS:
            with self.subTest(quiz=quiz_id, question=question_index + 1):
                data = json.loads(self.quiz_paths[quiz_id].read_text(encoding="utf-8"))
                question = data["questions"][question_index]
                self.assertEqual(question["answer"], expected_index)
                self.assertEqual(question["choices"][question["answer"]], expected_choice)


if __name__ == "__main__":
    unittest.main()
