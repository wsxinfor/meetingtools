"""Create the first admin user from environment variables.

Usage:
    ADMIN_USERNAME=admin ADMIN_PASSWORD=secret python seed_admin.py
"""
import asyncio
import os
import sys

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import User


async def main() -> None:
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "")

    if not password:
        print("ERROR: ADMIN_PASSWORD environment variable is required", file=sys.stderr)
        sys.exit(1)

    async with async_session_factory() as db:
        existing = await db.execute(select(User).where(User.username == username))
        if existing.scalar_one_or_none():
            print(f"User '{username}' already exists, skipping.")
            return

        admin = User(username=username, password_hash=hash_password(password), role="admin")
        db.add(admin)
        await db.commit()
        print(f"Admin user '{username}' created successfully.")


asyncio.run(main())
