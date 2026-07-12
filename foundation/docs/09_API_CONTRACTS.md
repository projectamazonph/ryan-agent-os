# API Contracts

The generated specification at [`api/openapi.json`](api/openapi.json) is authoritative for endpoints implemented in the repository. This document separates the current contract from the intended later surface.

## API conventions

- REST JSON API for transactional and query operations
- OpenAPI generated from FastAPI schemas
- `/api/v1` version prefix
- UUIDv7 identifiers
- RFC 3339 timestamps in UTC
- Bearer authentication for API calls
- Server-side cookie session for the web proxy

## Implemented endpoints

### Health and identity

- `GET /health/live`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Captures and sources

- `GET /api/v1/captures`
- `POST /api/v1/captures`
- `POST /api/v1/captures/files`
- `GET /api/v1/captures/{capture_id}`
- `POST /api/v1/captures/{capture_id}/process`
- `POST /api/v1/captures/{capture_id}/retry`
- `GET /api/v1/captures/{capture_id}/review`
- `POST /api/v1/captures/{capture_id}/archive`
- `POST /api/v1/captures/{capture_id}/projects`
- `POST /api/v1/captures/{capture_id}/relations`

### Projects

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/captures/{capture_id}`

### Execution packs

- `GET /api/v1/projects/{project_id}/execution-pack`
- `POST /api/v1/projects/{project_id}/execution-pack`
- `POST /api/v1/projects/{project_id}/execution-pack/approve`

Posting to the execution-pack endpoint creates the first version or regenerates a new version. Approval names the exact version number, preserving traceability.

### Task graphs and queue

- `GET /api/v1/projects/{project_id}/task-graph`
- `POST /api/v1/projects/{project_id}/task-graph`
- `GET /api/v1/queue`
- `PATCH /api/v1/tasks/{task_id}`

Task-graph generation requires the current execution-pack version to be approved. Generation is idempotent per approved version, preserves version and approval timestamps, rejects cyclic drafts, and supersedes the prior active graph when a newer approved version is materialized. Queue readiness is derived from dependency state.

## Generated schemas

The contract generator writes:

- Capture
- Classification
- Source object
- File capture
- Capture review
- Project
- Project detail
- Capture relation
- Execution-pack content
- Execution-pack version
- Execution pack
- Task
- Task graph
- Implementation queue

The backend regression suite compares every checked-in generated file with the live application schemas. Route or model drift blocks release until contracts are intentionally regenerated.

## Current error behavior

FastAPI validation errors use the framework-standard `HTTPValidationError` schema. Domain-level missing-resource and invalid-state paths currently use HTTP status codes and `detail` messages. The target normalized error envelope remains deferred.

Target envelope:

```json
{
  "error": {
    "code": "approval_required",
    "message": "This action requires owner approval.",
    "details": {},
    "request_id": "req_01J9K6QY2R9P3X5K8N2G"
  }
}
```

## Planned endpoints

The following are product targets and are not represented as implemented:

### Remaining task operations

- `GET /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/{task_id}/run`
- `POST /api/v1/tasks/{task_id}/verify`
- Queue filter, manual rank override, evidence, and stale-work endpoints

### Agent runs

- `GET /api/v1/agent-runs/{run_id}`
- `GET /api/v1/agent-runs/{run_id}/events`
- `POST /api/v1/agent-runs/{run_id}/stop`
- `POST /api/v1/agent-runs/{run_id}/retry`

### Approvals

- `GET /api/v1/approvals`
- `GET /api/v1/approvals/{approval_id}`
- `POST /api/v1/approvals/{approval_id}/approve`
- `POST /api/v1/approvals/{approval_id}/reject`

### Artifacts and connectors

- Artifact registry, version, validation, delivery, and export endpoints
- Connector authorization, preview, approval, and execution endpoints

## Deferred protocol requirements

- Normalized domain error envelope
- Idempotency keys for protected external writes
- Cursor pagination for large collections
- ETags and `If-Match` for mutable resources
- Provider-signature verification and deduplication for webhooks
- SSE or WebSocket events for agent runs
