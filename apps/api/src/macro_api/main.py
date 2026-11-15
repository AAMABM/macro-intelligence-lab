"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from macro_api import __version__
from macro_api.config import get_settings
from macro_api.core.db import dispose_engine
from macro_api.core.logging import configure_logging
from macro_api.middleware.access_log import AccessLogMiddleware
from macro_api.middleware.auth_context import AuthContextMiddleware
from macro_api.middleware.error_handler import ErrorHandlerMiddleware
from macro_api.middleware.request_id import RequestIDMiddleware
from macro_api.routers import auth, health, users


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()

    # Inner app hosts the /v1 namespace.
    api = FastAPI(
        title="Macro Intelligence Lab — API",
        version=__version__,
        docs_url="/v1/docs" if settings.env != "production" else None,
        redoc_url=None,
        openapi_url="/v1/openapi.json",
    )

    api.include_router(health.router, prefix="/v1")
    api.include_router(auth.router, prefix="/v1")
    api.include_router(users.router, prefix="/v1")

    # Outer app hosts middleware + mounts the API under /api.
    app = FastAPI(
        title="Macro Intelligence Lab",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    # Middleware order: outermost first.
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