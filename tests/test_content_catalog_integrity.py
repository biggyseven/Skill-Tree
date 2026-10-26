from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
LEVELS = ("debutant", "intermediaire", "expert")


class PedagogicalCatalogIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.nodes = json.loads((CONTENT / "nodes.json").read_text(encoding="utf-8"))
        cls.node_by_id = {node["id"]: node for node in cls.nodes}
        cls.lesson_paths = {path.stem: path for path in (CONTENT / "lessons").glob("*.md")}
        cls.quiz_paths = {path.stem: path for path in (CONTENT / "quiz").glob("*.json")}

    def test_node_ids_are_unique_and_prerequisites_resolve(self) -> None:
        ids = [node["id"] for node in self.nodes]
        self.assertEqual(len(ids), len(set(ids)), "Des identifiants de nœuds sont dupliqués.")
        known = set(ids)
        missing = {
            (node["id"], prereq)
            for node in self.nodes
            for prereq in node.get("prereqs", [])
            if prereq not in known
        }
        self.assertEqual(missing, set(), f"Prérequis inconnus : {sorted(missing)}")

    def test_each_lesson_has_a_node_and_matching_quiz(self) -> None:
        lesson_ids = set(self.lesson_paths)
        quiz_ids = set(self.quiz_paths)
        node_ids = set(self.node_by_id)
        self.assertEqual(lesson_ids - node_ids, set(), "Cours Markdown sans nœud de parcours.")
        self.assertEqual(lesson_ids - quiz_ids, set(), "Cours sans fichier de quiz correspondant.")
        self.assertEqual(quiz_ids - node_ids, set(), "Quiz sans nœud de parcours.")
        for quiz_id, path in self.quiz_paths.items():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data.get("node_id"), quiz_id, f"{path.name}: node_id incohérent.")
            self.assertIsInstance(data.get("questions"), list, f"{path.name}: questions absentes.")
            self.assertGreater(len(data["questions"]), 0, f"{path.name}: aucune question.")

    def test_tracks_that_have_three_levels_are_cumulative(self) -> None:
        groups: dict[str, set[str]] = {}
        for lesson_id in self.lesson_paths:
            match = re.match(r"^(.*)-(debutant|intermediaire|expert)$", lesson_id)
            if match:
                groups.setdefault(match.group(1), set()).add(match.group(2))
        problems = []
        for topic, present in groups.items():
            if set(LEVELS) != present:
                continue
            for level, expected in (("intermediaire", "debutant"), ("expert", "intermediaire")):
                node_id = f"{topic}-{level}"
                expected_id = f"{topic}-{expected}"
                if expected_id not in self.node_by_id[node_id].get("prereqs", []):
                    problems.append((node_id, expected_id))
        self.assertEqual(problems, [], f"Chaînes de niveaux non cumulatives : {problems}")

    def test_priority_devops_tracks_have_all_three_levels(self) -> None:
        required_topics = ("ansible-devops", "devsecops", "iac", "mesh", "observability")
        for topic in required_topics:
            expected = {f"{topic}-{level}" for level in LEVELS}
            self.assertTrue(expected <= set(self.lesson_paths), f"Parcours incomplet: {topic}")
            self.assertTrue(expected <= set(self.quiz_paths), f"Quiz manquants: {topic}")
            self.assertTrue(expected <= set(self.node_by_id), f"Nœuds manquants: {topic}")

    def test_cicd_expert_is_a_real_standalone_course(self) -> None:
        path = self.lesson_paths["cicd-expert"]
        content = path.read_text(encoding="utf-8").strip()
        self.assertGreaterEqual(len(content), 8000, "Le cours expert CI/CD est trop court.")
        self.assertTrue(content.startswith("# GitOps et Argo CD — Expert"))
        self.assertNotRegex(content[:500], r"(?im)^---\s*$|^node_id:|^filename:|^language:")
        self.assertNotIn("en cours de rédaction", content.lower())
        for heading in ("Objectifs d’apprentissage", "Prérequis", "TP guidé", "Exercices corrigés", "Défi final corrigé"):
            self.assertIn(heading, content)

    def test_cicd_expert_quiz_is_not_a_placeholder(self) -> None:
        data = json.loads(self.quiz_paths["cicd-expert"].read_text(encoding="utf-8"))
        questions = data["questions"]
        self.assertGreaterEqual(len(questions), 5)
        prompts = [question["prompt"].strip().lower() for question in questions]
        self.assertEqual(len(prompts), len(set(prompts)), "Questions dupliquées.")
        for index, question in enumerate(questions, 1):
            self.assertNotRegex(question["prompt"].lower(), r"question temporaire|avez-vous lu le cours|question placeholder")
            self.assertTrue(question.get("explanation", "").strip(), f"Question {index} sans explication.")
            self.assertGreaterEqual(len(question.get("choices", [])), 4)
            self.assertIsInstance(question.get("answer"), int)
            self.assertGreaterEqual(question["answer"], 0)
            self.assertLess(question["answer"], len(question["choices"]))


if __name__ == "__main__":
    unittest.main()
