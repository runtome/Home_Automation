from httpx import AsyncClient


async def test_register_and_login(client: AsyncClient):
    r = await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "Passw0rd!"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "alice"
    assert body["role"] == "user"

    r = await client.post("/auth/login", json={"username": "alice", "password": "Passw0rd!"})
    assert r.status_code == 200
    tokens = r.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]


async def test_register_duplicate_username_rejected(client: AsyncClient):
    payload = {"username": "bob", "email": "bob@example.com", "password": "Passw0rd!"}
    r1 = await client.post("/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/auth/register", json={**payload, "email": "other@example.com"})
    assert r2.status_code == 409


async def test_login_wrong_password_rejected(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"username": "carol", "email": "carol@example.com", "password": "Passw0rd!"},
    )
    r = await client.post("/auth/login", json={"username": "carol", "password": "wrong"})
    assert r.status_code == 401


async def test_refresh_rotates_token(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"username": "dave", "email": "dave@example.com", "password": "Passw0rd!"},
    )
    login = await client.post("/auth/login", json={"username": "dave", "password": "Passw0rd!"})
    old_refresh = login.json()["refresh_token"]

    r = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert r.status_code == 200
    new_refresh = r.json()["refresh_token"]
    assert new_refresh != old_refresh

    # old refresh token was rotated out and must no longer work
    r2 = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert r2.status_code == 401


async def test_logout_revokes_refresh_token(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"username": "erin", "email": "erin@example.com", "password": "Passw0rd!"},
    )
    login = await client.post("/auth/login", json={"username": "erin", "password": "Passw0rd!"})
    refresh_token = login.json()["refresh_token"]

    r = await client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert r.status_code == 200

    r2 = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r2.status_code == 401


async def test_protected_route_requires_token(client: AsyncClient):
    r = await client.get("/devices")
    assert r.status_code == 401
