"""Country service."""

from sqlalchemy.ext.asyncio import AsyncSession

from macro_api.core.errors import NotFoundError
from macro_api.models.reference import Country
from macro_api.repositories.reference import CountryRepository
from macro_api.schemas.country import CountryDetail, CountrySummary


class CountryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CountryRepository(session)

    async def list_countries(self) -> list[CountrySummary]:
        countries = await self.repo.list_active()
        return [self._to_summary(c) for c in countries]

    async def get_country(self, iso2: str) -> CountryDetail:
        country = await self.repo.get_by_iso2(iso2)
        if country is None:
            raise NotFoundError(f"Country {iso2} not found.")

        region_name: str | None = None
        if country.region_id is not None:
            region = await self.repo.get_region(country.region_id)
            region_name = region.name if region else None

        currency_name: str | None = None
        if country.currency_code is not None:
            currency = await self.repo.get_currency(country.currency_code)
            currency_name = currency.name if currency else None

        return CountryDetail(
            id=country.id,
            iso2=country.iso2,
            iso3=country.iso3,
            name=country.name,
            flag_emoji=country.flag_emoji,
            region_code=country.region.code if country.region else None,
            region_name=region_name,
            currency_code=country.currency_code,
            currency_name=currency_name,
            is_active=country.is_active,
        )

    @staticmethod
    def _to_summary(country: Country) -> CountrySummary:
        return CountrySummary(
            id=country.id,
            iso2=country.iso2,
            iso3=country.iso3,
            name=country.name,
            flag_emoji=country.flag_emoji,
            region_code=country.region.code if country.region else None,
            currency_code=country.currency_code,
        )
