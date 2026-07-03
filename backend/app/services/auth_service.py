import hashlib
from datetime import datetime, timezone

import jwt

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair
from app.schemas.user import UserCreate
from app.services.log_service import LogService


class AuthError(Exception):
    """Raised for any auth failure that should surface as a 401."""


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
        log_service: LogService,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.log_service = log_service

    async def register_user(self, data: UserCreate) -> User:
        if await self.user_repo.get_by_username(data.username) is not None:
            raise AuthError("username already registered")
        if await self.user_repo.get_by_email(data.email) is not None:
            raise AuthError("email already registered")
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
        )
        return await self.user_repo.add(user)

    async def authenticate_user(self, username: str, password: str) -> User:
        user = await self.user_repo.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("invalid username or password")
        return user

    async def _issue_tokens(self, user: User) -> TokenPair:
        access_token = create_access_token(user.id, role=user.role.value)
        refresh_token, jti, expires_at = create_refresh_token(user.id)
        await self.refresh_repo.add(
            RefreshToken(
                user_id=user.id,
                jti=jti,
                token_hash=_hash_token(refresh_token),
                expires_at=expires_at,
            )
        )
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def login(self, username: str, password: str) -> TokenPair:
        user = await self.authenticate_user(username, password)
        tokens = await self._issue_tokens(user)
        await self.log_service.log(action="LOGIN", user_id=user.id, message=f"user {user.username} logged in")
        return tokens

    async def refresh(self, refresh_token: str) -> TokenPair:
        record = await self._validate_refresh_token(refresh_token)
        user = await self.user_repo.get(record.user_id)
        if user is None:
            raise AuthError("user not found")
        record.revoked = True
        await self.refresh_repo.session.flush()
        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        record = await self._validate_refresh_token(refresh_token)
        await self.refresh_repo.revoke(record)

    async def _validate_refresh_token(self, refresh_token: str) -> RefreshToken:
        try:
            decoded = decode_token(refresh_token, expected_type="refresh")
        except jwt.InvalidTokenError as exc:
            raise AuthError("invalid refresh token") from exc

        record = await self.refresh_repo.get_by_jti(decoded.jti)
        if record is None or record.revoked:
            raise AuthError("refresh token revoked or unknown")
        if record.token_hash != _hash_token(refresh_token):
            raise AuthError("refresh token mismatch")
        if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise AuthError("refresh token expired")
        return record
