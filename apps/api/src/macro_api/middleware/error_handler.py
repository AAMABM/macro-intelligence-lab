"""Exception → envelope middleware."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from macro_api.core.envelope import ErrorBody, ErrorEnvelope
from macro_api.core.errors import AppError, ValidationError

log = logging.getLogger("macro_api.errors")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except AppError as exc:
            return _error_response(
                request,
                status=exc.status_code,
                code=exc.code,
                message=exc.message,
                details=exc.details,
                log_level="warning",
            )
        except RequestValidationError as exc:
            errors: dict[str, list[str]] = {}
            for err in exc.errors():
                loc = ".".join(str(p) for p in err["loc"] if p != "body") or "body"
                errors.setdefault(loc, []).append(err["msg"])
            return _error_response(
                request,
                status=422,
                code=ValidationError.code,
                message=ValidationError.message,
                details=errors,
                log_level="warning",
            )
        except Exception:
            log.exception(
                "unhandled_exception",
                extra={"request_id": getattr(request.state, "request_id", None)},
            )
            return _error_response(
                request,
                status=500,
                code="internal_error",
                message="An unexpected error occurred.",
                details={},
                log_level="error",
            )


def _error_response(
    request: Request,
    *,
    status: int,
    code: str,
    message: str,
    details: dict[str, Any],
    log_level: str,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "") or ""
    body = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            details=details,
            request_id=request_id,
        )
    )
    getattr(log, log_level)(
        f"{code}: {message}",
        extra={"request_id": request_id, "status": status},
    )
    return JSONResponse(status_code=status, content=body.model_dump(by_alias=True))