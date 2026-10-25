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
        self.assertGreater(workspace_route, v2_check)
        self.assertGreater(legacy_fallback, workspace_route)
        self.assertIn("if (openInNewTab && labWindow && !labWindow.closed) labWindow.close();", open_lab_method)



if __name__ == "__main__":
    unittest.main(verbosity=2)
