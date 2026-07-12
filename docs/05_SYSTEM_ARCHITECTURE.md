# System Architecture

## Architecture choice

Ryan Agent OS starts as a modular monolith with background workers and clearly separated domain modules. This provides faster development and simpler operations than premature microservices while preserving future extraction boundaries.

## High-level architecture

```mermaid
flowchart LR
    U[Ryan] --> WEB[Next.js Web App]
    WEB --> API[FastAPI Application]
    API --> AUTH[Auth and Policy]
    API --> CAP[Capture Module]
    API --> PROJ[Project Module]
    API --> TASK[Task Graph]
    API --> APR[Approval Module]
    API --> ART[Artifact Module]
    API --> MEM[Memory and Search]
    API --> AGW[Agent Gateway]
    API --> RUN[Agent Run Service]

    CAP --> DB[(PostgreSQL + pgvector)]
    PROJ --> DB
    TASK --> DB
    APR --> DB
    ART --> DB
    MEM --> DB
    RUN --> DB

    API --> REDIS[(Redis)]
    REDIS --> WORKERS[Background Workers]
    WORKERS --> AGW
    WORKERS --> PARSERS[Document Parsers]
    WORKERS --> CONNECTORS[External Connectors]
    WORKERS --> STORAGE[(Object Storage)]

    AGW --> LOCAL[Hermes / Local Models]
    AGW --> CLOUD[Cloud Model Providers]

    CONNECTORS --> GH[GitHub]
    CONNECTORS --> GD[Google Drive]
    CONNECTORS --> CU[ClickUp]
    CONNECTORS --> GM[Gmail and Calendar]
```

## Major components

### Web application

Responsibilities:

- Capture interface
- Implementation queue
- Project workspace
- Execution pack editor
- Agent run console
- Approval center
- Artifact viewer
- Search
- Settings and connector management

The web app contains presentation logic only. Domain decisions remain in the API.

### API application

Responsibilities:

- Authentication and authorization
- Domain validation
- Transactional writes
- Query APIs
- Policy evaluation
- Job submission
- Webhook handling
- Audit logging

### Background workers

Responsibilities:

- File extraction
- Embedding generation
- Classification
- Duplicate detection
- Execution pack generation
- Agent-run execution may move to workers after a durable workflow engine is selected
- External connector operations
- Artifact conversion
- Verification jobs

### PostgreSQL

PostgreSQL is the system of record for structured records. pgvector stores embeddings for semantic retrieval. Object binaries remain in object storage.

### Redis

Redis provides:

- Job queue backing
- Short-lived locks
- Idempotency keys
- Rate limiting
- Cache
- Future distributed live-agent event fanout

Redis is not a source of truth.

### Object storage

Stores original inputs, generated artifacts, exports, screenshots, and evidence files. Each object is addressed through a database record containing checksum, content type, sensitivity, and provenance.

### Agent run service

The current modular service provides:

- Versioned agent-definition lookup
- Immutable context-package construction
- Guarded run-state transitions
- Append-only run events
- Tool-policy receipts
- Retry and verification lineage
- Deterministic execution and QA baselines
- Database-polled resumable SSE traces

It currently executes in the API process. A workflow engine and distributed event transport remain future extraction candidates.

### Agent gateway

The gateway exposes one internal interface for model providers and agent runtimes. It handles:

- Model selection
- Prompt assembly
- Tool allowlists
- Structured outputs
- Token accounting
- Retries
- Timeouts
- Safety and policy checks
- Provider fallback

The gateway is implemented for typed classification adapters. General agent runs record routing metadata but use the deterministic executor in release 0.5.0.

### Connector layer

Each external system uses an adapter with:

- Typed operations
- Explicit permission scopes
- Idempotency support
- Dry-run support where possible
- Audit events
- Webhook verification
- Rate-limit handling

## Module boundaries

```text
identity
capture
projects
planning
tasks
agents
approvals
artifacts
memory
search
connectors
notifications
audit
settings
```

Modules communicate through application services and domain events rather than writing directly into each other's tables.

## Event examples

- `capture.received`
- `capture.extracted`
- `capture.classified`
- `project.created`
- `execution_pack.approved`
- `task.ready`
- `agent_run.started`
- `approval.requested`
- `approval.granted`
- `artifact.created`
- `task.verified`
- `project.completed`

## Deployment topology

### Local development

- Web container
- API container
- Worker container
- PostgreSQL
- Redis
- MinIO
- Optional local model service

### Production MVP

- Managed PostgreSQL
- Managed Redis
- S3-compatible object storage
- Web deployment
- API deployment
- Worker deployment
- Secret manager
- Centralized logs and error tracking

## Scaling path

Likely future extraction candidates:

1. Document processing worker
2. Agent execution service
3. Search and retrieval service
4. Connector service
5. Artifact rendering service

Extraction should occur only after measured operational pressure, not architectural fashion.
