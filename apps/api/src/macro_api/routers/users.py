"""User routes."""

from fastapi import APIRouter, Request, status

from macro_api.core.envelope import Envelope, Meta
from macro_api.routers.deps import DB, CurrentUserDep, ResearchUserDep
from macro_api.schemas.user import UpdateProfileRequest, UserDetail
from macro_api.services.auth_service import AuthService
from macro_api.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _meta(request: Request) -> Meta:
    from datetime import UTC, datetime
    return Meta(request_id=request.state.request_id, as_of=datetime.now(UTC))


@router.get("/me", response_model=Envelope[UserDetail])
async def get_me(
    request: Request, user: CurrentUserDep, db: DB
) -> Envelope[UserDetail]:
    service = UserService(db)
    detail = await service.get_detail(user.id)
    return Envelope(data=detail, meta=_meta(request))


@router.patch("/me", response_model=Envelope[UserDetail])
async def update_me(
    payload: UpdateProfileRequest,
    request: Request,
    user: ResearchUserDep,
    db: DB,
) -> Envelope[UserDetail]:
    service = UserService(db)
    detail = await service.update_profile(
        user.id,
        display_name=payload.display_name,
        avatar_url=payload.avatar_url,
        bio=payload.bio,
    )
    return Envelope(data=detail, meta=_meta(request))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(user: ResearchUserDep, db: DB) -> None:
    """Soft-delete account and revoke all refresh tokens."""
    from datetime import UTC, datetime

    from macro_api.repositories.users import RefreshTokenRepository, UserRepository

    users = UserRepository(db)
    tokens = RefreshTokenRepository(db)
    record = await users.get_by_id(user.id)
    if record is not None:
        record.deleted_at = datetime.now(UTC)
        await tokens.revoke_all_for_user(user.id)
        await db.commit()


# AuthService import intentionally unused in Sprint 1 (password change in S2).
_ = AuthService
