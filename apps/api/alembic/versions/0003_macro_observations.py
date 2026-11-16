"""macro observations — provenance and vintage tracking

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "indicator_observations",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "indicator_id",
            sa.SmallInteger,
            sa.ForeignKey("indicators.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "country_id",
            sa.SmallInteger,
            sa.ForeignKey("countries.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("period", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date),
        sa.Column("value", sa.Numeric(20, 6), nullable=False),
        sa.Column("revision", sa.SmallInteger, server_default="0", nullable=False),
        sa.Column(
            "is_latest", sa.Boolean, server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "is_preliminary", sa.Boolean, server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "source_id",
            sa.SmallInteger,
            sa.ForeignKey("data_sources.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("source_ts", sa.DateTime(timezone=True)),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Exactly one is_latest row per (indicator, country, period)
    op.create_index(
        "uq_obs_latest",
        "indicator_observations",
        ["indicator_id", "country_id", "period"],
        unique=True,
        postgresql_where=sa.text("is_latest"),
    )
    # Uniqueness across revisions
    op.create_index(
        "uq_obs_revision",
        "indicator_observations",
        ["indicator_id", "country_id", "period", "revision"],
        unique=True,
    )
    # Hot read paths
    op.create_index(
        "ix_obs_country_indicator_period",
        "indicator_observations",
        ["country_id", "indicator_id", sa.text("period DESC")],
    )
    op.create_index(
        "ix_obs_indicator_period",
        "indicator_observations",
        ["indicator_id", sa.text("period DESC")],
    )


def downgrade() -> None:
    op.drop_table("indicator_observations")