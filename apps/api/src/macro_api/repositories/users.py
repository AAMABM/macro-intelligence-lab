"""User and refresh-token repository."""

from datetime import UTC, datetime

from sqlalchemy import select, update

from macro_api.models.identity import (
    PasswordResetToken,
    RefreshToken,
    User,
    UserPreferences,
)
from macro_api.repositories.base import Repository


class UserRepository(Repository):
    async def get_by_id(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email.lower()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def add_preferences(self, prefs: UserPreferences) -> UserPreferences:
        self.session.add(prefs)
        await self.session.flush()
        return prefs

    async def touch_last_login(self, user_id: str, when: datetime | None = None) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=when or datetime.now(UTC))
        )
        await self.session.execute(stmt)

    async def update_password(self, user_id: str, new_hash: str) -> None:
        stmt = update(User).where(User.id == user_id).values(password_hash=new_hash)
        await self.session.execute(stmt)


class RefreshTokenRepository(Repository):
    async def add(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, token_id: str, when: datetime | None = None) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.id == token_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=when or datetime.now(UTC))
        )
        await self.session.execute(stmt)

    async def revoke_family(self, family_id: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)

    async def revoke_all_for_user(self, user_id: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)


class PasswordResetTokenRepository(Repository):
    async def add(self, token: PasswordResetToken) -> None:
        self.session.add(token)
        await self.session.flush()

    async def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_used(self, token_id: str) -> None:
        stmt = (
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(used_at=datetime.now(UTC))
        )
        await self.session.execute(stmt)
