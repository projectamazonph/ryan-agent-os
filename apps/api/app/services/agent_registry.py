from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import AgentDefinition

COMMON_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["objective", "acceptance_criteria", "project_summary"],
    "properties": {
        "objective": {"type": "string"},
        "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
        "project_summary": {"type": "string"},
        "source_excerpts": {"type": "array"},
        "decisions_constraints": {"type": "array", "items": {"type": "string"}},
    },
}

WORK_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["summary", "acceptance_criteria", "evidence", "next_actions"],
    "properties": {
        "summary": {"type": "string"},
        "acceptance_criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["criterion", "status"],
                "properties": {
                    "criterion": {"type": "string"},
                    "status": {"enum": ["covered", "partial", "missing"]},
                },
            },
        },
        "evidence": {"type": "array", "items": {"type": "string"}},
        "next_actions": {"type": "array", "items": {"type": "string"}},
    },
}

QA_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["verdict", "defects", "evidence_checked"],
    "properties": {
        "verdict": {"enum": ["pass", "fail"]},
        "defects": {"type": "array", "items": {"type": "string"}},
        "evidence_checked": {"type": "array", "items": {"type": "string"}},
    },
}

BUILTIN_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "key": "orchestrator",
        "version": 1,
        "name": "Executive Orchestrator",
        "purpose": "Sequence approved work, select bounded specialists, and escalate blockers.",
        "allowed_task_types": ["planning", "coordination", "delivery"],
        "allowed_tools": ["project.read", "task.read", "agent.run.create", "audit.read"],
        "denied_actions": ["connector.write_without_approval", "self_approve"],
        "model_policy": {"preferred": "cloud", "fallback": "hermes"},
        "max_iterations": 10,
        "timeout_seconds": 1200,
        "cost_ceiling_cents": 300,
    },
    {
        "key": "developer",
        "version": 1,
        "name": "Developer Agent",
        "purpose": "Implement scoped code changes using TDD and produce verification evidence.",
        "allowed_task_types": ["software", "implementation", "testing"],
        "allowed_tools": ["filesystem.read", "filesystem.write", "shell.exec", "git.diff"],
        "denied_actions": ["git.push", "secret.read", "connector.write_without_approval"],
        "model_policy": {"preferred": "hermes", "fallback": "cloud"},
        "max_iterations": 12,
        "timeout_seconds": 1800,
        "cost_ceiling_cents": 500,
    },
    {
        "key": "documentation",
        "version": 1,
        "name": "Documentation Agent",
        "purpose": "Create and maintain precise, versioned documentation without content loss.",
        "allowed_task_types": ["documentation", "writing", "release"],
        "allowed_tools": ["filesystem.read", "filesystem.write", "docs.validate"],
        "denied_actions": ["delete_source_content", "connector.write_without_approval"],
        "model_policy": {"preferred": "hermes", "fallback": "cloud"},
        "max_iterations": 8,
        "timeout_seconds": 1200,
        "cost_ceiling_cents": 250,
    },
    {
        "key": "research",
        "version": 1,
        "name": "Research Agent",
        "purpose": "Gather evidence, separate fact from inference, and preserve citations.",
        "allowed_task_types": ["research", "analysis"],
        "allowed_tools": ["source.read", "web.search", "citation.write"],
        "denied_actions": ["uncited_claim", "connector.write_without_approval"],
        "model_policy": {"preferred": "cloud", "fallback": "hermes"},
        "max_iterations": 10,
        "timeout_seconds": 1500,
        "cost_ceiling_cents": 400,
    },
    {
        "key": "qa",
        "version": 1,
        "name": "QA Verification Agent",
        "purpose": "Verify acceptance criteria and reject unsupported completion claims.",
        "allowed_task_types": ["verification", "testing", "review"],
        "allowed_tools": ["filesystem.read", "shell.exec", "test.run", "audit.read"],
        "denied_actions": ["modify_candidate_output", "self_approve_source_work"],
        "model_policy": {"preferred": "rules", "fallback": "hermes"},
        "max_iterations": 6,
        "timeout_seconds": 900,
        "cost_ceiling_cents": 150,
        "output_schema": QA_OUTPUT_SCHEMA,
    },
    {
        "key": "amazon-ppc",
        "version": 1,
        "name": "Amazon PPC Strategist",
        "purpose": "Apply Ryan's advertising frameworks to audits, operations, and training.",
        "allowed_task_types": ["amazon-ppc", "advertising", "training"],
        "allowed_tools": ["source.read", "spreadsheet.read", "analysis.calculate"],
        "denied_actions": ["campaign.write_without_approval", "invent_performance_data"],
        "model_policy": {"preferred": "cloud", "fallback": "hermes"},
        "max_iterations": 10,
        "timeout_seconds": 1500,
        "cost_ceiling_cents": 400,
    },
)


