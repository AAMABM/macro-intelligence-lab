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


def _envelope(
    request: Request,
    *,
    status: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "") or ""
    body = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            details=details or {},
            request_id=request_id,
        )
    )
    return JSONResponse(status_code=status, content=body.model_dump(by_alias=True))


def _find_app_error(group: BaseException) -> AppError | None:
    """Walk nested ExceptionGroups looking for an AppError."""
    if isinstance(group, AppError):
        return group
    if isinstance(group, BaseExceptionGroup):
        for exc in group.exceptions:
            found = _find_app_error(exc)
            if found is not None:
                return found
    return None


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
            request_id = getattr(request.state, "request_id", None)
            log.warning(
                "%s: %s",
                exc.code,
                exc.message,
                extra={"request_id": request_id, "status": exc.status_code},
            )
            return _envelope(
                request, status=exc.status_code, code=exc.code,
                message=exc.message, details=exc.details,
            )
        except RequestValidationError as exc:
            errors: dict[str, list[str]] = {}
            for err in exc.errors():
                loc = ".".join(str(p) for p in err["loc"] if p != "body") or "body"
                errors.setdefault(loc, []).append(err["msg"])
            return _envelope(
                request, status=422, code=ValidationError.code,
                message=ValidationError.message, details=errors,
            )
        except BaseExceptionGroup as eg:
            # Starlette's BaseHTTPMiddleware wraps exceptions in ExceptionGroup
            # (Python 3.11+). Unwrap to find any AppError underneath.
            app_exc = _find_app_error(eg)
            if app_exc is not None:
                request_id = getattr(request.state, "request_id", None)
                log.warning(
                    "%s: %s (via ExceptionGroup)",
                    app_exc.code,
                    app_exc.message,
                    extra={"request_id": request_id, "status": app_exc.status_code},
                )
                return _envelope(
                    request, status=app_exc.status_code, code=app_exc.code,
                    message=app_exc.message, details=app_exc.details,
                )
            raise
        except Exception:
            log.exception(
                "unhandled_exception",
                extra={"request_id": getattr(request.state, "request_id", None)},
            )
            return _envelope(
                request, status=500, code="internal_error",
                message="An unexpected error occurred.",
            )
