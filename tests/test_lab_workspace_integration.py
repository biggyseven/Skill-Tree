"""Regression checks for the published React Flow Lab Workspace entrypoint.

These checks verify that the Vite build and FastAPI static mount agree on the
public /lab/ URL. A browser smoke test is still needed for end-to-end behavior.
"""
from pathlib import Path
import unittest

from app.db import connect, initialize
from app.lab_routes import seed_lab_v2_catalog


ROOT = Path(__file__).resolve().parents[1]
STATIC_LAB = ROOT / "static" / "lab"


class LabWorkspaceIntegrationTests(unittest.TestCase):
    def test_database_initialization_provisions_lab_workspace_v2_tables(self):
        conn = connect(":memory:")
        try:
            initialize(conn)
            tables = {
                row["name"]
                for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            self.assertIn("labs", tables)
            self.assertIn("lab_attempts", tables)

            lab_columns = {row["name"] for row in conn.execute('PRAGMA table_info("labs")')}
            self.assertTrue({
                "id", "title", "level", "module", "prompt", "objectives", "hints",
                "duration_min", "difficulty", "xp_reward", "badges", "schema_version",
                "definition_json", "migration_note",
            }.issubset(lab_columns))

            attempt_columns = {row["name"] for row in conn.execute('PRAGMA table_info("lab_attempts")')}
            self.assertTrue({
                "id", "lab_id", "user_id", "started_at", "finished_at", "passed",
                "config_snapshot", "check_result_json",
            }.issubset(attempt_columns))
        finally:
            conn.close()

    def test_startup_catalog_seed_imports_tracked_scenarios_idempotently(self):
        conn = connect(":memory:")
        try:
            initialize(conn)
            inserted = seed_lab_v2_catalog(conn)
            ids = {
                row["id"]
                for row in conn.execute("SELECT id FROM labs")
            }
            self.assertGreaterEqual(inserted, 7)
            self.assertIn("acl-debutant", ids)
            self.assertIn("vlan-trunk", ids)
            self.assertIn("secu-acl-intermediaire", ids)

            # The bootstrap is safe across repeated starts and does not overwrite
            # metadata that already exists in a user's persistent database.
            conn.execute("UPDATE labs SET title = ? WHERE id = ?", ("Titre conservé", "acl-debutant"))
            conn.commit()
            self.assertEqual(seed_lab_v2_catalog(conn), 0)
            title = conn.execute(
                "SELECT title FROM labs WHERE id = ?", ("acl-debutant",)
            ).fetchone()["title"]
            self.assertEqual(title, "Titre conservé")
        finally:
            conn.close()

    def test_vite_base_matches_the_published_static_mount(self):
        vite_config = (ROOT / "app" / "lab-workspace" / "vite.config.js").read_text(encoding="utf-8-sig")
        entrypoint = (STATIC_LAB / "index.html").read_text(encoding="utf-8")
        api_source = (ROOT / "app" / "api.py").read_text(encoding="utf-8")

        self.assertRegex(vite_config, r"\bbase\s*:\s*['\"]\/lab\/['\"]")
        self.assertIn('src="/lab/main.js"', entrypoint)
        self.assertIn('href="/lab/main.css"', entrypoint)
        self.assertTrue((STATIC_LAB / "main.js").is_file(), "Published Lab Workspace JavaScript bundle is missing")
        self.assertTrue((STATIC_LAB / "main.css").is_file(), "Published Lab Workspace CSS bundle is missing")
        self.assertIn('app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")', api_source)

    def test_free_workspace_is_blank_by_default_and_demo_is_explicit(self):
        app = (ROOT / "app" / "lab-workspace" / "src" / "App.jsx").read_text(encoding="utf-8-sig")
        store = (ROOT / "app" / "lab-workspace" / "src" / "store" / "useLabStore.js").read_text(encoding="utf-8-sig")
        brief = (ROOT / "app" / "lab-workspace" / "src" / "brief" / "BriefPanel.jsx").read_text(encoding="utf-8-sig")

        self.assertIn("if (demo === '1')", app)
        self.assertIn("if (!labId)", app)
        self.assertIn("loadFreeWorkspace()", app)
        self.assertIn("loadDemo()", app)
        self.assertIn("loadFreeWorkspace() {", store)
        self.assertIn("lab: { ...(definition || {}), id: labId }", store)
        self.assertIn("lab.hints.map((hint, i)", brief)
        self.assertIn('aria-label="Indices pour réussir"', brief)


    def test_equipment_and_cable_libraries_are_separate_and_published(self):
        app = (ROOT / "app" / "lab-workspace" / "src" / "App.jsx").read_text(encoding="utf-8-sig")
        palette = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "Palette.jsx").read_text(encoding="utf-8-sig")
        cables = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "CablePalette.jsx").read_text(encoding="utf-8-sig")
        static_entry = (STATIC_LAB / "index.html").read_text(encoding="utf-8")
        static_library_bundle = STATIC_LAB / "main.js"

        self.assertIn('data-library-tabs', app)
        self.assertIn('data-library-tab="equipment"', app)
        self.assertIn('data-library-tab="cables"', app)
        cable_catalog = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "cableCatalog.js").read_text(encoding="utf-8-sig")

        self.assertIn('Bibliothèque', palette)
        self.assertIn("import { CABLES, WIRELESS_LINK } from './cableCatalog.js';", cables)
        self.assertIn("CABLES.map(cable =>", cables)
        self.assertIn("CableCard cable={WIRELESS_LINK}", cables)
        self.assertIn('Cuivre droit RJ45', cable_catalog)
        self.assertIn('Cuivre croisé RJ45', cable_catalog)
        self.assertIn('Fibre optique', cable_catalog)
        self.assertIn("id: 'console'", cable_catalog)
        self.assertIn("id: 'wireless'", cable_catalog)
        self.assertTrue(static_library_bundle.is_file(), "Published Lab Workspace JavaScript bundle is missing")
        self.assertIn('src="/lab/main.js"', static_entry)
        bundle = static_library_bundle.read_text(encoding="utf-8")
        self.assertIn('data-library-tabs', bundle)
        self.assertIn('data-library-tab', bundle)
        self.assertIn('Cuivre droit', bundle)
        self.assertIn('Fibre optique', bundle)

    def test_cli_rebinds_to_current_device_and_submit_requires_fresh_check(self):
        cli = (ROOT / "app" / "lab-workspace" / "src" / "cli" / "CLITab.jsx").read_text(encoding="utf-8-sig")
        toolbar = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "TopologyToolbar.jsx").read_text(encoding="utf-8")
        bridge = (ROOT / "app" / "lab-workspace" / "src" / "bridge" / "alpineBridge.js").read_text(encoding="utf-8-sig")

        self.assertIn("parserRef.current.device = latestDevice", cli)
        self.assertIn("...(topologyChanged ? { checkResult: null } : {})", cli)
        self.assertIn("!checkResult", toolbar)
        self.assertIn("checkResult.ok === true", toolbar)
        self.assertIn("previousCheck.stale", bridge)
        self.assertIn("topologySnapshot", bridge)

    def test_locked_course_lab_allows_practice_but_blocks_submission_in_workspace(self):
        app = (ROOT / "app" / "lab-workspace" / "src" / "App.jsx").read_text(encoding="utf-8-sig")
        brief = (ROOT / "app" / "lab-workspace" / "src" / "brief" / "BriefPanel.jsx").read_text(encoding="utf-8-sig")
        toolbar = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "TopologyToolbar.jsx").read_text(encoding="utf-8")
        bridge = (ROOT / "app" / "lab-workspace" / "src" / "bridge" / "alpineBridge.js").read_text(encoding="utf-8-sig")

        self.assertIn("courseLocked: data.course_locked === true", app)
        self.assertIn("Laboratoire verrouillé — mode entraînement", brief)
        self.assertIn("practice_only", brief)
        self.assertIn("practice_only", toolbar)
        self.assertIn("const submitDisabled =", toolbar)
        submit_guard = toolbar[toolbar.index("const submitDisabled ="):]
        self.assertIn("lab?.courseLocked === true", submit_guard)

        check_handler = bridge[
            bridge.index("window.addEventListener('lab:check'"):
            bridge.index("window.addEventListener('lab:submit'")
        ]
        self.assertNotIn("courseLocked === true", check_handler)
        self.assertIn("window.addEventListener('lab:submit'", bridge)

    def test_free_workspace_and_demo_do_not_run_graded_checks(self):
        brief = (ROOT / "app" / "lab-workspace" / "src" / "brief" / "BriefPanel.jsx").read_text(encoding="utf-8-sig")
        toolbar = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "TopologyToolbar.jsx").read_text(encoding="utf-8")
        bridge = (ROOT / "app" / "lab-workspace" / "src" / "bridge" / "alpineBridge.js").read_text(encoding="utf-8-sig")

        self.assertIn("Atelier libre — non noté", brief)
        self.assertIn("Démonstration — non notée", brief)
        self.assertIn("lab?.sandbox === true", toolbar)
        self.assertIn("initial.lab.sandbox === true", bridge)
        self.assertIn("initial.lab.id === 'demo'", bridge)

    def test_workspace_submission_result_refreshes_dashboard_progress(self):
        dashboard = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        on_validated_start = dashboard.index("        onLabValidated(data) {")
        on_validated_end = dashboard.index("        checkRewards()", on_validated_start)
        on_validated_method = dashboard[on_validated_start:on_validated_end]
        self.assertIn("data.stale === true", on_validated_method)
        self.assertIn("data.sandbox === true", on_validated_method)

        bridge = (ROOT / "app" / "lab-workspace" / "src" / "bridge" / "alpineBridge.js").read_text(encoding="utf-8-sig")
        dashboard = (ROOT / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("window.opener.postMessage({ type, detail }, window.location.origin)", bridge)
        self.assertIn("emit('lab:submit-result', finalResult)", bridge)

        init_start = dashboard.index("        async init() {")
        init_end = dashboard.index("        // --- Préférences d'affichage du lecteur", init_start)
        init_method = dashboard[init_start:init_end]
        self.assertIn("if (event.origin !== window.location.origin) return;", init_method)
        self.assertIn("message.type === 'lab:submit-result' && message.detail", init_method)
        self.assertIn("this.onLabValidated(message.detail)", init_method)
        self.assertIn("this.refreshAll()", init_method)

        refresh_start = dashboard.index("        async refreshAll() {")
        refresh_end = dashboard.index("        async retryDashboardData()", refresh_start)
        refresh_method = dashboard[refresh_start:refresh_end]
        self.assertIn("await Promise.all([this.loadTree(), this.loadDailyPlan(), this.loadStreak(), this.loadUserStats(), this.loadDiplomas()])", refresh_method)

    def test_workspace_check_wraps_the_topology_for_the_check_request_schema(self):
        bridge = (ROOT / "app" / "lab-workspace" / "src" / "bridge" / "alpineBridge.js").read_text(encoding="utf-8-sig")
        schema = (ROOT / "app" / "lab_schema_v2.py").read_text(encoding="utf-8")

        self.assertIn("body: JSON.stringify({ topology: initial.topology })", bridge)
        self.assertIn("class CheckRequest(SchemaModel)", schema)
        self.assertIn("topology: Topology = Field(default_factory=Topology)", schema)

    def test_sandbox_status_is_preserved_and_rewards_are_visible_after_submission(self):
        app = (ROOT / "app" / "lab-workspace" / "src" / "App.jsx").read_text(encoding="utf-8-sig")
        bridge = (ROOT / "app" / "lab-workspace" / "src" / "bridge" / "alpineBridge.js").read_text(encoding="utf-8-sig")
        toolbar = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "TopologyToolbar.jsx").read_text(encoding="utf-8")

        self.assertIn("sandbox: data.sandbox === true", app)
        self.assertIn("initial.lab.sandbox === true", bridge)
        self.assertIn("persistSuccessfulLab(finalResult)", bridge)
        self.assertIn("const storageKey = 'st:labs-done';", bridge)
        self.assertIn("result.stale === true", bridge)
        self.assertIn("lab?.sandbox === true", toolbar)
        self.assertIn("Bac à sable — non noté", toolbar)
        self.assertIn("checkResult.xp_gained", toolbar)
        self.assertIn("checkResult.first_success", toolbar)
        self.assertIn("checkResult.course_attempt_recorded", toolbar)
        self.assertIn("Détails des vérifications", toolbar)
        self.assertIn('aria-label="Détails des vérifications"', toolbar)
        self.assertIn("checkResult.results.map((item, index)", toolbar)
        self.assertIn("item.passed ? 'text-[var(--emerald-400)]' : 'text-[var(--rose-400)]'", toolbar)
        self.assertIn("Badge(s) débloqué(s)", toolbar)

    def test_workspace_uses_single_panel_navigation_below_desktop_breakpoint(self):
        app = (ROOT / "app" / "lab-workspace" / "src" / "App.jsx").read_text(encoding="utf-8-sig")

        self.assertIn("const [mobilePane, setMobilePane] = useState('brief')", app)
        self.assertIn('aria-label="Panneaux du laboratoire"', app)
        self.assertIn("onClick={() => setMobilePane('brief')}", app)
        self.assertIn("onClick={() => setMobilePane('canvas')}", app)
        self.assertIn("onClick={() => setMobilePane('inspector')}", app)
        self.assertGreaterEqual(app.count("'hidden xl:flex'"), 2)
        self.assertIn('xl:hidden', app)

    def test_dashboard_uses_the_v2_route_before_legacy_fallback(self):
        dashboard = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        start = dashboard.rindex("async openLab(id, openInNewTab = false) {")
        end = dashboard.index("        isLabDone(id)", start)
        open_lab_method = dashboard[start:end]

        v2_check = open_lab_method.find("fetch(`/api/lab/v2/${encodeURIComponent(nodeId)}`)")
        workspace_route = open_lab_method.find("navigate(`/lab.html?id=${encodeURIComponent(nodeId)}`)")
        legacy_fallback = open_lab_method.find("await this.show(nodeId);")
        self.assertGreaterEqual(v2_check, 0)
        self.assertIn("const labPayload = await response.json();", open_lab_method)
        topology_check = open_lab_method.find("const topologyNodes = labPayload.initial_topology?.nodes?.length")
        self.assertGreaterEqual(topology_check, v2_check)
        self.assertIn("labPayload.initial_topology.nodes", open_lab_method)
        self.assertIn("labPayload.definition?.initial_topology?.nodes", open_lab_method)
        self.assertIn("Array.isArray(topologyNodes)", open_lab_method)
        self.assertIn("topologyNodes.length > 0", open_lab_method)
        self.assertGreater(workspace_route, topology_check)
        self.assertGreater(legacy_fallback, workspace_route)
        self.assertIn("labWindow.location.replace('/?openLab=' + encodeURIComponent(nodeId));", open_lab_method)
        self.assertIn("this.labWorkspaceFallbackId = null;", open_lab_method)
        self.assertNotIn("this.labWorkspaceFallbackId = nodeId;", open_lab_method)
        self.assertIn("if (openInNewTab && labWindow && !labWindow.closed)", open_lab_method)


    def test_standalone_workspace_route_resolves_entrypoint_from_project_root(self):
        api_source = (ROOT / "app" / "api.py").read_text(encoding="utf-8")
        entrypoint = ROOT / "lab.html"

        self.assertTrue(entrypoint.is_file(), "Standalone Lab Workspace HTML entrypoint is missing")
        self.assertIn('@app.get("/lab.html")', api_source)
        self.assertIn('return FileResponse(PROJECT_ROOT / "lab.html")', api_source)


    def test_course_lab_button_checks_v2_before_opening_and_prevents_legacy_redirect_loops(self):
        dashboard = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn(":href=\"labIndex[n.id]?.kind === 'workspace-v2' ? '/lab.html?id=' + encodeURIComponent(n.id)", dashboard)
        self.assertIn(":data-lab-kind=\"labIndex[n.id]?.kind === 'workspace-v2' ? 'workspace-v2' : 'legacy'\"", dashboard)
        self.assertIn('@click="openVisualLab()"', dashboard)
        self.assertIn("async openVisualLab()", dashboard)
        self.assertIn("payload.sandbox === true", dashboard)
        self.assertIn("!Array.isArray(topologyNodes)", dashboard)
        self.assertIn("labWorkspaceFallbackId === detail.id", dashboard)
        self.assertIn('x-if="hasVisualLab(detail.id)"', dashboard)
        self.assertIn('x-if="!hasVisualLab(detail.id)"', dashboard)
        self.assertIn("Ce laboratoire utilise actuellement le mode classique", dashboard)
        self.assertIn("🧪 Réessayer le Lab Workspace", dashboard)
        self.assertNotIn("Ce laboratoire n’a pas de scénario visuel v2 disponible", dashboard)
        self.assertNotIn(':disabled="labWorkspaceFallbackId === detail.id"', dashboard)
        self.assertNotIn(":href=\"'/?openLab=' + encodeURIComponent(detail.id)\"", dashboard)
        self.assertNotIn("@click=\"window.open('/lab.html?id=' + (detail?.id || ''), '_blank')\"", dashboard)
        self.assertIn("Ouvrir l’atelier libre, sans scénario de cours", dashboard)


if __name__ == "__main__":
    unittest.main(verbosity=2)
