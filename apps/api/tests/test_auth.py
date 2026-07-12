from httpx import AsyncClient


async def test_login_and_me(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["workspace_slug"] == "ryan-personal"


async def test_login_rejects_bad_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
