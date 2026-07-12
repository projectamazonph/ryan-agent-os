from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import AgentContextPackage, AgentDefinition
from app.models.capture import Capture
from app.models.execution_pack import ExecutionPackVersion
from app.models.project import Project, ProjectCapture
from app.models.task import Task, TaskGraph
from app.schemas.execution_pack import ExecutionPackContent


def _canonical_checksum(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


async def build_context_package(
    session: AsyncSession,
    *,
    task: Task,
    definition: AgentDefinition,
) -> AgentContextPackage:
    graph_result = await session.execute(
        select(TaskGraph).where(TaskGraph.id == task.task_graph_id)
    )
    graph = graph_result.scalar_one()
    project_result = await session.execute(select(Project).where(Project.id == task.project_id))
    project = project_result.scalar_one()
    version_result = await session.execute(
        select(ExecutionPackVersion).where(
            ExecutionPackVersion.id == graph.execution_pack_version_id
        )
    )
    version = version_result.scalar_one()
    content = ExecutionPackContent.model_validate(version.content_json)
    capture_result = await session.execute(
        select(Capture)
        .join(ProjectCapture, ProjectCapture.capture_id == Capture.id)
        .where(ProjectCapture.project_id == project.id)
        .order_by(Capture.created_at.desc())
        .limit(8)
    )
    captures = list(capture_result.scalars().all())
    source_excerpts = [
        {
            "capture_id": str(capture.id),
            "title": capture.title,
            "type": capture.type,
            "sensitivity": capture.sensitivity,
            "excerpt": capture.content[:2000],
        }
        for capture in captures
    ]
    acceptance_criteria = [task.verification, *content.success_criteria]
    decisions_constraints = [*content.assumptions, *content.out_of_scope]
    payload: dict[str, Any] = {
        "project_id": str(project.id),
        "task_id": str(task.id),
        "task_graph_id": str(graph.id),
        "execution_pack_version_id": str(version.id),
        "agent_key": definition.key,
        "agent_version": definition.version,
        "objective": task.description,
        "acceptance_criteria": acceptance_criteria,
        "project_summary": project.summary or project.title,
        "source_excerpts": source_excerpts,
        "decisions_constraints": decisions_constraints,
        "allowed_tools": definition.allowed_tools_json,
        "output_schema": definition.output_schema_json,
        "max_iterations": definition.max_iterations,
        "timeout_seconds": definition.timeout_seconds,
        "cost_ceiling_cents": definition.cost_ceiling_cents,
    }
    checksum = _canonical_checksum(payload)
    existing_result = await session.execute(
        select(AgentContextPackage).where(AgentContextPackage.checksum_sha256 == checksum)
    )
    existing = existing_result.scalar_one_or_none()
    if existing is not None:
        return existing
    package = AgentContextPackage(
        workspace_id=task.workspace_id,
        project_id=project.id,
        task_id=task.id,
        task_graph_id=graph.id,
        execution_pack_version_id=version.id,
        objective=task.description,
        acceptance_criteria_json=acceptance_criteria,
        project_summary=project.summary or project.title,
        source_excerpts_json=source_excerpts,
        decisions_constraints_json=decisions_constraints,
        allowed_tools_json=definition.allowed_tools_json,
        output_schema_json=definition.output_schema_json,
        max_iterations=definition.max_iterations,
        timeout_seconds=definition.timeout_seconds,
        cost_ceiling_cents=definition.cost_ceiling_cents,
        checksum_sha256=checksum,
    )
    session.add(package)
    await session.flush()
    return package
