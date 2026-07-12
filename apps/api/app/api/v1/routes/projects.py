from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import select

from app.api.deps import AppSettings, CurrentOwner, DbSession
from app.models.capture import Capture
from app.models.execution_pack import ExecutionPack, ExecutionPackVersion
from app.models.project import Project
from app.schemas.capture import CaptureResponse
from app.schemas.execution_pack import (
    ExecutionPackApproveRequest,
    ExecutionPackContent,
    ExecutionPackGenerateRequest,
    ExecutionPackResponse,
    ExecutionPackVersionResponse,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
)
from app.services.audit import write_audit_event
from app.services.execution_pack import (
    RulesExecutionPlanner,
    approve_execution_pack,
    generate_execution_pack,
    get_execution_pack,
)
from app.services.project import create_project, link_capture, list_projects, project_captures
from app.services.workspace import get_or_create_default_workspace

router = APIRouter()


async def _detail(session: DbSession, project: Project) -> ProjectDetailResponse:
    captures = await project_captures(session, project.id)
    return ProjectDetailResponse(
        **ProjectResponse.model_validate(project).model_dump(),
        captures=[CaptureResponse.model_validate(item) for item in captures],
    )


@router.post("", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_project_route(
    payload: ProjectCreate,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ProjectDetailResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    project = await create_project(session, workspace.id, payload)
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="project.created",
        resource_type="project",
        resource_id=str(project.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"status": project.status, "domain": project.domain},
    )
    await session.commit()
    await session.refresh(project)
    return await _detail(session, project)


@router.get("", response_model=ProjectListResponse)
async def list_projects_route(
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
    q: str | None = Query(default=None, max_length=200),
    project_status: str | None = Query(default=None, alias="status", max_length=24),
    limit: int = Query(default=50, ge=1, le=100),
) -> ProjectListResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    items = await list_projects(
        session,
        workspace.id,
        query=q,
        status=project_status,
        limit=limit,
    )
    return ProjectListResponse(items=[ProjectResponse.model_validate(item) for item in items])


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_route(
    project_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ProjectDetailResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace.id)
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return await _detail(session, project)


@router.post("/{project_id}/captures/{capture_id}", response_model=ProjectDetailResponse)
async def link_capture_route(
    project_id: UUID,
    capture_id: UUID,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ProjectDetailResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    project_result = await session.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace.id)
    )
    project = project_result.scalar_one_or_none()
    capture_result = await session.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace.id)
    )
    capture = capture_result.scalar_one_or_none()
    if project is None or capture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project or capture not found",
        )
    created = await link_capture(session, project, capture)
    if created:
        await write_audit_event(
            session,
            workspace_id=workspace.id,
            actor_type="user",
            actor_id=owner.email,
            action="project.capture_linked",
            resource_type="project",
            resource_id=str(project.id),
            request_id=getattr(request.state, "request_id", None),
            metadata={"capture_id": str(capture.id)},
        )
    await session.commit()
    await session.refresh(project)
    return await _detail(session, project)


def _execution_pack_response(
    pack: ExecutionPack, versions: list[ExecutionPackVersion]
) -> ExecutionPackResponse:
    version_responses = [
        ExecutionPackVersionResponse(
            id=version.id,
            version_number=version.version_number,
            content=ExecutionPackContent.model_validate(version.content_json),
            change_summary=version.change_summary,
            created_at=version.created_at,
            approved_at=version.approved_at,
        )
        for version in versions
    ]
    current = next(
        item for item in version_responses if item.version_number == pack.current_version_number
    )
    return ExecutionPackResponse(
        id=pack.id,
        project_id=pack.project_id,
        status=pack.status,
        current_version_number=pack.current_version_number,
        current_version=current,
        versions=version_responses,
    )


@router.post(
    "/{project_id}/execution-pack",
    response_model=ExecutionPackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_execution_pack_route(
    project_id: UUID,
    payload: ExecutionPackGenerateRequest,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ExecutionPackResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace.id)
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    captures = await project_captures(session, project.id)
    pack, version = await generate_execution_pack(
        session,
        project,
        captures,
        RulesExecutionPlanner(),
        payload.change_summary,
    )
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="execution_pack.version_created",
        resource_type="execution_pack",
        resource_id=str(pack.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"project_id": str(project.id), "version_number": version.version_number},
    )
    await session.commit()
    loaded = await get_execution_pack(session, project.id)
    assert loaded is not None
    return _execution_pack_response(*loaded)


@router.get(
    "/{project_id}/execution-pack",
    response_model=ExecutionPackResponse,
)
async def get_execution_pack_route(
    project_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ExecutionPackResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    project_result = await session.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace.id)
    )
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    loaded = await get_execution_pack(session, project_id)
    if loaded is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution pack not found",
        )
    return _execution_pack_response(*loaded)


@router.post(
    "/{project_id}/execution-pack/approve",
    response_model=ExecutionPackResponse,
)
async def approve_execution_pack_route(
    project_id: UUID,
    payload: ExecutionPackApproveRequest,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ExecutionPackResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    project_result = await session.execute(
        select(Project).where(Project.id == project_id, Project.workspace_id == workspace.id)
    )
    if project_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    loaded = await get_execution_pack(session, project_id)
    if loaded is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution pack not found",
        )
    pack, versions = loaded
    try:
        version = await approve_execution_pack(
            session, pack, versions, payload.version_number
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="execution_pack.approved",
        resource_type="execution_pack",
        resource_id=str(pack.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"project_id": str(project_id), "version_number": version.version_number},
    )
    await session.commit()
    loaded = await get_execution_pack(session, project_id)
    assert loaded is not None
    return _execution_pack_response(*loaded)
