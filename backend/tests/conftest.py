import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).parent / "test.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ.setdefault("MQTT_HOST", "127.0.0.1")
os.environ.setdefault("MQTT_PORT", "1")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production-use-only")

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import update  # noqa: E402

import app.models  # noqa: E402,F401 - registers all models on Base.metadata
from app.database.base import Base  # noqa: E402
from app.database.session import async_session_maker, engine  # noqa: E402
from app.models.user import Role, User  # noqa: E402
from app.utils.rate_limit import limiter  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def _reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    limiter.reset()
    yield


@pytest_asyncio.fixture
async def client():
    from app.main import app, lifespan

    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


async def _register_and_login(client: AsyncClient, username: str, password: str = "Passw0rd!") -> str:
    await client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    r = await client.post("/auth/login", json={"username": username, "password": password})
    return r.json()["access_token"]


@pytest_asyncio.fixture
async def user_headers(client: AsyncClient) -> dict:
    token = await _register_and_login(client, "testuser")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient) -> dict:
    await client.post(
        "/auth/register",
        json={"username": "admin", "email": "admin@example.com", "password": "Passw0rd!"},
    )
    async with async_session_maker() as session:
        await session.execute(update(User).where(User.username == "admin").values(role=Role.ADMIN))
        await session.commit()
    r = await client.post("/auth/login", json={"username": "admin", "password": "Passw0rd!"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
