from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.uuid7 import uuid7
from app.db.base import Base, TimestampMixin


class TaskGraph(Base):
    __tablename__ = "task_graphs"
    __table_args__ = (
        UniqueConstraint(
            "execution_pack_version_id", name="uq_task_graph_execution_pack_version"
        ),
        Index("ix_task_graphs_project_status", "project_id", "status"),
        Index("ix_task_graphs_workspace_status", "workspace_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    execution_pack_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("execution_pack_versions.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint("task_graph_id", "key", name="uq_task_graph_key"),
        CheckConstraint("impact >= 0 AND impact <= 100", name="ck_tasks_impact_range"),
        CheckConstraint("urgency >= 0 AND urgency <= 100", name="ck_tasks_urgency_range"),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 100", name="ck_tasks_confidence_range"
        ),
        CheckConstraint("effort >= 0 AND effort <= 100", name="ck_tasks_effort_range"),
        CheckConstraint(
            "rank_score >= 0 AND rank_score <= 100", name="ck_tasks_rank_score_range"
        ),
        Index("ix_tasks_workspace_status_rank", "workspace_id", "status", "rank_score"),
        Index("ix_tasks_project_position", "project_id", "position"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    task_graph_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_graphs.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    verification: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="planned")
    impact: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    urgency: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    effort: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    rank_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    __table_args__ = (
        CheckConstraint("task_id <> depends_on_task_id", name="ck_task_dependency_not_self"),
        Index("ix_task_dependencies_depends_on", "depends_on_task_id"),
    )

    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    depends_on_task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
