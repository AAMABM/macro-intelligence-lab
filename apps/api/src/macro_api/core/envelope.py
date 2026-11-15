"""Response envelope and pagination types."""

from datetime import UTC, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class CamelModel(BaseModel):
    """Base model with camelCase JSON output and snake_case Python.

    All request/response schemas extend this so the frontend gets
    ``asOf`` instead of ``as_of`` without lossy transformation.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
    )


class Meta(CamelModel):
    request_id: str
    as_of: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PageMeta(Meta):
    next_cursor: str | None = None
    total: int | None = None


class Envelope(CamelModel, Generic[T]):
    data: T
    meta: Meta


class Page(CamelModel, Generic[T]):
    data: list[T]
    meta: PageMeta


class ErrorBody(CamelModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)
    request_id: str


class ErrorEnvelope(CamelModel):
    error: ErrorBody