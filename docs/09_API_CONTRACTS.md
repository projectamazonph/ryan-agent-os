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
- Named server-sent events for live run traces

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

### Agent definitions and runs

- `GET /api/v1/agents`
- `GET /api/v1/agents/{agent_key}/versions`
- `POST /api/v1/tasks/{task_id}/agent-runs`
- `GET /api/v1/agent-runs`
- `GET /api/v1/agent-runs/{run_id}`
- `GET /api/v1/agent-runs/{run_id}/events`
- `GET /api/v1/agent-runs/{run_id}/events/stream`
- `POST /api/v1/agent-runs/{run_id}/execute`
- `POST /api/v1/agent-runs/{run_id}/cancel`
- `POST /api/v1/agent-runs/{run_id}/retry`
- `POST /api/v1/agent-runs/{run_id}/verify`
- `POST /api/v1/agent-runs/{run_id}/tool-invocations`

Run creation requires a ready task in the active graph. The response includes exact agent version, context package, route metadata, usage, retry lineage, and tool receipts. Execution moves work to review. Verification creates a QA child run and returns both source and QA records.

### Run-event streaming contract

The stream endpoint uses `text/event-stream` and emits:

```text
id: 4
event: run.output_generated
data: {"sequence":4,"event_type":"run.output_generated",...}
```

Supported resume inputs:

- `after_sequence` query parameter
- `Last-Event-ID` request header

The later cursor wins. `follow_seconds` is bounded from zero to sixty seconds. Heartbeats are SSE comments and carry no domain event. Native browser reconnection is supported through the same-origin Next.js proxy.

## Generated schemas

The contract generator writes nineteen schemas:

- Agent definition
- Agent context package
- Agent run
- Agent run event
- Agent tool invocation
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

### Remaining task operations

- `GET /api/v1/tasks/{task_id}`
- Queue filter, manual rank override, evidence, and stale-work endpoints

### Approval center

- `GET /api/v1/approvals`
- `GET /api/v1/approvals/{approval_id}`
- `POST /api/v1/approvals/{approval_id}/approve`
- `POST /api/v1/approvals/{approval_id}/reject`
- `POST /api/v1/approvals/{approval_id}/revoke`

### Artifacts and connectors

- Artifact registry, version, validation, delivery, and export endpoints
- Connector authorization, preview, approval, and execution endpoints

## Deferred protocol requirements

- Normalized domain error envelope
- Idempotency keys for protected external writes
- Cursor pagination for large collections
- ETags and `If-Match` for mutable resources
- Provider-signature verification and deduplication for webhooks
- Redis or workflow-engine fanout for long-lived run streams
