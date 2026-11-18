"""Macro observations — the provenance backbone."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    desc,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from macro_api.models.base import Base


class IndicatorObservation(Base):
    __tablename__ = "indicator_observations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    indicator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("indicators.id", ondelete="RESTRICT"), nullable=False
    )
    country_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("countries.id", ondelete="RESTRICT"), nullable=False
    )
    period: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date | None] = mapped_column(Date)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    is_latest: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), nullable=False
    )
    is_preliminary: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False
    )
    source_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index(
            "uq_obs_latest",
            "indicator_id",
            "country_id",
            "period",
            unique=True,
            postgresql_where=text("is_latest"),
        ),
        Index(
            "uq_obs_revision",
            "indicator_id",
            "country_id",
            "period",
            "revision",
            unique=True,
        ),
        Index("ix_obs_country_indicator_period", "country_id", "indicator_id", desc("period")),
        Index("ix_obs_indicator_period", "indicator_id", desc("period")),
    )
