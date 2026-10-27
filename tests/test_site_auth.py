from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from app import api, auth


_TEST_PASSWORD = "SkillTree-test-password-7391"
_TEST_HASH = auth.create_password_hash(_TEST_PASSWORD, salt=bytes(range(16)))
_TEST_SECRET = "test-only-session-signing-secret-1234567890"


class SiteAuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        auth.reset_login_failures_for_tests()
        self.temporary = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(api, "DB_PATH", Path(self.temporary.name) / "skilltree.db")
        self.db_patch.start()
        self.env_patch = patch.dict(
            os.environ,
            {
                "SKILLTREE_REQUIRE_AUTH": "true",
                "SKILLTREE_AUTH_PASSWORD_HASH": _TEST_HASH,
                "SKILLTREE_AUTH_SECRET": _TEST_SECRET,
                "RENDER_SERVICE_ID": "",
            },
        )
        self.env_patch.start()
        self.client = TestClient(api.app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.env_patch.stop()
        self.db_patch.stop()
        self.temporary.cleanup()
        auth.reset_login_failures_for_tests()

    def _login(self) -> None:
        response = self.client.post("/api/auth/login", json={"password": _TEST_PASSWORD})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["authenticated"])

    def test_private_pages_and_api_require_a_signed_session(self) -> None:
        home = self.client.get("/", follow_redirects=False)
        self.assertEqual(home.status_code, 303)
        self.assertEqual(home.headers["location"], "/login.html")
        data = self.client.get("/api/tree")
        self.assertEqual(data.status_code, 401, data.text)
        labs = self.client.get("/api/lab/v2")
        self.assertEqual(labs.status_code, 401, labs.text)

        login_page = self.client.get("/login.html")
        self.assertEqual(login_page.status_code, 200, login_page.text)
        self.assertIn("Se connecter", login_page.text)

        self._login()
        status = self.client.get("/api/auth/status")
        self.assertEqual(status.status_code, 200, status.text)
        self.assertTrue(status.json()["authenticated"])
        tree = self.client.get("/api/tree")
        self.assertEqual(tree.status_code, 200, tree.text)
        self.assertEqual(self.client.get("/", follow_redirects=False).status_code, 200)

    def test_protected_lab_links_keep_their_destination_through_login(self) -> None:
        cases = (
            ("/?openTab=labs", "/?openTab=labs"),
            ("/?openLab=acl-debutant", "/?openLab=acl-debutant"),
            ("/lab.html?id=acl-debutant", "/lab.html?id=acl-debutant"),
        )
        for requested_url, expected_next in cases:
            with self.subTest(requested_url=requested_url):
                response = self.client.get(requested_url, follow_redirects=False)
                self.assertEqual(response.status_code, 303, response.text)
                login_url = urlsplit(response.headers["location"])
                self.assertEqual(login_url.path, "/login.html")
                self.assertEqual(parse_qs(login_url.query).get("next"), [expected_next])

    def test_login_rejects_wrong_password_and_uses_secure_cookie_attributes(self) -> None:
        failed = self.client.post("/api/auth/login", json={"password": "not the password"})
        self.assertEqual(failed.status_code, 401)
        self.assertEqual(failed.headers["cache-control"], "no-store")

        accepted = self.client.post("/api/auth/login", json={"password": _TEST_PASSWORD})
        self.assertEqual(accepted.status_code, 200, accepted.text)
        set_cookie = accepted.headers.get("set-cookie", "").lower()
        self.assertIn("httponly", set_cookie)
        self.assertIn("samesite=strict", set_cookie)
        self.assertIn("max-age=43200", set_cookie)
        self.assertNotIn("secure", set_cookie)  # TestClient uses local HTTP; Render forces Secure.

    def test_logout_removes_the_session(self) -> None:
        self._login()
        logout = self.client.post("/api/auth/logout")
        self.assertEqual(logout.status_code, 204)
        self.assertEqual(self.client.get("/api/tree").status_code, 401)

    def test_cross_origin_login_is_rejected(self) -> None:
        response = self.client.post(
            "/api/auth/login",
            json={"password": _TEST_PASSWORD},
            headers={"Origin": "https://attacker.example"},
        )
        self.assertEqual(response.status_code, 403, response.text)
        self.assertNotIn("set-cookie", response.headers)
        self.assertEqual(self.client.get("/api/tree").status_code, 401)

    def test_render_session_cookie_is_marked_secure(self) -> None:
        with patch.dict(os.environ, {"RENDER_SERVICE_ID": "srv-test"}):
            response = self.client.post(
                "/api/auth/login", json={"password": _TEST_PASSWORD}
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("secure", response.headers.get("set-cookie", "").lower())

    def test_authenticated_mutations_reject_a_foreign_origin(self) -> None:
        self._login()
        rejected = self.client.post(
            "/api/trigger-update",
            headers={"Origin": "https://attacker.example"},
        )
        self.assertEqual(rejected.status_code, 403, rejected.text)
        accepted = self.client.post(
            "/api/trigger-update",
            headers={"Origin": "http://testserver"},
        )
        self.assertEqual(accepted.status_code, 200, accepted.text)

    def test_signed_session_rejects_tampering_and_expired_tokens(self) -> None:
        token = auth.create_session_token(now=100_000)
        self.assertTrue(auth.verify_session_token(token, now=100_001))
        tampered = token[:-1] + ("0" if token[-1] != "0" else "1")
        self.assertFalse(auth.verify_session_token(tampered, now=100_001))
        self.assertFalse(
            auth.verify_session_token(
                token, now=100_000 + auth.AUTH_SESSION_TTL_SECONDS + 1
            )
        )

    def test_login_failure_tracker_locks_after_five_attempts(self) -> None:
        key = "auth-test-client"
        self.assertFalse(auth.login_is_limited(key, now=10_000))
        for offset in range(auth.LOGIN_MAX_FAILURES):
            auth.record_failed_login(key, now=10_000 + offset)
        self.assertTrue(auth.login_is_limited(key, now=10_010))
        self.assertFalse(
            auth.login_is_limited(key, now=10_004 + auth.LOGIN_WINDOW_SECONDS + 1)
        )

    def test_render_fails_closed_if_authentication_is_not_configured(self) -> None:
        with patch.dict(
            os.environ,
            {
                "RENDER_SERVICE_ID": "srv-test",
                "SKILLTREE_REQUIRE_AUTH": "",
                "SKILLTREE_AUTH_PASSWORD_HASH": "",
                "SKILLTREE_AUTH_SECRET": "",
            },
        ):
            status = self.client.get("/api/auth/status")
            self.assertTrue(status.json()["required"])
            self.assertFalse(status.json()["configured"])
            protected = self.client.get("/api/tree")
            self.assertEqual(protected.status_code, 503, protected.text)
            self.assertEqual(
                self.client.get("/", follow_redirects=False).headers["location"],
                "/login.html",
            )


if __name__ == "__main__":
    unittest.main()