def _definition_values(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": spec["key"],
        "version": spec["version"],
        "name": spec["name"],
        "purpose": spec["purpose"],
        "allowed_task_types_json": spec["allowed_task_types"],
        "input_schema_json": spec.get("input_schema", COMMON_INPUT_SCHEMA),
        "output_schema_json": spec.get("output_schema", WORK_OUTPUT_SCHEMA),
        "allowed_tools_json": spec["allowed_tools"],
        "denied_actions_json": spec["denied_actions"],
        "model_policy_json": spec["model_policy"],
        "max_iterations": spec["max_iterations"],
        "timeout_seconds": spec["timeout_seconds"],
        "cost_ceiling_cents": spec["cost_ceiling_cents"],
        "escalation_conditions_json": [
            "Acceptance criteria cannot be satisfied with available context",
            "A denied tool is required",
            "The iteration, timeout, or cost ceiling is reached",
        ],
        "evaluation_rubric_json": {
            "acceptance_criteria_coverage": 40,
            "evidence_quality": 30,
            "tool_discipline": 20,
            "edit_precision": 10,
        },
        "is_active": True,
    }


async def ensure_builtin_agent_definitions(
    session: AsyncSession, workspace_id: UUID
) -> list[AgentDefinition]:
    existing_result = await session.execute(
        select(AgentDefinition).where(AgentDefinition.workspace_id == workspace_id)
    )
    existing = {(item.key, item.version): item for item in existing_result.scalars().all()}
    for spec in BUILTIN_DEFINITIONS:
        identity = (str(spec["key"]), int(spec["version"]))
        if identity in existing:
            continue
        definition = AgentDefinition(workspace_id=workspace_id, **_definition_values(spec))
        session.add(definition)
        existing[identity] = definition
    await session.flush()
    return list(existing.values())


async def list_current_agent_definitions(
    session: AsyncSession, workspace_id: UUID
) -> list[AgentDefinition]:
    definitions = await ensure_builtin_agent_definitions(session, workspace_id)
    latest: dict[str, AgentDefinition] = {}
    for definition in definitions:
        current = latest.get(definition.key)
        if definition.is_active and (current is None or definition.version > current.version):
            latest[definition.key] = definition
    return sorted(latest.values(), key=lambda item: item.key)


async def list_agent_versions(
    session: AsyncSession, workspace_id: UUID, key: str
) -> list[AgentDefinition]:
    await ensure_builtin_agent_definitions(session, workspace_id)
    result = await session.execute(
        select(AgentDefinition)
        .where(AgentDefinition.workspace_id == workspace_id, AgentDefinition.key == key)
        .order_by(AgentDefinition.version)
    )
    return list(result.scalars().all())


async def get_agent_definition(
    session: AsyncSession,
    workspace_id: UUID,
    key: str,
    version: int | None = None,
) -> AgentDefinition | None:
    await ensure_builtin_agent_definitions(session, workspace_id)
    statement = select(AgentDefinition).where(
        AgentDefinition.workspace_id == workspace_id,
        AgentDefinition.key == key,
        AgentDefinition.is_active.is_(True),
    )
    if version is not None:
        statement = statement.where(AgentDefinition.version == version)
    else:
        statement = statement.order_by(AgentDefinition.version.desc())
    result = await session.execute(statement.limit(1))
    return result.scalar_one_or_none()
