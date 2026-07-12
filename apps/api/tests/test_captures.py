from httpx import AsyncClient


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_create_and_list_capture(client: AsyncClient) -> None:
    headers = await auth_header(client)
    created = await client.post(
        "/api/v1/captures",
        headers=headers,
        json={
            "type": "conversation",
            "title": "Build Ryan Agent OS",
            "content": "Create the app, API, worker, and documentation.",
            "domain_hint": "personal_ai",
            "sensitivity": "confidential",
        },
    )
    assert created.status_code == 201
    assert created.json()["status"] == "received"

    listed = await client.get("/api/v1/captures", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1


async def test_duplicate_capture_is_idempotent(client: AsyncClient) -> None:
    headers = await auth_header(client)
    payload = {
        "type": "note",
        "title": "Same note",
        "content": "Same content",
        "sensitivity": "internal",
    }
    first = await client.post("/api/v1/captures", headers=headers, json=payload)
    second = await client.post("/api/v1/captures", headers=headers, json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
