#!/usr/bin/env python3
"""Bootstraps the first admin user directly in the database (there is no public
registration flag for admin, by design). Run from the repo root, or inside the
backend container:

    python scripts/create_admin.py <username> <email> <password>
    docker compose exec backend python /app/../scripts/create_admin.py admin admin@example.com Passw0rd!
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import select  # noqa: E402

from app.auth.security import hash_password  # noqa: E402
from app.database.session import async_session_maker  # noqa: E402
from app.models.user import Role, User  # noqa: E402


async def create_admin(username: str, email: str, password: str) -> None:
    async with async_session_maker() as session:
        existing = await session.execute(select(User).where(User.username == username))
        user = existing.scalar_one_or_none()
        if user is not None:
            user.role = Role.ADMIN
            print(f"User '{username}' already existed; promoted to admin.")
        else:
            user = User(
                username=username, email=email, password_hash=hash_password(password), role=Role.ADMIN
            )
            session.add(user)
            print(f"Created admin user '{username}'.")
        await session.commit()


def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    _, username, email, password = sys.argv
    asyncio.run(create_admin(username, email, password))


if __name__ == "__main__":
    main()
