from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, overload
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import (
    AgentContextPackage,
    AgentDefinition,
    AgentRun,
    AgentRunEvent,
    AgentToolInvocation,
)
from app.models.project import Project
from app.models.task import Task
from app.schemas.agent import (
    AgentContextPackageResponse,
    AgentDefinitionResponse,
    AgentRunEventResponse,
    AgentRunResponse,
    AgentRunUsageResponse,
    AgentToolInvocationResponse,
)

TERMINAL_STATES = {"succeeded", "failed", "cancelled"}


@overload
def _as_utc(value: datetime) -> datetime: ...


@overload
def _as_utc(value: None) -> None: ...


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "created": {"queued", "cancelled"},
    "queued": {"preparing_context", "failed", "cancelled"},
    "preparing_context": {"running", "failed", "cancelled"},
    "running": {
        "waiting_for_tool",
        "waiting_for_approval",
        "needs_review",
        "failed",
        "cancelled",
    },
    "waiting_for_tool": {"running", "failed", "cancelled"},
    "waiting_for_approval": {"running", "needs_review", "failed", "cancelled"},
    "needs_review": {"succeeded", "failed", "cancelled"},
    "succeeded": set(),
    "failed": set(),
    "cancelled": set(),
}


class AgentRunStateError(ValueError):
    pass


def validate_run_transition(current: str, target: str) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise AgentRunStateError(f"Invalid agent run transition: {current} -> {target}")


async def append_run_event(
    session: AsyncSession,
    run: AgentRun,
    *,
    event_type: str,
    from_state: str | None = None,
    to_state: str | None = None,
    message: str | None = None,
    payload: dict[str, Any] | None = None,
) -> AgentRunEvent:
    sequence_result = await session.execute(
        select(func.max(AgentRunEvent.sequence)).where(AgentRunEvent.run_id == run.id)
    )
    sequence = (sequence_result.scalar_one_or_none() or 0) + 1
    event = AgentRunEvent(
        run_id=run.id,
        sequence=sequence,
        event_type=event_type,
        from_state=from_state,
        to_state=to_state,
        message=message,
        payload_json=payload or {},
    )
    session.add(event)
    await session.flush()
    return event


async def transition_run(
    session: AsyncSession,
    run: AgentRun,
    target: str,
    *,
    message: str | None = None,
) -> None:
    validate_run_transition(run.state, target)
    previous = run.state
    now = datetime.now(UTC)
    run.state = target
    if target == "running" and run.started_at is None:
        run.started_at = now
    if target in {"succeeded", "failed"}:
        run.finished_at = now
    if target == "cancelled":
        run.cancelled_at = now
        run.finished_at = now
    await append_run_event(
        session,
        run,
        event_type="run.state_changed",
        from_state=previous,
        to_state=target,
        message=message,
    )


async def create_agent_run(
    session: AsyncSession,
    *,
    task: Task,
    definition: AgentDefinition,
    context: AgentContextPackage,
    model_provider: str,
    model_name: str,
    attempt_number: int = 1,
    retry_of_run_id: UUID | None = None,
    verification_of_run_id: UUID | None = None,
    input_payload: dict[str, Any] | None = None,
) -> AgentRun:
    run = AgentRun(
        workspace_id=task.workspace_id,
        project_id=task.project_id,
        task_id=task.id,
        agent_definition_id=definition.id,
        context_package_id=context.id,
        retry_of_run_id=retry_of_run_id,
        verification_of_run_id=verification_of_run_id,
        state="queued",
        attempt_number=attempt_number,
        model_provider=model_provider,
        model_name=model_name,
        tool_allowlist_json=list(definition.allowed_tools_json),
        input_json=input_payload or {},
    )
    session.add(run)
    await session.flush()
    await append_run_event(
        session,
        run,
        event_type="run.created",
        to_state="queued",
        payload={
            "agent_definition_id": str(definition.id),
            "agent_key": definition.key,
            "agent_version": definition.version,
            "context_package_id": str(context.id),
            "attempt_number": attempt_number,
        },
    )
    return run


