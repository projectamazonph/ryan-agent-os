from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.models.project import Project, ProjectCapture, ProjectStatusHistory
from app.schemas.project import ProjectCreate, ProjectFromCaptureRequest


async def create_project(
    session: AsyncSession,
    workspace_id: UUID,
    payload: ProjectCreate,
) -> Project:
    project = Project(
        workspace_id=workspace_id,
        title=payload.title.strip(),
        summary=payload.summary.strip() if payload.summary else None,
        domain=payload.domain,
        status=payload.status,
        priority=payload.priority,
        next_action=payload.next_action.strip() if payload.next_action else None,
        blocker=payload.blocker.strip() if payload.blocker else None,
    )
    session.add(project)
    await session.flush()
    session.add(
        ProjectStatusHistory(
            project_id=project.id,
            from_status=None,
            to_status=project.status,
            reason="project.created",
        )
    )
    await session.flush()
    return project


async def link_capture(
    session: AsyncSession,
    project: Project,
    capture: Capture,
    relationship_type: str = "reference",
) -> bool:
    result = await session.execute(
        select(ProjectCapture).where(
            ProjectCapture.project_id == project.id,
            ProjectCapture.capture_id == capture.id,
        )
    )
    if result.scalar_one_or_none() is not None:
        capture.review_status = "linked"
        return False
    session.add(
        ProjectCapture(
            project_id=project.id,
            capture_id=capture.id,
            relationship_type=relationship_type,
        )
    )
    capture.review_status = "linked"
    await session.flush()
    return True


def _capture_domain(capture: Capture) -> str | None:
    if capture.classification and isinstance(capture.classification.get("domain"), str):
        return str(capture.classification["domain"])
    return capture.domain_hint


async def create_project_from_capture(
    session: AsyncSession,
    workspace_id: UUID,
    capture: Capture,
    payload: ProjectFromCaptureRequest,
) -> Project:
    summary = payload.summary or capture.summary or capture.content[:4000] or None
    project = await create_project(
        session,
        workspace_id,
        ProjectCreate(
            title=payload.title or capture.title,
            summary=summary,
            domain=_capture_domain(capture),
            status=payload.status,
            priority=payload.priority,
            next_action=payload.next_action,
            blocker=payload.blocker,
        ),
    )
    await link_capture(session, project, capture, relationship_type="origin")
    return project


async def project_captures(session: AsyncSession, project_id: UUID) -> list[Capture]:
    result = await session.execute(
        select(Capture)
        .join(ProjectCapture, ProjectCapture.capture_id == Capture.id)
        .where(ProjectCapture.project_id == project_id)
        .order_by(Capture.created_at)
    )
    return list(result.scalars().all())


async def capture_projects(session: AsyncSession, capture_id: UUID) -> list[Project]:
    result = await session.execute(
        select(Project)
        .join(ProjectCapture, ProjectCapture.project_id == Project.id)
        .where(ProjectCapture.capture_id == capture_id)
        .order_by(desc(Project.updated_at))
    )
    return list(result.scalars().all())


async def list_projects(
    session: AsyncSession,
    workspace_id: UUID,
    *,
    query: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[Project]:
    statement = select(Project).where(Project.workspace_id == workspace_id)
    if query:
        pattern = f"%{query.strip()}%"
        statement = statement.where(
            or_(
                Project.title.ilike(pattern),
                Project.summary.ilike(pattern),
                Project.domain.ilike(pattern),
                Project.next_action.ilike(pattern),
            )
        )
    if status:
        statement = statement.where(Project.status == status)
    result = await session.execute(statement.order_by(desc(Project.updated_at)).limit(limit))
    return list(result.scalars().all())
