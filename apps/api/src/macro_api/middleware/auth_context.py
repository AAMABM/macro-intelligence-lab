"""Auth context middleware."""

from collections.abc import Awaitable, Callable

import jwt as pyjwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from macro_api.core.security import decode_access_token


class AuthContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.claims = None
        header = request.headers.get("authorization")
        if header and header.lower().startswith("bearer "):
            token = header[7:].strip()
            try:
                request.state.claims = decode_access_token(token)
            except pyjwt.PyJWTError:
                # Invalid tokens are treated as unauthenticated; a protected
                # route will 401 via its dependency.
                request.state.claims = None
        return await call_next(request)
