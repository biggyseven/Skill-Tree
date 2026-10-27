"""Authenticated, read-only HTTP client for production smoke workflows.

The production site is private. Smoke tests must use a dedicated Actions secret and
must never disable or bypass the site's authentication middleware.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.cookiejar import CookieJar


PASSWORD_ENV = "SKILLTREE_PRODUCTION_SMOKE_PASSWORD"


def authenticated_opener(base_url: str, *, timeout: int = 30):
    """Log in with the dedicated Actions secret and return a cookie-aware opener."""
    password = os.environ.get(PASSWORD_ENV, "")
    if not password:
        raise RuntimeError(
            f"Missing GitHub Actions secret {PASSWORD_ENV}. Add it under repository "
            "Settings → Secrets and variables → Actions before running production smoke tests. "
            "Do not bypass production authentication."
        )

    base = base_url.rstrip("/")
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    request = urllib.request.Request(
        base + "/api/auth/login",
        data=json.dumps({"password": password}).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": base,
            "Referer": base + "/login.html",
        },
        method="POST",
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        # Do not include the request body or secret in error output.
        raise RuntimeError(
            f"Production smoke login failed with HTTP {error.code}; "
            f"verify the {PASSWORD_ENV} Actions secret."
        ) from None
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise RuntimeError(
            f"Production smoke login request failed ({type(error).__name__}); "
            "check production availability."
        ) from error

    if not isinstance(payload, dict) or payload.get("authenticated") is not True:
        raise RuntimeError(
            "Production smoke login did not return an authenticated session; "
            f"verify the {PASSWORD_ENV} Actions secret."
        )
    if not any(cookie.name == "skilltree_session" for cookie in cookie_jar):
        raise RuntimeError(
            "Production smoke login succeeded without the expected session cookie; "
            "check the production authentication response."
        )
    return opener
