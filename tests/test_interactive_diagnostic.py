"""Regression tests for the interactive troubleshooting diagnostic."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
from scripts.dashboard_source import load_dashboard_source

DASHBOARD = load_dashboard_source(ROOT)
NETWORK_DOWN = json.loads(
    (ROOT / "content" / "diagnostics" / "network_down.json").read_text(encoding="utf-8")
)
_RAW_CATALOG = json.loads(
    (ROOT / "content" / "nodes.json").read_text(encoding="utf-8")
)
CATALOG = {
    node["id"]: node
    for node in (_RAW_CATALOG if isinstance(_RAW_CATALOG, list) else _RAW_CATALOG.values())
}


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

    def test_wrong_answers_trigger_adaptive_consolidation_and_persist(self):
        self.assertIn("const DIAG_REMEDIATION = {", DASHBOARD)
        self.assertIn("Question de consolidation adaptée", DASHBOARD)
        self.assertIn("diagChooseAdaptive(choice)", DASHBOARD)
        self.assertIn("diagContinueAfterSupport()", DASHBOARD)
        self.assertIn("adaptiveQuestion: this.diagAdaptiveQuestion", DASHBOARD)
        self.assertIn("diagAdaptiveAttempts", DASHBOARD)
        self.assertIn("diagNextScenarioRecommendation()", DASHBOARD)

    def test_recommendation_links_only_reference_existing_catalog_nodes(self):
        section_start = DASHBOARD.index("const DIAG_LEARNING_PATHS = {")
        section_end = DASHBOARD.index("function skilltreeExt()", section_start)
        section = DASHBOARD[section_start:section_end]
        references = set()
        for match in re.finditer(r"(?:courseIds|labIds):\s*\[([^\]]*)\]", section):
            references.update(re.findall(r'"([a-z0-9_-]+)"', match.group(1)))
        self.assertTrue(references)
        self.assertTrue(references.issubset(set(CATALOG)), sorted(references - set(CATALOG)))
        lab_ids = {
            node_id for node_id, node in CATALOG.items()
            if node.get("category") == "Labs pratiques" or node_id.startswith("lab_")
        }
        mapped_labs = set()
        for match in re.finditer(r"labIds:\s*\[([^\]]*)\]", section):
            mapped_labs.update(re.findall(r'"([a-z0-9_-]+)"', match.group(1)))
        self.assertTrue(mapped_labs.issubset(lab_ids), sorted(mapped_labs - lab_ids))


    def test_context_menu_can_start_speech_at_any_heading_and_reader_keeps_pause_controls_visible(self):
        self.assertIn('@contextmenu="openReadingContextMenu($event)"', DASHBOARD)
        self.assertIn("Lire à ce niveau", DASHBOARD)
        self.assertIn("openReadingContextMenu(event)", DASHBOARD)
        self.assertIn("startReadingFromContextMenu()", DASHBOARD)
        self.assertIn("readingContextMenu", DASHBOARD)
        self.assertIn("startSectionSelection", DASHBOARD)
        self.assertIn("startLessonAtSelection()", DASHBOARD)
        self.assertIn('aria-label="Commandes flottantes de lecture vocale"', DASHBOARD)
        self.assertIn('aria-label="Mettre en pause la lecture vocale"', DASHBOARD)
        self.assertIn('aria-label="Reprendre la lecture vocale"', DASHBOARD)
        self.assertIn("closeReadingContextMenu()", DASHBOARD)
        self.assertIn("speechStatusLabel()", DASHBOARD)

    def test_linux_security_and_cloud_scenarios_have_scored_decisions(self):
        for scenario_id in ("linux-service-down", "security-suspicious-login", "cloud-instance-unreachable"):
            with self.subTest(scenario=scenario_id):
                self.assertIn(f"'{scenario_id}': {{", DASHBOARD)
        for competency in (
            "Services Linux", "Journaux Linux", "Configuration de service Linux",
            "Réponse à incident", "Analyse des journaux de sécurité",
            "Contrôle d’accès et identité", "Diagnostic cloud réseau",
            "Règles de sécurité cloud", "Connectivité cloud privée"
        ):
            with self.subTest(competency=competency):
                self.assertIn(f'"{competency}": {{', DASHBOARD)

    def test_learning_paths_include_valid_course_ids_for_linux_security_and_cloud(self):
        section_start = DASHBOARD.index("const DIAG_LEARNING_PATHS = {")
        section_end = DASHBOARD.index("function skilltreeExt()", section_start)
        section = DASHBOARD[section_start:section_end]
        references = set()
        for match in re.finditer(r"(?:courseIds|labIds):\s*\[([^\]]*)\]", section):
            references.update(re.findall(r'"([a-z0-9_-]+)"', match.group(1)))
        self.assertTrue(references)
        self.assertTrue(references.issubset(set(CATALOG)), sorted(references - set(CATALOG)))

    def test_recommendations_explain_when_a_prerequisite_must_be_completed(self):
        self.assertIn("Prérequis à valider pour débloquer le parcours ciblé.", DASHBOARD)
        self.assertIn("const isPrimaryTarget =", DASHBOARD)
        self.assertIn("node.status === 'locked'", DASHBOARD)
        self.assertIn("x-text=\"rec.reason\"", DASHBOARD)

    def test_course_and_lab_recommendations_are_connected_to_existing_actions(self):
        self.assertIn("diagOpenCourse(rec.node.id)", DASHBOARD)
        self.assertIn("diagStartGuidedReview(rec.node.id)", DASHBOARD)
        self.assertIn("diagOpenLab(rec.node.id)", DASHBOARD)
        self.assertIn("this.openLab(nodeId)", DASHBOARD)
        self.assertIn("this.reviewNodeId = String(nodeId)", DASHBOARD)


    def test_completed_diagnostic_keeps_best_score_separate_from_latest_attempt(self):
        start = DASHBOARD.index("diagCompleteRun() {")
        end = DASHBOARD.index("diagChoose(c) {", start)
        completion = DASHBOARD[start:end]
        self.assertIn("best[id] = Math.max(Number(best[id]) || 0, score);", completion)
        self.assertIn("this.diagResultsMap = { ...this.diagResultsMap, [id]: result };", completion)
        self.assertIn("LS.set('diag-results', this.diagResultsMap);", completion)
        self.assertIn("delete progress[id];", completion)
        self.assertIn("LS.set('diag-progress', progress);", completion)
        self.assertIn("' · dernier : ' + diagResultsMap[s.id].score + ' %'", DASHBOARD)
        self.assertIn("'Meilleur : ' + diagDoneMap[s.id] + ' %'", DASHBOARD)

    def test_resume_rejects_corrupt_trail_and_invalid_adaptive_step_references(self):
        start = DASHBOARD.index("async openDiag(id) {")
        end = DASHBOARD.index("get diagStep()", start)
        resume = DASHBOARD[start:end]
        self.assertIn("const validTrail =", resume)
        self.assertIn("!!steps[item.key]", resume)
        self.assertIn("const validAdaptiveQuestion =", resume)
        self.assertIn("const validAdaptiveKeys =", resume)
        self.assertIn("if (saved && !canResume)", resume)
        self.assertIn("LS.set('diag-progress', cleanedProgress);", resume)

    def test_progression_uses_level_domain_and_completion_state(self):
        for scenario_id, domain in (
            ("wifi-lent", "network"),
            ("vlan-hote", "network"),
            ("etherchannel-suspendu", "network"),
            ("linux-service-down", "linux"),
            ("security-suspicious-login", "security"),
            ("cloud-instance-unreachable", "cloud"),
        ):
            with self.subTest(scenario=scenario_id):
                start = DASHBOARD.index(f"'{scenario_id}': {{")
                fragment = DASHBOARD[start:start + 180]
                self.assertIn(f"domain: '{domain}'", fragment)

        self.assertIn("domain: 'network'", DASHBOARD[DASHBOARD.index("this.diagList = [{"):DASHBOARD.index("async openDiag(id)")])
        start = DASHBOARD.index("diagLevelRank(level) {")
        end = DASHBOARD.index("async diagStartNextScenario() {", start)
        progression = DASHBOARD[start:end]
        self.assertIn("score < 60", progression)
        self.assertIn("score < 80", progression)
        self.assertIn("higherLevel = scenarios.filter", progression)
        self.assertIn("isCompleted", progression)
        self.assertIn("diagDomainLabel", progression)
        self.assertNotIn("const options = ['network_down', 'wifi-lent', 'vlan-hote', 'etherchannel-suspendu']", progression)

    def test_progression_has_no_false_promotion_when_no_new_scenario_exists(self):
        start = DASHBOARD.index("diagNextScenarioRecommendation() {", DASHBOARD.index("diagLevelRank(level) {"))
        end = DASHBOARD.index("async diagStartNextScenario() {", start)
        progression = DASHBOARD[start:end]
        self.assertIn("if (!unplayedPeer) return null;", progression)
        self.assertIn("this.diagLevelRank(item.level) > currentRank", progression)
        self.assertIn("this.diagLevelRank(item.level) === currentRank", progression)
        self.assertIn("higherLevel.filter(item => !isCompleted(item))", progression)
        self.assertIn("sameLevel.filter(item => !isCompleted(item))", progression)
        self.assertIn("Tu as terminé les scénarios inédits disponibles à ce niveau.", DASHBOARD)
        self.assertIn("sans répétition automatique", DASHBOARD)

    def test_progression_prioritizes_unplayed_scenarios_over_domain_preference(self):
        start = DASHBOARD.index("diagNextScenarioRecommendation() {", DASHBOARD.index("diagLevelRank(level) {"))
        end = DASHBOARD.index("async diagStartNextScenario() {", start)
        progression = DASHBOARD[start:end]
        self.assertIn("const isCompleted = item => Object.prototype.hasOwnProperty.call(completed, item.id);", progression)
        self.assertIn("const unplayedPeers = preferSameDomain(sameLevel.filter(item => !isCompleted(item)));", progression)
        self.assertIn("const unplayedHigher = higherLevel.filter(item => !isCompleted(item)).sort", progression)
        self.assertNotIn("localeCompare(String(a.id)", progression)
        self.assertIn("Preserve the curriculum", progression)
        self.assertNotIn("orderCandidates(higherLevel, true)[0]", progression)



    def test_recommendations_never_fall_back_to_locked_courses(self):
        start = DASHBOARD.index("diagLearningRecommendations() {")
        end = DASHBOARD.index("async diagOpenCourse(nodeId) {", start)
        recommendation_logic = DASHBOARD[start:end]
        self.assertIn("const course = candidates.find(node => node.status !== 'validated' && node.status !== 'locked');", recommendation_logic)
        self.assertNotIn("|| candidates.find(node => node.status !== 'validated')", recommendation_logic)
        self.assertNotIn("|| candidates[0]", recommendation_logic)



if __name__ == "__main__":
    unittest.main()
