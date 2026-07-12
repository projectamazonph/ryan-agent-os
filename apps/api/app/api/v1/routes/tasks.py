from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import AppSettings, CurrentOwner, DbSession
from app.models.project import Project
from app.models.task import Task
from app.schemas.task_graph import ImplementationQueueResponse, TaskResponse, TaskStatusUpdate
from app.services.audit import write_audit_event
from app.services.task_graph import (
    list_implementation_queue,
    load_task_graph,
    task_response,
    unresolved_dependency_keys,
    update_task_status,
)
from app.services.workspace import get_or_create_default_workspace

router = APIRouter()


@router.get("/queue", response_model=ImplementationQueueResponse)
async def implementation_queue_route(
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ImplementationQueueResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    return ImplementationQueueResponse(items=await list_implementation_queue(session, workspace.id))


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_route(
    task_id: UUID,
    payload: TaskStatusUpdate,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> TaskResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.workspace_id == workspace.id)
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    loaded = await load_task_graph(session, project_id=task.project_id)
    if loaded is None or task.id not in loaded.dependencies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is not part of the active task graph",
        )
    blocked_by = unresolved_dependency_keys(loaded.dependencies[task.id])
    if payload.status in {"in_progress", "done"} and blocked_by:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task is blocked by: {', '.join(blocked_by)}",
        )
    previous_status = task.status
    try:
        await update_task_status(task, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="task.status_changed",
        resource_type="task",
        resource_id=str(task.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"from_status": previous_status, "to_status": task.status},
    )
    await session.commit()
    await session.refresh(task)
    project_result = await session.execute(select(Project).where(Project.id == task.project_id))
    project = project_result.scalar_one()
    return task_response(
        task,
        project_title=project.title,
        dependencies=loaded.dependencies.get(task.id, []),
    )
