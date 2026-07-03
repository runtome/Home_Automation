from httpx import AsyncClient


async def test_admin_can_create_and_list_device(client: AsyncClient, admin_headers: dict):
    r = await client.post(
        "/devices",
        json={"device_id": "light001", "device_name": "Living Room Light", "room": "Living Room"},
        headers=admin_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["device_id"] == "light001"
    assert body["status"] == "UNKNOWN"
    assert body["online"] is False

    r = await client.get("/devices", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["total"] == 1


async def test_non_admin_cannot_create_device(client: AsyncClient, user_headers: dict):
    r = await client.post(
        "/devices",
        json={"device_id": "light002", "device_name": "Kitchen Light", "room": "Kitchen"},
        headers=user_headers,
    )
    assert r.status_code == 403


async def test_duplicate_device_id_rejected(client: AsyncClient, admin_headers: dict):
    payload = {"device_id": "light003", "device_name": "Hallway Light", "room": "Hallway"}
    r1 = await client.post("/devices", json=payload, headers=admin_headers)
    assert r1.status_code == 201
    r2 = await client.post("/devices", json=payload, headers=admin_headers)
    assert r2.status_code == 409


async def test_get_update_delete_device(client: AsyncClient, admin_headers: dict):
    r = await client.post(
        "/devices",
        json={"device_id": "light004", "device_name": "Garage Light", "room": "Garage"},
        headers=admin_headers,
    )
    device_pk = r.json()["id"]

    r = await client.get(f"/devices/{device_pk}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["device_name"] == "Garage Light"

    r = await client.put(
        f"/devices/{device_pk}", json={"device_name": "Garage Light Updated"}, headers=admin_headers
    )
    assert r.status_code == 200
    assert r.json()["device_name"] == "Garage Light Updated"

    r = await client.delete(f"/devices/{device_pk}", headers=admin_headers)
    assert r.status_code == 204

    r = await client.get(f"/devices/{device_pk}", headers=admin_headers)
    assert r.status_code == 404


async def test_get_nonexistent_device_404(client: AsyncClient, user_headers: dict):
    r = await client.get("/devices/9999", headers=user_headers)
    assert r.status_code == 404
