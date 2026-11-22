"""Market service."""
from sqlalchemy.ext.asyncio import AsyncSession

from macro_api.core.errors import NotFoundError
from macro_api.repositories.market import MarketRepository
from macro_api.schemas.market import MarketInstrumentSummary, MarketPricePoint, MarketSeriesResponse


class MarketService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MarketRepository(session)

    async def list_instruments(self) -> list[MarketInstrumentSummary]:
        instruments = await self.repo.list_instruments()
        return [
            MarketInstrumentSummary(
                id=i.id,
                symbol=i.symbol,
                name=i.name,
                asset_class=i.asset_class,
                currency_code=i.currency_code,
            )
            for i in instruments
        ]

    async def get_series(self, symbol: str) -> MarketSeriesResponse:
        instrument = await self.repo.get_series(symbol)
        if not instrument:
            raise NotFoundError(f"Market instrument {symbol} not found.")

        # Sort prices by date ascending for the chart
        sorted_prices = sorted(instrument.prices, key=lambda p: p.price_date)

        points = [
            MarketPricePoint(price_date=p.price_date, close_price=p.close_price)
            for p in sorted_prices
        ]

        return MarketSeriesResponse(symbol=instrument.symbol, name=instrument.name, points=points)
