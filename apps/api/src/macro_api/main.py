"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from macro_api import __version__
from macro_api.config import get_settings
from macro_api.core.db import dispose_engine
from macro_api.core.envelope import ErrorBody, ErrorEnvelope
from macro_api.core.errors import AppError, ValidationError
from macro_api.core.logging import configure_logging
from macro_api.middleware.access_log import AccessLogMiddleware
from macro_api.middleware.auth_context import AuthContextMiddleware
from macro_api.middleware.error_handler import ErrorHandlerMiddleware
from macro_api.middleware.request_id import RequestIDMiddleware
from macro_api.routers import auth, health, users


def _envelope_response(
    *,
    request: Request,
    status: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "") or ""
    body = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            details=details or {},
            request_id=request_id,
        )
    )
    return JSONResponse(status_code=status, content=body.model_dump(by_alias=True))


async def _handle_app_error(request: Request, exc: Exception) -> JSONResponse:
    # Registration on `AppError` guarantees the runtime type; the cast tells
    # mypy the same thing, since Starlette's handler type is invariant on
    # `Exception` and rejects narrower types otherwise.
    app_exc = cast("AppError", exc)
    return _envelope_response(
        request=request,
        status=app_exc.status_code,
        code=app_exc.code,
        message=app_exc.message,
        details=app_exc.details,
    )


async def _handle_validation_error(
    request: Request, exc: Exception
) -> JSONResponse:
    val_exc = cast("RequestValidationError", exc)
    errors: dict[str, list[str]] = {}
    for err in val_exc.errors():
        loc = ".".join(str(p) for p in err["loc"] if p != "body") or "body"
        errors.setdefault(loc, []).append(err["msg"])
    return _envelope_response(
        request=request,
        status=422,
        code=ValidationError.code,
        message=ValidationError.message,
        details=errors,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()

    api = FastAPI(
        title="Macro Intelligence Lab — API",
        version=__version__,
        docs_url="/v1/docs" if settings.env != "production" else None,
        redoc_url=None,
        openapi_url="/v1/openapi.json",
    )

    # Exception handlers on the inner app so AppError and validation errors
    # are converted to the platform envelope BEFORE ServerErrorMiddleware
    # turns them into a generic 500.
    api.add_exception_handler(AppError, _handle_app_error)
    api.add_exception_handler(RequestValidationError, _handle_validation_error)

    api.include_router(health.router, prefix="/v1")
    api.include_router(auth.router, prefix="/v1")
    api.include_router(users.router, prefix="/v1")

    app = FastAPI(
        title="Macro Intelligence Lab",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(AuthContextMiddleware)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIDMiddleware)

    app.mount("/api", api)
    return app


app = create_app()
