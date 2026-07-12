from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select

from app.api.deps import AppSettings, CurrentOwner, DbSession
from app.models.project import Project
from app.schemas.execution_pack import ExecutionPackContent
from app.schemas.task_graph import TaskGraphResponse
from app.services.audit import write_audit_event
from app.services.execution_pack import get_execution_pack
from app.services.task_graph import (
    LoadedTaskGraph,
    RulesTaskGraphPlanner,
    create_or_get_task_graph,
    load_task_graph,
    task_response,
)
from app.services.workspace import get_or_create_default_workspace

router = APIRouter()


def _response(loaded: LoadedTaskGraph) -> TaskGraphResponse:
    assert loaded.version.approved_at is not None
    return TaskGraphResponse(
        id=loaded.graph.id,
        project_id=loaded.graph.project_id,
        status=loaded.graph.status,
        source_execution_pack_version_id=loaded.version.id,
        source_execution_pack_version_number=loaded.version.version_number,
        source_execution_pack_approved_at=loaded.version.approved_at,
        created_at=loaded.graph.created_at,
        tasks=[
            task_response(
                task,
                project_title=loaded.project.title,
                dependencies=loaded.dependencies[task.id],
            )
            for task in loaded.tasks
        ],
    )


@router.post(
    "/{project_id}/task-graph",
    response_model=TaskGraphResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_task_graph_route(
    project_id: UUID,
    request: Request,
    response: Response,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> TaskGraphResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    project_result = await session.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace.id)
    )
    project = project_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    pack_loaded = await get_execution_pack(session, project_id)
    if pack_loaded is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approve the current execution pack before task generation",
        )
    pack, versions = pack_loaded
    current = next(item for item in versions if item.version_number == pack.current_version_number)
    if pack.status != "approved" or current.approved_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approve the current execution pack before task generation",
        )
    graph, created = await create_or_get_task_graph(
        session,
        project=project,
        version=current,
        content=ExecutionPackContent.model_validate(current.content_json),
        planner=RulesTaskGraphPlanner(),
    )
    if created:
        await write_audit_event(
            session,
            workspace_id=workspace.id,
            actor_type="user",
            actor_id=owner.email,
            action="task_graph.created",
            resource_type="task_graph",
            resource_id=str(graph.id),
            request_id=getattr(request.state, "request_id", None),
            metadata={
                "project_id": str(project.id),
                "execution_pack_version_id": str(current.id),
                "execution_pack_version_number": current.version_number,
            },
        )
    else:
        response.status_code = status.HTTP_200_OK
    await session.commit()
    loaded = await load_task_graph(
        session,
        project_id=project.id,
        execution_pack_version_id=current.id,
    )
    assert loaded is not None
    return _response(loaded)


@router.get("/{project_id}/task-graph", response_model=TaskGraphResponse)
async def get_task_graph_route(
    project_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> TaskGraphResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    project_result = await session.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace.id)
    )
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    loaded = await load_task_graph(session, project_id=project_id)
    if loaded is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task graph not found")
    return _response(loaded)
