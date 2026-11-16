"""Authentication service."""

import logging
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from zxcvbn import zxcvbn

from macro_api.config import get_settings
from macro_api.core.errors import (
    ConflictError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    NotFoundError,
    TokenExpiredError,
    UnauthorizedError,
    WeakPasswordError,
)
from macro_api.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from macro_api.models.identity import (
    PasswordResetToken,
    RefreshToken,
    User,
    UserPreferences,
    UserRole,
    UserStatus,
)
from macro_api.repositories.users import (
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    UserRepository,
)
from macro_api.schemas.auth import AuthResponse, TokenPair
from macro_api.schemas.user import UserDetail
from macro_api.schemas.user import UserRole as SchemaUserRole
from macro_api.schemas.user import UserStatus as SchemaUserStatus

log = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
        self.reset_tokens = PasswordResetTokenRepository(session)

    # --- Register --------------------------------------------------------

    async def register(
        self,
        *,
        email: str,
        password: str,
        display_name: str,
        user_agent: str | None,
        ip: str | None,
    ) -> AuthResponse:
        email_norm = email.strip().lower()

        # zxcvbn strength check (score 0-4; require 3+)
        strength = zxcvbn(password)
        if strength["score"] < 3:
            raise WeakPasswordError(details={"score": strength["score"]})

        if await self.users.email_exists(email_norm):
            raise EmailAlreadyRegisteredError()

        user = User(
            id=str(uuid4()),
            email=email_norm,
            password_hash=hash_password(password),
            display_name=display_name.strip(),
            role=UserRole.research_user,
            status=UserStatus.active,
        )
        await self.users.add(user)

        prefs = UserPreferences(user_id=user.id)
        await self.users.add_preferences(prefs)

        tokens = await self._issue_tokens(
            user=user, user_agent=user_agent, ip=ip, family_id=None, rotated_from_id=None
        )
        await self.session.commit()

        log.info("user_registered", extra={"user_id": user.id})
        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            access_expires_at=tokens.access_expires_at,
            user=self._to_detail(user),
        )

    # --- Login -----------------------------------------------------------

    async def login(
        self,
        *,
        email: str,
        password: str,
        user_agent: str | None,
        ip: str | None,
    ) -> AuthResponse:
        email_norm = email.strip().lower()
        user = await self.users.get_by_email(email_norm)
        # Constant-ish time: verify against a dummy hash if user missing, to
        # avoid user-enumeration via timing.
        if user is None:
            hash_password("dummy-password-for-timing")
            raise InvalidCredentialsError()
        if user.status != UserStatus.active or user.deleted_at is not None:
            raise InvalidCredentialsError()
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        tokens = await self._issue_tokens(
            user=user, user_agent=user_agent, ip=ip, family_id=None, rotated_from_id=None
        )
        await self.users.touch_last_login(user.id)
        await self.session.commit()

        log.info("user_login", extra={"user_id": user.id})
        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            access_expires_at=tokens.access_expires_at,
            user=self._to_detail(user),
        )

    # --- Refresh (rotation + theft detection) ----------------------------

    async def refresh(
        self,
        *,
        refresh_token: str,
        user_agent: str | None,
        ip: str | None,
    ) -> AuthResponse:
        token_hash = hash_refresh_token(refresh_token)
        stored = await self.refresh_tokens.get_by_hash(token_hash)
        if stored is None:
            raise UnauthorizedError("Invalid refresh token.")
        if stored.revoked_at is not None:
            # Replay of a rotated token => possible theft. Revoke the family.
            await self.refresh_tokens.revoke_family(stored.family_id)
            await self.session.commit()
            log.warning(
                "refresh_token_reuse_detected",
                extra={"user_id": stored.user_id, "family_id": stored.family_id},
            )
            raise UnauthorizedError("Session is no longer valid.")
        if stored.expires_at < datetime.now(UTC):
            raise TokenExpiredError()

        user = await self.users.get_by_id(stored.user_id)
        if user is None or user.status != UserStatus.active or user.deleted_at is not None:
            raise UnauthorizedError("Session is no longer valid.")

        # Rotate: revoke current, issue new in same family
        await self.refresh_tokens.revoke(stored.id)
        tokens = await self._issue_tokens(
            user=user,
            user_agent=user_agent,
            ip=ip,
            family_id=stored.family_id,
            rotated_from_id=stored.id,
        )
        await self.session.commit()

        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            access_expires_at=tokens.access_expires_at,
            user=self._to_detail(user),
        )

    # --- Logout ----------------------------------------------------------

    async def logout(self, *, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token)
        stored = await self.refresh_tokens.get_by_hash(token_hash)
        if stored is not None and stored.revoked_at is None:
            await self.refresh_tokens.revoke(stored.id)
            await self.session.commit()

    async def logout_all(self, *, user_id: str) -> None:
        await self.refresh_tokens.revoke_all_for_user(user_id)
        await self.session.commit()

    # --- Forgot / Reset --------------------------------------------------

    async def forgot_password(self, *, email: str) -> None:
        """Always succeeds silently — do not leak whether the email exists."""
        user = await self.users.get_by_email(email.strip().lower())
        if user is None or user.status != UserStatus.active:
            return
        raw = generate_refresh_token()
        token = PasswordResetToken(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=hash_refresh_token(raw),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        await self.reset_tokens.add(token)
        await self.session.commit()
        # Sprint 1: log the raw token. Sprint 2: send via email.
        log.info("password_reset_requested", extra={"user_id": user.id, "token": raw})

    async def reset_password(self, *, token: str, new_password: str) -> None:
        strength = zxcvbn(new_password)
        if strength["score"] < 3:
            raise WeakPasswordError(details={"score": strength["score"]})

        token_hash = hash_refresh_token(token)
        stored = await self.reset_tokens.get_by_hash(token_hash)
        if stored is None or stored.used_at is not None:
            raise UnauthorizedError("Invalid or expired reset token.")
        if stored.expires_at < datetime.now(UTC):
            raise TokenExpiredError("Reset token has expired.")

        await self.users.update_password(stored.user_id, hash_password(new_password))
        await self.reset_tokens.mark_used(stored.id)
        await self.refresh_tokens.revoke_all_for_user(stored.user_id)
        await self.session.commit()
        log.info("password_reset_completed", extra={"user_id": stored.user_id})

    # --- Internal --------------------------------------------------------

    async def _issue_tokens(
        self,
        *,
        user: User,
        user_agent: str | None,
        ip: str | None,
        family_id: str | None,
        rotated_from_id: str | None,
    ) -> TokenPair:
        settings = get_settings()
        access_token, access_expires_at = create_access_token(
            user_id=user.id,
            role=user.role.value,
            email=user.email,
        )
        raw_refresh = generate_refresh_token()
        refresh = RefreshToken(
            id=str(uuid4()),
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh),
            family_id=family_id or str(uuid4()),
            rotated_from_id=rotated_from_id,
            user_agent=user_agent,
            ip=ip,
            expires_at=datetime.now(UTC)
            + timedelta(seconds=settings.jwt_refresh_ttl_seconds),
        )
        await self.refresh_tokens.add(refresh)
        return TokenPair(
            access_token=access_token,
            refresh_token=raw_refresh,
            access_expires_at=access_expires_at,
        )

    @staticmethod
    def _to_detail(user: User) -> UserDetail:
        return UserDetail(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=SchemaUserRole(user.role.value),
            status=SchemaUserStatus(user.status.value),
            avatar_url=user.avatar_url,
            bio=user.bio,
            email_verified_at=user.email_verified_at,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
        )


__all__ = ["AuthService", "ConflictError", "NotFoundError"]
