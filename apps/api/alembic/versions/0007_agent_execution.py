"""Add versioned agents, immutable context packages, and auditable runs.

Revision ID: 0007_agent_execution
Revises: 0006_task_graphs
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_agent_execution"
down_revision: str | None = "0006_task_graphs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_definitions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("allowed_task_types_json", sa.JSON(), nullable=False),
        sa.Column("input_schema_json", sa.JSON(), nullable=False),
        sa.Column("output_schema_json", sa.JSON(), nullable=False),
        sa.Column("allowed_tools_json", sa.JSON(), nullable=False),
        sa.Column("denied_actions_json", sa.JSON(), nullable=False),
        sa.Column("model_policy_json", sa.JSON(), nullable=False),
        sa.Column("max_iterations", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("cost_ceiling_cents", sa.Integer(), nullable=False),
        sa.Column("escalation_conditions_json", sa.JSON(), nullable=False),
        sa.Column("evaluation_rubric_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "key", "version", name="uq_agent_definition_version"),
    )
    op.create_index(
        "ix_agent_definitions_workspace_key",
        "agent_definitions",
        ["workspace_id", "key", "version"],
        unique=False,
    )
    op.create_table(
        "agent_context_packages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("task_graph_id", sa.Uuid(), nullable=False),
        sa.Column("execution_pack_version_id", sa.Uuid(), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("acceptance_criteria_json", sa.JSON(), nullable=False),
        sa.Column("project_summary", sa.Text(), nullable=False),
        sa.Column("source_excerpts_json", sa.JSON(), nullable=False),
        sa.Column("decisions_constraints_json", sa.JSON(), nullable=False),
        sa.Column("allowed_tools_json", sa.JSON(), nullable=False),
        sa.Column("output_schema_json", sa.JSON(), nullable=False),
        sa.Column("max_iterations", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("cost_ceiling_cents", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["execution_pack_version_id"], ["execution_pack_versions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_graph_id"], ["task_graphs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("checksum_sha256", name="uq_agent_context_checksum"),
    )
    op.create_index(
        "ix_agent_context_packages_task_created",
        "agent_context_packages",
        ["task_id", "created_at"],
        unique=False,
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("agent_definition_id", sa.Uuid(), nullable=False),
        sa.Column("context_package_id", sa.Uuid(), nullable=False),
        sa.Column("retry_of_run_id", sa.Uuid(), nullable=True),
        sa.Column("verification_of_run_id", sa.Uuid(), nullable=True),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("model_provider", sa.String(length=40), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("tool_allowlist_json", sa.JSON(), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost_cents", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("attempt_number >= 1", name="ck_agent_runs_attempt_positive"),
        sa.ForeignKeyConstraint(
            ["agent_definition_id"], ["agent_definitions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["context_package_id"], ["agent_context_packages.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["retry_of_run_id"], ["agent_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["verification_of_run_id"], ["agent_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_runs_task_created", "agent_runs", ["task_id", "created_at"], unique=False
    )
    op.create_index(
        "ix_agent_runs_workspace_state_created",
        "agent_runs",
        ["workspace_id", "state", "created_at"],
        unique=False,
    )
    op.create_table(
        "agent_run_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("from_state", sa.String(length=32), nullable=True),
        sa.Column("to_state", sa.String(length=32), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "sequence", name="uq_agent_run_event_sequence"),
    )
    op.create_index(
        "ix_agent_run_events_run_created",
        "agent_run_events",
        ["run_id", "created_at"],
        unique=False,
    )
    op.create_table(
        "agent_tool_invocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("tool_name", sa.String(length=160), nullable=False),
        sa.Column("decision", sa.String(length=24), nullable=False),
        sa.Column("arguments_hash", sa.String(length=64), nullable=False),
        sa.Column("arguments_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_agent_tool_invocations_run_created",
        "agent_tool_invocations",
        ["run_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_agent_tool_invocations_run_created", table_name="agent_tool_invocations")
    op.drop_table("agent_tool_invocations")
    op.drop_index("ix_agent_run_events_run_created", table_name="agent_run_events")
    op.drop_table("agent_run_events")
    op.drop_index("ix_agent_runs_workspace_state_created", table_name="agent_runs")
    op.drop_index("ix_agent_runs_task_created", table_name="agent_runs")
    op.drop_table("agent_runs")
    op.drop_index("ix_agent_context_packages_task_created", table_name="agent_context_packages")
    op.drop_table("agent_context_packages")
    op.drop_index("ix_agent_definitions_workspace_key", table_name="agent_definitions")
    op.drop_table("agent_definitions")
