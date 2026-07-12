"""Add versioned execution packs.

Revision ID: 0005_execution_packs
Revises: 0004_intelligence_layer
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_execution_packs"
down_revision: str | None = "0004_intelligence_layer"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "execution_packs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("current_version_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", name="uq_execution_pack_project"),
    )
    op.create_index(
        "ix_execution_packs_workspace_status",
        "execution_packs",
        ["workspace_id", "status"],
        unique=False,
    )
    op.create_table(
        "execution_pack_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("execution_pack_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["execution_pack_id"], ["execution_packs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "execution_pack_id", "version_number", name="uq_execution_pack_version"
        ),
    )
    op.create_index(
        "ix_execution_pack_versions_pack_created",
        "execution_pack_versions",
        ["execution_pack_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_execution_pack_versions_pack_created", table_name="execution_pack_versions"
    )
    op.drop_table("execution_pack_versions")
    op.drop_index("ix_execution_packs_workspace_status", table_name="execution_packs")
    op.drop_table("execution_packs")
