"""Add capture review state and project registry.

Revision ID: 0003_project_registry
Revises: 0002_capture_sources
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_project_registry"
down_revision: str | None = "0002_capture_sources"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "captures",
        sa.Column(
            "review_status",
            sa.String(length=24),
            nullable=False,
            server_default="unreviewed",
        ),
    )
    op.create_index("ix_captures_review_status", "captures", ["review_status"])
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("domain", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.Column("blocker", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_projects_workspace_status", "projects", ["workspace_id", "status"])
    op.create_index("ix_projects_workspace_updated", "projects", ["workspace_id", "updated_at"])
    op.create_table(
        "project_captures",
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "capture_id",
            sa.Uuid(),
            sa.ForeignKey("captures.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("relationship_type", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("project_id", "capture_id", name="uq_project_capture_link"),
    )
    op.create_index("ix_project_captures_capture", "project_captures", ["capture_id"])
    op.create_table(
        "project_status_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Uuid(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_status", sa.String(length=24), nullable=True),
        sa.Column("to_status", sa.String(length=24), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_project_status_history_project",
        "project_status_history",
        ["project_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_table("project_status_history")
    op.drop_table("project_captures")
    op.drop_table("projects")
    op.drop_index("ix_captures_review_status", table_name="captures")
    op.drop_column("captures", "review_status")
