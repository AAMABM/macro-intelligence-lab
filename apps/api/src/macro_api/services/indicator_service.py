"""Indicator service."""

from sqlalchemy.ext.asyncio import AsyncSession

from macro_api.core.errors import NotFoundError
from macro_api.models.reference import Indicator
from macro_api.repositories.observations import ObservationRepository
from macro_api.repositories.reference import CountryRepository, IndicatorRepository
from macro_api.schemas.indicator import (
    IndicatorDetail,
    IndicatorSummary,
    ObservationPoint,
    SeriesResponse,
)


class IndicatorService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = IndicatorRepository(session)
        self.country_repo = CountryRepository(session)
        self.obs_repo = ObservationRepository(session)

    async def list_indicators(self) -> list[IndicatorSummary]:
        indicators = await self.repo.list_active()
        return [self._to_summary(i) for i in indicators]

    async def get_indicator(self, code: str) -> IndicatorDetail:
        indicator = await self.repo.get_by_code(code)
        if indicator is None:
            raise NotFoundError(f"Indicator {code} not found.")

        source_code: str | None = None
        source_name: str | None = None
        if indicator.source_id is not None:
            source = await self.repo.get_source(indicator.source_id)
            if source is not None:
                source_code = source.code
                source_name = source.name

        return IndicatorDetail(
            id=indicator.id,
            code=indicator.code,
            name=indicator.name,
            description=indicator.description,
            unit=indicator.unit,
            frequency=indicator.frequency.value,
            category=indicator.category.value,
            source_code=source_code,
            source_name=source_name,
            higher_is_better=indicator.higher_is_better,
            methodology_note=indicator.methodology_note,
            is_active=indicator.is_active,
        )

    async def get_series(self, code: str, country_iso2: str) -> SeriesResponse:
        indicator = await self.repo.get_by_code(code)
        if indicator is None:
            raise NotFoundError(f"Indicator {code} not found.")

        country = await self.country_repo.get_by_iso2(country_iso2)
        if country is None:
            raise NotFoundError(f"Country {country_iso2} not found.")

        observations = await self.obs_repo.get_series(indicator.id, country.id)
        
        points = [
            ObservationPoint(period=obs.period, value=obs.value) 
            for obs in observations
        ]

        return SeriesResponse(
            indicator_code=indicator.code,
            country_iso2=country.iso2,
            points=points,
        )

    @staticmethod
    def _to_summary(indicator: Indicator) -> IndicatorSummary:
        return IndicatorSummary(
            id=indicator.id,
            code=indicator.code,
            name=indicator.name,
            unit=indicator.unit,
            frequency=indicator.frequency.value,
            category=indicator.category.value,
        )