from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

TaskStatus = Literal["planned", "in_progress", "blocked", "done", "skipped"]


class TaskDraft(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=10_000)
    verification: str = Field(min_length=1, max_length=5000)
    impact: int = Field(default=50, ge=0, le=100)
    urgency: int = Field(default=50, ge=0, le=100)
    confidence: int = Field(default=50, ge=0, le=100)
    effort: int = Field(default=50, ge=0, le=100)
    dependencies: list[str] = Field(default_factory=list, max_length=30)


class TaskResponse(BaseModel):
    id: UUID
    task_graph_id: UUID
    project_id: UUID
    project_title: str
    key: str
    title: str
    description: str
    verification: str
    status: str
    impact: int
    urgency: int
    confidence: int
    effort: int
    rank_score: int
    position: int
    dependency_keys: list[str]
    blocked_by: list[str]
    is_ready: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class TaskGraphResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    source_execution_pack_version_id: UUID
    source_execution_pack_version_number: int
    source_execution_pack_approved_at: datetime
    created_at: datetime
    tasks: list[TaskResponse]


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class ImplementationQueueResponse(BaseModel):
    items: list[TaskResponse]
