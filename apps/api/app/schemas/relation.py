from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

CaptureRelationAction = Literal["reference", "merge"]


class CaptureRelationCreate(BaseModel):
    target_capture_id: UUID
    action: CaptureRelationAction


class CaptureRelationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    source_capture_id: UUID
    target_capture_id: UUID
    relation_type: str
    created_at: datetime
