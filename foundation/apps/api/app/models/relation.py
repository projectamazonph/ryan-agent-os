from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.uuid7 import uuid7
from app.db.base import Base


class CaptureRelation(Base):
    __tablename__ = "capture_relations"
    __table_args__ = (
        UniqueConstraint(
            "source_capture_id",
            "target_capture_id",
            "relation_type",
            name="uq_capture_relation",
        ),
        CheckConstraint(
            "source_capture_id <> target_capture_id", name="ck_capture_relation_distinct"
        ),
        Index("ix_capture_relations_source", "source_capture_id", "created_at"),
        Index("ix_capture_relations_target", "target_capture_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    source_capture_id: Mapped[UUID] = mapped_column(
        ForeignKey("captures.id", ondelete="CASCADE"), nullable=False
    )
    target_capture_id: Mapped[UUID] = mapped_column(
        ForeignKey("captures.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
