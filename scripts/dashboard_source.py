"""Helpers for source-level checks against the dashboard's split frontend assets.

Build a virtual source view by putting extracted JS/CSS back at their original
HTML locations. Runtime tests still use the actual HTML/assets via the browser.
"""
from __future__ import annotations

import re
from pathlib import Path


SCRIPT_ASSETS = (
    "skilltree-core.js",
    "skilltree-catalog.js",
    "skilltree-study.js",
    "skilltree-ux.js",
    "skilltree-polish.js",
)


def load_dashboard_source(root: Path | None = None) -> str:
    """Return dashboard HTML with versioned JS/CSS references expanded to source."""
    project_root = root or Path(__file__).resolve().parents[1]
    html = (project_root / "static" / "index.html").read_text(encoding="utf-8")

    for asset in SCRIPT_ASSETS:
        source_path = project_root / "app" / "main_ui" / asset
        source = source_path.read_text(encoding="utf-8")
        pattern = re.compile(
            r'<script src="/assets/'
            + re.escape(asset)
            + r'\?v=[0-9a-f]{12}"></script>'
        )
        html, count = pattern.subn(lambda _match, source=source: "<script>\n" + source + "\n</script>", html, count=1)
        if count != 1:
            raise AssertionError(
                f"Expected exactly one versioned script reference for {asset}; found {count}"
            )

    css_path = project_root / "app" / "main_ui" / "skilltree-ui.css"
    css = css_path.read_text(encoding="utf-8")
    css_pattern = re.compile(
        r'<link rel="stylesheet" href="/assets/skilltree-ui\.css\?v=[0-9a-f]{12}">'
    )
    html, count = css_pattern.subn(lambda _match: "<style>\n" + css + "\n</style>", html, count=1)
    if count != 1:
        raise AssertionError(
            f"Expected one versioned dashboard stylesheet reference; found {count}"
        )
    return html
