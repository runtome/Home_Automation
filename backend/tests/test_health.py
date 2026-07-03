from httpx import AsyncClient


async def test_health_ok(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["db"] == "ok"
    assert body["mqtt"] == "disconnected"
    assert "timestamp" in body
