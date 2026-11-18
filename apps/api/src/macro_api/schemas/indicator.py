"""Indicator schemas."""

from macro_api.schemas.common import CamelModel
from datetime import date
from decimal import Decimal


class IndicatorSummary(CamelModel):
    id: int
    code: str
    name: str
    unit: str | None = None
    frequency: str
    category: str


class IndicatorDetail(CamelModel):
    id: int
    code: str
    name: str
    description: str | None = None
    unit: str | None = None
    frequency: str
    category: str
    source_code: str | None = None
    source_name: str | None = None
    higher_is_better: bool
    methodology_note: str | None = None
    is_active: bool


class ObservationPoint(CamelModel):
    period: date
    value: Decimal


class SeriesResponse(CamelModel):
    indicator_code: str
    country_iso2: str
    points: list[ObservationPoint]