"""Add dependency-aware task graphs and implementation queue tasks.

Revision ID: 0006_task_graphs
Revises: 0005_execution_packs
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_task_graphs"
down_revision: str | None = "0005_execution_packs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "task_graphs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("execution_pack_version_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["execution_pack_version_id"], ["execution_pack_versions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "execution_pack_version_id", name="uq_task_graph_execution_pack_version"
        ),
    )
    op.create_index(
        "ix_task_graphs_project_status", "task_graphs", ["project_id", "status"], unique=False
    )
    op.create_index(
        "ix_task_graphs_workspace_status", "task_graphs", ["workspace_id", "status"], unique=False
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_graph_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("verification", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("impact", sa.Integer(), nullable=False),
        sa.Column("urgency", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("effort", sa.Integer(), nullable=False),
        sa.Column("rank_score", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 100", name="ck_tasks_confidence_range"
        ),
        sa.CheckConstraint("effort >= 0 AND effort <= 100", name="ck_tasks_effort_range"),
        sa.CheckConstraint("impact >= 0 AND impact <= 100", name="ck_tasks_impact_range"),
        sa.CheckConstraint(
            "rank_score >= 0 AND rank_score <= 100", name="ck_tasks_rank_score_range"
        ),
        sa.CheckConstraint("urgency >= 0 AND urgency <= 100", name="ck_tasks_urgency_range"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_graph_id"], ["task_graphs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_graph_id", "key", name="uq_task_graph_key"),
    )
    op.create_index("ix_tasks_project_position", "tasks", ["project_id", "position"], unique=False)
    op.create_index(
        "ix_tasks_workspace_status_rank",
        "tasks",
        ["workspace_id", "status", "rank_score"],
        unique=False,
    )
    op.create_table(
        "task_dependencies",
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("depends_on_task_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("task_id <> depends_on_task_id", name="ck_task_dependency_not_self"),
        sa.ForeignKeyConstraint(["depends_on_task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("task_id", "depends_on_task_id"),
    )
    op.create_index(
        "ix_task_dependencies_depends_on", "task_dependencies", ["depends_on_task_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_task_dependencies_depends_on", table_name="task_dependencies")
    op.drop_table("task_dependencies")
    op.drop_index("ix_tasks_workspace_status_rank", table_name="tasks")
    op.drop_index("ix_tasks_project_position", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_task_graphs_workspace_status", table_name="task_graphs")
    op.drop_index("ix_task_graphs_project_status", table_name="task_graphs")
    op.drop_table("task_graphs")
