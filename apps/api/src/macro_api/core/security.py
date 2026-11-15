"""Password hashing and JWT helpers."""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, cast

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from macro_api.config import get_settings

_hasher = PasswordHasher()  # Argon2id default parameters per RFC 9106

ACCESS_TOKEN_TYPE: Literal["access"] = "access"
REFRESH_TOKEN_TYPE: Literal["refresh"] = "refresh"


# --- Password hashing ---------------------------------------------------

def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:  # malformed hash, etc.
        return False


# --- JWT -----------------------------------------------------------------

def create_access_token(
    *,
    user_id: str,
    role: str,
    email: str,
    ttl_seconds: int | None = None,
) -> tuple[str, datetime]:
    """Return (encoded_jwt, expires_at)."""
    settings = get_settings()
    now = datetime.now(UTC)
    ttl = ttl_seconds if ttl_seconds is not None else settings.jwt_access_ttl_seconds
    expires_at = now + timedelta(seconds=ttl)
    payload: dict[str, Any] = {
        "sub": user_id,
        "role": role,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(uuid.uuid4()),
        "typ": ACCESS_TOKEN_TYPE,
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_at


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT. Raises ``jwt.PyJWTError`` on failure."""
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "sub", "typ", "jti"]},
    )
    if payload.get("typ") != ACCESS_TOKEN_TYPE:
        msg = "Not an access token"
        raise jwt.InvalidTokenError(msg)
    return cast("dict[str, Any]", payload)


# --- Refresh tokens ------------------------------------------------------
# Refresh tokens are opaque random strings; only the SHA-256 hash is stored.

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# --- Misc ----------------------------------------------------------------

def generate_uuid() -> str:
    return str(uuid.uuid4())