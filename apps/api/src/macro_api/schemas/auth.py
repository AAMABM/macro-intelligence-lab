"""Authentication schemas."""

from datetime import datetime

from pydantic import EmailStr, Field

from macro_api.schemas.common import CamelModel
from macro_api.schemas.user import UserDetail


class RegisterRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class LoginRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(CamelModel):
    refresh_token: str = Field(min_length=10, max_length=200)


class LogoutRequest(CamelModel):
    refresh_token: str = Field(min_length=10, max_length=200)


class ForgotPasswordRequest(CamelModel):
    email: EmailStr


class ResetPasswordRequest(CamelModel):
    token: str = Field(min_length=10, max_length=200)
    new_password: str = Field(min_length=12, max_length=128)


class TokenPair(CamelModel):
    access_token: str
    refresh_token: str
    access_expires_at: datetime


class AuthResponse(CamelModel):
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    user: UserDetail