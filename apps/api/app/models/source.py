from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.uuid7 import uuid7
from app.db.base import Base


class SourceObject(Base):
    """A database record for an immutable source blob.

    The bytes addressed by ``storage_key`` are write-once. Extraction state and
    derived text may change without replacing the original object.
    """

    __tablename__ = "source_objects"
    __table_args__ = (
        UniqueConstraint("capture_id", name="uq_source_object_capture"),
        UniqueConstraint(
            "workspace_id", "checksum_sha256", name="uq_source_workspace_checksum"
        ),
        UniqueConstraint("storage_key", name="uq_source_storage_key"),
        Index("ix_source_objects_workspace_created", "workspace_id", "created_at"),
        Index("ix_source_objects_extraction_status", "extraction_status"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    capture_id: Mapped[UUID] = mapped_column(
        ForeignKey("captures.id", ondelete="CASCADE"), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(700), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(300), nullable=False)
    content_type: Mapped[str] = mapped_column(String(160), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    extraction_status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extraction_attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
