"""Shared router dependencies."""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from macro_api.core.db import get_session
from macro_api.core.errors import ForbiddenError, UnauthorizedError
from macro_api.schemas.user import CurrentUser, UserRole
from macro_api.services.user_service import UserService

DB = Annotated[AsyncSession, Depends(get_session)]


async def _get_optional_user(request: Request, db: DB) -> CurrentUser | None:
    claims = getattr(request.state, "claims", None)
    if not claims:
        return None
    service = UserService(db)
    try:
        return await service.load_current_user(claims["sub"])
    except (UnauthorizedError, ForbiddenError):
        return None


async def get_current_user(
    user: Annotated[CurrentUser | None, Depends(_get_optional_user)],
) -> CurrentUser:
    if user is None:
        raise UnauthorizedError()
    return user


async def require_research_user(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    if user.role not in (UserRole.research_user, UserRole.admin):
        raise ForbiddenError("Research user role required.")
    return user


async def require_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    if user.role != UserRole.admin:
        raise ForbiddenError("Admin role required.")
    return user


OptionalUser = Annotated[CurrentUser | None, Depends(_get_optional_user)]
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
ResearchUserDep = Annotated[CurrentUser, Depends(require_research_user)]
AdminDep = Annotated[CurrentUser, Depends(require_admin)]