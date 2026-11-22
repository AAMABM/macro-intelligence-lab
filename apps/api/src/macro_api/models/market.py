"""Market data models."""

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
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from macro_api.models.base import Base


class MarketInstrument(Base):
    __tablename__ = "market_instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(40), nullable=False)
    currency_code: Mapped[str | None] = mapped_column(String(3))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    prices: Mapped[list["MarketPriceDaily"]] = relationship(
        back_populates="instrument", cascade="all, delete-orphan"
    )


class MarketPriceDaily(Base):
    __tablename__ = "market_prices_daily"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("market_instruments.id", ondelete="CASCADE"), nullable=False
    )
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    high_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    low_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int | None] = mapped_column(BigInteger)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    instrument: Mapped[MarketInstrument] = relationship(back_populates="prices")

    __table_args__ = (
        UniqueConstraint(
            "instrument_id", "price_date", name="uq_market_prices_instrument_date"
        ),
        Index("ix_market_prices_instrument_date", "instrument_id", "price_date"),
    )
