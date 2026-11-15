"""User service."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from macro_api.core.errors import ForbiddenError, NotFoundError, UnauthorizedError
from macro_api.models.identity import User, UserStatus
from macro_api.repositories.users import UserRepository
from macro_api.schemas.user import CurrentUser, UserDetail, UserRole, UserStatus as SchemaUserStatus

log = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def load_current_user(self, user_id: str) -> CurrentUser:
        user = await self.users.get_by_id(user_id)
        if user is None or user.deleted_at is not None:
            raise UnauthorizedError("Session is no longer valid.")
        if user.status != UserStatus.active:
            raise ForbiddenError("This account is suspended.")
        return CurrentUser(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=UserRole(user.role.value),
            status=SchemaUserStatus(user.status.value),
        )

    async def get_detail(self, user_id: str) -> UserDetail:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return self._to_detail(user)

    async def update_profile(
        self,
        user_id: str,
        *,
        display_name: str | None,
        avatar_url: str | None,
        bio: str | None,
    ) -> UserDetail:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        if display_name is not None:
            user.display_name = display_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        if bio is not None:
            user.bio = bio
        await self.session.commit()
        await self.session.refresh(user)
        return self._to_detail(user)

    @staticmethod
    def _to_detail(user: User) -> UserDetail:
        return UserDetail(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=UserRole(user.role.value),
            status=SchemaUserStatus(user.status.value),
            avatar_url=user.avatar_url,
            bio=user.bio,
            email_verified_at=user.email_verified_at,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
        )