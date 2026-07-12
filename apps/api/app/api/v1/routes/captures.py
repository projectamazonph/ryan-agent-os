from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import select

from app.api.deps import AppSettings, CurrentOwner, DbSession, JobQueueDep, ObjectStoreDep
from app.models.capture import Capture
from app.models.source import SourceObject
from app.schemas.capture import CaptureCreate, CaptureListResponse, CaptureResponse, Sensitivity
from app.schemas.project import ProjectDetailResponse, ProjectFromCaptureRequest, ProjectResponse
from app.schemas.relation import CaptureRelationCreate, CaptureRelationResponse
from app.schemas.source import (
    CaptureReviewResponse,
    FileCaptureResponse,
    RelatedCaptureResponse,
    SourceObjectResponse,
)
from app.services.audit import write_audit_event
from app.services.capture import create_capture, list_captures
from app.services.project import (
    capture_projects,
    create_project_from_capture,
    project_captures,
)
from app.services.related import find_related_captures
from app.services.relations import SelfRelationError, create_capture_relation
from app.services.source import (
    UnsupportedSourceTypeError,
    UploadTooLargeError,
    create_file_capture,
    read_upload,
)
from app.services.workspace import get_or_create_default_workspace

router = APIRouter()


@router.post("", response_model=CaptureResponse, status_code=status.HTTP_201_CREATED)
async def create_capture_route(
    payload: CaptureCreate,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
    queue: JobQueueDep,
) -> CaptureResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    capture, created = await create_capture(session, workspace.id, payload)
    if created:
        await write_audit_event(
            session,
            workspace_id=workspace.id,
            actor_type="user",
            actor_id=owner.email,
            action="capture.created",
            resource_type="capture",
            resource_id=str(capture.id),
            request_id=getattr(request.state, "request_id", None),
            metadata={"type": capture.type, "sensitivity": capture.sensitivity},
        )
    await session.commit()
    await session.refresh(capture)

    if created and settings.auto_process_captures:
        await queue.enqueue(
            "capture.process", {"capture_id": str(capture.id)}
        )

    return CaptureResponse.model_validate(capture)


@router.post("/files", response_model=FileCaptureResponse, status_code=status.HTTP_201_CREATED)
async def upload_capture_file_route(
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
    store: ObjectStoreDep,
    queue: JobQueueDep,
    file: Annotated[UploadFile, File()],
    title: Annotated[str | None, Form(max_length=300)] = None,
    domain_hint: Annotated[str | None, Form(max_length=80)] = None,
    sensitivity: Annotated[Sensitivity, Form()] = "internal",
) -> FileCaptureResponse:
    try:
        body = await read_upload(file, settings.max_upload_bytes)
    except UnsupportedSourceTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        ) from exc
    except UploadTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds upload limit",
        ) from exc

    workspace = await get_or_create_default_workspace(session, settings)
    capture, source, created = await create_file_capture(
        session,
        store,
        workspace.id,
        body=body,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        title=title,
        domain_hint=domain_hint,
        sensitivity=sensitivity,
    )
    if created:
        await write_audit_event(
            session,
            workspace_id=workspace.id,
            actor_type="user",
            actor_id=owner.email,
            action="capture.file_uploaded",
            resource_type="source_object",
            resource_id=str(source.id),
            request_id=getattr(request.state, "request_id", None),
            metadata={
                "capture_id": str(capture.id),
                "filename": source.original_filename,
                "content_type": source.content_type,
                "size_bytes": source.size_bytes,
            },
        )
    await session.commit()
    await session.refresh(capture)
    await session.refresh(source)

    if created and settings.auto_process_captures:
        await queue.enqueue(
            "source.extract", {"source_id": str(source.id)}
        )

    return FileCaptureResponse(
        capture=CaptureResponse.model_validate(capture),
        source=SourceObjectResponse.model_validate(source),
    )


@router.get("", response_model=CaptureListResponse)
async def list_capture_route(
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
    limit: int = Query(default=50, ge=1, le=100),
) -> CaptureListResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    items = await list_captures(session, workspace.id, limit)
    return CaptureListResponse(items=[CaptureResponse.model_validate(item) for item in items])


@router.get("/{capture_id}/review", response_model=CaptureReviewResponse)
async def get_capture_review_route(
    capture_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> CaptureReviewResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace.id)
    )
    capture = result.scalar_one_or_none()
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")

    source_result = await session.execute(
        select(SourceObject).where(SourceObject.capture_id == capture.id)
    )
    source = source_result.scalar_one_or_none()
    related = await find_related_captures(session, capture)
    projects = await capture_projects(session, capture.id)
    return CaptureReviewResponse(
        capture=CaptureResponse.model_validate(capture),
        source=SourceObjectResponse.model_validate(source) if source is not None else None,
        related=[
            RelatedCaptureResponse(
                capture=CaptureResponse.model_validate(item.capture),
                score=item.score,
                reasons=item.reasons,
            )
            for item in related
        ],
        projects=[ProjectResponse.model_validate(item) for item in projects],
    )


