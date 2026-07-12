from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.uuid7 import uuid7
from app.db.base import Base, TimestampMixin


class AgentDefinition(Base):
    __tablename__ = "agent_definitions"
    __table_args__ = (
        UniqueConstraint("workspace_id", "key", "version", name="uq_agent_definition_version"),
        Index("ix_agent_definitions_workspace_key", "workspace_id", "key", "version"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(80), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    allowed_task_types_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    input_schema_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_schema_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    allowed_tools_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    denied_actions_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    model_policy_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=900)
    cost_ceiling_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    escalation_conditions_json: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    evaluation_rubric_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class AgentContextPackage(Base):
    __tablename__ = "agent_context_packages"
    __table_args__ = (
        Index("ix_agent_context_packages_task_created", "task_id", "created_at"),
        UniqueConstraint("checksum_sha256", name="uq_agent_context_checksum"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    task_graph_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_graphs.id", ondelete="CASCADE"), nullable=False
    )
    execution_pack_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("execution_pack_versions.id", ondelete="RESTRICT"), nullable=False
    )
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    project_summary: Mapped[str] = mapped_column(Text, nullable=False)
    source_excerpts_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    decisions_constraints_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    allowed_tools_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    output_schema_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_ceiling_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class AgentRun(TimestampMixin, Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        CheckConstraint("attempt_number >= 1", name="ck_agent_runs_attempt_positive"),
        Index("ix_agent_runs_workspace_state_created", "workspace_id", "state", "created_at"),
        Index("ix_agent_runs_task_created", "task_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    agent_definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_definitions.id", ondelete="RESTRICT"), nullable=False
    )
    context_package_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_context_packages.id", ondelete="RESTRICT"), nullable=False
    )
    retry_of_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL"), nullable=True
    )
    verification_of_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL"), nullable=True
    )
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    model_provider: Mapped[str] = mapped_column(String(40), nullable=False, default="rules")
    model_name: Mapped[str] = mapped_column(String(120), nullable=False, default="rules-v1")
    tool_allowlist_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AgentRunEvent(Base):
    __tablename__ = "agent_run_events"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_agent_run_event_sequence"),
        Index("ix_agent_run_events_run_created", "run_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class AgentToolInvocation(Base):
    __tablename__ = "agent_tool_invocations"
    __table_args__ = (Index("ix_agent_tool_invocations_run_created", "run_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String(160), nullable=False)
    decision: Mapped[str] = mapped_column(String(24), nullable=False)
    arguments_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    arguments_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
