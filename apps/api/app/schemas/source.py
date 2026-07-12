from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.capture import CaptureResponse
from app.schemas.project import ProjectResponse


class SourceObjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    capture_id: UUID
    storage_key: str
    original_filename: str
    content_type: str
    size_bytes: int
    checksum_sha256: str
    extraction_status: str
    extracted_text: str | None
    extraction_error: str | None
    metadata_json: dict[str, Any]
    created_at: datetime
    extracted_at: datetime | None
    extraction_attempts: int
    last_attempt_at: datetime | None


class FileCaptureResponse(BaseModel):
    capture: CaptureResponse
    source: SourceObjectResponse


class RelatedCaptureResponse(BaseModel):
    capture: CaptureResponse
    score: float
    reasons: list[str]


class CaptureReviewResponse(BaseModel):
    capture: CaptureResponse
    source: SourceObjectResponse | None
    related: list[RelatedCaptureResponse]
    projects: list[ProjectResponse]
