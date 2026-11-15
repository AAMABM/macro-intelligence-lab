"""SQLAlchemy models.

Importing this package registers every mapped class on ``Base.metadata``,
which Alembic's autogenerate and ``create_all`` both rely on.
"""

from macro_api.models.base import Base
from macro_api.models.identity import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserPreferences,
)

__all__ = [
    "Base",
    "User",
    "UserPreferences",
    "RefreshToken",
    "PasswordResetToken",
    "EmailVerificationToken",
]