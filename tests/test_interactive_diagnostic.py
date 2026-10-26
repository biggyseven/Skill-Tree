"""Regression tests for the interactive troubleshooting diagnostic."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
NETWORK_DOWN = json.loads(
    (ROOT / "content" / "diagnostics" / "network_down.json").read_text(encoding="utf-8")
)


class InteractiveDiagnosticTests(unittest.TestCase):
    def test_network_down_decisions_are_scored_and_explained(self):
        self.assertEqual(NETWORK_DOWN["title"], "Poste sans accès au réseau")
        for step_id, step in NETWORK_DOWN["steps"].items():
            if step.get("choices"):
                with self.subTest(step=step_id):
                    self.assertTrue(step.get("competency"), "Chaque décision doit être rattachée à une compétence")
                    for choice in step["choices"]:
                        self.assertIsInstance(choice.get("good"), bool)
                        self.assertTrue(choice.get("feedback"))

        command_step = NETWORK_DOWN["steps"]["step-3"]
        self.assertTrue(command_step.get("competency"))
        self.assertTrue(command_step.get("command", {}).get("regex"))

    def test_diagnostic_supports_command_steps_competency_feedback_and_resume(self):
        self.assertIn("diagSubmitCommand()", DASHBOARD)
        self.assertIn("diagStep.command.prompt", DASHBOARD)
        self.assertIn("diagCompetencySummary()", DASHBOARD)
        self.assertIn("diagCompetencyToReview()", DASHBOARD)
        self.assertIn("diagProgressMap: LS.get('diag-progress', {})", DASHBOARD)
        self.assertIn("LS.set('diag-progress', this.diagProgressMap)", DASHBOARD)
        self.assertIn("LS.set('diag-results', this.diagResultsMap)", DASHBOARD)
        self.assertIn("const canResume =", DASHBOARD)
        self.assertIn("diagSaveProgress()", DASHBOARD)


if __name__ == "__main__":
    unittest.main()
