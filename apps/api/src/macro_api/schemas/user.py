"""User schemas."""

from datetime import datetime
from enum import Enum

from pydantic import EmailStr, Field

from macro_api.schemas.common import CamelModel


class UserRole(str, Enum):
    guest = "guest"
    research_user = "research_user"
    admin = "admin"


class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class UserSummary(CamelModel):
    id: str
    email: EmailStr
    display_name: str
    role: UserRole
    status: UserStatus


class UserDetail(CamelModel):
    id: str
    email: EmailStr
    display_name: str
    role: UserRole
    status: UserStatus
    avatar_url: str | None = None
    bio: str | None = None
    email_verified_at: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime


class CurrentUser(CamelModel):
    """Authenticated principal passed to services via DI."""

    id: str
    email: str
    display_name: str
    role: UserRole
    status: UserStatus


class UpdateProfileRequest(CamelModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    avatar_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=2000)