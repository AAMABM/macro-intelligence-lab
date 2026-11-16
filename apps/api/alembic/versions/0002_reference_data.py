"""reference data — regions, currencies, countries, data_sources, indicators

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- enums --------------------------------------------------------
    frequency = postgresql.ENUM(
        "daily", "weekly", "monthly", "quarterly", "annual",
        name="frequency", create_type=False,
    )
    indicator_category = postgresql.ENUM(
        "growth", "inflation", "labor", "rates", "external", "fiscal",
        "survey", "money",
        name="indicator_category", create_type=False,
    )
    frequency.create(op.get_bind(), checkfirst=True)
    indicator_category.create(op.get_bind(), checkfirst=True)

    # --- regions ------------------------------------------------------
    op.create_table(
        "regions",
        sa.Column("id", sa.SmallInteger, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.UniqueConstraint("code", name="uq_regions_code"),
    )

    # --- currencies ---------------------------------------------------
    op.create_table(
        "currencies",
        sa.Column("code", sa.String(3), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("symbol", sa.String(8)),
        sa.Column("decimals", sa.SmallInteger, server_default="2", nullable=False),
    )

    # --- countries ----------------------------------------------------
    op.create_table(
        "countries",
        sa.Column("id", sa.SmallInteger, primary_key=True, autoincrement=True),
        sa.Column("iso2", sa.String(2), nullable=False),
        sa.Column("iso3", sa.String(3), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column(
            "region_id",
            sa.SmallInteger,
            sa.ForeignKey("regions.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "currency_code",
            sa.String(3),
            sa.ForeignKey("currencies.code", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("flag_emoji", sa.String(8)),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.UniqueConstraint("iso2", name="uq_countries_iso2"),
        sa.UniqueConstraint("iso3", name="uq_countries_iso3"),
    )
    op.create_index("ix_countries_region", "countries", ["region_id"])

    # --- data_sources -------------------------------------------------
    op.create_table(
        "data_sources",
        sa.Column("id", sa.SmallInteger, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("homepage_url", sa.String(500)),
        sa.Column("license", sa.String(120)),
        sa.Column("refresh_cadence", sa.String(40)),
        sa.UniqueConstraint("code", name="uq_data_sources_code"),
    )

    # --- indicators ---------------------------------------------------
    op.create_table(
        "indicators",
        sa.Column("id", sa.SmallInteger, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("unit", sa.String(40)),
        sa.Column("frequency", frequency, nullable=False),
        sa.Column("category", indicator_category, nullable=False),
        sa.Column(
            "source_id",
            sa.SmallInteger,
            sa.ForeignKey("data_sources.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("higher_is_better", sa.Boolean, server_default="true", nullable=False),
        sa.Column("methodology_note", sa.Text),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.UniqueConstraint("code", name="uq_indicators_code"),
    )
    op.create_index("ix_indicators_category", "indicators", ["category"])


def downgrade() -> None:
    op.drop_index("ix_indicators_category", table_name="indicators")
    op.drop_table("indicators")
    op.drop_table("data_sources")
    op.drop_index("ix_countries_region", table_name="countries")
    op.drop_table("countries")
    op.drop_table("currencies")
    op.drop_table("regions")
    op.execute("DROP TYPE IF EXISTS indicator_category")
    op.execute("DROP TYPE IF EXISTS frequency")