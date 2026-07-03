from httpx import AsyncClient


async def _create_device(client: AsyncClient, admin_headers: dict, device_id: str = "light010") -> int:
    r = await client.post(
        "/devices",
        json={"device_id": device_id, "device_name": "Test Light", "room": "Office"},
        headers=admin_headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


async def test_turn_on_off_toggle(client: AsyncClient, admin_headers: dict):
    device_pk = await _create_device(client, admin_headers)

    r = await client.post(f"/devices/{device_pk}/on", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "ON"

    r = await client.post(f"/devices/{device_pk}/off", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "OFF"

    r = await client.post(f"/devices/{device_pk}/toggle", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "ON"


async def test_relay_command_writes_activity_log(client: AsyncClient, admin_headers: dict):
    device_pk = await _create_device(client, admin_headers, "light011")
    await client.post(f"/devices/{device_pk}/on", headers=admin_headers)

    r = await client.get("/logs", params={"action": "RELAY_ON"}, headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert body["items"][0]["device_id"] == device_pk


async def test_relay_on_unknown_device_404(client: AsyncClient, admin_headers: dict):
    r = await client.post("/devices/99999/on", headers=admin_headers)
    assert r.status_code == 404


async def test_regular_user_can_control_relay(client: AsyncClient, admin_headers: dict, user_headers: dict):
    device_pk = await _create_device(client, admin_headers, "light012")
    r = await client.post(f"/devices/{device_pk}/on", headers=user_headers)
    assert r.status_code == 200
