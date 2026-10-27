from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware

from app import api


class SecurityBaselineTests(unittest.TestCase):
    def test_cors_defaults_to_same_origin_and_without_credentials(self) -> None:
        cors = next(
            middleware for middleware in api.app.user_middleware
            if middleware.cls is CORSMiddleware
        )
        self.assertEqual(cors.options["allow_origins"], [])
        self.assertFalse(cors.options["allow_credentials"])
        self.assertEqual(cors.options["allow_methods"], ["GET", "POST"])
        self.assertEqual(cors.options["allow_headers"], ["Authorization", "Content-Type"])

    def test_cors_environment_accepts_only_explicit_http_origins(self) -> None:
        self.assertEqual(
            api._cors_origins_from_environment(" https://learn.example/,https://portal.example "),
            ["https://learn.example", "https://portal.example"],
        )
        self.assertEqual(
            api._cors_origins_from_environment("https://learn.example,https://learn.example/"),
            ["https://learn.example"],
        )
        for invalid in ("*", "https://learn.example/path", "javascript://example", "https://user:pass@example.com"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    api._cors_origins_from_environment(invalid)

    def test_quality_workflows_keep_pr_checks_read_only(self) -> None:
        root = Path(api.PROJECT_ROOT)
        quality = (root / ".github" / "workflows" / "quality-checks.yml").read_text(encoding="utf-8")
        publisher = (root / ".github" / "workflows" / "publish-lab-bundle.yml").read_text(encoding="utf-8")

        self.assertIn("permissions:\\n  contents: read", quality)
        self.assertNotIn("contents: write", quality)
        self.assertNotIn("Publish generated static bundle", quality)
        self.assertIn('branches: ["feature/lab-workspace"]', publisher)
        self.assertIn("pull_request:", publisher) is False
        self.assertIn("contents: write", publisher)

    def test_unapproved_origin_receives_no_cors_grant_and_security_headers_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.sqlite3"
            with patch.object(api, "DB_PATH", database_path):
                with TestClient(api.app) as client:
                    response = client.get("/api/tree")
                    preflight = client.options(
                        "/api/tree",
                        headers={
                            "Origin": "https://attacker.invalid",
                            "Access-Control-Request-Method": "POST",
                        },
                    )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["Referrer-Policy"], "strict-origin-when-cross-origin")
        self.assertEqual(response.headers["Permissions-Policy"], "camera=(), geolocation=(), payment=()")
        self.assertNotIn("access-control-allow-origin", preflight.headers)


if __name__ == "__main__":
    unittest.main()
