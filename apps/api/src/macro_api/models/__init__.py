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
from macro_api.models.macro import IndicatorObservation
from macro_api.models.reference import (
    Country,
    Currency,
    DataSource,
    Frequency,
    Indicator,
    IndicatorCategory,
    Region,
)
from macro_api.models.market import MarketInstrument, MarketPriceDaily

__all__ = [
    "Base",
    "Country",
    "Currency",
    "DataSource",
    "EmailVerificationToken",
    "Frequency",
    "Indicator",
    "IndicatorCategory",
    "IndicatorObservation",
    "PasswordResetToken",
    "RefreshToken",
    "Region",
    "User",
    "UserPreferences",
]
