"""Observation repository for time-series data."""

from sqlalchemy import select

from macro_api.models.macro import IndicatorObservation
from macro_api.repositories.base import Repository


class ObservationRepository(Repository):
    async def get_series(
        self, indicator_id: int, country_id: int
    ) -> list[IndicatorObservation]:
        """Fetch all latest observations for a given indicator and country, ordered by date."""
        stmt = (
            select(IndicatorObservation)
            .where(
                IndicatorObservation.indicator_id == indicator_id,
                IndicatorObservation.country_id == country_id,
                IndicatorObservation.is_latest.is_(True),
            )
            .order_by(IndicatorObservation.period.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())
