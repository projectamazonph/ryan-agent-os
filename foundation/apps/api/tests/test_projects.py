from httpx import AsyncClient


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def create_capture(client: AsyncClient, headers: dict[str, str], title: str, content: str):
    response = await client.post(
        "/api/v1/captures",
        headers=headers,
        json={
            "type": "note",
            "title": title,
            "content": content,
            "domain_hint": "software",
            "sensitivity": "internal",
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_create_project_from_capture_and_query_registry(client: AsyncClient) -> None:
    headers = await auth_header(client)
    capture = await create_capture(
        client,
        headers,
        "Extraction pipeline",
        "Implement file ingestion, extraction jobs, and capture review.",
    )

    created = await client.post(
        f"/api/v1/captures/{capture['id']}/projects",
        headers=headers,
        json={"status": "planned", "next_action": "Finish the review workflow"},
    )

    assert created.status_code == 201
    project = created.json()
    assert project["title"] == "Extraction pipeline"
    assert project["status"] == "planned"
    assert project["domain"] == "software"
    assert project["next_action"] == "Finish the review workflow"
    assert project["captures"][0]["id"] == capture["id"]

    listed = await client.get("/api/v1/projects?q=extraction", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [project["id"]]

    reviewed = await client.get(
        f"/api/v1/captures/{capture['id']}/review", headers=headers
    )
    assert reviewed.json()["capture"]["review_status"] == "linked"
    assert reviewed.json()["projects"][0]["id"] == project["id"]


async def test_link_capture_to_project_is_idempotent(client: AsyncClient) -> None:
    headers = await auth_header(client)
    first = await create_capture(client, headers, "Agent OS", "Build the operating system.")
    second = await create_capture(client, headers, "Memory layer", "Add durable project memory.")
    project = (
        await client.post(
            f"/api/v1/captures/{first['id']}/projects",
            headers=headers,
            json={"status": "active"},
        )
    ).json()

    link_one = await client.post(
        f"/api/v1/projects/{project['id']}/captures/{second['id']}", headers=headers
    )
    link_two = await client.post(
        f"/api/v1/projects/{project['id']}/captures/{second['id']}", headers=headers
    )

    assert link_one.status_code == 200
    assert link_two.status_code == 200
    assert len(link_two.json()["captures"]) == 2


async def test_archive_capture_from_review_queue(client: AsyncClient) -> None:
    headers = await auth_header(client)
    capture = await create_capture(client, headers, "Old idea", "Do not pursue this idea.")

    archived = await client.post(
        f"/api/v1/captures/{capture['id']}/archive", headers=headers
    )

    assert archived.status_code == 200
    assert archived.json()["review_status"] == "archived"
