"""Alembic environment — async aware."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from macro_api.config import get_settings
from macro_api.models import Base  # noqa: F401 — registers metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", str(settings.database_url))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    url_str = config.get_main_option("sqlalchemy.url")
    parsed_url = make_url(url_str)
    
    connect_args = {}
    if parsed_url.drivername == "postgresql+asyncpg":
        # Fix: Convert query to dict to make it mutable
        query = dict(parsed_url.query)
        
        if "sslmode" in query:
            sslmode = query.pop("sslmode")
            if isinstance(sslmode, tuple):
                sslmode = sslmode[0]
            if sslmode != "disable":
                connect_args["ssl"] = sslmode
                
        if "channel_binding" in query:
            query.pop("channel_binding")
            
        # Reassign the modified query
        parsed_url = parsed_url.set(query=query)

    connectable = create_async_engine(
        parsed_url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())