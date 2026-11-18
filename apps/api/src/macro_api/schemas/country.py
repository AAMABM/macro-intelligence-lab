"""Country schemas."""

from macro_api.schemas.common import CamelModel


class CountrySummary(CamelModel):
    id: int
    iso2: str
    iso3: str
    name: str
    flag_emoji: str | None = None
    region_code: str | None = None
    currency_code: str | None = None


class CountryDetail(CamelModel):
    id: int
    iso2: str
    iso3: str
    name: str
    flag_emoji: str | None = None
    region_code: str | None = None
    region_name: str | None = None
    currency_code: str | None = None
    currency_name: str | None = None
    is_active: bool
