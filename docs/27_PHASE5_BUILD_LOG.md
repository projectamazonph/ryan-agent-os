# Phase 5 Agent Execution Build Log

## Release

- Version: `0.5.0-agent-execution`
- Date: 2026-07-13
- Method: Test-Driven Development and Loop Engineering

## Loop 1: Honest baseline

### Observe

The inherited release passed 38 backend tests and 14 frontend tests, but the checked-in OpenAPI file was stale.

### Decision

Regenerate the contract and restore a genuinely green baseline before adding agent execution. Contract drift was treated as a release defect, not ignored as generated-file noise.

## Loop 2: Agent registry and immutable context

### Red

Tests were written first for:

- idempotent built-in definition seeding
- immutable version history
- ready-task enforcement
- exact task, graph, approval, and source provenance
- checksum-stable context packages

The first run failed because no agent models, schemas, registry, or context builder existed.

### Green

Implemented:

- versioned agent-definition persistence
- six bounded built-in definitions
- typed policy and evaluation contracts
- immutable context-package persistence
- canonical context hashing and exact-package reuse

### Observe

Registry and context tests passed without weakening task-readiness rules.

## Loop 3: Run state machine and receipts

### Red

Tests were written first for:

- guarded state transitions
- append-only event sequences
- usage and cost records
- cancellation and retry lineage
- same-context retry behavior
- tool allow and deny auditing
- QA-only success promotion

### Green

Implemented:

- auditable run, event, and tool-invocation models
- bounded deterministic executor
- transition validator
- retry and cancellation services
- policy decisions persisted before responses
- QA verification child runs and verdicts

### Observe

Ten focused backend tests passed, including explicit invalid-transition and denied-tool cases.

## Loop 4: Operator console

### Red

Component tests were added before the launch and console components. They failed because ready-task launch, run actions, and state-aware controls did not exist.

### Green

Implemented:

- agent launcher in the implementation queue
- agent registry summary
- run console
- execute, cancel, retry, and verify controls
- authenticated Next.js proxy routes
- state, model, usage, cost, output, and error display

### Observe

Frontend interaction tests passed and the complete browser suite remained green.

## Loop 5: Resumable run-event stream

### Red

An API test expected a cursor-based `text/event-stream` response and received HTTP 404.

### Green

Implemented:

- ordered SSE frames with event IDs and named event types
- `after_sequence` cursor
- bounded follow duration
- heartbeat comments
- isolated streaming database sessions

### Observe

The stream test passed without leaking the stream session.

## Loop 6: Browser reconnection interoperability

### Observe

Review found that native `EventSource` reconnects with `Last-Event-ID`, while the first stream implementation only accepted a query cursor.

### Red

The resume test sent `Last-Event-ID: 3` and received earlier events.

### Green

The endpoint now chooses the later of the query cursor and `Last-Event-ID`. A same-origin streaming proxy forwards the browser header. An on-demand trace component deduplicates and orders events by sequence.

### Observe

The API resume regression and the mocked-EventSource component test passed.

## Refactoring

- Kept route handlers focused on authorization, audit records, response mapping, and transport.
- Moved definition, context, execution, transition, retry, tool-policy, and verification behavior into typed services.
- Reused exact context packages across retries instead of rebuilding mutable prompts.
- Used append-only run events as the trace source rather than deriving history from current state.
- Opened live streams only on demand to avoid one persistent connection per rendered run card.

## Final validation

- 49 backend tests passed
- 18 frontend tests passed across 11 files
- Ruff passed
- Strict MyPy passed across 67 source files
- ESLint passed
- TypeScript passed
- Migration `0007` passed upgrade, downgrade, and re-upgrade
- Next.js optimized production build passed
- Python dependency integrity passed
- Production npm audit reported zero vulnerabilities
- OpenAPI and nineteen JSON Schemas matched generated contracts

## Deferred gaps

- Live PostgreSQL, Redis, MinIO, worker, and browser-stack certification
- Distributed SSE fanout or durable workflow orchestration
- Live general-purpose agent execution through Hermes or a cloud provider
- Actual connector invocation behind the tool-policy records
- Human approval requests for protected actions
- Domain-deep and model-backed QA evaluation
- Artifact registry and validated delivery pipeline
