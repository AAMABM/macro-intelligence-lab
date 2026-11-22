"""market data

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-21
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Instruments (S&P 500, Gold, etc.)
    op.create_table(
        "market_instruments",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("asset_class", sa.String(40), nullable=False), # equity, commodity, fx
        sa.Column("currency_code", sa.String(3), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.UniqueConstraint("symbol", name="uq_market_instruments_symbol"),
    )

    # 2. Daily Prices
    op.create_table(
        "market_prices_daily",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "instrument_id",
            sa.Integer,
            sa.ForeignKey("market_instruments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("price_date", sa.Date, nullable=False),
        sa.Column("open_price", sa.Numeric(18, 6), nullable=True),
        sa.Column("high_price", sa.Numeric(18, 6), nullable=True),
        sa.Column("low_price", sa.Numeric(18, 6), nullable=True),
        sa.Column("close_price", sa.Numeric(18, 6), nullable=False),
        sa.Column("volume", sa.BigInteger, nullable=True),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "instrument_id", "price_date", name="uq_market_prices_instrument_date"
        ),
    )
    op.create_index(
        "ix_market_prices_instrument_date",
        "market_prices_daily",
        ["instrument_id", "price_date"],
    )


def downgrade() -> None:
    op.drop_table("market_prices_daily")
    op.drop_table("market_instruments")