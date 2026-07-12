from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from time import monotonic
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.deps import AppSettings, CurrentOwner, DbSession
from app.models.agent import AgentRun, AgentRunEvent
from app.models.task import Task
from app.schemas.agent import (
    AgentRunCancelRequest,
    AgentRunCreate,
    AgentRunEventListResponse,
    AgentRunListResponse,
    AgentRunResponse,
    AgentRunRetryRequest,
    AgentToolInvocationResponse,
    AgentVerificationResponse,
    ToolInvocationRequest,
)
from app.services.agent_context import build_context_package
from app.services.agent_registry import get_agent_definition
from app.services.agent_runs import (
    AgentRunStateError,
    LoadedAgentRun,
    cancel_agent_run,
    create_agent_run,
    event_response,
    execute_agent_run,
    list_agent_runs,
    list_run_events,
    load_agent_run,
    record_tool_invocation,
    retry_agent_run,
    run_response,
    tool_invocation_response,
    verify_agent_run,
)
from app.services.audit import write_audit_event
from app.services.task_graph import load_task_graph, unresolved_dependency_keys
from app.services.workspace import get_or_create_default_workspace

router = APIRouter()


def _model_defaults(settings: AppSettings, payload: AgentRunCreate) -> tuple[str, str]:
    provider = payload.model_provider or settings.model_provider
    if payload.model_name:
        name = payload.model_name
    elif provider == "rules":
        name = "rules-v1"
    else:
        name = settings.model_name
    return provider, name


async def _owned_loaded_run(session: DbSession, workspace_id: UUID, run_id: UUID) -> LoadedAgentRun:
    loaded = await load_agent_run(session, run_id)
    if loaded is None or loaded.run.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")
    return loaded


@router.post(
    "/tasks/{task_id}/agent-runs",
    response_model=AgentRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent_run_route(
    task_id: UUID,
    payload: AgentRunCreate,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentRunResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    task_result = await session.execute(
        select(Task).where(Task.id == task_id, Task.workspace_id == workspace.id)
    )
    task = task_result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    graph = await load_task_graph(session, project_id=task.project_id)
    if graph is None or task.id not in graph.dependencies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is not part of the active task graph",
        )
    blocked_by = unresolved_dependency_keys(graph.dependencies[task.id])
    if blocked_by:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task is blocked by: {', '.join(blocked_by)}",
        )
    if task.status not in {"planned", "in_progress"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task in state {task.status} cannot launch an agent run",
        )
    definition = await get_agent_definition(
        session, workspace.id, payload.agent_key, payload.agent_version
    )
    if definition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    context = await build_context_package(session, task=task, definition=definition)
    provider, model_name = _model_defaults(settings, payload)
    run = await create_agent_run(
        session,
        task=task,
        definition=definition,
        context=context,
        model_provider=provider,
        model_name=model_name,
    )
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="agent_run.created",
        resource_type="agent_run",
        resource_id=str(run.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={
            "task_id": str(task.id),
            "agent_key": definition.key,
            "agent_version": definition.version,
            "context_checksum": context.checksum_sha256,
        },
    )
    await session.commit()
    loaded = await load_agent_run(session, run.id)
    assert loaded is not None
    return run_response(loaded)


