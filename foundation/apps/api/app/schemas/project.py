from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.capture import CaptureResponse

ProjectStatus = Literal["planned", "active", "on_hold", "completed", "archived"]


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    summary: str | None = Field(default=None, max_length=20_000)
    domain: str | None = Field(default=None, max_length=80)
    status: ProjectStatus = "planned"
    priority: int = Field(default=50, ge=0, le=100)
    next_action: str | None = Field(default=None, max_length=5000)
    blocker: str | None = Field(default=None, max_length=5000)


class ProjectFromCaptureRequest(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    summary: str | None = Field(default=None, max_length=20_000)
    status: ProjectStatus = "planned"
    priority: int = Field(default=50, ge=0, le=100)
    next_action: str | None = Field(default=None, max_length=5000)
    blocker: str | None = Field(default=None, max_length=5000)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    title: str
    summary: str | None
    domain: str | None
    status: str
    priority: int
    next_action: str | None
    blocker: str | None
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectResponse):
    captures: list[CaptureResponse]


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
