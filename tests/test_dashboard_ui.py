"""Source-level regression checks for the inline Alpine dashboard.

These checks guard important wiring in static/index.html. They are not a
substitute for browser-level end-to-end tests.
"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


class DashboardUiRegressionTests(unittest.TestCase):
    def test_course_reader_voice_and_contextual_tutor_are_wired(self):
        self.assertIn('aria-label="Lecture vocale du cours"', DASHBOARD_HTML)
        self.assertIn('x-ref="lessonArticle"', DASHBOARD_HTML)
        self.assertIn('x-ref="speechAudio"', DASHBOARD_HTML)
        self.assertIn("fetch('/api/tts'", DASHBOARD_HTML)
        self.assertIn("Intl.Segmenter", DASHBOARD_HTML)
        self.assertIn("prefetchSpeechChunk(index + 1, runId)", DASHBOARD_HTML)
        self.assertIn("toggleLessonSpeech()", DASHBOARD_HTML)
        self.assertIn("pauseSpeech()", DASHBOARD_HTML)
        self.assertIn("resumeSpeech()", DASHBOARD_HTML)
        self.assertIn("speechSynthesis", DASHBOARD_HTML)
        self.assertIn("startBrowserSpeechFallback", DASHBOARD_HTML)
        self.assertIn("speakNextBrowserChunk", DASHBOARD_HTML)
        self.assertIn("Lecture avec la voix de secours du navigateur", DASHBOARD_HTML)
        self.assertIn("Expliquer le schéma", DASHBOARD_HTML)
        self.assertIn("Expliquer ma sélection", DASHBOARD_HTML)
        self.assertIn('x-show="open && tutorOpen && modalTab === \'lesson\'"', DASHBOARD_HTML)
        self.assertIn("speakTutorMessage(message.text)", DASHBOARD_HTML)
        self.assertIn("selected_text: selectedText, history", DASHBOARD_HTML)
        self.assertIn("course-tutor-panel", DASHBOARD_HTML)
        self.assertIn("resize: both", DASHBOARD_HTML)
        self.assertIn("setTutorSize('compact')", DASHBOARD_HTML)
        self.assertIn("setTutorSize('normal')", DASHBOARD_HTML)
        self.assertIn("setTutorSize('large')", DASHBOARD_HTML)
        self.assertIn("skilltree-tutor-size", DASHBOARD_HTML)
        self.assertIn("Titre du cours", DASHBOARD_HTML)
        self.assertIn("Sous-section", DASHBOARD_HTML)
        self.assertIn("readable.querySelectorAll('p, li, blockquote, figcaption')", DASHBOARD_HTML)
        self.assertIn("Intl.Segmenter", DASHBOARD_HTML)
        self.assertIn("paragraph.split(/(?<=[.!?…;:])\\s+/u)", DASHBOARD_HTML)
        self.assertIn("ne jamais inventer de ponctuation", DASHBOARD_HTML)
        self.assertIn("block.append(readable.ownerDocument.createTextNode('\\n\\n'))", DASHBOARD_HTML)
        self.assertIn("Une ligne Markdown terminée par un saut forcé (<br>)", DASHBOARD_HTML)
        self.assertIn("readable.querySelectorAll('p').forEach(paragraph =>", DASHBOARD_HTML)
        self.assertIn("paragraph.querySelector('br')", DASHBOARD_HTML)
        self.assertIn("parts.forEach(piece => paragraph.parentNode.insertBefore(piece, paragraph))", DASHBOARD_HTML)
        self.assertIn("const spokenLabel = readable.ownerDocument.createElement('p')", DASHBOARD_HTML)
        self.assertIn("const spokenValue = readable.ownerDocument.createElement('p')", DASHBOARD_HTML)
        self.assertIn("value.replace(/\\s*→\\s*/gu, ', puis ')", DASHBOARD_HTML)
        self.assertIn("Garder la ponctuation", DASHBOARD_HTML)
        self.assertIn("chunks.push(clean)", DASHBOARD_HTML)
        self.assertNotIn("clean.replace(/[.;:]+$/u, '')", DASHBOARD_HTML)
        self.assertIn("isContentsList", DASHBOARD_HTML)
        self.assertNotIn("lesson-section-back", DASHBOARD_HTML)
        self.assertNotIn("Retour au sommaire des sections", DASHBOARD_HTML)
        self.assertIn("tab !== 'tree'", DASHBOARD_HTML)
        self.assertIn('@click="goBackTab()"', DASHBOARD_HTML)
        self.assertIn("tabHistory: []", DASHBOARD_HTML)
        self.assertIn("goBackTab() {", DASHBOARD_HTML)
        self.assertIn("async setTab(name, options = {})", DASHBOARD_HTML)
        self.assertIn("this.setTab(target, { skipHistory: true })", DASHBOARD_HTML)
        self.assertNotIn("createTextNode('.\\n')", DASHBOARD_HTML)

    def test_course_reader_restores_position_per_course_and_allows_start_selection(self):
        self.assertIn("skilltree-lesson-positions", DASHBOARD_HTML)
        self.assertIn("loadLessonPositions()", DASHBOARD_HTML)
        self.assertIn("saveLessonPosition(nodeId, position)", DASHBOARD_HTML)
        self.assertIn("restoreLessonPosition(container, savedPosition = null)", DASHBOARD_HTML)
        self.assertIn("startLessonAtSelection()", DASHBOARD_HTML)
        self.assertIn('option value="__resume__">Reprendre où j’étais</option>', DASHBOARD_HTML)
        self.assertIn('option value="__top__">Début du cours</option>', DASHBOARD_HTML)
        self.assertIn("sectionOffset", DASHBOARD_HTML)
        self.assertIn("const requestedStart = this.startSectionSelection === '__top__'", DASHBOARD_HTML)
        self.assertIn("this.restoreLessonPosition(s, this.lessonPositions[String(this.detail?.id || '')] || null)", DASHBOARD_HTML)

    def test_reader_guides_diagram_formats_and_requests_contextual_explanations(self):
        self.assertIn("prepareLessonDiagrams(wrap)", DASHBOARD_HTML)
        self.assertIn("className = 'lesson-mermaid'", DASHBOARD_HTML)
        self.assertIn("async renderLessonDiagrams()", DASHBOARD_HTML)
        self.assertIn("explainDiagramFromButton(button)", DASHBOARD_HTML)
        self.assertIn("const sourceCode = visual.querySelector('.mermaid[data-original-source]')", DASHBOARD_HTML)
        self.assertIn("'Code source du diagramme : ' + (sourceCode", DASHBOARD_HTML)
        self.assertIn("btn-explain-diagram", DASHBOARD_HTML)
        self.assertIn("lesson-diagram-guide", DASHBOARD_HTML)
        self.assertIn("graphviz", DASHBOARD_HTML)
        self.assertIn("img[alt]", DASHBOARD_HTML)
        self.assertIn("N’invente aucune étiquette, connexion, donnée, direction de trafic", DASHBOARD_HTML)
        self.assertIn("await this.renderLessonDiagrams()", DASHBOARD_HTML)

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

    def test_dashboard_separates_resume_lesson_from_next_recommended_lesson(self):
        resume_start = DASHBOARD_HTML.index("        get resumeButtonLabel() {")
        resume_end = DASHBOARD_HTML.index("        get parcours() {", resume_start)
        resume_methods = DASHBOARD_HTML[resume_start:resume_end]
        self.assertIn("get nextLessonNode()", resume_methods)
        self.assertIn("if (!this.resumableLastNode) return null", resume_methods)
        self.assertIn("String(next.id) === String(this.resumableLastNode.id)", resume_methods)
        self.assertIn('x-show="nextLessonNode"', DASHBOARD_HTML)
        self.assertIn("nextLessonNode ? nextLessonNode.title : ''", DASHBOARD_HTML)
        self.assertIn("nextLessonNode && show(nextLessonNode.id)", DASHBOARD_HTML)
        self.assertIn("Prochaine leçon →", DASHBOARD_HTML)

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
        self.assertIn("const savedPosition = this.lessonPositions[nodeKey] || null", show_method)
        self.assertIn("this.startSectionSelection = '__resume__'", show_method)
        self.assertIn("await this.renderLessonDiagrams()", show_method)
        self.assertIn("this.restoreLessonPosition(s, this.lessonPositions[String(this.detail?.id || '')] || null)", show_method)

        init_start = DASHBOARD_HTML.index("        async init() {")
        init_end = DASHBOARD_HTML.index("        // --- Préférences d'affichage du lecteur", init_start)
        init_method = DASHBOARD_HTML[init_start:init_end]
        self.assertIn("message.type === 'lab:submit-result'", init_method)
        self.assertIn("this.onLabValidated(message.detail)", init_method)
        self.assertIn("this.refreshAll()", init_method)

        validation_start = DASHBOARD_HTML.index("        onLabValidated(data) {")
        validation_end = DASHBOARD_HTML.index("        // ---------- récompenses", validation_start)
        validation_method = DASHBOARD_HTML[validation_start:validation_end]
        self.assertIn("data.sandbox === true", validation_method)
        self.assertIn("data.attempt_recorded === false", validation_method)
        self.assertIn("const nodeId = String(data.lab_id || (this.detail && this.detail.id) || '');", validation_method)
        self.assertIn("if (!data || !data.passed || data.sandbox === true || data.stale === true || data.attempt_recorded === false) return;", validation_method)

    def test_daily_focus_timer_tracks_active_time_and_persists_the_daily_goal(self):
        self.assertIn("function skilltreeStudySession()", DASHBOARD_HTML)
        self.assertIn("const storageKey = 'skilltree-study-session-v1';", DASHBOARD_HTML)
        self.assertIn("const goals = [15, 25, 45, 60];", DASHBOARD_HTML)
        self.assertIn("if (saved && saved.date === todayKey())", DASHBOARD_HTML)
        self.assertIn("document.addEventListener('visibilitychange', this._onVisibilityChange);", DASHBOARD_HTML)
        self.assertIn("window.addEventListener('pagehide', this._onPageHide);", DASHBOARD_HTML)
        self.assertIn("this._interval = window.setInterval(() =>", DASHBOARD_HTML)
        self.assertIn("if (this.goalReached)", DASHBOARD_HTML)
        self.assertIn("this.elapsedSeconds % 5 === 0", DASHBOARD_HTML)
        self.assertIn('x-data="skilltreeStudySession()" class="mb-5 rounded-2xl', DASHBOARD_HTML)
        self.assertIn('role="group" aria-label="Durée cible de la session"', DASHBOARD_HTML)
        self.assertIn('@click="setTarget(minutes)"', DASHBOARD_HTML)
        self.assertIn(':aria-pressed="targetMinutes === minutes"', DASHBOARD_HTML)
        self.assertIn('x-text="elapsedLabel()"', DASHBOARD_HTML)
        self.assertIn('x-text="statusLabel"', DASHBOARD_HTML)
        self.assertIn('@click="toggle()"', DASHBOARD_HTML)
        self.assertIn('@click="reset()"', DASHBOARD_HTML)
        self.assertIn(':aria-valuenow="progressPercent"', DASHBOARD_HTML)
        self.assertIn("Le temps est compté pendant que la page est active.", DASHBOARD_HTML)

    def test_daily_review_action_opens_a_course_scoped_flashcard_session(self):
        action_start = DASHBOARD_HTML.index("        async openPlanAction(action) {")
        action_end = DASHBOARD_HTML.index("        renderSpiderChart() {", action_start)
        action_method = DASHBOARD_HTML[action_start:action_end]
        review_start = action_method.index("if (action.action === 'review')")
        review_end = action_method.index("await this.show(nodeId);", review_start)
        review_action = action_method[review_start:review_end]

        self.assertIn("this.reviewNodeId = nodeId;", review_action)
        self.assertIn("this.reviewDaysSince = Number(action.days_since) || null;", review_action)
        self.assertIn("mode: 'all'", review_action)
        self.assertIn("await this.setTab('memo');", review_action)

        self.assertIn("reviewNodeId: null, reviewDaysSince: null", DASHBOARD_HTML)
        build_start = DASHBOARD_HTML.index("        buildDeck() {")
        build_end = DASHBOARD_HTML.index("        clearGuidedReview()", build_start)
        build_method = DASHBOARD_HTML[build_start:build_end]
        self.assertIn("String(c.node_id) === String(this.reviewNodeId)", build_method)
        self.assertIn("if (!this.reviewNodeId && f.mode === 'due')", build_method)

        clear_start = DASHBOARD_HTML.index("        clearGuidedReview() {")
        clear_end = DASHBOARD_HTML.index("        markFlashcard(known)", clear_start)
        guided_methods = DASHBOARD_HTML[clear_start:clear_end]
        self.assertIn("this.reviewNodeId = null;", guided_methods)
        self.assertIn("this.cardFilter = { ...this.cardFilter, module: 'all', level: 'all', mode: 'due' };", guided_methods)
        self.assertIn("await this.setTab('tree');", guided_methods)
        self.assertIn("await this.show(nodeId);", guided_methods)

        self.assertIn('x-show="reviewNodeId"', DASHBOARD_HTML)
        self.assertIn("Révision guidée du plan du jour", DASHBOARD_HTML)
        self.assertIn("Dernière validation il y a ' + reviewDaysSince", DASHBOARD_HTML)
        self.assertIn(':disabled="reviewNodeId"', DASHBOARD_HTML)
        self.assertIn('@click="openGuidedReviewLesson()"', DASHBOARD_HTML)
        self.assertIn("Aucune carte mémorisée pour ce cours pour le moment.", DASHBOARD_HTML)

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
        self.assertIn("await this.setTab('challenges')", DASHBOARD_HTML)
        self.assertIn("await this.startChallenge(nodeId)", DASHBOARD_HTML)
        self.assertIn("if (action.action === 'lab')", DASHBOARD_HTML)
        self.assertIn("await this.openLab(nodeId)", DASHBOARD_HTML)
        self.assertIn("lab: status === 'available'", DASHBOARD_HTML)
        self.assertIn("label: 'Lab à lancer'", DASHBOARD_HTML)
        self.assertIn("label: 'Lab à poursuivre'", DASHBOARD_HTML)
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
        self.assertIn("expectedSummary: challenge.expected_summary", DASHBOARD_HTML)
        self.assertNotIn("expected: ch.expected_topology", DASHBOARD_HTML)
        self.assertIn("challengeResult.attemptRecorded", DASHBOARD_HTML)
        self.assertIn("this.challengesDone = [...this.challengesDone, ch.id]", DASHBOARD_HTML)
        self.assertIn("LS.set('challenges-done', this.challengesDone)", DASHBOARD_HTML)
        self.assertIn("Récompenses :", DASHBOARD_HTML)
        self.assertIn("const refreshAlreadyCelebrated = Array.isArray(seenBadgesBeforeRefresh)", DASHBOARD_HTML)
        self.assertIn("if (!refreshAlreadyCelebrated) this.celebrate();", DASHBOARD_HTML)
        self.assertIn("Badge « Architecte » débloqué.", DASHBOARD_HTML)
        self.assertIn("challengeResult.xpGained > 0", DASHBOARD_HTML)
        self.assertIn("challengeResult.coinsGained > 0", DASHBOARD_HTML)
        self.assertIn("Number(result.coins_gained) || 0", DASHBOARD_HTML)
        self.assertIn("Badges débloqués", DASHBOARD_HTML)
        self.assertIn("const passed = !timeout && score >= this.challenge.minScore;", DASHBOARD_HTML)
        self.assertIn(':disabled="!c.builtin && c.status === \'locked\'"', DASHBOARD_HTML)
        self.assertIn("app.challengeState = function (c)", DASHBOARD_HTML)
        self.assertIn("if (state === 'validated') return '✅ Validé dans le parcours · rejouable'", DASHBOARD_HTML)
        self.assertIn("if (state === 'in_progress') return '↻ Tentative enregistrée · à poursuivre'", DASHBOARD_HTML)

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
        start = DASHBOARD_HTML.rindex("async openLab(id, openInNewTab = true) {")
        end = DASHBOARD_HTML.index("        isLabDone(id)", start)
        open_lab_method = DASHBOARD_HTML[start:end]

        self.assertIn("fetch(`/api/lab/v2/${encodeURIComponent(nodeId)}`)", open_lab_method)
        self.assertIn("async openLab(id, openInNewTab = true)", open_lab_method)
        self.assertIn("navigate(`/?openLegacyLab=${encodeURIComponent(nodeId)}`)", open_lab_method)
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
        self.assertIn("themeIsActive(id) { return this.activeThemeId === id; }", DASHBOARD_HTML)
        sync_start = DASHBOARD_HTML.index("        syncTheme() {")
        sync_end = DASHBOARD_HTML.index("        closeThemeOnOutside(event)", sync_start)
        sync = DASHBOARD_HTML[sync_start:sync_end]
        self.assertIn("this.themes.some(x => x.id === stored)", sync)
        self.assertIn("root.dataset.theme = id;", sync)
        self.assertIn("this.theme = id;", sync)
        self.assertIn("this.activeThemeId = id;", sync)
        self.assertIn("localStorage.setItem('skilltree-theme2', id)", sync)
        self.assertIn("@click=\"setTheme(t.id)\"", DASHBOARD_HTML)
        self.assertIn(":aria-pressed=\"themeIsActive(t.id)\"", DASHBOARD_HTML)
        self.assertIn("@click=\"themeMenuOpen = true; settingsMenuOpen = false; notificationsOpen = false; profileMenuOpen = false\"", DASHBOARD_HTML)

    def test_theme_choice_uses_one_reactive_id_and_remains_visible_after_selection(self):
        self.assertIn("activeThemeId: document.documentElement.dataset.theme || 'graphite'", DASHBOARD_HTML)
        self.assertIn("themeIsActive(id) { return this.activeThemeId === id; }", DASHBOARD_HTML)
        self.assertIn('@click.outside="themeMenuOpen = false"', DASHBOARD_HTML)
        self.assertIn('@keydown.escape.window="themeMenuOpen = false"', DASHBOARD_HTML)
        set_start = DASHBOARD_HTML.index("        setTheme(id) {")
        set_end = DASHBOARD_HTML.index("        toggleTheme()", set_start)
        set_method = DASHBOARD_HTML[set_start:set_end]
        self.assertIn("this.activeThemeId = id;", set_method)
        self.assertNotIn("this.themeMenuOpen = false;", set_method)

    def test_active_modals_close_on_outside_click_without_interrupting_inside_actions(self):
        self.assertIn('@click.window.capture="closeModalsOnOutside($event); closeThemeOnOutside($event)"', DASHBOARD_HTML)
        start = DASHBOARD_HTML.index("closeModalsOnOutside(event) {")
        end = DASHBOARD_HTML.index("closeThemeOnOutside(event)", start)
        close_method = DASHBOARD_HTML[start:end]
        self.assertIn('target.closest(\'[role="dialog"][aria-modal="true"], [data-modal-content]\')', close_method)
        self.assertIn("if (this.open) this.close();", close_method)
        self.assertIn("if (this.mobileSearchOpen) this.closeMobileSearch();", close_method)
        self.assertIn("if (this.shopOpen) this.shopOpen = false;", close_method)
        self.assertIn("if (this.diplomaView) this.diplomaView = null;", close_method)
        self.assertIn("if (this.modMgrOpen) this.modMgrOpen = false;", close_method)
        self.assertGreaterEqual(DASHBOARD_HTML.count('data-modal-content role="dialog" aria-modal="true"'), 3)
        self.assertIn('@click.self="closeMobileSearch()"', DASHBOARD_HTML)
        self.assertIn('@click.self="shopOpen = false"', DASHBOARD_HTML)

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

    def test_settings_menu_actions_match_their_names_and_close_the_menu(self):
        self.assertIn("Changer de thème", DASHBOARD_HTML)
        self.assertIn('@click="themeMenuOpen = true; settingsMenuOpen = false; notificationsOpen = false; profileMenuOpen = false"', DASHBOARD_HTML)
        self.assertIn("Recharger les données", DASHBOARD_HTML)
        self.assertIn('@click="reloadContent(); settingsMenuOpen = false"', DASHBOARD_HTML)
        self.assertIn("Gérer les modules et niveaux", DASHBOARD_HTML)
        self.assertIn('@click="modMgrOpen = true; settingsMenuOpen = false"', DASHBOARD_HTML)
        self.assertIn("Exporter mes données (JSON)", DASHBOARD_HTML)
        self.assertIn('@click="exportData(); settingsMenuOpen = false"', DASHBOARD_HTML)
        export_start = DASHBOARD_HTML.index("        app.exportData = function () {")
        export_end = DASHBOARD_HTML.index("        app._allowChallengeClear = false;", export_start)
        self.assertIn("preferences:", DASHBOARD_HTML[export_start:export_end])
        self.assertIn("progress:", DASHBOARD_HTML[export_start:export_end])


    def test_flashcard_loading_distinguishes_api_errors_from_an_empty_deck(self):
        start = DASHBOARD_HTML.rindex("        async loadFlashcards() {")
        end = DASHBOARD_HTML.index("        buildDeck() {", start)
        method = DASHBOARD_HTML[start:end]
        self.assertIn("if (!r.ok) throw new Error", method)
        self.assertIn("Array.isArray(d.cards)", method)
        self.assertIn("this.cardLoadError =", method)
        self.assertIn("finally", method)

        memo_start = DASHBOARD_HTML.index('<section x-show="tab === \'memo\'"')
        memo_end = DASHBOARD_HTML.index("<!-- ============ ONGLET DIAGNOSTIC ============ -->", memo_start)
        memo = DASHBOARD_HTML[memo_start:memo_end]
        self.assertIn('x-show="flashcardsLoading"', memo)
        self.assertIn('x-show="cardLoadError"', memo)
        self.assertIn('role="alert" aria-live="polite"', memo)
        self.assertIn('@click="loadFlashcards()"', memo)
        self.assertIn('x-if="!flashcardsLoading && !cardLoadError && currentFlashcard"', memo)
        self.assertIn('x-if="!flashcardsLoading && !cardLoadError && !currentFlashcard"', memo)


    def test_dashboard_statistics_never_present_unloaded_defaults_as_real_values(self):
        self.assertIn(
            'x-text="streakLoaded ? streakDays : \'—\'"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            'x-text="userStatsLoaded ? userStats.total_xp : \'—\'"',
            DASHBOARD_HTML,
        )
        # The compact header and the main dashboard should use the same loaded flags.
        self.assertIn(
            'x-text="userStatsLoaded ? `${userStats.total_xp} XP` : \'— XP\'"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            'x-text="streakLoaded ? streakDays : \'—\'"',
            DASHBOARD_HTML,
        )


    def test_radar_distinguishes_api_failure_from_a_genuinely_empty_history(self):
        stats_start = DASHBOARD_HTML.index('<section x-show="tab === \'stats\'"')
        stats_end = DASHBOARD_HTML.index('<!-- ============ ONGLET RÉVISIONS ============ -->', stats_start)
        stats_markup = DASHBOARD_HTML[stats_start:stats_end]

        self.assertIn('x-show="dashboardDataErrors.stats"', stats_markup)
        self.assertIn("Cela ne signifie pas que ta progression est vide.", stats_markup)
        self.assertIn('@click="loadStats()"', stats_markup)
        self.assertIn(
            'x-show="!statsLoading && !dashboardDataErrors.stats && !radarHasData()"',
            stats_markup,
        )
        self.assertIn(
            'x-show="!statsLoading && !dashboardDataErrors.stats && radarHasData() && !radarHasPositiveRate()"',
            stats_markup,
        )


    def test_dashboard_progress_uses_placeholders_when_initial_tree_load_fails(self):
        self.assertIn(
            'x-text="loading || (treeError && !nodes.length) ? \'—\' : progress"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            'x-text="loading || (treeError && !nodes.length) ? \'—\' : validated"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            'x-text="loading || (treeError && !nodes.length) ? \'—\' : total"',
            DASHBOARD_HTML,
        )
        self.assertIn(
            "stats?.totals ? stats.totals.validated + ' / ' + stats.totals.nodes : (loading || (treeError && !nodes.length) ? '—' : validated + ' / ' + total)",
            DASHBOARD_HTML,
        )


    def test_revision_access_is_visible_from_dashboard_and_navigation(self):
        nav_start = DASHBOARD_HTML.index("const NAV_ITEMS = [")
        nav_end = DASHBOARD_HTML.index("/* Scénarios de diagnostic intégrés", nav_start)
        nav_items = DASHBOARD_HTML[nav_start:nav_end]

        self.assertIn("{ id: 'memo', label: 'Révisions', title: 'Révisions espacées'", nav_items)
        self.assertIn("Ouvrir les révisions espacées", DASHBOARD_HTML)
        self.assertIn("setTab('memo')", DASHBOARD_HTML)
        self.assertIn("<!-- ============ ONGLET RÉVISIONS ============ -->", DASHBOARD_HTML)
        self.assertIn("Révisions espacées", DASHBOARD_HTML)
        # The revisions section remains accessible even when the server has no review action due today.
        self.assertIn("même lorsqu’aucune révision n’est encore due dans le plan du jour", DASHBOARD_HTML)
        self.assertIn("['tree','labs','exam','challenges','memo','diagnostic','stats']", DASHBOARD_HTML)
        self.assertIn("grid-template-columns: repeat(7, minmax(0,1fr))", DASHBOARD_HTML)
        self.assertIn("item.id === 'memo' ? 'Réviser' : item.label", DASHBOARD_HTML)

    def test_topology_navigation_is_replaced_by_challenges_and_lab_workspace_is_independent(self):
        self.assertIn("tab === 'challenges'", DASHBOARD_HTML)
        self.assertIn("{ id: 'challenges', label: 'Défis', title:", DASHBOARD_HTML)
        self.assertNotIn("id: 'topology', label: 'Topologie'", DASHBOARD_HTML)
        self.assertNotIn("tab === 'topology'", DASHBOARD_HTML)
        self.assertNotIn("Mode libre", DASHBOARD_HTML)
        self.assertIn("effacera les ${count} équipement(s) du défi précédent", DASHBOARD_HTML)
        self.assertNotIn("Sauvegarde-la si tu veux la conserver", DASHBOARD_HTML)

        challenge_start = DASHBOARD_HTML.index("<!-- ============ ONGLET DÉFIS ============ -->")
        challenge_end = DASHBOARD_HTML.index("<!-- ============ ONGLET LABS ============ -->", challenge_start)
        challenge_markup = DASHBOARD_HTML[challenge_start:challenge_end]
        self.assertIn('x-show="challenge" x-cloak class="grid gap-6 lg:grid-cols-[16rem_1fr]"', challenge_markup)
        self.assertNotIn("loadTopology()", challenge_markup)
        self.assertNotIn("saveTopology()", challenge_markup)
        self.assertIn("if (this.challenge) {", DASHBOARD_HTML)
        self.assertNotIn("if (name === 'challenges') { await this.$nextTick(); await this.initTopology(); }", DASHBOARD_HTML)
        self.assertNotIn("if (draft) { try { ed.import(draft); } catch (e) { } }", DASHBOARD_HTML)
        self.assertIn("await this.initTopology();", DASHBOARD_HTML)
        self.assertIn("await this.setTab('challenges')", DASHBOARD_HTML)

        self.assertIn("window.open('/lab.html', '_blank', 'noopener,noreferrer')", DASHBOARD_HTML)
        self.assertIn("Ouvrir l’atelier libre, sans scénario de cours", DASHBOARD_HTML)

    def test_server_challenge_loading_handles_api_errors_and_bounds_the_timer(self):
        start = DASHBOARD_HTML.index("        async startChallenge(id) {")
        end = DASHBOARD_HTML.index("        endChallenge()", start)
        loader = DASHBOARD_HTML[start:end]

        self.assertIn("encodeURIComponent(String(id))", loader)
        self.assertIn("if (!response.ok) throw new Error(data.detail || `Erreur HTTP ${response.status}`)", loader)
        self.assertIn("response.json().catch(() => ({}))", loader)
        self.assertLess(loader.index("if (!challenge.expected_summary)"), loader.index("this.clearTopology();"))
        self.assertIn("Number.isFinite(timeLimit) && timeLimit > 0", loader)
        self.assertIn("this.challengeLeft = Math.max(0, this.challengeLeft - 1)", loader)
        self.assertIn("if (!this.challenge || this.challengeResult)", loader)


    def test_challenge_catalog_filters_and_distinguishes_training_from_path_progress(self):
        self.assertIn('x-model="challengeQuery"', DASHBOARD_HTML)
        self.assertIn('x-model="challengeLevelFilter"', DASHBOARD_HTML)
        self.assertIn('x-model="challengeStateFilter"', DASHBOARD_HTML)
        self.assertIn('x-for="c in filteredChallengeNodes"', DASHBOARD_HTML)
        self.assertIn("app.challengeStatusLabel = function (c)", DASHBOARD_HTML)
        self.assertIn("Entraînement libre", DASHBOARD_HTML)
        self.assertIn("Parcours noté", DASHBOARD_HTML)
        self.assertIn("'challenge-fabric-aci-multi-tenant': 'expert'", DASHBOARD_HTML)
        self.assertIn("'challenge-vpn-inter-sites': 'intermediaire'", DASHBOARD_HTML)
        self.assertIn("'challenge-dual-isp-ha': 'expert'", DASHBOARD_HTML)
        self.assertIn("'challenge-it-ot-segmentation': 'expert'", DASHBOARD_HTML)
        self.assertIn("{ type: 'apic', label: 'Contrôleur APIC'", DASHBOARD_HTML)
        self.assertIn("{ type: 'plc', label: 'Automate industriel'", DASHBOARD_HTML)
        self.assertIn("plc: '<svg viewBox", DASHBOARD_HTML)

    def test_challenge_details_include_professional_context_guidance_and_debrief(self):
        self.assertIn('aria-labelledby="challenge-brief-title"', DASHBOARD_HTML)
        self.assertIn("Brief de mission", DASHBOARD_HTML)
        self.assertIn("Objectifs d’apprentissage", DASHBOARD_HTML)
        self.assertIn("Notions à mobiliser", DASHBOARD_HTML)
        self.assertIn("Mission, étape par étape", DASHBOARD_HTML)
        self.assertIn("Critères de réussite", DASHBOARD_HTML)
        self.assertIn("Ce que le vérificateur contrôle réellement", DASHBOARD_HTML)
        self.assertIn("Besoin d’un indice ? Afficher les indices progressifs", DASHBOARD_HTML)
        self.assertIn("À retenir après la tentative", DASHBOARD_HTML)
        self.assertIn("brief: challenge.brief || {}", DASHBOARD_HTML)
        self.assertIn("BUILTIN_CHALLENGE_BRIEFS[id] || {}", DASHBOARD_HTML)

    def test_course_reader_width_and_mobile_controls_are_persisted(self):
        self.assertIn('aria-labelledby="course-reader-title"', DASHBOARD_HTML)
        self.assertIn('aria-label="Commandes de lecture"', DASHBOARD_HTML)
        self.assertIn('aria-label="Réduire la taille du texte"', DASHBOARD_HTML)
        self.assertIn("lesson-width-comfortable", DASHBOARD_HTML)
        self.assertIn("lesson-width-wide", DASHBOARD_HTML)
        self.assertIn("toggleReadingWidth()", DASHBOARD_HTML)
        self.assertIn("readingWidth: this.readingWidth", DASHBOARD_HTML)
        self.assertIn("p.readingWidth === 'comfortable' || p.readingWidth === 'wide'", DASHBOARD_HTML)

if __name__ == "__main__":
    unittest.main()
