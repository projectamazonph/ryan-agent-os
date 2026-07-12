# Phase 2 Core Build Log

## Build

- Release: `0.2.0-phase2-core`
- Date: 2026-07-13
- Method: Test-Driven Development and Loop Engineering
- Scope: File ingestion, extraction, typed classification, capture review, and project registry

## Loop 1: Immutable file ingestion

### Red

Added failing API tests for authenticated multipart upload, MIME validation, size limits, immutable checksums, object storage persistence, and exact-file idempotency.

### Green

Implemented source objects, S3-compatible byte storage, upload guardrails, checksum-addressed records, and `POST /api/v1/captures/files`.

### Observation

Exact re-uploads return the existing capture and source object rather than creating duplicates.

## Loop 2: Extraction and typed classification

### Red

Added failing tests for plain text extraction, structured document extraction, unsupported extraction behavior, typed model-gateway output, and failure-state persistence.

### Green

Implemented extraction for text, Markdown, CSV, HTML, JSON, PDF, and DOCX sources. Added the provider-agnostic `ModelGateway` protocol and a deterministic `RulesModelGateway` returning validated classification data.

### Observation

Extraction failures store an explicit error and retryable state rather than leaving a capture indefinitely processing.

## Loop 3: Capture review and related context

### Red

Added failing review tests requiring immutable source provenance, classification output, and ranked related captures.

### Green

Implemented `GET /api/v1/captures/{capture_id}/review` and deterministic lexical related-capture ranking.

### Observation

The lexical scorer provides a stable fallback. Vector embeddings and true semantic hybrid ranking remain deferred.

## Loop 4: File upload and review interface

### Red

Added component tests for multipart file submission and review rendering.

### Green

Implemented the file capture form, authenticated server proxy, capture review page, source details, classification evidence, and related-capture display.

### Defect found

The initial browser test exposed an unsafe assumption that implicit form serialization would preserve the selected `File`. The component now appends the selected object explicitly to `FormData`.

## Loop 5: Project registry

### Red

Added failing backend tests for project creation, idempotent capture linking, project search, status history, and capture archival. Added frontend tests for create-project, archive, and registry rendering.

### Green

Implemented project models, status history, capture links, project APIs, searchable project list, project workspace pages, create-from-capture action, archive action, and tested server proxies.

### Observation

Capture-to-project conversion is durable and traceable. Merge actions, decisions, risks, and project relation graphs remain deferred.

## Loop 6: Release hardening

### Red and observation

The release gate found:

- Alembic import-order and migration-format violations
- A Next.js build process that completed but held the interactive execution channel open outside CI mode

### Green

- Corrected formatting and import order.
- Added explicit CI and telemetry-disabled settings to the production-build gate.
- Added reversible migration checks to `make check` and CI.
- Regenerated OpenAPI and JSON Schema contracts.
- Verified Python and production npm dependency integrity.

## Loop 7: Generated-contract drift protection

### Red

Added a test that imported a not-yet-existing contract renderer and failed during collection.

### Green

Implemented a single renderer for OpenAPI and all checked-in JSON Schemas, added a reusable generation command, and made contract synchronization part of the backend regression suite.

### Observation

Schema or route changes now fail the release gate until generated contracts are intentionally refreshed.

## Validation evidence

- Backend tests: 21 passed
- Frontend component tests: 5 passed across 4 files
- Ruff: passed
- Strict MyPy: passed across 47 source files
- Alembic upgrade, downgrade, and re-upgrade: passed
- ESLint: passed
- TypeScript: passed
- Next.js optimized production build: passed
- Python dependency check: no broken requirements
- Production npm audit: 0 vulnerabilities
- OpenAPI and seven JSON Schemas regenerated

## Deferred from complete Phase 2

- pgvector storage and embeddings
- Semantic vector retrieval and hybrid fusion
- Cloud-model adapter
- Hermes/local-model adapter
- Dedicated extraction retry controls in the UI
- Explicit merge and reference-only review actions
- Full browser end-to-end suite against PostgreSQL, Redis, and MinIO

These are not represented as complete. The current release is the validated Phase 2 core.
