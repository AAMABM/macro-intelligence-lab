"""Async SQLAlchemy engine and session management."""

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from macro_api.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_engine() -> AsyncEngine:
    settings = get_settings()
    url_str = str(settings.database_url)
    parsed_url = make_url(url_str)

    connect_args: dict[str, Any] = {}

    if parsed_url.drivername == "postgresql+asyncpg":
        query = dict(parsed_url.query)

        if "sslmode" in query:
            sslmode = query.pop("sslmode")
            if isinstance(sslmode, tuple):
                sslmode = sslmode[0]
            if sslmode != "disable":
                connect_args["ssl"] = sslmode

        if "channel_binding" in query:
            query.pop("channel_binding")

        parsed_url = parsed_url.set(query=query)

        connect_args["statement_cache_size"] = settings.database_statement_cache_size
        connect_args["server_settings"] = {"application_name": "mil-api"}

    return create_async_engine(
        parsed_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=settings.database_pool_pre_ping,
        pool_recycle=300,
        connect_args=connect_args,
        echo=False,
    )


def get_engine() -> AsyncEngine:
    """Return the process-wide engine, creating it lazily."""
    global _engine, _session_factory
    if _engine is None:
        _engine = _build_engine()
        _session_factory = async_sessionmaker(
            _engine, expire_on_commit=False, class_=AsyncSession
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory, initialising the engine if needed."""
    get_engine()  # ensure initialised
    assert _session_factory is not None
    return _session_factory


async def dispose_engine() -> None:
    """Close the engine's pool. Called from the app lifespan on shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a per-request session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
