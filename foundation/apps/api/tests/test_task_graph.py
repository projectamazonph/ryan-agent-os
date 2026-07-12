from __future__ import annotations

from httpx import AsyncClient

from app.schemas.task_graph import TaskDraft
from app.services.task_graph import TaskGraphCycleError, validate_task_dag


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_validate_task_dag_rejects_dependency_cycles() -> None:
    tasks = [
        TaskDraft(
            key="task-a",
            title="Task A",
            description="First task",
            verification="A is verified",
            dependencies=["task-b"],
        ),
        TaskDraft(
            key="task-b",
            title="Task B",
            description="Second task",
            verification="B is verified",
            dependencies=["task-a"],
        ),
    ]

    try:
        validate_task_dag(tasks)
    except TaskGraphCycleError as exc:
        assert exc.cycle == ["task-a", "task-b", "task-a"]
    else:
        raise AssertionError("A cyclic task graph must be rejected")


async def _create_project_with_pack(
    client: AsyncClient, headers: dict[str, str], *, approve: bool
) -> str:
    project_response = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Dependency-aware implementation queue",
            "summary": "Turn an approved plan into ranked work.",
            "domain": "software",
            "priority": 90,
            "next_action": "Generate the task graph",
        },
    )
    project_id = project_response.json()["id"]
    pack = await client.post(
        f"/api/v1/projects/{project_id}/execution-pack",
        headers=headers,
        json={"change_summary": "Phase 4 plan"},
    )
    if approve:
        await client.post(
            f"/api/v1/projects/{project_id}/execution-pack/approve",
            headers=headers,
            json={"version_number": pack.json()["current_version_number"]},
        )
    return project_id


async def test_task_graph_requires_an_approved_execution_pack(client: AsyncClient) -> None:
    headers = await auth_header(client)
    project_id = await _create_project_with_pack(client, headers, approve=False)

    response = await client.post(
        f"/api/v1/projects/{project_id}/task-graph",
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Approve the current execution pack before task generation"


async def test_task_graph_preserves_approval_traceability_and_is_idempotent(
    client: AsyncClient,
) -> None:
    headers = await auth_header(client)
    project_id = await _create_project_with_pack(client, headers, approve=True)

    first = await client.post(
        f"/api/v1/projects/{project_id}/task-graph",
        headers=headers,
    )
    second = await client.post(
        f"/api/v1/projects/{project_id}/task-graph",
        headers=headers,
    )

    assert first.status_code == 201
    body = first.json()
    assert body["project_id"] == project_id
    assert body["source_execution_pack_version_number"] == 1
    assert body["source_execution_pack_approved_at"] is not None
    assert body["tasks"]
    assert all(task["verification"] for task in body["tasks"])
    assert second.status_code == 200
    assert second.json()["id"] == body["id"]
    assert len(second.json()["tasks"]) == len(body["tasks"])
