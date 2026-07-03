import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

import bcrypt
import jwt
from pydantic import BaseModel

from app.config import get_settings

settings = get_settings()

TokenType = Literal["access", "refresh"]


class DecodedToken(BaseModel):
    sub: int
    type: TokenType
    jti: str
    role: str | None = None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_token(user_id: int, token_type: TokenType, expires_delta: timedelta, role: str | None = None) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": now + expires_delta,
    }
    if role is not None:
        payload["role"] = role
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def create_access_token(user_id: int, role: str) -> str:
    token, _ = _create_token(
        user_id, "access", timedelta(minutes=settings.access_token_expire_minutes), role=role
    )
    return token


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    """Returns (token, jti, expires_at) so the caller can persist the jti/hash."""
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    token, jti = _create_token(user_id, "refresh", expires_delta)
    expires_at = datetime.now(timezone.utc) + expires_delta
    return token, jti, expires_at


def decode_token(token: str, expected_type: TokenType) -> DecodedToken:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"expected token type {expected_type!r}, got {payload.get('type')!r}")
    return DecodedToken(
        sub=int(payload["sub"]), type=payload["type"], jti=payload["jti"], role=payload.get("role")
    )
