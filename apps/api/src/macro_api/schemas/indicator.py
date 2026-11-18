"""Indicator schemas."""

from macro_api.schemas.common import CamelModel


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
