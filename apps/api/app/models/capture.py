from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.uuid7 import uuid7
from app.db.base import Base, TimestampMixin


class Capture(TimestampMixin, Base):
    __tablename__ = "captures"
    __table_args__ = (
        UniqueConstraint("workspace_id", "checksum_sha256", name="uq_capture_workspace_checksum"),
        Index("ix_captures_workspace_created", "workspace_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    domain_hint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sensitivity: Mapped[str] = mapped_column(String(24), nullable=False, default="internal")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="received", index=True)
    review_status: Mapped[str] = mapped_column(
        String(24), nullable=False, default="unreviewed", index=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
