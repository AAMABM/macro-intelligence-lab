"""Indicator routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request

from macro_api.core.envelope import Envelope, Meta, Page, PageMeta
from macro_api.routers.deps import DB
from macro_api.schemas.indicator import (
    ForecastResponse,
    IndicatorDetail,
    IndicatorSummary,
    SeriesResponse,
)
from macro_api.services.forecast_service import ForecastService
from macro_api.services.indicator_service import IndicatorService

router = APIRouter(prefix="/indicators", tags=["indicators"])


def _meta(request: Request) -> Meta:
    return Meta(request_id=request.state.request_id, as_of=datetime.now(UTC))


@router.get("", response_model=Page[IndicatorSummary])
async def list_indicators(request: Request, db: DB) -> Page[IndicatorSummary]:
    service = IndicatorService(db)
    items = await service.list_indicators()
    return Page(
        data=items,
        meta=PageMeta(
            request_id=request.state.request_id,
            as_of=datetime.now(UTC),
            total=len(items),
        ),
    )


@router.get("/{code}", response_model=Envelope[IndicatorDetail])
async def get_indicator(
    code: str, request: Request, db: DB
) -> Envelope[IndicatorDetail]:
    service = IndicatorService(db)
    indicator = await service.get_indicator(code)
    return Envelope(data=indicator, meta=_meta(request))


@router.get("/{code}/series", response_model=Envelope[SeriesResponse])
async def get_indicator_series(
    code: str,
    request: Request,
    db: DB,
    country: str = "US",
) -> Envelope[SeriesResponse]:
    """Fetch the historical time-series for a given indicator and country."""
    service = IndicatorService(db)
    series = await service.get_series(code, country)
    return Envelope(data=series, meta=_meta(request))


@router.get("/{code}/forecast", response_model=Envelope[ForecastResponse])
async def get_indicator_forecast(
    code: str,
    request: Request,
    db: DB,
    country: str = "US",
) -> Envelope[ForecastResponse]:
    """Generate a 12-month ARIMA forecast for a given indicator."""
    service = ForecastService(db)
    try:
        forecast = await service.generate_forecast(code, country)
        return Envelope(data=forecast, meta=_meta(request))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
