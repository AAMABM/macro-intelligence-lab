"""Market routes."""
from datetime import UTC, datetime
from fastapi import APIRouter, Request
from macro_api.core.envelope import Envelope, Meta, Page, PageMeta
from macro_api.routers.deps import DB
from macro_api.schemas.market import MarketInstrumentSummary, MarketSeriesResponse
from macro_api.services.market_service import MarketService

router = APIRouter(prefix="/markets", tags=["markets"])

def _meta(request: Request) -> Meta:
    return Meta(request_id=request.state.request_id, as_of=datetime.now(UTC))

@router.get("", response_model=Page[MarketInstrumentSummary])
async def list_instruments(request: Request, db: DB) -> Page[MarketInstrumentSummary]:
    service = MarketService(db)
    items = await service.list_instruments()
    return Page(
        data=items,
        meta=PageMeta(request_id=request.state.request_id, as_of=datetime.now(UTC), total=len(items)),
    )

@router.get("/{symbol}/series", response_model=Envelope[MarketSeriesResponse])
async def get_market_series(symbol: str, request: Request, db: DB) -> Envelope[MarketSeriesResponse]:
    service = MarketService(db)
    series = await service.get_series(symbol)
    return Envelope(data=series, meta=_meta(request))