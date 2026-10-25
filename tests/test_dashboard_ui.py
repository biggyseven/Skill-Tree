"""Source-level regression checks for the inline Alpine dashboard.

These checks guard important wiring in static/index.html. They are not a
substitute for browser-level end-to-end tests.
"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


class DashboardUiRegressionTests(unittest.TestCase):
    def test_mobile_search_dialog_uses_shared_search_state(self):
        self.assertIn('role="dialog" aria-modal="true" aria-labelledby="mobile-search-title"', DASHBOARD_HTML)
        self.assertIn('x-ref="mobileSearchBox"', DASHBOARD_HTML)
        self.assertIn('x-model="searchQuery"', DASHBOARD_HTML)
        self.assertIn('@click.stop="openMobileSearch()"', DASHBOARD_HTML)
        self.assertIn('@keydown.enter.prevent="openSearchResult(searchResults[searchActive])"', DASHBOARD_HTML)

    def test_global_search_shortcut_opens_mobile_search_on_small_screens(self):
        self.assertIn("window.matchMedia('(max-width: 1023px)').matches", DASHBOARD_HTML)
        self.assertIn("this.openMobileSearch()", DASHBOARD_HTML)

    def test_favorites_filter_only_shows_saved_favorites(self):
        # skilltreeTheme() overrides the earlier legacy getter; verify the
        # effective getter instead of an unused implementation.
        start = DASHBOARD_HTML.rindex("get categories()")
        end = DASHBOARD_HTML.index("get modMgrNodes()", start)
        categories_getter = DASHBOARD_HTML[start:end]

        self.assertIn(
            "this.treeFilter === 'favorites' ? this.isFavorite(n.id)",
            categories_getter,
        )
        self.assertIn("Aucun favori pour le moment", DASHBOARD_HTML)

    def test_daily_plan_routes_each_action_to_the_matching_workspace(self):
        self.assertIn('@click="openPlanAction(action)"', DASHBOARD_HTML)
        self.assertIn("if (action.action === 'challenge')", DASHBOARD_HTML)
        self.assertIn("await this.setTab('topology')", DASHBOARD_HTML)
        self.assertIn("await this.startChallenge(nodeId)", DASHBOARD_HTML)
        self.assertIn("if (action.action === 'lab')", DASHBOARD_HTML)
        self.assertIn("await this.openLab(nodeId)", DASHBOARD_HTML)
        self.assertIn("label: 'Révision'", DASHBOARD_HTML)
        self.assertIn("label: 'Défi à poursuivre'", DASHBOARD_HTML)

    def test_active_learning_path_prefers_in_progress_work(self):
        start = DASHBOARD_HTML.rindex("get parcours()")
        end = DASHBOARD_HTML.index("get planActions()", start)
        parcours_getter = DASHBOARD_HTML[start:end]

        self.assertIn("pool.findIndex(node => node.status === 'in_progress')", parcours_getter)
        self.assertIn("activePlanAction", parcours_getter)
        self.assertIn("ci >= 0 && !finished ? pool[ci] : null", parcours_getter)
        self.assertIn("statusMeta(s)", DASHBOARD_HTML)
        self.assertIn("in_progress: { label: 'En cours'", DASHBOARD_HTML)

    def test_module_progress_uses_canonical_module_and_validated_nodes(self):
        start = DASHBOARD_HTML.index("get modulesList()")
        end = DASHBOARD_HTML.index("get progress()", start)
        modules_getter = DASHBOARD_HTML[start:end]

        self.assertIn("this.moduleOf(node)", modules_getter)
        self.assertIn("node.status === 'validated'", modules_getter)
        self.assertIn("progress: item.total ? Math.round((item.validated / item.total) * 100) : 0", modules_getter)
        self.assertNotIn("progress: 0", modules_getter)

    def test_remote_challenge_score_is_checked_and_saved_by_the_server(self):
        self.assertIn("/api/node/${encodeURIComponent(ch.id)}/challenge", DASHBOARD_HTML)
        self.assertIn("JSON.stringify({ topology: graph, timeout: !!timeout })", DASHBOARD_HTML)
        self.assertIn("if (!ch.builtin) {", DASHBOARD_HTML)
        self.assertIn("challengeResult.pending", DASHBOARD_HTML)
        self.assertIn("clearInterval(this.challengeTimer);\n            this.challengeSubmissionBusy = true;", DASHBOARD_HTML)
        self.assertIn("expectedSummary: ch.expected_summary", DASHBOARD_HTML)
        self.assertNotIn("expected: ch.expected_topology", DASHBOARD_HTML)
        self.assertIn("challengeResult.attemptRecorded", DASHBOARD_HTML)
        self.assertIn("const passed = !timeout && score >= this.challenge.minScore;", DASHBOARD_HTML)
        self.assertIn(':disabled="!c.builtin && c.status === \'locked\'"', DASHBOARD_HTML)
        self.assertIn("c.status === 'validated' ? '✅ Validé dans le parcours · rejouable'", DASHBOARD_HTML)
        self.assertIn("c.status === 'in_progress' ? '↻ Tentative enregistrée · à poursuivre'", DASHBOARD_HTML)

    def test_empty_daily_plan_distinguishes_completion_from_missing_data(self):
        self.assertIn("Préparation de ta session…", DASHBOARD_HTML)
        self.assertIn("Tu as validé tout le parcours actuellement disponible.", DASHBOARD_HTML)
        self.assertIn("Aucune action recommandée pour le moment.", DASHBOARD_HTML)
        self.assertNotIn(
            "Aucune action disponible : valide un cours pour débloquer la suite.",
            DASHBOARD_HTML,
        )

    def test_completed_learning_path_remains_navigable(self):
        self.assertIn(
            ':disabled="!parcours.steps.length || (parcours.cur && parcours.cur.status === \'locked\')"',
            DASHBOARD_HTML,
        )
        self.assertIn("'Revoir l’arbre complet'", DASHBOARD_HTML)


    def test_locked_last_opened_lesson_is_not_offered_as_resume_target(self):
        start = DASHBOARD_HTML.rindex("get resumableLastNode()")
        end = DASHBOARD_HTML.index("get resumeNode()", start)
        resumable_getter = DASHBOARD_HTML[start:end]

        self.assertIn("return node && node.status !== 'locked' ? node : null;", resumable_getter)
        self.assertIn("return this.resumableLastNode || this.parcours.cur", DASHBOARD_HTML)
        self.assertIn("x-text=\"resumableLastNode ? 'Reprise disponible'", DASHBOARD_HTML)
        self.assertIn('x-show="resumableLastNode"', DASHBOARD_HTML)
        self.assertIn("x-text=\"resumableLastNode ? (lastLessonProgress", DASHBOARD_HTML)

    def test_daily_path_does_not_promote_an_available_challenge_to_in_progress(self):
        start = DASHBOARD_HTML.rindex("get parcours()")
        end = DASHBOARD_HTML.index("get planActions()", start)
        parcours_getter = DASHBOARD_HTML[start:end]

        self.assertIn("action.status === 'in_progress'", parcours_getter)
        self.assertIn("['continue', 'lab', 'challenge'].includes(action.action)", parcours_getter)
        self.assertIn("pool.findIndex(node => node.status === 'in_progress')", parcours_getter)
        self.assertIn("pool.findIndex(node => node.status === 'available')", parcours_getter)

if __name__ == "__main__":
    unittest.main()
