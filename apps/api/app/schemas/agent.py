from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

AgentRunState = Literal[
    "created",
    "queued",
    "preparing_context",
    "running",
    "waiting_for_tool",
    "waiting_for_approval",
    "needs_review",
    "succeeded",
    "failed",
    "cancelled",
]


class AgentDefinitionResponse(BaseModel):
    id: UUID
    key: str
    version: int
    name: str
    purpose: str
    allowed_task_types: list[str]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    allowed_tools: list[str]
    denied_actions: list[str]
    model_policy: dict[str, Any]
    max_iterations: int
    timeout_seconds: int
    cost_ceiling_cents: int
    escalation_conditions: list[str]
    evaluation_rubric: dict[str, Any]
    is_active: bool
    created_at: datetime


class AgentDefinitionListResponse(BaseModel):
    items: list[AgentDefinitionResponse]


class AgentContextPackageResponse(BaseModel):
    id: UUID
    project_id: UUID
    task_id: UUID
    task_graph_id: UUID
    source_execution_pack_version_id: UUID
    objective: str
    acceptance_criteria: list[str]
    project_summary: str
    source_excerpts: list[dict[str, Any]]
    decisions_constraints: list[str]
    allowed_tools: list[str]
    output_schema: dict[str, Any]
    max_iterations: int
    timeout_seconds: int
    cost_ceiling_cents: int
    checksum_sha256: str
    created_at: datetime


class AgentRunCreate(BaseModel):
    agent_key: str = Field(min_length=1, max_length=80)
    agent_version: int | None = Field(default=None, ge=1)
    model_provider: Literal["rules", "hermes", "cloud"] | None = None
    model_name: str | None = Field(default=None, min_length=1, max_length=120)


class AgentRunCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class AgentRunRetryRequest(BaseModel):
    model_provider: Literal["rules", "hermes", "cloud"] | None = None
    model_name: str | None = Field(default=None, min_length=1, max_length=120)


class ToolInvocationRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=160)
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentToolInvocationResponse(BaseModel):
    id: UUID
    run_id: UUID
    tool_name: str
    decision: str
    arguments_hash: str
    arguments: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None
    created_at: datetime


class AgentRunUsageResponse(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_cents: int


class AgentRunResponse(BaseModel):
    id: UUID
    project_id: UUID
    project_title: str
    task_id: UUID
    task_title: str
    agent_key: str
    agent_name: str
    agent_version: int
    state: AgentRunState
    attempt_number: int
    retry_of_run_id: UUID | None
    verification_of_run_id: UUID | None
    model_provider: str
    model_name: str
    tool_allowlist: list[str]
    input: dict[str, Any]
    output: dict[str, Any] | None
    error: str | None
    usage: AgentRunUsageResponse
    context_package: AgentContextPackageResponse
    tool_invocations: list[AgentToolInvocationResponse]
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    cancelled_at: datetime | None


class AgentRunListResponse(BaseModel):
    items: list[AgentRunResponse]


class AgentRunEventResponse(BaseModel):
    id: UUID
    run_id: UUID
    sequence: int
    event_type: str
    from_state: str | None
    to_state: str | None
    message: str | None
    payload: dict[str, Any]
    created_at: datetime


class AgentRunEventListResponse(BaseModel):
    items: list[AgentRunEventResponse]


class AgentVerificationResponse(BaseModel):
    source_run: AgentRunResponse
    qa_run: AgentRunResponse
