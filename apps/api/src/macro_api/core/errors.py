"""Domain exceptions and their HTTP mapping."""

from typing import Any


class AppError(Exception):
    """Base for all domain errors.

    The ``code`` string is stable — clients branch on it. The ``message``
    is user-facing and safe to display. Never include internal detail.
    """

    code: str = "internal_error"
    status_code: int = 500
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        if message:
            self.message = message
        self.details: dict[str, Any] = details or {}
        super().__init__(self.message)


class UnauthorizedError(AppError):
    code = "unauthorized"
    status_code = 401
    message = "Authentication required."


class InvalidCredentialsError(AppError):
    code = "invalid_credentials"
    status_code = 401
    message = "Email or password is incorrect."


class TokenExpiredError(AppError):
    code = "token_expired"
    status_code = 401
    message = "Session expired. Please sign in again."


class ForbiddenError(AppError):
    code = "forbidden"
    status_code = 403
    message = "You do not have permission to perform this action."


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404
    message = "Resource not found."


class ConflictError(AppError):
    code = "conflict"
    status_code = 409
    message = "Resource already exists."


class EmailAlreadyRegisteredError(ConflictError):
    code = "email_already_registered"
    message = "An account with this email already exists."


class ValidationError(AppError):
    code = "validation_error"
    status_code = 422
    message = "The request could not be validated."


class WeakPasswordError(ValidationError):
    code = "weak_password"
    message = "Password does not meet the minimum strength requirement."


class RateLimitedError(AppError):
    code = "rate_limited"
    status_code = 429
    message = "Too many requests. Please try again later."


class UpstreamError(AppError):
    code = "upstream_error"
    status_code = 502
    message = "An upstream service returned an error."
