"""Test fixtures.

Uses SQLite (aiosqlite) for speed and cross-platform parity on Windows
developer machines. Postgres-specific types are monkey-patched to their
generic equivalents on the test engine only. CI runs an additional Postgres
integration pass via `docker compose`.

We accept the trade-off: SQLite won't catch Postgres-only constraint bugs
but it makes local iteration instant, and the migration-safety CI job runs
against real Postgres.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from macro_api.config import Settings, get_settings
from macro_api.core.db import get_session
from macro_api.main import create_app
from macro_api.models import Base
from macro_api.models.identity import User, UserPreferences, UserRole, UserStatus
from macro_api.core.security import hash_password


@pytest.fixture(autouse=True)
def _test_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Inject deterministic settings for every test."""
    monkeypatch.setenv("MIL_ENV", "development")
    monkeypatch.setenv("MIL_LOG_LEVEL", "WARNING")
    monkeypatch.setenv(
        "MIL_DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test"
    )
    monkeypatch.setenv("MIL_JWT_SECRET", "test-secret-that-is-at-least-32-chars-long")
    monkeypatch.setenv("MIL_CORS_ORIGINS", '["http://testserver"]')
    get_settings.cache_clear()


@pytest.fixture
async def engine():
    """Per-test in-memory SQLite engine with shared connection.

    The models use ``CITEXT``, ``JSONB``, and ``UUID``; on SQLite those
    types are unavailable. We use the base ``Base.metadata`` but let SQLAlchemy
    fall back to compatible types by using the dialect's type adaptation.
    """
    # SQLite doesn't support these PG types; the tables are created with
    # generic adaptation. For Sprint 1 tests we don't assert on type
    # semantics, only on ORM + routing behaviour.
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Adapt Postgres types for SQLite by re-registering models against a
    # temp metadata.
    from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON  # noqa: PLC0415
    from sqlalchemy import String, Text  # noqa: PLC0415
    from macro_api.models import identity as idmod  # noqa: PLC0415

    # Monkey-patch the column types at the SQLAlchemy type level.
    idmod.User.__table__.c.email.type = Text()
    idmod.User.__table__.c.id.type = String(36)
    idmod.UserPreferences.__table__.c.user_id.type = String(36)
    idmod.UserPreferences.__table__.c.default_dashboard_id.type = String(36)
    idmod.UserPreferences.__table__.c.notifications.type = SQLiteJSON()
    idmod.RefreshToken.__table__.c.id.type = String(36)
    idmod.RefreshToken.__table__.c.user_id.type = String(36)
    idmod.RefreshToken.__table__.c.family_id.type = String(36)
    idmod.RefreshToken.__table__.c.rotated_from_id.type = String(36)
    idmod.PasswordResetToken.__table__.c.id.type = String(36)
    idmod.PasswordResetToken.__table__.c.user_id.type = String(36)
    idmod.EmailVerificationToken.__table__.c.id.type = String(36)
    idmod.EmailVerificationToken.__table__.c.user_id.type = String(36)

    # Enums → String on SQLite
    from sqlalchemy import String as _S  # noqa: PLC0415
    idmod.User.__table__.c.role.type = _S(20)
    idmod.User.__table__.c.status.type = _S(20)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
async def session(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as s:
        yield s


@pytest.fixture
async def client(session_factory) -> AsyncIterator[AsyncClient]:
    app = create_app()

    async def override_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as s:
            try:
                yield s
            except Exception:
                await s.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(session: AsyncSession) -> User:
    from uuid import uuid4

    user = User(
        id=str(uuid4()),
        email="admin@example.com",
        password_hash=hash_password("AdminPassword123!ok"),
        display_name="Admin",
        role=UserRole.admin,
        status=UserStatus.active,
    )
    session.add(user)
    session.add(UserPreferences(user_id=user.id))
    await session.commit()
    return user


# Silence: Settings import is used indirectly via fixtures.
_ = Settings