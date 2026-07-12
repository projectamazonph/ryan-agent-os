from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.models.project import Project, ProjectCapture
from app.models.relation import CaptureRelation


class SelfRelationError(ValueError):
    pass


async def create_capture_relation(
    session: AsyncSession,
    source: Capture,
    target: Capture,
    action: str,
) -> tuple[CaptureRelation, bool]:
    if source.id == target.id:
        raise SelfRelationError("A capture cannot relate to itself")
    relation_type = "merged_into" if action == "merge" else "reference"
    result = await session.execute(
        select(CaptureRelation).where(
            CaptureRelation.source_capture_id == source.id,
            CaptureRelation.target_capture_id == target.id,
            CaptureRelation.relation_type == relation_type,
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing, False

    relation = CaptureRelation(
        workspace_id=source.workspace_id,
        source_capture_id=source.id,
        target_capture_id=target.id,
        relation_type=relation_type,
    )
    session.add(relation)
    if action == "merge":
        source.review_status = "merged"
        target_projects = (
            await session.execute(
                select(Project)
                .join(ProjectCapture, ProjectCapture.project_id == Project.id)
                .where(ProjectCapture.capture_id == target.id)
            )
        ).scalars().all()
        for project in target_projects:
            link_result = await session.execute(
                select(ProjectCapture).where(
                    ProjectCapture.project_id == project.id,
                    ProjectCapture.capture_id == source.id,
                )
            )
            if link_result.scalar_one_or_none() is None:
                session.add(
                    ProjectCapture(
                        project_id=project.id,
                        capture_id=source.id,
                        relationship_type="merged_source",
                    )
                )
    else:
        source.review_status = "referenced"
    await session.flush()
    return relation, True
