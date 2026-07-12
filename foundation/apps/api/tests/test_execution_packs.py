from __future__ import annotations

from httpx import AsyncClient

from app.models.capture import Capture
from app.models.project import Project
from app.schemas.execution_pack import ExecutionPackContent
from app.services.execution_pack import RulesExecutionPlanner


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_rules_execution_planner_returns_typed_actionable_pack() -> None:
    project = Project(
        workspace_id="01900000-0000-7000-8000-000000000001",
        title="Ryan Agent OS execution queue",
        summary="Turn approved plans into ranked work.",
        domain="software",
        status="planned",
        priority=80,
        next_action="Define the task graph",
    )
    capture = Capture(
        workspace_id="01900000-0000-7000-8000-000000000001",
        type="note",
        title="Queue requirements",
        content="Rank tasks by impact, urgency, confidence, and effort. Preserve dependencies.",
        sensitivity="internal",
        checksum_sha256="a" * 64,
    )

    pack = await RulesExecutionPlanner().plan(project, [capture])

    assert isinstance(pack, ExecutionPackContent)
    assert pack.objective
    assert pack.success_criteria
    assert pack.deliverables
    assert pack.workstreams
    assert any("task" in item.name.lower() for item in pack.deliverables)


async def test_execution_pack_is_versioned_and_approvable(client: AsyncClient) -> None:
    headers = await auth_header(client)
    project_response = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Execution queue",
            "summary": "Build a ranked implementation queue.",
            "domain": "software",
            "priority": 80,
            "next_action": "Define task dependencies",
        },
    )
    project_id = project_response.json()["id"]
    capture_response = await client.post(
        "/api/v1/captures",
        headers=headers,
        json={
            "type": "note",
            "title": "Queue rules",
            "content": "Rank tasks by impact, urgency, confidence, and effort.",
            "domain_hint": "software",
        },
    )
    capture_id = capture_response.json()["id"]
    await client.post(
        f"/api/v1/projects/{project_id}/captures/{capture_id}", headers=headers
    )

    first = await client.post(
        f"/api/v1/projects/{project_id}/execution-pack",
        headers=headers,
        json={"change_summary": "Initial plan"},
    )
    second = await client.post(
        f"/api/v1/projects/{project_id}/execution-pack",
        headers=headers,
        json={"change_summary": "Regenerated after review"},
    )
    approved = await client.post(
        f"/api/v1/projects/{project_id}/execution-pack/approve",
        headers=headers,
        json={"version_number": 2},
    )
    fetched = await client.get(
        f"/api/v1/projects/{project_id}/execution-pack", headers=headers
    )

    assert first.status_code == 201
    assert first.json()["current_version_number"] == 1
    assert first.json()["status"] == "draft"
    assert second.status_code == 201
    assert second.json()["current_version_number"] == 2
    assert len(second.json()["versions"]) == 2
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["current_version"]["approved_at"] is not None
    assert fetched.json()["current_version_number"] == 2