@router.get("/agent-runs", response_model=AgentRunListResponse)
async def list_agent_runs_route(
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentRunListResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    runs = await list_agent_runs(session, workspace.id)
    return AgentRunListResponse(items=[run_response(item) for item in runs])


@router.get("/agent-runs/{run_id}/events/stream")
async def stream_agent_run_events_route(
    run_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
    after_sequence: int = Query(default=0, ge=0),
    follow_seconds: float = Query(default=15, ge=0, le=60),
    last_event_id: int | None = Header(default=None, alias="Last-Event-ID", ge=0),
) -> StreamingResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    await _owned_loaded_run(session, workspace.id, run_id)
    if session.bind is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable",
        )
    stream_session_factory = async_sessionmaker(session.bind, expire_on_commit=False)

    async def event_stream() -> AsyncIterator[str]:
        cursor = max(after_sequence, last_event_id or 0)
        deadline = monotonic() + follow_seconds
        terminal_states = {"succeeded", "failed", "cancelled"}

        async with stream_session_factory() as stream_session:
            while True:
                result = await stream_session.execute(
                    select(AgentRunEvent)
                    .where(
                        AgentRunEvent.run_id == run_id,
                        AgentRunEvent.sequence > cursor,
                    )
                    .order_by(AgentRunEvent.sequence)
                )
                events = list(result.scalars().all())
                for event in events:
                    payload = event_response(event).model_dump(mode="json")
                    yield (
                        f"id: {event.sequence}\n"
                        f"event: {event.event_type}\n"
                        f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"
                    )
                    cursor = event.sequence

                state_result = await stream_session.execute(
                    select(AgentRun.state).where(AgentRun.id == run_id)
                )
                run_state = state_result.scalar_one_or_none()
                if run_state is None or (run_state in terminal_states and not events):
                    break
                if follow_seconds == 0 or monotonic() >= deadline:
                    break

                yield ": heartbeat\n\n"
                await asyncio.sleep(0.25)
                stream_session.expire_all()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/agent-runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run_route(
    run_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentRunResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    return run_response(await _owned_loaded_run(session, workspace.id, run_id))


@router.get("/agent-runs/{run_id}/events", response_model=AgentRunEventListResponse)
async def get_agent_run_events_route(
    run_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentRunEventListResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    await _owned_loaded_run(session, workspace.id, run_id)
    events = await list_run_events(session, run_id)
    return AgentRunEventListResponse(items=[event_response(item) for item in events])


@router.post("/agent-runs/{run_id}/execute", response_model=AgentRunResponse)
async def execute_agent_run_route(
    run_id: UUID,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentRunResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    loaded = await _owned_loaded_run(session, workspace.id, run_id)
    try:
        await execute_agent_run(
            session,
            loaded.run,
            definition=loaded.definition,
            context=loaded.context,
        )
    except AgentRunStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="agent_run.executed",
        resource_type="agent_run",
        resource_id=str(run_id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"state": loaded.run.state},
    )
    await session.commit()
    refreshed = await load_agent_run(session, run_id)
    assert refreshed is not None
    return run_response(refreshed)


@router.post("/agent-runs/{run_id}/cancel", response_model=AgentRunResponse)
async def cancel_agent_run_route(
    run_id: UUID,
    payload: AgentRunCancelRequest,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentRunResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    loaded = await _owned_loaded_run(session, workspace.id, run_id)
    try:
        await cancel_agent_run(session, loaded.run, reason=payload.reason)
    except AgentRunStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="agent_run.cancelled",
        resource_type="agent_run",
        resource_id=str(run_id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"reason": payload.reason},
    )
    await session.commit()
    refreshed = await load_agent_run(session, run_id)
    assert refreshed is not None
    return run_response(refreshed)


@router.post(
    "/agent-runs/{run_id}/retry",
    response_model=AgentRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def retry_agent_run_route(
    run_id: UUID,
    payload: AgentRunRetryRequest,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentRunResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    loaded = await _owned_loaded_run(session, workspace.id, run_id)
    try:
        retried = await retry_agent_run(
            session,
            loaded.run,
            task=loaded.task,
            definition=loaded.definition,
            context=loaded.context,
            model_provider=payload.model_provider,
            model_name=payload.model_name,
        )
    except AgentRunStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="agent_run.retried",
        resource_type="agent_run",
        resource_id=str(retried.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"retry_of_run_id": str(run_id), "attempt_number": retried.attempt_number},
    )
    await session.commit()
    refreshed = await load_agent_run(session, retried.id)
    assert refreshed is not None
    return run_response(refreshed)


@router.post("/agent-runs/{run_id}/verify", response_model=AgentVerificationResponse)
async def verify_agent_run_route(
    run_id: UUID,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentVerificationResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    loaded = await _owned_loaded_run(session, workspace.id, run_id)
    qa_definition = await get_agent_definition(session, workspace.id, "qa")
    assert qa_definition is not None
    try:
        qa_run = await verify_agent_run(
            session,
            source=loaded.run,
            task=loaded.task,
            qa_definition=qa_definition,
            context=loaded.context,
        )
    except AgentRunStateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="agent",
        actor_id=f"qa:v{qa_definition.version}",
        action="agent_run.verified",
        resource_type="agent_run",
        resource_id=str(run_id),
        request_id=getattr(request.state, "request_id", None),
        metadata={
            "qa_run_id": str(qa_run.id),
            "verdict": (qa_run.output_json or {}).get("verdict"),
        },
    )
    await session.commit()
    source_loaded = await load_agent_run(session, run_id)
    qa_loaded = await load_agent_run(session, qa_run.id)
    assert source_loaded is not None and qa_loaded is not None
    return AgentVerificationResponse(
        source_run=run_response(source_loaded),
        qa_run=run_response(qa_loaded),
    )


@router.post(
    "/agent-runs/{run_id}/tool-invocations",
    response_model=AgentToolInvocationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_tool_invocation_route(
    run_id: UUID,
    payload: ToolInvocationRequest,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> AgentToolInvocationResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    loaded = await _owned_loaded_run(session, workspace.id, run_id)
    invocation = await record_tool_invocation(
        session,
        run=loaded.run,
        tool_name=payload.tool_name,
        arguments=payload.arguments,
    )
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action=f"agent_tool.{invocation.decision}",
        resource_type="agent_run",
        resource_id=str(run_id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"tool_name": payload.tool_name, "arguments_hash": invocation.arguments_hash},
    )
    await session.commit()
    if invocation.decision == "denied":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=invocation.error_text,
        )
    return tool_invocation_response(invocation)
