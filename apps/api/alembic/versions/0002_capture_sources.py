"""Add immutable source objects for file captures.

Revision ID: 0002_capture_sources
Revises: 0001_foundation
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_capture_sources"
down_revision: str | None = "0001_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "source_objects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column(
            "capture_id",
            sa.Uuid(),
            sa.ForeignKey("captures.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_key", sa.String(length=700), nullable=False),
        sa.Column("original_filename", sa.String(length=300), nullable=False),
        sa.Column("content_type", sa.String(length=160), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "extraction_status", sa.String(length=24), nullable=False, server_default="pending"
        ),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("extraction_error", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("capture_id", name="uq_source_object_capture"),
        sa.UniqueConstraint(
            "workspace_id", "checksum_sha256", name="uq_source_workspace_checksum"
        ),
        sa.UniqueConstraint("storage_key", name="uq_source_storage_key"),
    )
    op.create_index(
        "ix_source_objects_workspace_created",
        "source_objects",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_source_objects_extraction_status", "source_objects", ["extraction_status"]
    )


def downgrade() -> None:
    op.drop_table("source_objects")
