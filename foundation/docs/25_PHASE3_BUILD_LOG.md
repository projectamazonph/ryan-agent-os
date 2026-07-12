# Phase 3 Intelligence and Execution Build Log

## Build

- Release: `0.3.0-intelligence-execution`
- Date: 2026-07-13
- Method: Test-Driven Development and Loop Engineering
- Scope: Embeddings, hybrid retrieval, model adapters, review completion, and versioned execution packs

## Baseline correction

### Observation

The first baseline run found that the checked-in OpenAPI contract did not match the live application, despite the previous release record marking contracts as synchronized.

### Adjustment

The generated contract was refreshed before new feature implementation. The existing drift test remained mandatory and later caught the expected route and schema changes from this phase.

### Result

Feature work began from an honestly green baseline rather than carrying a false release claim forward.

## Loop 1: Embedding persistence

### Red

Added failing tests for deterministic embedding generation, normalized vectors, idempotent capture embedding persistence, and cosine similarity.

### Green

Implemented `EmbeddingGateway`, `HashEmbeddingGateway`, pgvector-compatible `CaptureEmbedding`, embedding upsert, and capture text construction.

### Refactor

Kept embedding generation behind a protocol so a production provider can replace the deterministic baseline without changing retrieval or persistence callers.

### Observation

The local hash projection is reproducible and offline, but it is not a substitute for a benchmarked semantic embedding model.

## Loop 2: Hybrid related-context retrieval

### Red

Added a failing retrieval test requiring semantic ranking to improve on lexical-only matching while preserving a fallback when vectors are unavailable.

### Green

Implemented lexical and cosine scoring with deterministic fusion: 40 percent lexical and 60 percent semantic.

### Observation

Related results now identify semantic similarity explicitly. Missing embeddings do not break review because the lexical path remains active.

## Loop 3: Cloud and Hermes model gateways

### Red

Added failing contract tests for cloud and local Hermes gateways using mocked OpenAI-compatible transports, typed output validation, API-key handling, and provider configuration.

### Green

Implemented `CloudModelGateway`, `HermesModelGateway`, strict response parsing, timeout configuration, and `build_model_gateway`.

### Observation

The adapters are contract-tested without live external calls. Real endpoint certification remains a deployment task.

## Loop 4: Retry and capture relations

### Red

Added failing service and API tests for retry queueing, extraction-attempt metadata, idempotent reference relations, merge state, and project-link propagation.

### Green

Implemented an injectable job queue boundary, retry endpoint, relation model and service, and reference and merge endpoints.

### Refactor

Capture routes now receive the queue through dependency injection rather than constructing it directly, improving testability and later workflow-engine replacement.

## Loop 5: Review interface completion

### Red

Added component tests for retrying extraction, linking to an existing project, creating a reference, and merging a related capture.

### Green

Implemented authenticated proxy routes and review controls for every tested action.

### Observation

The UI no longer stops at displaying recommendations; the owner can resolve the review directly.

## Loop 6: Versioned execution packs

### Red

Added backend tests for typed deterministic planning, first-version creation, regeneration to version two, approval of a specific version, and retrieval. Added frontend tests for generating and approving packs.

### Green

Implemented execution-pack and version models, typed content schemas, a deterministic planner, generate, regenerate, get, and approve endpoints, and a project-workspace panel.

### Observation

The system now converts project context into a durable, reviewable plan. Section editing, diffing, and task-graph generation remain explicit follow-on work.

## Loop 7: Contract and release hardening

### Red

The generated-contract drift test failed after the new routes and schemas were introduced.

### Green

Expanded the generated schema set to include capture relations and execution-pack content, version, and aggregate responses. Regenerated the OpenAPI document and all schemas.

### Full observation loop

- Backend tests: 32 passed
- Frontend component tests: 11 passed across 6 files
- Ruff: passed
- Strict MyPy: passed across 55 source files
- Alembic upgrade, downgrade, and re-upgrade: passed
- ESLint: passed
- TypeScript: passed
- Next.js optimized production build: passed
- Python dependency check: no broken requirements
- Production npm audit: 0 vulnerabilities
- OpenAPI and eleven JSON Schemas synchronized

## Environment limitation

Docker was unavailable. The build did not execute the complete PostgreSQL, Redis, MinIO, worker, and browser stack. Pgvector migration logic is present and PostgreSQL uses `pgvector/pgvector:pg17`, but live container validation is still required.

## Next loop

Start task-graph generation from an approved execution-pack version. Write failing tests first for deterministic task creation, dependency integrity, cycle rejection, regeneration idempotency, and immutable linkage to the approved source version.
