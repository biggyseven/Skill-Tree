"""Regression checks for the published React Flow Lab Workspace entrypoint.

These checks verify that the Vite build and FastAPI static mount agree on the
public /lab/ URL. A browser smoke test is still needed for end-to-end behavior.
"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STATIC_LAB = ROOT / "static" / "lab"


class LabWorkspaceIntegrationTests(unittest.TestCase):
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

    def test_workspace_submission_result_refreshes_dashboard_progress(self):
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
        self.assertIn("await Promise.all([this.loadTree(), this.loadDailyPlan(), this.loadStreak(), this.loadUserStats()])", refresh_method)

    def test_sandbox_status_is_preserved_and_rewards_are_visible_after_submission(self):
        app = (ROOT / "app" / "lab-workspace" / "src" / "App.jsx").read_text(encoding="utf-8-sig")
        bridge = (ROOT / "app" / "lab-workspace" / "src" / "bridge" / "alpineBridge.js").read_text(encoding="utf-8-sig")
        toolbar = (ROOT / "app" / "lab-workspace" / "src" / "canvas" / "TopologyToolbar.jsx").read_text(encoding="utf-8")

        self.assertIn("sandbox: data.sandbox === true", app)
        self.assertIn("initial.lab.sandbox === true", bridge)
        self.assertIn("lab?.sandbox === true", toolbar)
        self.assertIn("Bac à sable — non noté", toolbar)
        self.assertIn("checkResult.xp_gained", toolbar)
        self.assertIn("checkResult.course_attempt_recorded", toolbar)
        self.assertIn("Badge(s) débloqué(s)", toolbar)

    def test_workspace_uses_single_panel_navigation_below_desktop_breakpoint(self):
        app = (ROOT / "app" / "lab-workspace" / "src" / "App.jsx").read_text(encoding="utf-8-sig")

        self.assertIn("const [mobilePane, setMobilePane] = useState('canvas')", app)
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
        sandbox_check = open_lab_method.find("if (!labPayload.sandbox)")
        self.assertGreater(sandbox_check, v2_check)
        self.assertGreater(workspace_route, sandbox_check)
        self.assertGreater(legacy_fallback, workspace_route)
        self.assertIn("if (openInNewTab && labWindow && !labWindow.closed) labWindow.close();", open_lab_method)


    def test_standalone_workspace_route_resolves_entrypoint_from_project_root(self):
        api_source = (ROOT / "app" / "api.py").read_text(encoding="utf-8")
        entrypoint = ROOT / "lab.html"

        self.assertTrue(entrypoint.is_file(), "Standalone Lab Workspace HTML entrypoint is missing")
        self.assertIn('@app.get("/lab.html")', api_source)
        self.assertIn('return FileResponse(PROJECT_ROOT / "lab.html")', api_source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
