from __future__ import annotations

from httpx import AsyncClient


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_agent_registry_seeds_versioned_builtin_definitions_idempotently(
    client: AsyncClient,
) -> None:
    headers = await auth_header(client)

    first = await client.get("/api/v1/agents", headers=headers)
    second = await client.get("/api/v1/agents", headers=headers)

    assert first.status_code == 200
    items = first.json()["items"]
    assert {item["key"] for item in items} >= {"developer", "qa", "documentation"}
    developer = next(item for item in items if item["key"] == "developer")
    assert developer["version"] == 1
    assert developer["allowed_tools"]
    assert developer["output_schema"]
    assert developer["max_iterations"] > 0
    assert second.json() == first.json()


async def test_agent_registry_exposes_immutable_version_history(client: AsyncClient) -> None:
    headers = await auth_header(client)

    response = await client.get("/api/v1/agents/developer/versions", headers=headers)

    assert response.status_code == 200
    versions = response.json()["items"]
    assert [item["version"] for item in versions] == [1]
    assert versions[0]["key"] == "developer"
