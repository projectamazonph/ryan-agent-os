from __future__ import annotations

import json
from collections.abc import Mapping

from pydantic import BaseModel

from app.main import app
from app.schemas.agent import (
    AgentContextPackageResponse,
    AgentDefinitionResponse,
    AgentRunEventResponse,
    AgentRunResponse,
    AgentToolInvocationResponse,
)
from app.schemas.capture import CaptureResponse
from app.schemas.classification import ClassificationResult
from app.schemas.execution_pack import (
    ExecutionPackContent,
    ExecutionPackResponse,
    ExecutionPackVersionResponse,
)
from app.schemas.project import ProjectDetailResponse, ProjectResponse
from app.schemas.relation import CaptureRelationResponse
from app.schemas.source import CaptureReviewResponse, FileCaptureResponse, SourceObjectResponse
from app.schemas.task_graph import ImplementationQueueResponse, TaskGraphResponse, TaskResponse


def _json_document(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def render_contracts() -> Mapping[str, str]:
    """Render every checked-in API contract from the current application schemas."""

    models: dict[str, type[BaseModel]] = {
        "docs/schemas/agent-definition.schema.json": AgentDefinitionResponse,
        "docs/schemas/agent-context-package.schema.json": AgentContextPackageResponse,
        "docs/schemas/agent-run.schema.json": AgentRunResponse,
        "docs/schemas/agent-run-event.schema.json": AgentRunEventResponse,
        "docs/schemas/agent-tool-invocation.schema.json": AgentToolInvocationResponse,
        "docs/schemas/capture.schema.json": CaptureResponse,
        "docs/schemas/classification.schema.json": ClassificationResult,
        "docs/schemas/source-object.schema.json": SourceObjectResponse,
        "docs/schemas/file-capture.schema.json": FileCaptureResponse,
        "docs/schemas/capture-review.schema.json": CaptureReviewResponse,
        "docs/schemas/project.schema.json": ProjectResponse,
        "docs/schemas/project-detail.schema.json": ProjectDetailResponse,
        "docs/schemas/capture-relation.schema.json": CaptureRelationResponse,
        "docs/schemas/execution-pack-content.schema.json": ExecutionPackContent,
        "docs/schemas/execution-pack-version.schema.json": ExecutionPackVersionResponse,
        "docs/schemas/execution-pack.schema.json": ExecutionPackResponse,
        "docs/schemas/task.schema.json": TaskResponse,
        "docs/schemas/task-graph.schema.json": TaskGraphResponse,
        "docs/schemas/implementation-queue.schema.json": ImplementationQueueResponse,
    }
    rendered = {"docs/api/openapi.json": _json_document(app.openapi())}
    rendered.update(
        {
            path: _json_document(model.model_json_schema())
            for path, model in models.items()
        }
    )
    return rendered
