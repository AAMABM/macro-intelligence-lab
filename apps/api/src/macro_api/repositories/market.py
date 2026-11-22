"""Market repository."""
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from macro_api.models.market import MarketInstrument
from macro_api.repositories.base import Repository

class MarketRepository(Repository):
    async def list_instruments(self) -> list[MarketInstrument]:
        stmt = select(MarketInstrument).where(MarketInstrument.is_active.is_(True)).order_by(MarketInstrument.symbol)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_series(self, symbol: str) -> MarketInstrument | None:
        stmt = (
            select(MarketInstrument)
            .options(selectinload(MarketInstrument.prices))
            .where(MarketInstrument.symbol == symbol)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()