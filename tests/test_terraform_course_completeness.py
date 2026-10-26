from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "content" / "lessons"
TERRAFORM_COURSES = (
    "terraform-debutant.md",
    "terraform-intermediaire.md",
    "terraform-expert.md",
)


class TerraformCourseCompletenessTests(unittest.TestCase):
    def test_each_terraform_course_has_a_context_box(self) -> None:
        for filename in TERRAFORM_COURSES:
            with self.subTest(course=filename):
                content = (LESSONS / filename).read_text(encoding="utf-8")
                self.assertRegex(
                    content,
                    r"(?im)^>\s*\*\*Mise en contexte\.\*\*",
                    f"Encadré de mise en contexte absent : {filename}",
                )

    def test_each_terraform_course_has_a_corrected_final_challenge(self) -> None:
        for filename in TERRAFORM_COURSES:
            with self.subTest(course=filename):
                content = (LESSONS / filename).read_text(encoding="utf-8")
                self.assertRegex(
                    content,
                    r"(?im)^#\s+\d+\.\s+Défi final corrigé\b",
                    f"Défi final corrigé absent : {filename}",
                )
                self.assertRegex(
                    content,
                    r"(?im)^##\s+Correction attendue\s*$",
                    f"Correction du défi final absente : {filename}",
                )

    def test_terraform_courses_do_not_use_horizontal_rule_separators(self) -> None:
        for filename in TERRAFORM_COURSES:
            with self.subTest(course=filename):
                content = (LESSONS / filename).read_text(encoding="utf-8")
                self.assertIsNone(
                    re.search(r"(?m)^\s*---\s*$", content),
                    f"Ligne de séparation horizontale inattendue : {filename}",
                )


if __name__ == "__main__":
    unittest.main()
