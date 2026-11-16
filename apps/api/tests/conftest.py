"""Test fixtures — test against real Postgres, no SQLite.

Schema is defined by Alembic migrations (extensions, enums, tables).
Per-test isolation uses TRUNCATE, not DROP/CREATE — dropping tables would
drop the enums and extensions the migrations created.
"""

import os
from collections.abc import AsyncIterator

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from macro_api.config import get_settings
from macro_api.core import db as db_module
from macro_api.main import create_app


@pytest.fixture(scope="session", autouse=True)
def _migrate_once():
    """Apply migrations once per test session.

    Idempotent — if the DB is already at head, this is a no-op. On the first
    run against a fresh mil_test database, it installs pgcrypto/citext,
    creates user_role/user_status enums, and creates the five tables.
    """
    os.environ.setdefault("MIL_ENV", "development")
    os.environ.setdefault("MIL_LOG_LEVEL", "WARNING")
    os.environ.setdefault(
        "MIL_JWT_SECRET", "test-secret-that-is-at-least-32-chars-long"
    )
    os.environ.setdefault("MIL_CORS_ORIGINS", '["http://testserver"]')

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    yield


@pytest.fixture(autouse=True)
def _reset_engine_singleton():
    """Reset the cached Settings and module-level engine before each test.

    Ensures each test builds a fresh engine bound to the current
    MIL_DATABASE_URL. Without this, module imports would freeze the first
    test's connection settings.
    """
    get_settings.cache_clear()
    db_module._engine = None
    db_module._session_factory = None
    yield
    get_settings.cache_clear()
    db_module._engine = None
    db_module._session_factory = None


@pytest.fixture
async def engine() -> AsyncIterator:
    """Truncate all tables before each test, then yield the engine.

    TRUNCATE ... CASCADE handles FK order automatically, and
    RESTART IDENTITY resets any sequences (UUIDs don't need it but harmless).
    Schema is left intact — enums, extensions, and constraints survive.
    """
    eng = db_module.get_engine()
    async with eng.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE "
                "email_verification_tokens, password_reset_tokens, "
                "refresh_tokens, user_preferences, users "
                "RESTART IDENTITY CASCADE"
            )
        )
    yield eng
    await eng.dispose()


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    factory = db_module.get_session_factory()
    async with factory() as s:
        yield s


@pytest.fixture
async def client(engine) -> AsyncIterator[AsyncClient]:
    """HTTP client. Depends on ``engine`` so tables are clean and present."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as c:
        yield c