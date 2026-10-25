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

    def test_exercise_submission_handles_errors_duplicates_and_progress_updates(self):
        start = DASHBOARD_HTML.index("        async submitAnswer() {")
        end = DASHBOARD_HTML.index("        async startLab()", start)
        methods = DASHBOARD_HTML[start:end]

        self.assertIn("if (this.exerciseBusy || !this.detail?.id) return;", methods)
        self.assertIn("if (this.quizBusy || !this.detail?.id) return;", methods)
        self.assertEqual(methods.count("encodeURIComponent(nodeId)"), 2)
        self.assertEqual(methods.count("if (!response.ok) throw new Error"), 2)
        self.assertIn("this.exerciseError = `La réponse n’a pas pu être enregistrée :", methods)
        self.assertIn("this.exerciseError = `Le quiz n’a pas pu être enregistré :", methods)
        self.assertGreaterEqual(methods.count("await this.refreshAll();"), 2)
        self.assertIn("requestId === this._detailRequestId && String(this.detail?.id) === nodeId", methods)

        start = DASHBOARD_HTML.index("<!-- ONGLET 2 : EXERCICE -->")
        end = DASHBOARD_HTML.index("<!-- ONGLET 3 : LAB / TERMINAL DOCKER -->", start)
        exercise_ui = DASHBOARD_HTML[start:end]
        self.assertIn(':disabled="exerciseBusy"', exercise_ui)
        self.assertIn(':disabled="quizBusy"', exercise_ui)
        self.assertEqual(exercise_ui.count('role="alert" aria-live="polite"'), 2)
        self.assertEqual(exercise_ui.count('role="status" aria-live="polite"'), 2)
        self.assertIn("Cours validé : ta progression a été actualisée.", exercise_ui)
        self.assertIn("d’autres exigences du cours restent à valider.", exercise_ui)
        self.assertIn("quizResult.results || []", exercise_ui)
        self.assertIn("exerciseError: null", DASHBOARD_HTML)

    def test_validation_advances_resume_target_and_reports_refresh_health(self):
        refresh_start = DASHBOARD_HTML.index("        async refreshAll() {")
        refresh_end = DASHBOARD_HTML.index("        async retryDashboardData()", refresh_start)
        refresh_method = DASHBOARD_HTML[refresh_start:refresh_end]
        self.assertIn("tree: !this.treeError", refresh_method)
        self.assertIn("dailyPlan: !this.dashboardDataErrors.dailyPlan", refresh_method)

        clear_start = DASHBOARD_HTML.index("        clearResumeTargetAfterValidation(nodeId) {")
        clear_end = DASHBOARD_HTML.index("        advanceResumeTargetAfterValidation(nodeId, requestId) {", clear_start)
        clear_method = DASHBOARD_HTML[clear_start:clear_end]
        self.assertIn("this.lastOpenedNodeId = ''", clear_method)
        self.assertIn("this.lastOpenedNodeStatus = ''", clear_method)
        self.assertIn("localStorage.removeItem('skilltree-last-node')", clear_method)
        self.assertIn("localStorage.removeItem('skilltree-last-status')", clear_method)
        self.assertIn("localStorage.removeItem('skilltree-last-progress')", clear_method)

        helper_start = clear_end
        helper_end = DASHBOARD_HTML.index("        async submitAnswer() {", helper_start)
        helper = DASHBOARD_HTML[helper_start:helper_end]
        self.assertIn("node.status !== 'validated' || this.allNodesValidated", helper)
        self.assertIn("this.clearResumeTargetAfterValidation(nodeId)", helper)

        start = DASHBOARD_HTML.index("        async submitAnswer() {")
        end = DASHBOARD_HTML.index("        async startLab()", start)
        submissions = DASHBOARD_HTML[start:end]
        self.assertEqual(
            submissions.count("if (result.validated && refreshed.tree) this.advanceResumeTargetAfterValidation(nodeId, requestId);"),
            2,
        )
        self.assertEqual(submissions.count("if (!refreshed.tree || !refreshed.dailyPlan)"), 2)
        self.assertIn("if (this.allNodesValidated)", DASHBOARD_HTML)

    def test_reading_progress_and_resume_status_survive_reload_and_external_validation(self):
        self.assertIn("lastOpenedNodeStatus: localStorage.getItem('skilltree-last-status') || ''", DASHBOARD_HTML)
        self.assertIn("lastLessonProgress: Math.max(0, Math.min(100, Number(localStorage.getItem('skilltree-last-progress') || 0) || 0))", DASHBOARD_HTML)

        refresh_start = DASHBOARD_HTML.index("        async refreshAll() {")
        refresh_end = DASHBOARD_HTML.index("        async retryDashboardData()", refresh_start)
        refresh_method = DASHBOARD_HTML[refresh_start:refresh_end]
        self.assertIn("resumeStatusBeforeRefresh", refresh_method)
        self.assertIn("resumeNodeAfterRefresh?.status === 'validated'", refresh_method)
        self.assertIn("resumeStatusBeforeRefresh !== 'validated'", refresh_method)
        self.assertIn("this.clearResumeTargetAfterValidation(resumeIdBeforeRefresh)", refresh_method)
        self.assertIn("localStorage.setItem('skilltree-last-status', resumeNodeAfterRefresh.status)", refresh_method)

        show_start = DASHBOARD_HTML.index("        async show(nodeId) {")
        show_end = DASHBOARD_HTML.index("        close() {", show_start)
        show_method = DASHBOARD_HTML[show_start:show_end]
        self.assertIn("localStorage.setItem('skilltree-last-status', this.lastOpenedNodeStatus)", show_method)
        self.assertIn("localStorage.removeItem('skilltree-last-progress')", show_method)
        self.assertIn("s.scrollTop = max > 0 ? Math.round(max * progress / 100) : 0", show_method)
        self.assertIn("this.onLessonScroll({ target: s })", show_method)

        init_start = DASHBOARD_HTML.index("        async init() {")
        init_end = DASHBOARD_HTML.index("        // --- Préférences d'affichage du lecteur", init_start)
        init_method = DASHBOARD_HTML[init_start:init_end]
        self.assertIn("message.type === 'lab:submit-result'", init_method)
        self.assertIn("this.onLabValidated(message.detail)", init_method)
        self.assertIn("this.refreshAll()", init_method)

    def test_daily_plan_filters_resume_and_path_but_keeps_other_available_courses(self):
        self.assertIn("this.dailyPlan.filter(action => !visibleNodeIds.includes(String(action.node_id)))", DASHBOARD_HTML)
        self.assertIn("this.nodes\n            .filter(n => n.status === 'available' && !visibleNodeIds.includes(String(n.id)))", DASHBOARD_HTML)
        self.assertIn("this.dailyPlan.length", DASHBOARD_HTML)
        self.assertIn("Les priorités du jour sont déjà mises en évidence", DASHBOARD_HTML)

    def test_course_reader_surfaces_load_errors_and_ignores_stale_requests(self):
        start = DASHBOARD_HTML.index("        async show(nodeId) {")
        end = DASHBOARD_HTML.index("        close() {", start)
        show_method = DASHBOARD_HTML[start:end]

        self.assertIn("const requestId = ++this._detailRequestId;", show_method)
        self.assertIn("encodeURIComponent(nodeKey)", show_method)
        self.assertIn("if (!r.ok) throw new Error", show_method)
        self.assertGreaterEqual(show_method.count("requestId !== this._detailRequestId"), 4)
        self.assertIn("this.detailLoadError =", show_method)
        self.assertIn("this.detail = null;", show_method)
        self.assertIn('x-show="!detailLoading && detailLoadError"', DASHBOARD_HTML)
        self.assertIn('role="alert" aria-live="assertive"', DASHBOARD_HTML)
        self.assertIn('@click="detailRequestedNodeId && show(detailRequestedNodeId)"', DASHBOARD_HTML)
        self.assertIn("detailLoadError: null, detailRequestedNodeId: null, _detailRequestId: 0", DASHBOARD_HTML)

        close_start = DASHBOARD_HTML.index("        close() {")
        close_end = DASHBOARD_HTML.index("        canStartExercise()", close_start)
        close_method = DASHBOARD_HTML[close_start:close_end]
        self.assertIn("this._detailRequestId += 1;", close_method)
        self.assertIn("this.detailLoadError = null;", close_method)

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
        self.assertIn("this.themes.some(x => x.id === stored)", DASHBOARD_HTML)
        self.assertIn("this.themes.some(x => x.id === applied) ? applied : 'graphite'", DASHBOARD_HTML)
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

    def test_daily_plan_avoids_duplicating_the_resume_and_current_path_nodes(self):
        start = DASHBOARD_HTML.index("        get planActions() {")
        end = DASHBOARD_HTML.index("        get notifications()", start)
        plan_getters = DASHBOARD_HTML[start:end]

        self.assertIn("this.resumeNode?.id", plan_getters)
        self.assertIn("this.parcours.cur?.id", plan_getters)
        self.assertIn(
            "return this.dailyPlan.filter(action => !visibleNodeIds.includes(String(action.node_id)));",
            plan_getters,
        )
        self.assertIn(
            ".filter(n => n.status === 'available' && !visibleNodeIds.includes(String(n.id)))",
            plan_getters,
        )
        self.assertIn("get planEmptyMessage()", plan_getters)
        self.assertIn(
            "Les priorités du jour sont déjà mises en évidence dans les cartes de reprise et du parcours.",
            plan_getters,
        )
        self.assertIn('x-text="planEmptyMessage"', DASHBOARD_HTML)

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

    def test_dashboard_first_screen_uses_compact_responsive_card_spacing(self):
        self.assertIn(
            'class="mb-8 grid gap-4 sm:gap-6 lg:grid-cols-[1fr_2fr]"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            'bg-[color:var(--s1)] p-5 shadow-2xl sm:p-7',
            DASHBOARD_HTML,
        )
        self.assertIn(
            'class="flex min-w-0 flex-col rounded-3xl border border-white/5 bg-[color:var(--s1)] p-5 shadow-2xl sm:p-6 xl:p-8"',
            DASHBOARD_HTML,
        )
        self.assertIn("sm:mt-7 sm:pt-5", DASHBOARD_HTML)
        self.assertIn(
            'role="group" aria-label="Étapes du parcours"',
            DASHBOARD_HTML,
        )

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

    def test_module_cards_expose_selection_and_progress_accessibly(self):
        start = DASHBOARD_HTML.index("<!-- Cartes modules compactes -->")
        end = DASHBOARD_HTML.index("<div class=\"mb-8 flex flex-wrap gap-3\">", start)
        module_cards = DASHBOARD_HTML[start:end]

        self.assertIn(':aria-pressed="moduleFilter === m.id"', module_cards)
        self.assertIn(
            ':aria-label="`${m.label}, ${m.validated} cours validés sur ${m.total}, ${m.pct} %. ${moduleFilter === m.id ? \'Module sélectionné\' : \'Afficher ce module\'}`"',
            module_cards,
        )
        self.assertIn('role="progressbar"', module_cards)
        self.assertIn(':aria-label="`Progression du module ${m.label}`"', module_cards)
        self.assertIn(':aria-valuenow="m.pct"', module_cards)
        self.assertIn('aria-valuemin="0" aria-valuemax="100"', module_cards)
        self.assertIn("focus-visible:ring-emerald-400/70", module_cards)

    def test_level_and_favorites_filters_announce_selection_accessibly(self):
        start = DASHBOARD_HTML.index('<div class="mb-8 flex flex-wrap gap-3">')
        end = DASHBOARD_HTML.index('<div id="tree-grid"', start)
        filter_controls = DASHBOARD_HTML[start:end]

        for filter_id in ("all", "beginner", "intermediaire", "expert", "favorites"):
            self.assertIn(
                f':aria-pressed="treeFilter === \'{filter_id}\'"',
                filter_controls,
            )
        self.assertEqual(filter_controls.count("focus-visible:ring-emerald-400/70"), 5)

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
        self.assertIn("get planEmptyMessage()", DASHBOARD_HTML)
        self.assertIn("this.treeError && !this.nodes.length", DASHBOARD_HTML)
        self.assertIn('x-text="planEmptyMessage"', DASHBOARD_HTML)
        self.assertIn("Aucun cours disponible", DASHBOARD_HTML)

    def test_desktop_mobile_and_header_navigation_controls_are_consistent(self):
        sidebar_start = DASHBOARD_HTML.index("<!-- Navigation -->")
        sidebar_end = DASHBOARD_HTML.index("<!-- Focus -->", sidebar_start)
        sidebar = DASHBOARD_HTML[sidebar_start:sidebar_end]

        self.assertIn(':aria-label="item.label"', sidebar)
        self.assertIn(':title="sidebarCollapsed ? item.label : null"', sidebar)
        self.assertIn('class="nav-item-icon', sidebar)
        self.assertIn("tab === item.id ? 'border-emerald-400/20 bg-emerald-400/10 text-emerald-200", sidebar)
        self.assertIn("focus-visible:ring-emerald-400/70", sidebar)
        self.assertIn(':aria-pressed="focusMode"', DASHBOARD_HTML)

        mobile_start = DASHBOARD_HTML.index('<!-- Barre de navigation mobile')
        mobile_end = DASHBOARD_HTML.index('<!-- Notification de mise à jour WebSocket -->', mobile_start)
        mobile_nav = DASHBOARD_HTML[mobile_start:mobile_end]
        self.assertIn('aria-label="Navigation mobile"', mobile_nav)
        self.assertIn(':aria-label="item.id === \'tree\' ? \'Accueil\' : item.label"', mobile_nav)
        self.assertIn(':aria-current="tab === item.id ? \'page\' : null"', mobile_nav)
        self.assertIn(".mobile-bottom-nav button.is-active::after", DASHBOARD_HTML)
        self.assertIn("min-height: 48px", DASHBOARD_HTML)
        self.assertIn("@media (max-width: 360px)", DASHBOARD_HTML)

        for label in ("Choisir un thème", "Modifier le profil", "Ouvrir les paramètres"):
            self.assertIn(f'aria-label="{label}"', DASHBOARD_HTML)
        self.assertIn(':aria-label="unreadNotificationCount > 0 ? \'Ouvrir les notifications, \' + unreadNotificationCount', DASHBOARD_HTML)
        for state in ("themeMenuOpen", "notificationsOpen", "profileMenuOpen", "settingsMenuOpen"):
            self.assertIn(f':aria-expanded="{state}"', DASHBOARD_HTML)
        self.assertGreaterEqual(DASHBOARD_HTML.count('class="nav-action-btn'), 5)

        profile_start = DASHBOARD_HTML.index("        editProfile() {")
        profile_end = DASHBOARD_HTML.index("        saveProfile() {", profile_start)
        self.assertIn("this.themeMenuOpen = false", DASHBOARD_HTML[profile_start:profile_end])

    def test_theme_selector_uses_alpine_reactive_state_and_saved_preference(self):
        self.assertIn("themeIsActive(id) { return this.theme === id; }", DASHBOARD_HTML)
        sync_start = DASHBOARD_HTML.index("        syncTheme() {")
        sync_end = DASHBOARD_HTML.index("        closeThemeOnOutside(event)", sync_start)
        sync = DASHBOARD_HTML[sync_start:sync_end]
        self.assertIn("this.themes.some(x => x.id === stored)", sync)
        self.assertIn("root.dataset.theme = id;", sync)
        self.assertIn("this.theme = id;", sync)
        self.assertIn("localStorage.setItem('skilltree-theme2', id)", sync)
        self.assertIn("@click=\"setTheme(t.id)\"", DASHBOARD_HTML)
        self.assertIn(":aria-pressed=\"themeIsActive(t.id)\"", DASHBOARD_HTML)
        self.assertIn("@click=\"syncTheme(); themeMenuOpen = true; settingsMenuOpen = false; notificationsOpen = false; profileMenuOpen = false\"", DASHBOARD_HTML)

    def test_notification_center_is_event_driven_persistent_and_marks_unread(self):
        self.assertIn("skilltree-notifications-v1", DASHBOARD_HTML)
        self.assertIn("get unreadNotificationCount()", DASHBOARD_HTML)
        self.assertIn("addNotification(event)", DASHBOARD_HTML)
        self.assertIn("markNotificationRead(id)", DASHBOARD_HTML)
        self.assertIn("markAllNotificationsRead()", DASHBOARD_HTML)
        self.assertIn("openNotification(notification)", DASHBOARD_HTML)
        self.assertIn("x-text=\"unreadNotificationCount > 9 ? '9+' : unreadNotificationCount\"", DASHBOARD_HTML)
        self.assertIn("@click=\"openNotification(n)\"", DASHBOARD_HTML)
        self.assertIn("@click=\"markAllNotificationsRead()\"", DASHBOARD_HTML)
        self.assertIn("Aucune notification pour le moment", DASHBOARD_HTML)
        self.assertIn("Les nouveaux cours, déblocages, validations, séries et badges apparaîtront ici.", DASHBOARD_HTML)
        self.assertNotIn("this.planActions.slice(0, 3).forEach(a => out.push", DASHBOARD_HTML)

    def test_course_changes_streaks_and_badges_create_deduplicated_notifications(self):
        self.assertIn("skilltree-node-snapshot-v1", DASHBOARD_HTML)
        self.assertIn("readNodeSnapshot()", DASHBOARD_HTML)
        self.assertIn("saveNodeSnapshot(this.nodes)", DASHBOARD_HTML)
        self.assertIn("courses-added:", DASHBOARD_HTML)
        self.assertIn("course-unlocked:", DASHBOARD_HTML)
        self.assertIn("course-validated:", DASHBOARD_HTML)
        self.assertIn("streak-milestone:", DASHBOARD_HTML)
        self.assertIn("badge-unlocked:", DASHBOARD_HTML)
        self.assertIn("this.addNotification({", DASHBOARD_HTML)
        # The previous implementation skipped all comparisons when the in-memory
        # tree was empty, which missed new courses added while the page was closed.
        self.assertNotIn("if (!prev.size) return; const ev = [];", DASHBOARD_HTML)

if __name__ == "__main__":
    unittest.main()
