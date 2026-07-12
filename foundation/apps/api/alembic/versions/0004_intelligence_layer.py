"""Add vector embeddings, capture relations, and extraction retry metadata.

Revision ID: 0004_intelligence_layer
Revises: 0003_project_registry
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "0004_intelligence_layer"
down_revision: str | None = "0003_project_registry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    vector_type = sa.JSON().with_variant(Vector(96), "postgresql")
    op.add_column(
        "source_objects",
        sa.Column("extraction_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "source_objects", sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_table(
        "capture_embeddings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("capture_id", sa.Uuid(), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("vector", vector_type, nullable=False),
        sa.Column("content_checksum", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("capture_id", name="uq_capture_embedding_capture"),
    )
    op.create_index(
        "ix_capture_embeddings_workspace", "capture_embeddings", ["workspace_id"], unique=False
    )
    op.create_table(
        "capture_relations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("source_capture_id", sa.Uuid(), nullable=False),
        sa.Column("target_capture_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "source_capture_id <> target_capture_id", name="ck_capture_relation_distinct"
        ),
        sa.ForeignKeyConstraint(
            ["source_capture_id"], ["captures.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["target_capture_id"], ["captures.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_capture_id",
            "target_capture_id",
            "relation_type",
            name="uq_capture_relation",
        ),
    )
    op.create_index(
        "ix_capture_relations_source",
        "capture_relations",
        ["source_capture_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_capture_relations_target",
        "capture_relations",
        ["target_capture_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_capture_relations_target", table_name="capture_relations")
    op.drop_index("ix_capture_relations_source", table_name="capture_relations")
    op.drop_table("capture_relations")
    op.drop_index("ix_capture_embeddings_workspace", table_name="capture_embeddings")
    op.drop_table("capture_embeddings")
    op.drop_column("source_objects", "last_attempt_at")
    op.drop_column("source_objects", "extraction_attempts")