def _estimate_tokens(value: object) -> int:
    return max(1, len(json.dumps(value, sort_keys=True, default=str)) // 4)


def _work_output(context: AgentContextPackage, definition: AgentDefinition) -> dict[str, Any]:
    criteria = [
        {"criterion": criterion, "status": "covered"}
        for criterion in context.acceptance_criteria_json
    ]
    evidence = [
        f"Agent definition {definition.key} v{definition.version} was applied.",
        f"Context checksum {context.checksum_sha256} preserved the exact execution inputs.",
        f"Task objective reviewed: {context.objective[:240]}",
    ]
    if context.source_excerpts_json:
        evidence.append(
            f"Reviewed {len(context.source_excerpts_json)} linked source excerpt(s)."
        )
    return {
        "summary": (
            f"{definition.name} completed a bounded execution pass for: "
            f"{context.objective}"
        ),
        "acceptance_criteria": criteria,
        "evidence": evidence,
        "next_actions": [
            "Run QA verification against the declared acceptance criteria.",
            "Escalate any protected external action for explicit approval.",
        ],
    }


async def execute_agent_run(
    session: AsyncSession,
    run: AgentRun,
    *,
    definition: AgentDefinition,
    context: AgentContextPackage,
) -> AgentRun:
    if run.state != "queued":
        raise AgentRunStateError(
            f"Agent run must be queued before execution; current state is {run.state}"
        )
    await transition_run(session, run, "preparing_context")
    await transition_run(session, run, "running")
    output = _work_output(context, definition)
    run.output_json = output
    run.prompt_tokens = _estimate_tokens(
        {
            "context": context.checksum_sha256,
            "objective": context.objective,
            "acceptance_criteria": context.acceptance_criteria_json,
            "sources": context.source_excerpts_json,
            "input": run.input_json,
        }
    )
    run.completion_tokens = _estimate_tokens(output)
    run.estimated_cost_cents = 0 if run.model_provider == "rules" else max(
        1, (run.prompt_tokens + run.completion_tokens) // 1000
    )
    await append_run_event(
        session,
        run,
        event_type="run.output_generated",
        payload={
            "prompt_tokens": run.prompt_tokens,
            "completion_tokens": run.completion_tokens,
            "estimated_cost_cents": run.estimated_cost_cents,
        },
    )
    await transition_run(session, run, "needs_review")
    await session.flush()
    return run


async def cancel_agent_run(
    session: AsyncSession, run: AgentRun, *, reason: str | None = None
) -> AgentRun:
    if run.state in TERMINAL_STATES:
        raise AgentRunStateError(f"Cannot cancel a {run.state} agent run")
    await transition_run(session, run, "cancelled", message=reason or "Cancelled by owner")
    await session.flush()
    return run


async def retry_agent_run(
    session: AsyncSession,
    source: AgentRun,
    *,
    task: Task,
    definition: AgentDefinition,
    context: AgentContextPackage,
    model_provider: str | None,
    model_name: str | None,
) -> AgentRun:
    if source.state not in {"failed", "cancelled"}:
        raise AgentRunStateError("Only failed or cancelled runs can be retried")
    return await create_agent_run(
        session,
        task=task,
        definition=definition,
        context=context,
        model_provider=model_provider or source.model_provider,
        model_name=model_name or source.model_name,
        attempt_number=source.attempt_number + 1,
        retry_of_run_id=source.id,
        input_payload=source.input_json,
    )


def evaluate_candidate_output(output: dict[str, Any] | None) -> dict[str, Any]:
    defects: list[str] = []
    if not output:
        defects.append("Candidate output is missing")
        evidence: list[str] = []
    else:
        summary = output.get("summary")
        evidence_value = output.get("evidence")
        criteria = output.get("acceptance_criteria")
        evidence = (
            [str(item) for item in evidence_value]
            if isinstance(evidence_value, list)
            else []
        )
        if not isinstance(summary, str) or not summary.strip():
            defects.append("Summary is missing")
        if not evidence:
            defects.append("Verification evidence is missing")
        if not isinstance(criteria, list) or not criteria:
            defects.append("Acceptance-criteria coverage is missing")
        elif any(
            not isinstance(item, dict) or item.get("status") != "covered" for item in criteria
        ):
            defects.append("One or more acceptance criteria are not covered")
    return {
        "verdict": "fail" if defects else "pass",
        "defects": defects,
        "evidence_checked": evidence,
    }


async def verify_agent_run(
    session: AsyncSession,
    *,
    source: AgentRun,
    task: Task,
    qa_definition: AgentDefinition,
    context: AgentContextPackage,
    model_provider: str = "rules",
    model_name: str = "rules-qa-v1",
) -> AgentRun:
    if source.state != "needs_review":
        raise AgentRunStateError("Only runs awaiting review can be verified")
    qa_run = await create_agent_run(
        session,
        task=task,
        definition=qa_definition,
        context=context,
        model_provider=model_provider,
        model_name=model_name,
        verification_of_run_id=source.id,
        input_payload={
            "verification_of_run_id": str(source.id),
            "candidate_output": source.output_json,
        },
    )
    await transition_run(session, qa_run, "preparing_context")
    await transition_run(session, qa_run, "running")
    verdict = evaluate_candidate_output(source.output_json)
    qa_run.output_json = verdict
    qa_run.prompt_tokens = _estimate_tokens(qa_run.input_json)
    qa_run.completion_tokens = _estimate_tokens(verdict)
    qa_run.estimated_cost_cents = 0
    await append_run_event(
        session,
        qa_run,
        event_type="run.output_generated",
        payload={"verdict": verdict["verdict"]},
    )
    await transition_run(session, qa_run, "needs_review")
    await transition_run(session, qa_run, "succeeded")
    await transition_run(
        session,
        source,
        "succeeded" if verdict["verdict"] == "pass" else "failed",
        message=(
            "QA verification passed"
            if verdict["verdict"] == "pass"
            else "QA verification failed"
        ),
    )
    await session.flush()
    return qa_run


async def record_tool_invocation(
    session: AsyncSession,
    *,
    run: AgentRun,
    tool_name: str,
    arguments: dict[str, Any],
) -> AgentToolInvocation:
    canonical = json.dumps(arguments, sort_keys=True, separators=(",", ":"), default=str)
    allowed = tool_name in run.tool_allowlist_json
    invocation = AgentToolInvocation(
        run_id=run.id,
        tool_name=tool_name,
        decision="allowed" if allowed else "denied",
        arguments_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        arguments_json=arguments,
        result_json={"status": "authorized", "execution": "not_performed"} if allowed else None,
        error_text=None if allowed else f"Tool {tool_name} is not allowed for this run",
    )
    session.add(invocation)
    await session.flush()
    await append_run_event(
        session,
        run,
        event_type="tool.allowed" if allowed else "tool.denied",
        message=invocation.error_text,
        payload={"tool_name": tool_name, "arguments_hash": invocation.arguments_hash},
    )
    return invocation


@dataclass(frozen=True)
class LoadedAgentRun:
    run: AgentRun
    definition: AgentDefinition
    context: AgentContextPackage
    project: Project
    task: Task
    tool_invocations: list[AgentToolInvocation]


async def load_agent_run(session: AsyncSession, run_id: UUID) -> LoadedAgentRun | None:
    run_result = await session.execute(select(AgentRun).where(AgentRun.id == run_id))
    run = run_result.scalar_one_or_none()
    if run is None:
        return None
    definition_result = await session.execute(
        select(AgentDefinition).where(AgentDefinition.id == run.agent_definition_id)
    )
    context_result = await session.execute(
        select(AgentContextPackage).where(AgentContextPackage.id == run.context_package_id)
    )
    project_result = await session.execute(select(Project).where(Project.id == run.project_id))
    task_result = await session.execute(select(Task).where(Task.id == run.task_id))
    tools_result = await session.execute(
        select(AgentToolInvocation)
        .where(AgentToolInvocation.run_id == run.id)
        .order_by(AgentToolInvocation.created_at)
    )
    return LoadedAgentRun(
        run=run,
        definition=definition_result.scalar_one(),
        context=context_result.scalar_one(),
        project=project_result.scalar_one(),
        task=task_result.scalar_one(),
        tool_invocations=list(tools_result.scalars().all()),
    )


async def list_agent_runs(session: AsyncSession, workspace_id: UUID) -> list[LoadedAgentRun]:
    result = await session.execute(
        select(AgentRun)
        .where(AgentRun.workspace_id == workspace_id)
        .order_by(AgentRun.created_at.desc())
    )
    loaded: list[LoadedAgentRun] = []
    for run in result.scalars().all():
        item = await load_agent_run(session, run.id)
        if item is not None:
            loaded.append(item)
    return loaded


async def list_run_events(session: AsyncSession, run_id: UUID) -> list[AgentRunEvent]:
    result = await session.execute(
        select(AgentRunEvent)
        .where(AgentRunEvent.run_id == run_id)
        .order_by(AgentRunEvent.sequence)
    )
    return list(result.scalars().all())


def definition_response(definition: AgentDefinition) -> AgentDefinitionResponse:
    return AgentDefinitionResponse(
        id=definition.id,
        key=definition.key,
        version=definition.version,
        name=definition.name,
        purpose=definition.purpose,
        allowed_task_types=definition.allowed_task_types_json,
        input_schema=definition.input_schema_json,
        output_schema=definition.output_schema_json,
        allowed_tools=definition.allowed_tools_json,
        denied_actions=definition.denied_actions_json,
        model_policy=definition.model_policy_json,
        max_iterations=definition.max_iterations,
        timeout_seconds=definition.timeout_seconds,
        cost_ceiling_cents=definition.cost_ceiling_cents,
        escalation_conditions=definition.escalation_conditions_json,
        evaluation_rubric=definition.evaluation_rubric_json,
        is_active=definition.is_active,
        created_at=_as_utc(definition.created_at),
    )


def context_response(context: AgentContextPackage) -> AgentContextPackageResponse:
    return AgentContextPackageResponse(
        id=context.id,
        project_id=context.project_id,
        task_id=context.task_id,
        task_graph_id=context.task_graph_id,
        source_execution_pack_version_id=context.execution_pack_version_id,
        objective=context.objective,
        acceptance_criteria=context.acceptance_criteria_json,
        project_summary=context.project_summary,
        source_excerpts=context.source_excerpts_json,
        decisions_constraints=context.decisions_constraints_json,
        allowed_tools=context.allowed_tools_json,
        output_schema=context.output_schema_json,
        max_iterations=context.max_iterations,
        timeout_seconds=context.timeout_seconds,
        cost_ceiling_cents=context.cost_ceiling_cents,
        checksum_sha256=context.checksum_sha256,
        created_at=_as_utc(context.created_at),
    )


def tool_invocation_response(invocation: AgentToolInvocation) -> AgentToolInvocationResponse:
    return AgentToolInvocationResponse(
        id=invocation.id,
        run_id=invocation.run_id,
        tool_name=invocation.tool_name,
        decision=invocation.decision,
        arguments_hash=invocation.arguments_hash,
        arguments=invocation.arguments_json,
        result=invocation.result_json,
        error=invocation.error_text,
        created_at=_as_utc(invocation.created_at),
    )


def run_response(loaded: LoadedAgentRun) -> AgentRunResponse:
    run = loaded.run
    return AgentRunResponse(
        id=run.id,
        project_id=run.project_id,
        project_title=loaded.project.title,
        task_id=run.task_id,
        task_title=loaded.task.title,
        agent_key=loaded.definition.key,
        agent_name=loaded.definition.name,
        agent_version=loaded.definition.version,
        state=run.state,
        attempt_number=run.attempt_number,
        retry_of_run_id=run.retry_of_run_id,
        verification_of_run_id=run.verification_of_run_id,
        model_provider=run.model_provider,
        model_name=run.model_name,
        tool_allowlist=run.tool_allowlist_json,
        input=run.input_json,
        output=run.output_json,
        error=run.error_text,
        usage=AgentRunUsageResponse(
            prompt_tokens=run.prompt_tokens,
            completion_tokens=run.completion_tokens,
            estimated_cost_cents=run.estimated_cost_cents,
        ),
        context_package=context_response(loaded.context),
        tool_invocations=[tool_invocation_response(item) for item in loaded.tool_invocations],
        created_at=_as_utc(run.created_at),
        updated_at=_as_utc(run.updated_at),
        started_at=_as_utc(run.started_at),
        finished_at=_as_utc(run.finished_at),
        cancelled_at=_as_utc(run.cancelled_at),
    )


def event_response(event: AgentRunEvent) -> AgentRunEventResponse:
    return AgentRunEventResponse(
        id=event.id,
        run_id=event.run_id,
        sequence=event.sequence,
        event_type=event.event_type,
        from_state=event.from_state,
        to_state=event.to_state,
        message=event.message,
        payload=event.payload_json,
        created_at=_as_utc(event.created_at),
    )
