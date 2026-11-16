"""Access log middleware."""

import logging
import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

log = logging.getLogger("macro_api.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        log.info(
            "request",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "user_id": _user_id(request),
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": elapsed_ms,
            },
        )
        return response


def _user_id(request: Request) -> str | None:
    claims = getattr(request.state, "claims", None)
    if isinstance(claims, dict):
        sub = claims.get("sub")
        return str(sub) if sub else None
    return None
