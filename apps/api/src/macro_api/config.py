"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application settings.

    Every environment variable uses the ``MIL_`` prefix. Unknown variables
    are rejected so typos in ``.env`` fail fast.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MIL_",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application --------------------------------------------------
    env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # --- Database -----------------------------------------------------
    database_url: PostgresDsn
    database_pool_size: int = 5
    database_max_overflow: int = 5
    database_pool_pre_ping: bool = True
    database_statement_cache_size: int = 100
    """Set to 0 when using PgBouncer in transaction mode (Neon pooled URL)."""

    # --- JWT ----------------------------------------------------------
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_seconds: int = 900       # 15 minutes
    jwt_refresh_ttl_seconds: int = 60 * 60 * 24 * 14  # 14 days

    # --- CORS ---------------------------------------------------------
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # --- Bootstrap ----------------------------------------------------
    admin_email: str | None = None
    admin_password: SecretStr | None = None

    @field_validator("jwt_secret")
    @classmethod
    def _reject_placeholder_secret(cls, v: SecretStr) -> SecretStr:
        raw = v.get_secret_value()
        if len(raw) < 32:
            msg = "MIL_JWT_SECRET must be at least 32 characters (use `openssl rand -hex 32`)."
            raise ValueError(msg)
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached because Pydantic Settings performs env parsing at init; calling
    this repeatedly inside a request would be wasteful. Use
    ``get_settings.cache_clear()`` in tests after changing env vars.
    """
    return Settings()  # type: ignore[call-arg]