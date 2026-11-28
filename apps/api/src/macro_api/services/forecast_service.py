"""Forecast service using ARIMA."""

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from statsmodels.tsa.arima.model import ARIMA

from macro_api.core.errors import NotFoundError
from macro_api.repositories.observations import ObservationRepository
from macro_api.repositories.reference import CountryRepository, IndicatorRepository
from macro_api.schemas.indicator import ForecastPoint, ForecastResponse


class ForecastService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = IndicatorRepository(session)
        self.country_repo = CountryRepository(session)
        self.obs_repo = ObservationRepository(session)

    async def generate_forecast(
        self, code: str, country_iso2: str, steps: int = 12
    ) -> ForecastResponse:
        indicator = await self.repo.get_by_code(code)
        if not indicator:
            raise NotFoundError(f"Indicator {code} not found.")

        country = await self.country_repo.get_by_iso2(country_iso2)
        if not country:
            raise NotFoundError(f"Country {country_iso2} not found.")

        observations = await self.obs_repo.get_series(indicator.id, country.id)

        if len(observations) < 24:
            raise ValueError(
                "Not enough historical data to generate a forecast "
                "(need at least 24 months)."
            )

        # Convert to Pandas Series
        data = pd.Series(
            [float(o.value) for o in observations],
            index=pd.DatetimeIndex([o.period for o in observations]),
        )

        # Ensure monthly frequency and fill missing gaps
        data = data.asfreq("MS")
        data = data.interpolate(method="linear")

        # Fit ARIMA(1,1,1) model
        model = ARIMA(data, order=(1, 1, 1))
        fitted_model = model.fit()

        # Generate forecast
        forecast = fitted_model.get_forecast(steps=steps)
        predicted_mean = forecast.predicted_mean
        conf_int = forecast.conf_int(alpha=0.20)  # 80% confidence interval

        points = []
        for i in range(steps):
            period_date = predicted_mean.index[i].date()
            points.append(
                ForecastPoint(
                    period=period_date,
                    yhat=round(predicted_mean.iloc[i], 4),
                    yhat_lower=round(conf_int.iloc[i, 0], 4),
                    yhat_upper=round(conf_int.iloc[i, 1], 4),
                )
            )

        return ForecastResponse(
            indicator_code=indicator.code,
            country_iso2=country.iso2,
            points=points,
        )
