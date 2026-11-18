"""Country routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from macro_api.core.envelope import Envelope, Meta, Page, PageMeta
from macro_api.routers.deps import DB
from macro_api.schemas.country import CountryDetail, CountrySummary
from macro_api.services.country_service import CountryService

router = APIRouter(prefix="/countries", tags=["countries"])


def _meta(request: Request) -> Meta:
    return Meta(request_id=request.state.request_id, as_of=datetime.now(UTC))


@router.get("", response_model=Page[CountrySummary])
async def list_countries(request: Request, db: DB) -> Page[CountrySummary]:
    service = CountryService(db)
    items = await service.list_countries()
    return Page(
        data=items,
        meta=PageMeta(
            request_id=request.state.request_id,
            as_of=datetime.now(UTC),
            total=len(items),
        ),
    )


@router.get("/{iso2}", response_model=Envelope[CountryDetail])
async def get_country(
    iso2: str, request: Request, db: DB
) -> Envelope[CountryDetail]:
    service = CountryService(db)
    country = await service.get_country(iso2)
    return Envelope(data=country, meta=_meta(request))
