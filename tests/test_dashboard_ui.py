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

    def test_graphite_is_the_default_without_overwriting_saved_theme(self):
        self.assertIn(
            "var t = localStorage.getItem('skilltree-theme2') || (localStorage.getItem('skilltree-theme') === 'light' ? 'lumiere' : 'graphite');",
            DASHBOARD_HTML,
        )
        self.assertIn("this.themes.some(x => x.id === stored) ? stored : 'graphite'", DASHBOARD_HTML)
        self.assertIn("this.setTheme(k === 'dark' ? 'lumiere' : 'graphite')", DASHBOARD_HTML)

    def test_ambient_glows_are_subtle_and_status_motion_is_not_continuous(self):
        self.assertEqual(DASHBOARD_HTML.count("--halo:.55;"), 7)
        self.assertIn(".glow-lime { box-shadow:", DASHBOARD_HTML)
        self.assertIn(".glow-fuchsia { box-shadow:", DASHBOARD_HTML)
        self.assertNotIn(".glow-lime { animation: glowLime", DASHBOARD_HTML)
        self.assertNotIn(".glow-fuchsia { animation: glowFuchsia", DASHBOARD_HTML)
        self.assertIn("@media (prefers-reduced-motion: reduce)", DASHBOARD_HTML)

    def test_daily_plan_routes_each_action_to_the_matching_workspace(self):
        self.assertIn('@click="openPlanAction(action)"', DASHBOARD_HTML)
        self.assertIn("if (action.action === 'challenge')", DASHBOARD_HTML)
        self.assertIn("await this.setTab('topology')", DASHBOARD_HTML)
        self.assertIn("await this.startChallenge(nodeId)", DASHBOARD_HTML)
        self.assertIn("if (action.action === 'lab')", DASHBOARD_HTML)
        self.assertIn("await this.openLab(nodeId)", DASHBOARD_HTML)
        self.assertIn("label: 'Révision'", DASHBOARD_HTML)
        self.assertIn("label: 'Défi à poursuivre'", DASHBOARD_HTML)

    def test_daily_plan_highlights_server_priority_and_supports_keyboard_navigation(self):
        self.assertIn('x-for="(action, actionIndex) in planActions"', DASHBOARD_HTML)
        self.assertIn(
            "actionIndex === 0 && dailyPlan.length > 0 ? '!border-emerald-400/35 shadow-lg' : ''",
            DASHBOARD_HTML,
        )
        self.assertIn('x-show="actionIndex === 0 && dailyPlan.length > 0"', DASHBOARD_HTML)
        self.assertIn(">Priorité du jour</span>", DASHBOARD_HTML)
        self.assertIn(
            ":aria-label=\"action.label + '. ' + (action.reason || 'Action du parcours') + '. Ouvrir cette activité.'\"",
            DASHBOARD_HTML,
        )
        self.assertIn("min-h-[164px]", DASHBOARD_HTML)
        self.assertIn("focus-visible:ring-emerald-400/70", DASHBOARD_HTML)
        self.assertIn("Ouvrir l’activité", DASHBOARD_HTML)

    def test_daily_plan_continuation_opens_the_backend_selected_exercise_kind(self):
        self.assertIn("next_requirement_kind=target_kind.value if target_kind is not None else None", (ROOT / "app" / "engine.py").read_text(encoding="utf-8"))
        self.assertIn("exercisePreferredKind: null", DASHBOARD_HTML)
        self.assertIn("this.exercisePreferredKind = action.next_requirement_kind;", DASHBOARD_HTML)
        self.assertIn("const preferredKind = this.exercisePreferredKind;", DASHBOARD_HTML)
        self.assertIn("if ((preferredKind === 'terminal' || (!preferredKind && this.detail.terminal)) && this.detail.terminal)", DASHBOARD_HTML)
        self.assertIn("['quiz', 'terminal'].includes(action.next_requirement_kind)", DASHBOARD_HTML)

    def test_daily_plan_challenge_badge_distinguishes_available_and_in_progress(self):
        self.assertIn('planMeta(action).classes', DASHBOARD_HTML)
        self.assertIn('x-text="planMeta(action).label"', DASHBOARD_HTML)

        start = DASHBOARD_HTML.index("        planMeta(action) {")
        end = DASHBOARD_HTML.index("        async openPlanAction(action)", start)
        plan_meta = DASHBOARD_HTML[start:end]

        self.assertIn("const status = action && typeof action === 'object' ? action.status : null;", plan_meta)
        self.assertIn("status === 'available'", plan_meta)
        self.assertIn("label: 'Défi à relever'", plan_meta)
        self.assertIn("label: 'Défi à poursuivre'", plan_meta)

    def test_active_learning_path_prefers_in_progress_work(self):
        start = DASHBOARD_HTML.rindex("get parcours()")
        end = DASHBOARD_HTML.index("get planActions()", start)
        parcours_getter = DASHBOARD_HTML[start:end]

        self.assertIn("pool.findIndex(node => node.status === 'in_progress')", parcours_getter)
        self.assertIn("activePlanAction", parcours_getter)
        self.assertIn("ci >= 0 && !finished ? pool[ci] : null", parcours_getter)
        self.assertIn("statusMeta(s)", DASHBOARD_HTML)
        self.assertIn("in_progress: { label: 'En cours'", DASHBOARD_HTML)

    def test_learning_path_steps_remain_readable_on_narrow_screens(self):
        self.assertIn(
            'class="relative flex-1 overflow-x-auto pb-2" role="group" aria-label="Étapes du parcours"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            ':style="`min-width: ${Math.max(parcours.steps.length * 6, 12)}rem`"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            'class="relative flex min-h-[120px] items-center justify-between"',
            DASHBOARD_HTML,
        )

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
        self.assertIn("return this.resumableLastNode\n            || this.parcours.cur", DASHBOARD_HTML)
        self.assertIn('x-text="resumeBadge"', DASHBOARD_HTML)
        self.assertIn('x-show="resumableLastNode"', DASHBOARD_HTML)
        self.assertIn('x-text="resumeButtonLabel"', DASHBOARD_HTML)

    def test_daily_path_does_not_promote_an_available_challenge_to_in_progress(self):
        start = DASHBOARD_HTML.rindex("get parcours()")
        end = DASHBOARD_HTML.index("get planActions()", start)
        parcours_getter = DASHBOARD_HTML[start:end]

        self.assertIn("action.status === 'in_progress'", parcours_getter)
        self.assertIn("['continue', 'lab', 'challenge'].includes(action.action)", parcours_getter)
        self.assertIn("pool.findIndex(node => node.status === 'in_progress')", parcours_getter)
        self.assertIn("pool.findIndex(node => node.status === 'available')", parcours_getter)

    def test_resume_button_label_matches_the_current_target_status(self):
        self.assertIn("get resumeButtonLabel()", DASHBOARD_HTML)
        self.assertIn("if (this.resumeNode?.status === 'in_progress') return 'Reprendre cette activité';", DASHBOARD_HTML)
        self.assertIn("if (this.resumeNode?.status === 'validated') return 'Réviser cette leçon';", DASHBOARD_HTML)
        self.assertIn("return this.lastLessonProgress >= 100 ? 'Revoir cette leçon' : 'Reprendre la lecture';", DASHBOARD_HTML)
        self.assertIn('x-text="resumeButtonLabel"', DASHBOARD_HTML)

    def test_fully_validated_path_still_offers_a_review_target(self):
        self.assertIn("get allNodesValidated()", DASHBOARD_HTML)
        self.assertIn("return this.nodes.length > 0 && this.nodes.every(node => node.status === 'validated');", DASHBOARD_HTML)
        self.assertIn("this.nodes.find(n => n.status === 'validated')", DASHBOARD_HTML)
        self.assertIn("if (this.allNodesValidated) return 'Parcours terminé';", DASHBOARD_HTML)
        self.assertIn("Tu as validé tout le parcours disponible.", DASHBOARD_HTML)

    def test_v2_lab_opens_react_flow_workspace_and_keeps_legacy_fallback(self):
        start = DASHBOARD_HTML.rindex("async openLab(id, openInNewTab = false) {")
        end = DASHBOARD_HTML.index("        isLabDone(id)", start)
        open_lab_method = DASHBOARD_HTML[start:end]

        self.assertIn("fetch(`/api/lab/v2/${encodeURIComponent(nodeId)}`)", open_lab_method)
        self.assertIn("navigate(`/lab.html?id=${encodeURIComponent(nodeId)}`)", open_lab_method)
        self.assertIn("if (response.status !== 404)", open_lab_method)
        self.assertIn("navigate(`/lab.html?id=${encodeURIComponent(nodeId)}`)", open_lab_method)
        self.assertIn("await this.show(nodeId);", open_lab_method)
        self.assertIn("this.modalTab = 'lab';", open_lab_method)
        self.assertIn("this.openLab(this.detail.id, true);", DASHBOARD_HTML)

    def test_dashboard_api_loaders_surface_errors_without_replacing_data_with_defaults(self):
        self.assertIn("dashboardDataErrors: { userStats: null, streak: null, dailyPlan: null, stats: null }", DASHBOARD_HTML)
        self.assertIn("Certaines données n’ont pas pu être actualisées", DASHBOARD_HTML)
        self.assertIn("Les valeurs valides déjà chargées sont conservées", DASHBOARD_HTML)
        self.assertIn('@click="retryDashboardData()"', DASHBOARD_HTML)

        for method, endpoint, error_key in [
            ("loadUserStats", "/api/user-stats", "userStats"),
            ("loadStreak", "/api/streak", "streak"),
            ("loadDailyPlan", "/api/daily-plan", "dailyPlan"),
            ("loadStats", "/api/stats", "stats"),
        ]:
            start = DASHBOARD_HTML.index(f"async {method}() {{")
            next_method = DASHBOARD_HTML.find("\n        async ", start + 1)
            end = next_method if next_method >= 0 else len(DASHBOARD_HTML)
            body = DASHBOARD_HTML[start:end]
            self.assertIn(f"fetch('{endpoint}')", body)
            self.assertIn("if (!r.ok) throw new Error", body)
            self.assertIn(f"this.dashboardDataErrors.{error_key} = null;", body)
            self.assertIn(f"this.dashboardDataErrors.{error_key} =", body)
            self.assertIn("catch (e)", body)

        self.assertNotIn("this.streakDays = d.days || 0;", DASHBOARD_HTML)
        self.assertNotIn("this.dailyPlan = d.actions || [];", DASHBOARD_HTML)
        self.assertIn("userStatsLoaded ? userStats.total_xp : '—'", DASHBOARD_HTML)
        self.assertIn("streakLoaded ? streakDays : '—'", DASHBOARD_HTML)
        self.assertIn("sélection locale", DASHBOARD_HTML)
        retry_start = DASHBOARD_HTML.index("async retryDashboardData()")
        retry_end = DASHBOARD_HTML.index("editProfile()", retry_start)
        self.assertIn("this.refreshAll()", DASHBOARD_HTML[retry_start:retry_end])
        self.assertIn("this.loadStats()", DASHBOARD_HTML[retry_start:retry_end])
        self.assertNotIn("this.loadStats()", DASHBOARD_HTML[DASHBOARD_HTML.index("async refreshAll()"):retry_start])

    def test_tree_loading_finishes_and_api_failures_are_visible(self):
        start = DASHBOARD_HTML.index("async loadTree() {")
        end = DASHBOARD_HTML.index("async loadUserStats()", start)
        load_tree = DASHBOARD_HTML[start:end]

        self.assertIn("if (!r.ok) throw new Error(`HTTP ${r.status}`);", load_tree)
        self.assertIn("!Array.isArray(d.nodes)", load_tree)
        self.assertIn("this.treeError =", load_tree)
        self.assertIn("finally {", load_tree)
        self.assertIn("this.loading = false;", load_tree)
        self.assertIn('x-show="treeError && tab === \'tree\'"', DASHBOARD_HTML)
        self.assertIn('@click="refreshAll()"', DASHBOARD_HTML)
        self.assertIn("treeError && !nodes.length", DASHBOARD_HTML)
        self.assertIn("Aucun cours disponible", DASHBOARD_HTML)

if __name__ == "__main__":
    unittest.main()
