from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

CaptureType = Literal["conversation", "note", "markdown", "url", "repository"]
Sensitivity = Literal["public", "internal", "confidential", "restricted"]


class CaptureCreate(BaseModel):
    type: CaptureType = "conversation"
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1, max_length=500_000)
    domain_hint: str | None = Field(default=None, max_length=80)
    sensitivity: Sensitivity = "internal"


class CaptureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    type: str
    title: str
    content: str
    domain_hint: str | None
    sensitivity: str
    status: str
    review_status: str
    summary: str | None
    classification: dict[str, Any] | None
    checksum_sha256: str
    created_at: datetime
    updated_at: datetime


class CaptureListResponse(BaseModel):
    items: list[CaptureResponse]
