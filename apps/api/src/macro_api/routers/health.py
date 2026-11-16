"""Health endpoints."""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Request
from sqlalchemy import text

from macro_api import __version__
from macro_api.core.envelope import Envelope, Meta
from macro_api.core.errors import UpstreamError
from macro_api.routers.deps import DB

log = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


def _meta(request: Request) -> Meta:
    return Meta(
        request_id=request.state.request_id,
        as_of=datetime.now(UTC),
    )


@router.get("/health/live", response_model=Envelope[dict[str, str]])
async def live(request: Request) -> Envelope[dict[str, str]]:
    """Process liveness. No dependencies."""
    return Envelope(data={"status": "ok", "version": __version__}, meta=_meta(request))


@router.get("/health", response_model=Envelope[dict[str, str]])
async def health(request: Request, db: DB) -> Envelope[dict[str, str]]:
    """Basic health with a fast DB ping."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        log.exception("health_db_check_failed")
        raise UpstreamError("Database unreachable.") from exc
    return Envelope(
        data={"status": "ok", "version": __version__, "db": "ok"},
        meta=_meta(request),
    )


@router.get("/health/ready", response_model=Envelope[dict[str, str]])
async def ready(request: Request, db: DB) -> Envelope[dict[str, str]]:
    """Readiness — what Render and the deploy workflow poll.

    In Sprint 2 this will also verify that materialized views are populated.
    For Sprint 1 it is a DB connectivity check.
    """
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        log.exception("ready_db_check_failed")
        raise UpstreamError("Database not ready.") from exc
    return Envelope(
        data={
            "status": "ok",
            "version": __version__,
            "db": "ok",
            "mvsPopulated": "n/a",
        },
        meta=_meta(request),
    )
