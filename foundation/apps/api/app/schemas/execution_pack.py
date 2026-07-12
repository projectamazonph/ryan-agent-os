from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeliverableSpec(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=4000)
    format: str = Field(min_length=1, max_length=120)
    acceptance_criteria: list[str] = Field(min_length=1, max_length=12)


class WorkstreamSpec(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1, max_length=2000)
    steps: list[str] = Field(min_length=1, max_length=20)


class ExecutionPackContent(BaseModel):
    objective: str = Field(min_length=1, max_length=4000)
    problem_statement: str = Field(min_length=1, max_length=4000)
    success_criteria: list[str] = Field(min_length=1, max_length=20)
    in_scope: list[str] = Field(min_length=1, max_length=30)
    out_of_scope: list[str] = Field(default_factory=list, max_length=30)
    assumptions: list[str] = Field(default_factory=list, max_length=30)
    deliverables: list[DeliverableSpec] = Field(min_length=1, max_length=20)
    workstreams: list[WorkstreamSpec] = Field(min_length=1, max_length=20)
    risks: list[str] = Field(default_factory=list, max_length=30)
    recommended_agents: list[str] = Field(default_factory=list, max_length=20)


class ExecutionPackGenerateRequest(BaseModel):
    change_summary: str | None = Field(default=None, max_length=2000)


class ExecutionPackApproveRequest(BaseModel):
    version_number: int = Field(ge=1)


class ExecutionPackVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version_number: int
    content: ExecutionPackContent
    change_summary: str | None
    created_at: datetime
    approved_at: datetime | None


class ExecutionPackResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    current_version_number: int
    current_version: ExecutionPackVersionResponse
    versions: list[ExecutionPackVersionResponse]
