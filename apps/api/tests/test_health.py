"""Health endpoint tests."""

from httpx import AsyncClient


async def test_live_returns_ok(client: AsyncClient) -> None:
    r = await client.get("/api/v1/health/live")
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["status"] == "ok"
    assert "requestId" in body["meta"]
    assert r.headers["X-Request-ID"]


async def test_request_id_echoed(client: AsyncClient) -> None:
    r = await client.get(
        "/api/v1/health/live", headers={"X-Request-ID": "test-request-id-123"}
    )
    assert r.status_code == 200
    assert r.headers["X-Request-ID"] == "test-request-id-123"
    assert r.json()["meta"]["requestId"] == "test-request-id-123"
