from __future__ import annotations

from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    domain: str = Field(min_length=1, max_length=80)
    intent: str = Field(min_length=1, max_length=80)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list, max_length=12)
    engine: str = Field(min_length=1, max_length=80)
    needs_review: bool