@router.post(
    "/{capture_id}/projects",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_from_capture_route(
    capture_id: UUID,
    payload: ProjectFromCaptureRequest,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> ProjectDetailResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace.id)
    )
    capture = result.scalar_one_or_none()
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    project = await create_project_from_capture(session, workspace.id, capture, payload)
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="project.created_from_capture",
        resource_type="project",
        resource_id=str(project.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"capture_id": str(capture.id), "status": project.status},
    )
    await session.commit()
    await session.refresh(project)
    captures = await project_captures(session, project.id)
    return ProjectDetailResponse(
        **ProjectResponse.model_validate(project).model_dump(),
        captures=[CaptureResponse.model_validate(item) for item in captures],
    )


@router.post("/{capture_id}/archive", response_model=CaptureResponse)
async def archive_capture_route(
    capture_id: UUID,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> CaptureResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace.id)
    )
    capture = result.scalar_one_or_none()
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    capture.review_status = "archived"
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="capture.archived",
        resource_type="capture",
        resource_id=str(capture.id),
        request_id=getattr(request.state, "request_id", None),
    )
    await session.commit()
    await session.refresh(capture)
    return CaptureResponse.model_validate(capture)


@router.post(
    "/{capture_id}/retry",
    response_model=FileCaptureResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def retry_capture_route(
    capture_id: UUID,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
    queue: JobQueueDep,
) -> FileCaptureResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace.id)
    )
    capture = result.scalar_one_or_none()
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    source_result = await session.execute(
        select(SourceObject).where(SourceObject.capture_id == capture.id)
    )
    source = source_result.scalar_one_or_none()
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capture has no file source",
        )
    if source.extraction_status != "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Only failed extraction can be retried"
        )
    source.extraction_status = "pending"
    source.extraction_error = None
    capture.status = "queued"
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action="source.extraction_retried",
        resource_type="source_object",
        resource_id=str(source.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={"capture_id": str(capture.id), "attempts": source.extraction_attempts},
    )
    await session.commit()
    await queue.enqueue("source.extract", {"source_id": str(source.id)})
    await session.refresh(capture)
    await session.refresh(source)
    return FileCaptureResponse(
        capture=CaptureResponse.model_validate(capture),
        source=SourceObjectResponse.model_validate(source),
    )


@router.post(
    "/{capture_id}/relations",
    response_model=CaptureRelationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_capture_relation_route(
    capture_id: UUID,
    payload: CaptureRelationCreate,
    response: Response,
    request: Request,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> CaptureRelationResponse:
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Capture).where(
            Capture.workspace_id == workspace.id,
            Capture.id.in_([capture_id, payload.target_capture_id]),
        )
    )
    captures = {item.id: item for item in result.scalars().all()}
    source = captures.get(capture_id)
    target = captures.get(payload.target_capture_id)
    if source is None or target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    try:
        relation, created = await create_capture_relation(
            session, source, target, payload.action
        )
    except SelfRelationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await write_audit_event(
        session,
        workspace_id=workspace.id,
        actor_type="user",
        actor_id=owner.email,
        action=f"capture.{payload.action}",
        resource_type="capture_relation",
        resource_id=str(relation.id),
        request_id=getattr(request.state, "request_id", None),
        metadata={
            "source_capture_id": str(source.id),
            "target_capture_id": str(target.id),
            "created": created,
        },
    )
    await session.commit()
    await session.refresh(relation)
    if not created:
        response.status_code = status.HTTP_200_OK
    return CaptureRelationResponse.model_validate(relation)


@router.get("/{capture_id}", response_model=CaptureResponse)
async def get_capture_route(
    capture_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
) -> CaptureResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace.id)
    )
    capture = result.scalar_one_or_none()
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    return CaptureResponse.model_validate(capture)


@router.post("/{capture_id}/process", response_model=CaptureResponse)
async def process_capture_route(
    capture_id: UUID,
    owner: CurrentOwner,
    settings: AppSettings,
    session: DbSession,
    queue: JobQueueDep,
) -> CaptureResponse:
    del owner
    workspace = await get_or_create_default_workspace(session, settings)
    result = await session.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace.id)
    )
    capture = result.scalar_one_or_none()
    if capture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")

    source_result = await session.execute(
        select(SourceObject).where(SourceObject.capture_id == capture.id)
    )
    source = source_result.scalar_one_or_none()
    if source is not None:
        await queue.enqueue("source.extract", {"source_id": str(source.id)})
        source.extraction_status = "queued"
    else:
        await queue.enqueue("capture.process", {"capture_id": str(capture.id)})
    capture.status = "queued"
    await session.commit()
    await session.refresh(capture)
    return CaptureResponse.model_validate(capture)
