"""Market schemas."""
from datetime import date
from decimal import Decimal

from macro_api.schemas.common import CamelModel


class MarketInstrumentSummary(CamelModel):
    id: int
    symbol: str
    name: str
    asset_class: str
    currency_code: str | None = None

class MarketPricePoint(CamelModel):
    price_date: date
    close_price: Decimal

class MarketSeriesResponse(CamelModel):
    symbol: str
    name: str
    points: list[MarketPricePoint]
