"""Reference data repositories."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from macro_api.models.reference import Country, Currency, DataSource, Indicator, Region
from macro_api.repositories.base import Repository


class CountryRepository(Repository):
    async def list_active(self) -> list[Country]:
        stmt = (
            select(Country)
            .options(selectinload(Country.region), selectinload(Country.currency))
            .where(Country.is_active.is_(True))
            .order_by(Country.iso2)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_by_iso2(self, iso2: str) -> Country | None:
        stmt = (
            select(Country)
            .options(selectinload(Country.region), selectinload(Country.currency))
            .where(Country.iso2 == iso2.upper())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_region(self, region_id: int) -> Region | None:
        return await self.session.get(Region, region_id)

    async def get_currency(self, code: str) -> Currency | None:
        return await self.session.get(Currency, code)

class IndicatorRepository(Repository):
    async def list_active(self) -> list[Indicator]:
        stmt = (
            select(Indicator)
            .where(Indicator.is_active.is_(True))
            .order_by(Indicator.category, Indicator.code)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_by_code(self, code: str) -> Indicator | None:
        stmt = select(Indicator).where(Indicator.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_source(self, source_id: int) -> DataSource | None:
        return await self.session.get(DataSource, source_id)
