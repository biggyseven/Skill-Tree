"""Keyboard regression checks for the Skill-Tree settings menu and desktop search."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


class SettingsMenuKeyboardRegressionTests(unittest.TestCase):
    def test_settings_menu_closes_on_escape(self):
        start = DASHBOARD_HTML.index('<div x-show="settingsMenuOpen"')
        end = DASHBOARD_HTML.index(">", start)
        settings_panel_tag = DASHBOARD_HTML[start:end]

        self.assertIn('@click.outside="settingsMenuOpen = false"', settings_panel_tag)
        self.assertIn('@keydown.escape.window="settingsMenuOpen = false"', settings_panel_tag)

    def test_desktop_search_escape_handler_remains_present(self):
        start = DASHBOARD_HTML.index('x-ref="searchBox"')
        end = DASHBOARD_HTML.index(">", start)
        desktop_search_input = DASHBOARD_HTML[start:end]

        self.assertIn(
            '@keydown.escape="searchOpen = false; $event.target.blur()"',
            desktop_search_input,
        )


if __name__ == "__main__":
    unittest.main()
