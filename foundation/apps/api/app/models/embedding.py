from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.uuid7 import uuid7
from app.db.base import Base

EMBEDDING_DIMENSIONS = 96
_VECTOR_TYPE: Any = JSON().with_variant(Vector(EMBEDDING_DIMENSIONS), "postgresql")


class CaptureEmbedding(Base):
    __tablename__ = "capture_embeddings"
    __table_args__ = (
        UniqueConstraint("capture_id", name="uq_capture_embedding_capture"),
        Index("ix_capture_embeddings_workspace", "workspace_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    capture_id: Mapped[UUID] = mapped_column(
        ForeignKey("captures.id", ondelete="CASCADE"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dimensions: Mapped[int] = mapped_column(nullable=False)
    vector: Mapped[list[float]] = mapped_column(_VECTOR_TYPE, nullable=False)
    content_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
