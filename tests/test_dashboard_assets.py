"""Regression checks for the split, versioned dashboard frontend assets."""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "static" / "index.html"
ASSET_DIR = ROOT / "static" / "assets"
ASSETS = (
    "skilltree-core.js",
    "skilltree-catalog.js",
    "skilltree-study.js",
    "skilltree-ux.js",
    "skilltree-polish.js",
    "skilltree-ui.css",
)


class DashboardAssetRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_dashboard_html_stays_compact(self):
        self.assertLess(
            HTML_PATH.stat().st_size,
            300_000,
            "The dashboard should not regress to embedding the large JS/CSS blocks.",
        )

    def test_external_assets_are_preloaded_and_versioned_by_content(self):
        for asset in ASSETS:
            with self.subTest(asset=asset):
                output = ASSET_DIR / asset
                self.assertTrue(output.is_file(), f"Missing generated dashboard asset: {asset}")
                content_hash = hashlib.sha256(output.read_bytes()).hexdigest()[:12]
                references = re.findall(
                    r"/assets/" + re.escape(asset) + r"\?v=([0-9a-f]{12})",
                    self.html,
                )
                # One preload plus one use in the page body/head.
                self.assertEqual(len(references), 2, f"Unexpected number of references for {asset}")
                self.assertEqual(set(references), {content_hash}, f"Stale content hash for {asset}")

                preload = f'href="/assets/{asset}?v={content_hash}"'
                self.assertIn(preload, self.html, f"{asset} must be preloaded")

                if asset.endswith(".js"):
                    use = f'src="/assets/{asset}?v={content_hash}"'
                    self.assertIn(use, self.html, f"{asset} must be used as a script")
                    self.assertLess(self.html.index(preload), self.html.index(use))
                else:
                    use = f'<link rel="stylesheet" href="/assets/{asset}?v={content_hash}">'
                    self.assertIn(use, self.html)
                    self.assertLess(self.html.index(preload), self.html.index(use))

    def test_tailwind_scans_the_extracted_javascript_sources(self):
        config = (ROOT / "static" / "tailwind.config.cjs").read_text(encoding="utf-8")
        self.assertIn("./app/main_ui/**/*.js", config)
        self.assertTrue((ROOT / "static" / "app.css").is_file())
        self.assertGreater((ROOT / "static" / "app.css").stat().st_size, 10_000)

    def test_versioned_assets_receive_immutable_cache_policy(self):
        api = (ROOT / "app" / "api.py").read_text(encoding="utf-8")
        self.assertIn('request.query_params.get("v", "")', api)
        self.assertIn('re.fullmatch(r"[0-9a-f]{12}", version)', api)
        self.assertIn('public, max-age=31536000, immutable', api)


if __name__ == "__main__":
    unittest.main()
