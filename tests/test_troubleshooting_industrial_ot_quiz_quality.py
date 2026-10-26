from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "content" / "quiz"
ROUTING_QUIZZES = (
    "troubleshooting-debutant",
    "troubleshooting-intermediaire",
    "troubleshooting-expert",
)
OT_SCADA_QUIZZES = ("ot-scada-debutant", "ot-scada-intermediaire", "ot-scada-expert")
OT_PROTOCOL_QUIZZES = (
    "ot-profinet-modbus-debutant",
    "ot-profinet-modbus-intermediaire",
    "ot-profinet-modbus-expert",
)
ALL_QUIZZES = ROUTING_QUIZZES + OT_SCADA_QUIZZES + OT_PROTOCOL_QUIZZES
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|"
    r"avez-vous bien lu ce cours|avez-vous lu le cours|^\s*(?:réponse|answer)\s+[a-d]\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Clés de correction choisies lors de la revue des cours et des quiz.
EXPECTED_ANSWER_KEYS = (
    ("troubleshooting-debutant", 0, 2, "« Depuis 10 h 15, un seul poste atteint la passerelle en IP, mais la résolution du nom interne échoue »"),
    ("troubleshooting-debutant", 3, 3, "Interroger explicitement le résolveur avec `nslookup nom.exemple` ou `Resolve-DnsName nom.exemple`"),
    ("troubleshooting-intermediaire", 2, 0, "La MTU/PMTUD ou une incohérence de MSS, en comparant des tailles contrôlées et les messages ICMP pertinents"),
    ("troubleshooting-intermediaire", 4, 1, "Le plan de contrôle calcule/maintient les états et routes, tandis que le plan de données transfère réellement les paquets selon les tables et politiques installées"),
    ("troubleshooting-expert", 0, 1, "Elle prédit des observations vérifiables et un résultat qui pourrait la réfuter"),
    ("troubleshooting-expert", 5, 1, "La capture peut refléter différemment les segments, sommes de contrôle ou tailles de paquets que ceux effectivement vus sur le fil ; il faut connaître le point et les effets de l’offload"),
    ("ot-scada-debutant", 0, 1, "Exécuter une logique de commande et interagir avec des entrées/sorties du procédé"),
    ("ot-scada-intermediaire", 0, 2, "Ils structurent les actifs selon leurs exigences et contrôlent les communications autorisées entre les zones"),
    ("ot-scada-intermediaire", 2, 3, "Le protocole traditionnel ne fournit pas, à lui seul, une authentification forte et une protection cryptographique du canal"),
    ("ot-scada-expert", 0, 2, "En prenant en compte l’accès plausible, les conséquences sur le procédé et les personnes, la sûreté, l’environnement, la production et les contrôles existants"),
    ("ot-scada-expert", 2, 3, "Préserver les journaux et captures disponibles, réduire le risque selon le plan d’intervention approuvé et coordonner l’analyse avec les responsables du procédé"),
    ("ot-profinet-modbus-debutant", 0, 1, "TCP 502"),
    ("ot-profinet-modbus-intermediaire", 0, 3, "Fonction 03"),
    ("ot-profinet-modbus-intermediaire", 6, 1, "Interpréter le code d’exception, la fonction, la famille d’objet, l’offset et la quantité demandée selon la documentation de l’équipement"),
    ("ot-profinet-modbus-expert", 2, 1, "C’est une variante distincte intégrant TLS et des certificats X.509 pour la protection cryptographique, avec compatibilité à vérifier et port spécifié 802"),
    ("ot-profinet-modbus-expert", 5, 2, "L’identité et la configuration du périphérique, les relations IO, les états de cycle/watchdog, diagnostics et indicateurs de validité"),
)


class TroubleshootingIndustrialOTQuizQualityTests(unittest.TestCase):
    def test_all_quizzes_are_complete_and_not_placeholders(self) -> None:
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
