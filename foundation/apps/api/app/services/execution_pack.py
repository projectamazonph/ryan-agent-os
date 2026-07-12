from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capture import Capture
from app.models.execution_pack import ExecutionPack, ExecutionPackVersion
from app.models.project import Project
from app.schemas.execution_pack import (
    DeliverableSpec,
    ExecutionPackContent,
    WorkstreamSpec,
)


class ExecutionPlanner(Protocol):
    async def plan(self, project: Project, captures: list[Capture]) -> ExecutionPackContent: ...


class RulesExecutionPlanner:
    """Deterministic first planner used as the TDD-safe baseline."""

    async def plan(self, project: Project, captures: list[Capture]) -> ExecutionPackContent:
        context_titles = [capture.title for capture in captures[:8]]
        context_text = " ".join(capture.content for capture in captures[:8]).lower()
        objective = project.summary or f"Complete {project.title} with a verifiable delivery path."
        problem = (
            f"{project.title} needs a bounded, sequenced implementation plan that converts "
            "captured context into approved deliverables and executable work."
        )
        deliverables = [
            DeliverableSpec(
                name="Task graph",
                description=(
                    "A dependency-aware implementation plan derived from the approved "
                    "execution pack."
                ),
                format="application/json",
                acceptance_criteria=[
                    "Every task has a clear outcome",
                    "Dependencies contain no cycles",
                    "Each task has verification evidence",
                ],
            ),
            DeliverableSpec(
                name="Validated implementation",
                description="The smallest production-ready implementation that satisfies the pack.",
                format="source-code",
                acceptance_criteria=[
                    "Tests are written before implementation",
                    "The full regression gate passes",
                    "Documentation reflects actual behavior",
                ],
            ),
        ]
        if "document" in context_text or "documentation" in context_text:
            deliverables.append(
                DeliverableSpec(
                    name="Documentation update",
                    description="Versioned operating and implementation documentation.",
                    format="text/markdown",
                    acceptance_criteria=[
                        "No unresolved placeholders",
                        "All internal links resolve",
                    ],
                )
            )
        workstreams = [
            WorkstreamSpec(
                name="Specification and tests",
                goal="Convert the approved scope into failing acceptance and integration tests.",
                steps=[
                    "Confirm bounded scope",
                    "Write failing tests for the next vertical slice",
                    "Record expected evidence",
                ],
            ),
            WorkstreamSpec(
                name="Implementation loop",
                goal="Make the smallest change that satisfies each failing test.",
                steps=[
                    "Implement the minimum passing behavior",
                    "Refactor while tests remain green",
                    "Run static, migration, security, and production-build gates",
                ],
            ),
        ]
        return ExecutionPackContent(
            objective=objective,
            problem_statement=problem,
            success_criteria=[
                "The documented objective is delivered",
                "All acceptance tests and release gates pass",
                "The implementation remains auditable and reversible",
            ],
            in_scope=[
                project.next_action or "Define the next executable action",
                "Versioned execution planning",
                "TDD and Loop Engineering evidence",
                *context_titles[:3],
            ],
            out_of_scope=[
                "Unapproved external writes",
                "Features not required by the current execution pack",
            ],
            assumptions=[
                "The current project and linked captures are the source of truth",
                "Protected actions require explicit approval",
            ],
            deliverables=deliverables,
            workstreams=workstreams,
            risks=[
                project.blocker or "Scope may expand faster than the current implementation loop",
                "Generated plans require human review before task creation",
            ],
            recommended_agents=["planner", "implementer", "qa", "documentation"],
        )


async def generate_execution_pack(
    session: AsyncSession,
    project: Project,
    captures: list[Capture],
    planner: ExecutionPlanner,
    change_summary: str | None,
) -> tuple[ExecutionPack, ExecutionPackVersion]:
    result = await session.execute(
        select(ExecutionPack).where(ExecutionPack.project_id == project.id)
    )
    pack = result.scalar_one_or_none()
    if pack is None:
        pack = ExecutionPack(
            workspace_id=project.workspace_id,
            project_id=project.id,
            status="draft",
            current_version_number=0,
        )
        session.add(pack)
        await session.flush()

    content = await planner.plan(project, captures)
    next_version = pack.current_version_number + 1
    version = ExecutionPackVersion(
        execution_pack_id=pack.id,
        version_number=next_version,
        content_json=content.model_dump(mode="json"),
        change_summary=change_summary.strip() if change_summary else None,
    )
    session.add(version)
    pack.current_version_number = next_version
    pack.status = "draft"
    await session.flush()
    return pack, version


async def get_execution_pack(
    session: AsyncSession, project_id: UUID
) -> tuple[ExecutionPack, list[ExecutionPackVersion]] | None:
    result = await session.execute(
        select(ExecutionPack).where(ExecutionPack.project_id == project_id)
    )
    pack = result.scalar_one_or_none()
    if pack is None:
        return None
    versions_result = await session.execute(
        select(ExecutionPackVersion)
        .where(ExecutionPackVersion.execution_pack_id == pack.id)
        .order_by(ExecutionPackVersion.version_number)
    )
    return pack, list(versions_result.scalars().all())


async def approve_execution_pack(
    session: AsyncSession,
    pack: ExecutionPack,
    versions: list[ExecutionPackVersion],
    version_number: int,
) -> ExecutionPackVersion:
    version = next((item for item in versions if item.version_number == version_number), None)
    if version is None:
        raise LookupError(f"Execution pack version {version_number} not found")
    version.approved_at = datetime.now(UTC)
    pack.current_version_number = version_number
    pack.status = "approved"
    await session.flush()
    return version
