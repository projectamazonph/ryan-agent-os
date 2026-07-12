from __future__ import annotations

from httpx import AsyncClient


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _seed_graph(client: AsyncClient, headers: dict[str, str]) -> dict[str, object]:
    project = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Queue engine",
            "summary": "Rank executable work without violating dependencies.",
            "priority": 80,
            "next_action": "Build the queue",
        },
    )
    project_id = project.json()["id"]
    pack = await client.post(
        f"/api/v1/projects/{project_id}/execution-pack",
        headers=headers,
        json={"change_summary": "Queue plan"},
    )
    await client.post(
        f"/api/v1/projects/{project_id}/execution-pack/approve",
        headers=headers,
        json={"version_number": pack.json()["current_version_number"]},
    )
    graph = await client.post(
        f"/api/v1/projects/{project_id}/task-graph",
        headers=headers,
    )
    return graph.json()


async def test_queue_ranks_ready_work_before_blocked_work_and_unlocks_dependencies(
    client: AsyncClient,
) -> None:
    headers = await auth_header(client)
    await _seed_graph(client, headers)

    queue = await client.get("/api/v1/queue", headers=headers)

    assert queue.status_code == 200
    items = queue.json()["items"]
    assert items
    assert items[0]["is_ready"] is True
    assert all(item["rank_score"] >= 0 for item in items)
    first_task = items[0]
    dependent = next(
        item for item in items if first_task["key"] in item["dependency_keys"]
    )
    assert dependent["is_ready"] is False
    assert first_task["key"] in dependent["blocked_by"]

    started = await client.patch(
        f"/api/v1/tasks/{first_task['id']}",
        headers=headers,
        json={"status": "in_progress"},
    )
    completed = await client.patch(
        f"/api/v1/tasks/{first_task['id']}",
        headers=headers,
        json={"status": "done"},
    )
    refreshed = await client.get("/api/v1/queue", headers=headers)
    refreshed_dependent = next(
        item for item in refreshed.json()["items"] if item["id"] == dependent["id"]
    )

    assert started.status_code == 200
    assert started.json()["status"] == "in_progress"
    assert completed.status_code == 200
    assert completed.json()["status"] == "done"
    assert completed.json()["completed_at"] is not None
    assert refreshed_dependent["is_ready"] is True
    assert refreshed_dependent["blocked_by"] == []


async def test_task_status_transition_rejects_done_to_in_progress(client: AsyncClient) -> None:
    headers = await auth_header(client)
    graph = await _seed_graph(client, headers)
    first_task = graph["tasks"][0]
    await client.patch(
        f"/api/v1/tasks/{first_task['id']}",
        headers=headers,
        json={"status": "done"},
    )

    response = await client.patch(
        f"/api/v1/tasks/{first_task['id']}",
        headers=headers,
        json={"status": "in_progress"},
    )

    assert response.status_code == 409
    assert "Invalid task transition" in response.json()["detail"]


async def test_blocked_task_cannot_start_before_dependencies_complete(
    client: AsyncClient,
) -> None:
    headers = await auth_header(client)
    graph = await _seed_graph(client, headers)
    first_task = graph["tasks"][0]
    blocked_task = next(
        task for task in graph["tasks"] if first_task["key"] in task["dependency_keys"]
    )

    response = await client.patch(
        f"/api/v1/tasks/{blocked_task['id']}",
        headers=headers,
        json={"status": "in_progress"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == f"Task is blocked by: {first_task['key']}"
