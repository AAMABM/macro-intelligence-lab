"""Authentication routes."""

from fastapi import APIRouter, Request, status

from macro_api.core.envelope import Envelope, Meta
from macro_api.routers.deps import DB, ResearchUserDep
from macro_api.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from macro_api.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _meta(request: Request) -> Meta:
    from datetime import UTC, datetime
    return Meta(request_id=request.state.request_id, as_of=datetime.now(UTC))


@router.post(
    "/register",
    response_model=Envelope[AuthResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest, request: Request, db: DB
) -> Envelope[AuthResponse]:
    service = AuthService(db)
    result = await service.register(
        email=payload.email,
        password=payload.password,
        display_name=payload.display_name,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )
    return Envelope(data=result, meta=_meta(request))


@router.post("/login", response_model=Envelope[AuthResponse])
async def login(
    payload: LoginRequest, request: Request, db: DB
) -> Envelope[AuthResponse]:
    service = AuthService(db)
    result = await service.login(
        email=payload.email,
        password=payload.password,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )
    return Envelope(data=result, meta=_meta(request))


@router.post("/refresh", response_model=Envelope[AuthResponse])
async def refresh(
    payload: RefreshRequest, request: Request, db: DB
) -> Envelope[AuthResponse]:
    service = AuthService(db)
    result = await service.refresh(
        refresh_token=payload.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )
    return Envelope(data=result, meta=_meta(request))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, db: DB) -> None:
    service = AuthService(db)
    await service.logout(refresh_token=payload.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(user: ResearchUserDep, db: DB) -> None:
    service = AuthService(db)
    await service.logout_all(user_id=user.id)


@router.post("/forgot", status_code=status.HTTP_204_NO_CONTENT)
async def forgot(payload: ForgotPasswordRequest, db: DB) -> None:
    service = AuthService(db)
    await service.forgot_password(email=payload.email)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset(payload: ResetPasswordRequest, db: DB) -> None:
    service = AuthService(db)
    await service.reset_password(token=payload.token, new_password=payload.new_password)


def _client_ip(request: Request) -> str | None:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None