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


if __name__ == "__main__":
    unittest.main()
