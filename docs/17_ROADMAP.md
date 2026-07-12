# Implementation Roadmap

## Phase 0: Documentation and decisions

### Goal
Establish the product and technical source of truth.

### Deliverables

- Product vision
- PRD
- Architecture
- Domain model
- Agent model
- Workflows
- API contracts
- Security model
- Test strategy
- MVP backlog
- Architecture decisions

### Status
Implemented and continuously maintained.

## Phase 1: Foundation

### Goal
Create the local development platform and core data model.

### Deliverables

- Monorepo
- Next.js shell
- FastAPI application
- PostgreSQL migrations
- Redis queue
- Object storage
- Authentication
- Audit events
- CI pipeline

### Status
Implemented.

## Phase 2: Capture, intelligence, and project registry

### Goal
Convert raw text and files into reviewed project records.

### Deliverables

- Capture inbox
- File ingestion
- Text extraction
- Classification agent
- Duplicate detection
- Project creation and linking
- Hybrid related-context search
- Capture merge and reference actions

### Status
Implemented with a deterministic embedding baseline and mocked provider-transport tests.

## Phase 3: Execution packs and task graph

### Goal
Turn approved project intent into structured work.

### Deliverables

- Execution-pack generator [implemented]
- Version history and approval flow [implemented]
- Section editor and diff view [deferred]
- Task dependency engine [implemented]
- Implementation queue [implemented]
- Deterministic ranking [implemented]
- Queue filters and manual priority overrides [deferred]

## Phase 4: Agent execution

### Goal
Run bounded specialist agents with complete traces.

### Deliverables

- Versioned agent registry [implemented]
- Immutable context builder [implemented]
- Agent-run state machine [implemented]
- Run console [implemented]
- Tool allowlist and decision receipts [implemented]
- Retry and cancellation [implemented]
- Usage and cost records [implemented]
- QA verification agent [implemented as deterministic baseline]
- Resumable event stream [implemented]
- Live model-driven general execution [deferred]
- Real connector tool execution [deferred]

## Phase 5: Approval center and artifacts

### Goal
Convert verified output into reviewable deliverables and protect every consequential side effect.

### Deliverables

- Protected-action policy registry
- Immutable approval requests
- Approval inbox
- Approve, reject, edit, expire, and revoke flows
- Approval enforcement before connector execution
- Artifact registry
- Immutable artifact versions
- Markdown and structured artifacts
- Validation receipts
- Artifact viewer
- ZIP project export

## Phase 6: Integrations

### Goal
Connect approved execution to Ryan's existing systems.

### Order

1. GitHub
2. Google Drive
3. ClickUp
4. Gmail
5. Calendar
6. Hermes local runtime certification

## Phase 7: Operational intelligence

### Goal
Make the system proactively useful without becoming noisy.

### Deliverables

- Daily operating brief
- Stale-project review
- Project risk signals
- Cost analytics
- Agent performance dashboard
- Reusable workflow templates
- Distributed workflow orchestration and event fanout

## Phase 8: Mobile and collaboration

### Goal
Expand access and controlled team use.

### Deliverables

- Progressive Web App refinements
- Android client or Expo app
- Multi-user roles
- Comments and reviews
- Shared workspace policies
