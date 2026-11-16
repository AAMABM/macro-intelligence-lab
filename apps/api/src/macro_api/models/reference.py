"""Reference data: regions, currencies, countries, data sources, indicators."""

from enum import StrEnum

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from macro_api.models.base import Base


class Frequency(StrEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"


class IndicatorCategory(StrEnum):
    growth = "growth"
    inflation = "inflation"
    labor = "labor"
    rates = "rates"
    external = "external"
    fiscal = "fiscal"
    survey = "survey"
    money = "money"


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)

    countries: Mapped[list["Country"]] = relationship(back_populates="region")


class Currency(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(8))
    decimals: Mapped[int] = mapped_column(SmallInteger, server_default="2", nullable=False)

    countries: Mapped[list["Country"]] = relationship(back_populates="currency")


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    iso2: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
    iso3: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    region_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("regions.id", ondelete="RESTRICT")
    )
    currency_code: Mapped[str | None] = mapped_column(
        String(3), ForeignKey("currencies.code", ondelete="RESTRICT")
    )
    flag_emoji: Mapped[str | None] = mapped_column(String(8))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    region: Mapped[Region | None] = relationship(back_populates="countries")
    currency: Mapped[Currency | None] = relationship(back_populates="countries")

    __table_args__ = (Index("ix_countries_region", "region_id"),)


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    homepage_url: Mapped[str | None] = mapped_column(String(500))
    license: Mapped[str | None] = mapped_column(String(120))
    refresh_cadence: Mapped[str | None] = mapped_column(String(40))


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(40))
    frequency: Mapped[Frequency] = mapped_column(
        SAEnum(Frequency, name="frequency", native_enum=True, create_type=False),
        nullable=False,
    )
    category: Mapped[IndicatorCategory] = mapped_column(
        SAEnum(
            IndicatorCategory,
            name="indicator_category",
            native_enum=True,
            create_type=False,
        ),
        nullable=False,
    )
    source_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("data_sources.id", ondelete="RESTRICT")
    )
    higher_is_better: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    methodology_note: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    __table_args__ = (Index("ix_indicators_category", "category"),)
