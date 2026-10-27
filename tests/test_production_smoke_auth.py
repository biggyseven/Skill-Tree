from __future__ import annotations

import json
import os
import sys
import unittest
from http.cookiejar import Cookie, CookieJar
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from production_smoke_auth import PASSWORD_ENV, authenticated_opener


class _FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps({"success": True, "required": True, "authenticated": True}).encode("utf-8")


class _FakeOpener:
    def __init__(self, cookie_jar: CookieJar):
        self.cookie_jar = cookie_jar
        self.request = None

    def open(self, request, timeout=30):
        self.request = request
        self.cookie_jar.set_cookie(Cookie(
            version=0,
            name="skilltree_session",
            value="test-session",
            port=None,
            port_specified=False,
            domain="example.invalid",
            domain_specified=False,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=True,
            expires=None,
            discard=True,
            comment=None,
            comment_url=None,
            rest={"HttpOnly": None},
            rfc2109=False,
        ))
        return _FakeResponse()


class ProductionSmokeAuthTests(unittest.TestCase):
    def test_missing_secret_fails_closed_with_clear_guidance(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, PASSWORD_ENV):
                authenticated_opener("https://example.invalid")

    def test_login_uses_same_origin_and_returns_cookie_aware_opener(self) -> None:
        with patch.dict(os.environ, {PASSWORD_ENV: "test-only-password"}):
            def build_fake_opener(processor):
                return _FakeOpener(processor.cookiejar)

            with patch("production_smoke_auth.urllib.request.build_opener", side_effect=build_fake_opener):
                opener = authenticated_opener("https://example.invalid")
        request = opener.request
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Origin"), "https://example.invalid")
        self.assertEqual(request.get_header("Referer"), "https://example.invalid/login.html")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"password": "test-only-password"})
        self.assertTrue(any(cookie.name == "skilltree_session" for cookie in opener.cookie_jar))


if __name__ == "__main__":
    unittest.main()
