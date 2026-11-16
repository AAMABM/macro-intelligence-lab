"""Auth flow tests."""

from httpx import AsyncClient

STRONG_PW = "CorrectHorseBattery!9"


async def test_register_returns_tokens(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": STRONG_PW,
            "displayName": "New User",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()["data"]
    assert body["accessToken"]
    assert body["refreshToken"]
    assert body["user"]["email"] == "new@example.com"
    assert body["user"]["role"] == "research_user"


async def test_duplicate_email_rejected(client: AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": STRONG_PW, "displayName": "Dup"}
    r1 = await client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "email_already_registered"


async def test_weak_password_rejected(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "password1234", "displayName": "W"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "weak_password"


async def test_login_success(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": STRONG_PW, "displayName": "L"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": STRONG_PW},
    )
    assert r.status_code == 200
    assert r.json()["data"]["accessToken"]


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "password": STRONG_PW, "displayName": "W"},
    )
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "NotTheRightOne!9"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "invalid_credentials"


async def test_refresh_rotates_token(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "rot@example.com", "password": STRONG_PW, "displayName": "R"},
    )
    refresh = r.json()["data"]["refreshToken"]
    r2 = await client.post("/api/v1/auth/refresh", json={"refreshToken": refresh})
    assert r2.status_code == 200
    assert r2.json()["data"]["refreshToken"] != refresh


async def test_refresh_replay_revokes_family(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "replay@example.com", "password": STRONG_PW, "displayName": "R"},
    )
    old_refresh = r.json()["data"]["refreshToken"]
    # First rotation succeeds
    r2 = await client.post("/api/v1/auth/refresh", json={"refreshToken": old_refresh})
    assert r2.status_code == 200
    new_refresh = r2.json()["data"]["refreshToken"]
    # Replaying the OLD token should 401 AND invalidate the family
    r3 = await client.post("/api/v1/auth/refresh", json={"refreshToken": old_refresh})
    assert r3.status_code == 401
    # Which means the new token is also dead
    r4 = await client.post("/api/v1/auth/refresh", json={"refreshToken": new_refresh})
    assert r4.status_code == 401


async def test_me_requires_auth(client: AsyncClient) -> None:
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401


async def test_me_returns_profile(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": STRONG_PW, "displayName": "Me"},
    )
    token = r.json()["data"]["accessToken"]
    r2 = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["email"] == "me@example.com"
