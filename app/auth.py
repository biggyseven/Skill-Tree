"""Single-owner authentication primitives for the private Skill-Tree deployment.

The application currently stores progress in shared tables, so this module intentionally
implements a site-wide owner session rather than pretending to provide multi-user isolation.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import threading
import time
from collections import deque
from typing import Deque

AUTH_COOKIE_NAME = "skilltree_session"
AUTH_SESSION_TTL_SECONDS = 12 * 60 * 60
PASSWORD_HASH_ITERATIONS = 600_000
MIN_PASSWORD_HASH_ITERATIONS = 300_000
MAX_PASSWORD_HASH_ITERATIONS = 1_000_000
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_MAX_FAILURES = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60

_failed_logins: dict[str, Deque[float]] = {}
_login_lock = threading.Lock()


def auth_required() -> bool:
    """Enforce auth on Render, when explicitly requested, or when auth is configured locally."""
    required = os.environ.get("SKILLTREE_REQUIRE_AUTH", "").strip().lower()
    return (
        bool(os.environ.get("RENDER_SERVICE_ID"))
        or required in {"1", "true", "yes", "on"}
        or bool(os.environ.get("SKILLTREE_AUTH_PASSWORD_HASH"))
        or bool(os.environ.get("SKILLTREE_AUTH_SECRET"))
    )


def _password_hash_parts() -> tuple[int, bytes, bytes] | None:
    encoded = os.environ.get("SKILLTREE_AUTH_PASSWORD_HASH", "").strip()
    parts = encoded.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return None
    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        digest = bytes.fromhex(parts[3])
    except (TypeError, ValueError):
        return None
    if not MIN_PASSWORD_HASH_ITERATIONS <= iterations <= MAX_PASSWORD_HASH_ITERATIONS:
        return None
    if len(salt) < 16 or len(digest) != hashlib.sha256().digest_size:
        return None
    return iterations, salt, digest


def auth_configuration_ready() -> bool:
    """Return true only when both the password hash and a strong signing secret are valid."""
    secret = os.environ.get("SKILLTREE_AUTH_SECRET", "")
    return len(secret) >= 32 and _password_hash_parts() is not None


def create_password_hash(password: str, *, salt: bytes | None = None) -> str:
    """Create a PBKDF2 password hash for local setup tooling; never stores the password."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str) -> bool:
    parts = _password_hash_parts()
    if parts is None or not isinstance(password, str):
        return False
    iterations, salt, expected = parts
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def create_session_token(*, now: int | None = None) -> str:
    """Issue a signed, stateless owner session with a strict absolute expiry."""
    secret = os.environ.get("SKILLTREE_AUTH_SECRET", "")
    if len(secret) < 32:
        raise ValueError("SKILLTREE_AUTH_SECRET must contain at least 32 characters.")
    issued_at = int(time.time() if now is None else now)
    payload = f"v1:{issued_at}:{secrets.token_urlsafe(18)}".encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")
    signature = hmac.new(secret.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def verify_session_token(token: str | None, *, now: int | None = None) -> bool:
    if not token or not auth_configuration_ready():
        return False
    try:
        encoded, supplied_signature = token.rsplit(".", 1)
        secret = os.environ["SKILLTREE_AUTH_SECRET"].encode("utf-8")
        expected_signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_signature, supplied_signature):
            return False
        padded = encoded + "=" * (-len(encoded) % 4)
        payload = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        version, issued_text, nonce = payload.split(":", 2)
        issued_at = int(issued_text)
        current = int(time.time() if now is None else now)
        if version != "v1" or len(nonce) < 16:
            return False
        if issued_at > current + 60 or current - issued_at > AUTH_SESSION_TTL_SECONDS:
            return False
        return True
    except (KeyError, ValueError, UnicodeError, TypeError):
        return False


def login_is_limited(key: str, *, now: float | None = None) -> bool:
    current = time.time() if now is None else now
    with _login_lock:
        entries = _failed_logins.setdefault(key, deque())
        while entries and current - entries[0] > LOGIN_WINDOW_SECONDS:
            entries.popleft()
        return len(entries) >= LOGIN_MAX_FAILURES


def record_failed_login(key: str, *, now: float | None = None) -> None:
    current = time.time() if now is None else now
    with _login_lock:
        entries = _failed_logins.setdefault(key, deque())
        while entries and current - entries[0] > LOGIN_WINDOW_SECONDS:
            entries.popleft()
        entries.append(current)
        # Bound memory growth if random client addresses are seen.
        if len(_failed_logins) > 2048:
            for old_key in list(_failed_logins)[:512]:
                _failed_logins.pop(old_key, None)


def clear_login_failures(key: str) -> None:
    with _login_lock:
        _failed_logins.pop(key, None)


def reset_login_failures_for_tests() -> None:
    with _login_lock:
        _failed_logins.clear()
