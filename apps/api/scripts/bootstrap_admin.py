"""Create an admin user from env vars. Idempotent."""

import asyncio
import sys
from uuid import uuid4

from macro_api.config import get_settings
from macro_api.core.db import dispose_engine, get_session_factory
from macro_api.core.security import hash_password
from macro_api.models.identity import User, UserPreferences, UserRole, UserStatus
from macro_api.repositories.users import UserRepository


async def main() -> int:
    settings = get_settings()
    if not settings.admin_email or not settings.admin_password:
        print("MIL_ADMIN_EMAIL and MIL_ADMIN_PASSWORD are required.", file=sys.stderr)
        return 1

    email = settings.admin_email.strip().lower()
    password = settings.admin_password.get_secret_value()

    factory = get_session_factory()
    async with factory() as session:
        users = UserRepository(session)
        existing = await users.get_by_email(email)
        if existing is not None:
            if existing.role != UserRole.admin:
                existing.role = UserRole.admin
                await session.commit()
                print(f"Promoted existing user {email} to admin.")
            else:
                print(f"Admin {email} already exists.")
            await dispose_engine()
            return 0

        user = User(
            id=str(uuid4()),
            email=email,
            password_hash=hash_password(password),
            display_name="Administrator",
            role=UserRole.admin,
            status=UserStatus.active,
        )
        await users.add(user)
        await users.add_preferences(UserPreferences(user_id=user.id))
        await session.commit()
        print(f"Created admin {email}.")
        await dispose_engine()
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
