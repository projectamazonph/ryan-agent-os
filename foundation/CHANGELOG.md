# Changelog

## 0.4.0-task-graph-queue - 2026-07-13

### Added

- Approval-traceable task graphs generated from exact execution-pack versions.
- Task, dependency, and graph persistence with reversible migration `0006`.
- Duplicate-key, unknown-dependency, and cycle validation.
- Idempotent graph generation and active-graph supersession.
- Guarded task transitions with dependency-bypass protection.
- Ranked cross-project implementation queue.
- Project task-graph panel and dedicated queue interface.
- Three generated contracts for tasks, task graphs, and queue responses.
- ADR-0008 and Phase 4 TDD build log.

### TDD evidence

- Wrote task-graph, queue, transition, and browser interaction tests before implementation.
- Added a second red loop after review proved a blocked task could bypass dependencies through the API.

### Validation

- 38 backend tests pass.
- 14 frontend component tests pass across 8 files.
- Ruff, strict MyPy, ESLint, TypeScript, reversible migrations, and optimized build pass.
- Python dependency integrity passes.
- Production npm audit reports zero vulnerabilities.
- OpenAPI and fourteen JSON Schemas are synchronized with the live application models.

## 0.3.0-intelligence-execution - 2026-07-13

### Added

- Deterministic local embedding gateway and pgvector-compatible capture embedding storage.
- Hybrid lexical-semantic related-capture ranking with a deterministic fallback.
- OpenAI-compatible cloud and Hermes adapters for typed summary and classification responses.
- Extraction retry endpoint, queue injection boundary, and retry controls in the capture review interface.
- Explicit capture reference and merge relations with idempotent persistence.
- Versioned execution-pack schema, deterministic planner, regeneration, approval, and project workspace interface.
- Four additional generated JSON Schema contracts for relations and execution packs.

### Changed

- Upgraded the application version to 0.3.0.
- Extended source records with extraction-attempt metadata.
- Extended the worker to generate embeddings after successful extraction.
- Updated the local PostgreSQL image to a pgvector-enabled distribution.
- Expanded the release gate to protect all generated API contracts from drift.

### TDD evidence

- Added tests before implementation for embeddings, hybrid retrieval, provider gateways, retry behavior, capture relations, execution packs, and frontend review actions.
- Corrected a stale checked-in OpenAPI baseline found by the contract-drift test before starting new feature work.

### Validation

- 32 backend tests pass.
- 11 frontend component tests pass across 6 files.
- Ruff, strict MyPy, ESLint, TypeScript, reversible migrations, and optimized build pass.
- Python dependency integrity passes.
- Production npm audit reports zero vulnerabilities.
- OpenAPI and eleven JSON Schemas are synchronized with the live application models.

## 0.2.0-phase2-core - 2026-07-13

### Added

- Immutable multipart file ingestion with checksum-addressed source records and S3-compatible byte storage.
- Extraction jobs for text, Markdown, CSV, HTML, JSON, PDF, and DOCX.
- Provider-agnostic model gateway and typed deterministic classification output.
- Capture review API and interface with source provenance and lexical related-context ranking.
- Project registry, create-from-capture, idempotent linking, search, status history, and project workspaces.
- Frontend component-test infrastructure.
- Test-Driven Development and Loop Engineering policy, ADR, and release evidence.
- Reversible migration validation in local and CI gates.

### Changed

- Extended `make check` to include backend tests, frontend tests, migrations, static analysis, and optimized build.
- Regenerated OpenAPI and seven JSON Schema contracts.
- Production builds now run explicitly in CI mode with telemetry disabled.

### Validation

- 21 backend tests pass.
- 5 frontend component tests pass.
- Ruff, strict MyPy, ESLint, TypeScript, reversible migrations, and optimized build pass.
- Python dependency integrity passes.
- Production npm audit reports zero vulnerabilities.

## 0.1.0 - 2026-07-13

### Added

- Renamed the product to Ryan Agent OS.
- Established the documentation-first product baseline.
- Added product vision, PRD, users and jobs, scope, architecture, domain model, agent architecture, workflows, API contracts, integrations, security, memory, artifact, observability, deployment, testing, roadmap, backlog, risks, and glossary.
- Added initial architecture decision records, runbooks, standards, and templates.

## 0.1.0-foundation - 2026-07-13

### Added

- Runnable Next.js and FastAPI monorepo foundation.
- PostgreSQL-compatible models and reversible Alembic migration.
- Redis job queue and capture-processing worker.
- MinIO-compatible object-storage adapter.
- Owner login, JWT authorization, workspace bootstrap, request IDs, and audit events.
- Capture Inbox API and responsive web interface.
- Exact duplicate capture prevention and deterministic starter classification.
- CI, tests, generated OpenAPI, JSON Schemas, and implementation status documentation.

### Security

- Upgraded to a patched Next.js release after package-manager security feedback.
- Overrode the affected PostCSS dependency and verified zero production npm audit findings.

### Validation

- Seven backend tests pass.
- Python lint, formatting, and strict typing pass.
- Frontend lint, type checks, and production build pass.
- Alembic round-trip migration and live API smoke test pass.
