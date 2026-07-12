# Implementation Status

## Release

- Version: `0.4.0-task-graph-queue`
- Date: 2026-07-13
- Status: Validated task-graph and implementation-queue slice
- Engineering method: Test-Driven Development and Loop Engineering

## Implemented

### Foundation through execution packs retained

- Next.js and FastAPI monorepo
- PostgreSQL-compatible SQLAlchemy models and reversible Alembic migrations
- Redis-backed background queue and S3-compatible immutable storage
- One-owner authentication, request IDs, structured logs, and audit events
- Text and file capture with extraction, classification, embeddings, and hybrid related-context ranking
- Capture review actions and searchable project registry
- Versioned execution packs with deterministic planning and exact-version approval

### Approved task graphs

- One task graph per approved execution-pack version
- Exact source-version ID, version number, and approval timestamp retained in responses
- Deterministic workstream-to-task planner
- Directed task dependencies
- Explicit duplicate-key and unknown-dependency validation
- Deterministic cycle detection with the detected cycle path
- Idempotent graph generation for the same approved version
- Prior active graph superseded when a newer approved version is materialized
- Historical graphs and tasks retained for traceability

### Task state and readiness

- Task states: planned, in progress, blocked, done, and skipped
- Guarded state transitions
- Blocked tasks cannot start or complete before dependencies resolve
- Done and skipped dependencies unlock downstream work
- Completion timestamp retained
- Status changes audited
- Readiness and blocked-by data derived from current dependency state

### Ranked implementation queue

- Cross-project queue from active task graphs only
- Ready work sorted above blocked work
- In-progress work prioritized within ready work
- Deterministic rank score using impact, urgency, confidence, and inverse effort
- Project provenance, verification criteria, dependencies, and score signals shown in the UI
- Start, complete, and manually block controls
- Project workspace task-graph panel
- Dedicated implementation-queue page

### TDD and release discipline

- Tests-first engineering policy and ADR
- Backend unit, service, API, dependency, transition, and contract tests
- Frontend component interaction tests
- Reversible migration gate through migration `0006`
- Generated OpenAPI and JSON Schema drift protection
- Static analysis, dependency integrity, and optimized production-build gates

## Validation evidence

- Backend: 38 tests passed
- Frontend: 14 tests passed across 8 files
- Ruff: passed
- Strict MyPy: passed across 60 source files
- Alembic upgrade, downgrade, and re-upgrade through migration `0006`: passed
- ESLint: passed
- TypeScript: passed
- Next.js optimized production build: passed
- Python dependency integrity: passed
- Production npm dependency audit: 0 vulnerabilities
- OpenAPI and fourteen JSON Schemas regenerated and drift-tested

## Partial backlog coverage

- RAOS-203: private single-owner authorization exists; general role policy remains
- RAOS-603: versioned execution-pack display exists; direct section editor remains
- RAOS-604: full-pack regeneration exists; section-level regeneration remains
- RAOS-507: status history is stored; status-edit workflow remains
- RAOS-704: a ranked queue exists; calendar-aware Today scheduling remains
- RAOS-705: blocked and ready states are visible; dedicated filters remain

## Deliberately deferred

- Section-level execution-pack editing and diff view
- Manual rank override, evidence attachments, and queue filters
- Task assignment, scheduling, estimates, and stale-work policy
- Agent registry, agent-run state machine, tool policy, retry, and cancellation
- Approval center and protected external actions
- Artifact registry and validation pipeline
- External GitHub and Drive writes
- Full container-backed browser end-to-end suite

## Known environment limit

Docker was not available in the build environment. Reversible migrations were validated against SQLite. The PostgreSQL configuration uses a pgvector-enabled image, but a live PostgreSQL, Redis, MinIO, worker, and browser integration run remains required before production deployment.

## Next implementation slice

Create the agent-execution foundation: versioned agent definitions, bounded context packages, an auditable agent-run state machine, tool allowlists, cancellation and retry rules, and a run console. The first red loop should prove that an agent cannot start from a blocked task or invoke a tool outside its policy.
