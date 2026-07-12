# Phase 4 Task Graph and Queue Build Log

## Release

- Version: `0.4.0-task-graph-queue`
- Date: 2026-07-13
- Method: Test-Driven Development and Loop Engineering

## Loop 1: Honest baseline

### Observe

The inherited release passed 32 backend tests and 11 frontend tests.

### Decision

Build the next vertical slice from approved execution-pack provenance through ranked executable work.

## Loop 2: Task-graph boundary

### Red

Tests were written first for:

- cycle rejection with an explicit cycle path
- approval required before generation
- exact approval-version traceability
- idempotent generation for the same version

The first run failed during collection because task-graph schemas and services did not exist.

### Green

Implemented:

- task graph, task, and dependency models
- deterministic graph planner
- dependency validation and DFS cycle detection
- graph generation and retrieval endpoints
- one graph per execution-pack version
- active-graph supersession

### Observe

Three task-graph tests passed.

## Loop 3: Queue and transitions

### Red

Tests were written first for:

- ready work sorted ahead of blocked work
- dependency completion unlocking downstream tasks
- invalid terminal-state reversal

The new endpoints and queue service were absent.

### Green

Implemented:

- queue endpoint
- task status endpoint
- deterministic ranking formula
- derived readiness and blocked-by signals
- audited status transitions

### Observe

Five Phase 4 backend tests passed.

## Loop 4: Browser surface

### Red

Component tests were added before the components. Both failed because the task-graph panel and implementation queue did not exist.

### Green

Implemented:

- project workspace task-graph panel
- explicit graph-creation control
- approval provenance and task readiness display
- ranked queue page
- start, complete, and block controls
- authenticated web proxy routes

### Observe

Three new frontend interaction tests passed.

## Loop 5: Dependency-bypass hardening

### Observe

Review found that a caller could patch a blocked task directly to `in_progress`, bypassing the UI.

### Red

A regression test expected HTTP 409 but received HTTP 200.

### Green

The status service now resolves the active graph and rejects start or completion while dependencies remain unresolved. Superseded-graph tasks are also rejected.

### Observe

The regression passed and downstream unlocking remained green.

## Refactoring

- Moved graph and queue behavior into typed services.
- Kept route handlers focused on authorization, state checks, audit events, and serialization.
- Added reusable dependency-resolution and ranking functions.
- Preserved immutable approval provenance rather than copying untraceable plan text.

## Final validation

- 38 backend tests passed
- 14 frontend tests passed across 8 files
- Ruff passed
- Strict MyPy passed across 60 source files
- ESLint passed
- TypeScript passed
- Migration `0006` passed upgrade, downgrade, and re-upgrade
- Next.js optimized production build passed
- Python dependency integrity passed
- Production npm audit reported zero vulnerabilities
- OpenAPI and fourteen JSON Schemas matched generated contracts

## Deferred gaps

- Live PostgreSQL, Redis, MinIO, worker, and browser-stack certification
- Queue filters, manual rank overrides, scheduling, and stale-work scoring
- Evidence attachment and task verification workflow
- Human and agent assignment
- Agent run orchestration and protected tool execution
