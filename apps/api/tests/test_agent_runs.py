from __future__ import annotations

from httpx import AsyncClient


async def auth_header(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ryan@example.com", "password": "test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def seed_graph(client: AsyncClient, headers: dict[str, str]) -> dict[str, object]:
    project = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Agent execution foundation",
            "summary": "Run bounded specialist agents with complete traces.",
            "domain": "software",
            "priority": 92,
            "next_action": "Launch the developer agent",
        },
    )
    project_id = project.json()["id"]
    pack = await client.post(
        f"/api/v1/projects/{project_id}/execution-pack",
        headers=headers,
        json={"change_summary": "Phase 5 agent plan"},
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


async def create_run(
    client: AsyncClient,
    headers: dict[str, str],
    task_id: str,
) -> dict[str, object]:
    response = await client.post(
        f"/api/v1/tasks/{task_id}/agent-runs",
        headers=headers,
        json={"agent_key": "developer"},
    )
    assert response.status_code == 201
    return response.json()


async def test_agent_run_requires_ready_task_and_builds_immutable_context(
    client: AsyncClient,
) -> None:
    headers = await auth_header(client)
    graph = await seed_graph(client, headers)
    ready = graph["tasks"][0]
    blocked = graph["tasks"][1]

    created = await client.post(
        f"/api/v1/tasks/{ready['id']}/agent-runs",
        headers=headers,
        json={"agent_key": "developer"},
    )
    rejected = await client.post(
        f"/api/v1/tasks/{blocked['id']}/agent-runs",
        headers=headers,
        json={"agent_key": "developer"},
    )

    assert created.status_code == 201
    run = created.json()
    assert run["state"] == "queued"
    assert run["agent_key"] == "developer"
    assert run["agent_version"] == 1
    assert run["context_package"]["task_id"] == ready["id"]
    assert run["context_package"]["source_execution_pack_version_id"] == graph[
        "source_execution_pack_version_id"
    ]
    assert run["context_package"]["checksum_sha256"]
    assert set(run["tool_allowlist"]) <= set(run["context_package"]["allowed_tools"])
    assert rejected.status_code == 409
    assert "blocked" in rejected.json()["detail"].lower()


async def test_agent_run_executes_with_complete_event_trace_and_needs_review(
    client: AsyncClient,
) -> None:
    headers = await auth_header(client)
    graph = await seed_graph(client, headers)
    run = await create_run(client, headers, graph["tasks"][0]["id"])

    executed = await client.post(
        f"/api/v1/agent-runs/{run['id']}/execute",
        headers=headers,
    )
    events = await client.get(
        f"/api/v1/agent-runs/{run['id']}/events",
        headers=headers,
    )

    assert executed.status_code == 200
    body = executed.json()
    assert body["state"] == "needs_review"
    assert body["output"]["summary"]
    assert body["output"]["evidence"]
    assert body["started_at"] is not None
    event_types = [item["event_type"] for item in events.json()["items"]]
    assert event_types == [
        "run.created",
        "run.state_changed",
        "run.state_changed",
        "run.output_generated",
        "run.state_changed",
    ]


async def test_tool_policy_records_allowed_and_denied_requests(client: AsyncClient) -> None:
    headers = await auth_header(client)
    graph = await seed_graph(client, headers)
    run = await create_run(client, headers, graph["tasks"][0]["id"])

    allowed_tool = run["tool_allowlist"][0]
    allowed = await client.post(
        f"/api/v1/agent-runs/{run['id']}/tool-invocations",
        headers=headers,
        json={"tool_name": allowed_tool, "arguments": {"path": "README.md"}},
    )
    denied = await client.post(
        f"/api/v1/agent-runs/{run['id']}/tool-invocations",
        headers=headers,
        json={"tool_name": "gmail.send", "arguments": {"to": "nobody@example.com"}},
    )
    detail = await client.get(f"/api/v1/agent-runs/{run['id']}", headers=headers)

    assert allowed.status_code == 201
    assert allowed.json()["decision"] == "allowed"
    assert denied.status_code == 403
    assert denied.json()["detail"] == "Tool gmail.send is not allowed for this run"
    decisions = [item["decision"] for item in detail.json()["tool_invocations"]]
    assert decisions == ["allowed", "denied"]


async def test_cancel_retry_and_fallback_preserve_run_lineage(client: AsyncClient) -> None:
    headers = await auth_header(client)
    graph = await seed_graph(client, headers)
    run = await create_run(client, headers, graph["tasks"][0]["id"])

    cancelled = await client.post(
        f"/api/v1/agent-runs/{run['id']}/cancel",
        headers=headers,
        json={"reason": "Switch to local fallback"},
    )
    execute_cancelled = await client.post(
        f"/api/v1/agent-runs/{run['id']}/execute",
        headers=headers,
    )
    retried = await client.post(
        f"/api/v1/agent-runs/{run['id']}/retry",
        headers=headers,
        json={"model_provider": "hermes", "model_name": "hermes-3"},
    )

    assert cancelled.status_code == 200
    assert cancelled.json()["state"] == "cancelled"
    assert execute_cancelled.status_code == 409
    assert retried.status_code == 201
    retry = retried.json()
    assert retry["attempt_number"] == 2
    assert retry["retry_of_run_id"] == run["id"]
    assert retry["context_package"]["id"] == run["context_package"]["id"]
    assert retry["model_provider"] == "hermes"
    assert retry["model_name"] == "hermes-3"


async def test_qa_verification_agent_promotes_reviewed_run_to_success(
    client: AsyncClient,
) -> None:
    headers = await auth_header(client)
    graph = await seed_graph(client, headers)
    run = await create_run(client, headers, graph["tasks"][0]["id"])
    await client.post(f"/api/v1/agent-runs/{run['id']}/execute", headers=headers)

    verified = await client.post(
        f"/api/v1/agent-runs/{run['id']}/verify",
        headers=headers,
    )

    assert verified.status_code == 200
    body = verified.json()
    assert body["source_run"]["state"] == "succeeded"
    assert body["qa_run"]["agent_key"] == "qa"
    assert body["qa_run"]["state"] == "succeeded"
    assert body["qa_run"]["output"]["verdict"] == "pass"
    assert body["qa_run"]["output"]["defects"] == []


async def test_run_console_lists_runs_with_usage_and_cost(client: AsyncClient) -> None:
    headers = await auth_header(client)
    graph = await seed_graph(client, headers)
    run = await create_run(client, headers, graph["tasks"][0]["id"])
    await client.post(f"/api/v1/agent-runs/{run['id']}/execute", headers=headers)

    response = await client.get("/api/v1/agent-runs", headers=headers)

    assert response.status_code == 200
    listed = next(item for item in response.json()["items"] if item["id"] == run["id"])
    assert listed["project_title"] == "Agent execution foundation"
    assert listed["task_title"]
    assert listed["usage"]["prompt_tokens"] > 0
    assert listed["usage"]["estimated_cost_cents"] >= 0


async def test_agent_run_events_support_resumable_sse_stream(client: AsyncClient) -> None:
    headers = await auth_header(client)
    graph = await seed_graph(client, headers)
    run = await create_run(client, headers, graph["tasks"][0]["id"])
    await client.post(f"/api/v1/agent-runs/{run['id']}/execute", headers=headers)

    response = await client.get(
        f"/api/v1/agent-runs/{run['id']}/events/stream?after_sequence=1&follow_seconds=0",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: run.state_changed" in response.text
    assert "event: run.output_generated" in response.text
    assert '"sequence":2' in response.text
    assert '"sequence":1' not in response.text

    resumed = await client.get(
        f"/api/v1/agent-runs/{run['id']}/events/stream?follow_seconds=0",
        headers={**headers, "Last-Event-ID": "3"},
    )

    assert resumed.status_code == 200
    assert '"sequence":2' not in resumed.text
    assert '"sequence":3' not in resumed.text
    assert '"sequence":4' in resumed.text
