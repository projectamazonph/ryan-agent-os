# MVP Backlog

## Status legend

- `[x]` validated in the current implementation
- `[~]` partially implemented; remaining scope is explicit in the implementation status
- `[ ]` not implemented

## Epic 0: Documentation baseline

- [x] RAOS-001 Approve documentation index and naming
- [x] RAOS-002 Resolve architecture conflicts through ADRs
- [x] RAOS-003 Define initial data schemas
- [x] RAOS-004 Define API OpenAPI skeleton
- [x] RAOS-005 Define agent output JSON schemas

## Epic 1: Repository and development foundation

- [x] RAOS-101 Create monorepo structure
- [x] RAOS-102 Configure Next.js TypeScript application
- [x] RAOS-103 Configure FastAPI application
- [x] RAOS-104 Configure PostgreSQL and Alembic
- [x] RAOS-105 Configure Redis and worker
- [x] RAOS-106 Configure MinIO for local storage
- [x] RAOS-107 Add linting, formatting, and type checks
- [x] RAOS-108 Add CI pipeline
- [x] RAOS-109 Add structured logging and request IDs
- [x] RAOS-110 Add local setup script and health checks

## Epic 2: Identity and workspace

- [x] RAOS-201 Implement owner login
- [x] RAOS-202 Create workspace model
- [~] RAOS-203 Add roles and permissions foundation
- [ ] RAOS-204 Add encrypted connector-secret storage interface
- [x] RAOS-205 Add audit-event writer

## Epic 3: Capture inbox

- [x] RAOS-301 Create capture API
- [x] RAOS-302 Build capture inbox UI
- [x] RAOS-303 Implement text and Markdown ingestion
- [x] RAOS-304 Implement file upload
- [x] RAOS-305 Store immutable source objects and checksums
- [x] RAOS-306 Add extraction jobs
- [x] RAOS-307 Add capture processing states
- [x] RAOS-308 Add error and retry UI

## Epic 4: Classification and duplicate detection

- [x] RAOS-401 Define classification schema
- [x] RAOS-402 Implement intake agent
- [x] RAOS-403 Implement model gateway abstraction
- [x] RAOS-404 Store confidence and evidence
- [x] RAOS-405 Add embeddings
- [x] RAOS-406 Implement hybrid related-project search
- [x] RAOS-407 Build review screen
- [x] RAOS-408 Add create, link, merge, reference, and archive actions

## Epic 5: Project registry

- [x] RAOS-501 Create project models and API
- [x] RAOS-502 Build project list
- [x] RAOS-503 Build project workspace
- [ ] RAOS-504 Add decisions and risks
- [ ] RAOS-505 Add related-project graph
- [x] RAOS-506 Add next-action and blocker fields
- [~] RAOS-507 Add project status history

## Epic 6: Execution packs

- [x] RAOS-601 Define execution-pack schema
- [x] RAOS-602 Implement planner agent
- [~] RAOS-603 Build versioned execution-pack editor
- [~] RAOS-604 Add section regeneration
- [ ] RAOS-605 Add diff view
- [x] RAOS-606 Add approval action
- [x] RAOS-607 Generate task graph from approved version

## Epic 7: Tasks and implementation queue

- [x] RAOS-701 Create task and dependency models
- [x] RAOS-702 Enforce task state transitions
- [x] RAOS-703 Build queue API
- [~] RAOS-704 Build Today view
- [~] RAOS-705 Add high impact, blocked, approval, review, and stale views
- [x] RAOS-706 Implement ranking formula
- [ ] RAOS-707 Add manual priority override
- [ ] RAOS-708 Add evidence attachments

## Epic 8: Agent runs

- [ ] RAOS-801 Create agent-definition registry
- [ ] RAOS-802 Implement context builder
- [ ] RAOS-803 Implement agent-run state machine
- [ ] RAOS-804 Add tool allowlists
- [ ] RAOS-805 Add streaming events
- [ ] RAOS-806 Build agent-run console
- [ ] RAOS-807 Add retry, stop, and fallback
- [ ] RAOS-808 Record usage and cost
- [ ] RAOS-809 Implement QA verification agent

## Epic 9: Approval center

- [ ] RAOS-901 Define protected action policies
- [ ] RAOS-902 Create approval-request model
- [ ] RAOS-903 Build approval inbox
- [ ] RAOS-904 Add approve, reject, and edit flow
- [ ] RAOS-905 Add expiration and revocation
- [ ] RAOS-906 Enforce approval before connector execution

## Epic 10: Artifacts

- [ ] RAOS-1001 Create artifact registry
- [ ] RAOS-1002 Add immutable versions
- [ ] RAOS-1003 Add Markdown artifact generation
- [ ] RAOS-1004 Add ZIP project export
- [ ] RAOS-1005 Add validation pipeline
- [ ] RAOS-1006 Build artifact viewer
- [ ] RAOS-1007 Add delivery destinations

## Epic 11: First integrations

- [ ] RAOS-1101 Add GitHub OAuth or app authorization
- [ ] RAOS-1102 Read repository and issue metadata
- [ ] RAOS-1103 Preview issue creation
- [ ] RAOS-1104 Execute approved issue creation
- [ ] RAOS-1105 Add Google Drive authorization
- [ ] RAOS-1106 Create approved project folder
- [ ] RAOS-1107 Upload approved artifact

## Epic 12: End-to-end release

- [ ] RAOS-1201 Create complete conversation-to-project test
- [ ] RAOS-1202 Create execution-pack approval test
- [ ] RAOS-1203 Create agent artifact test
- [ ] RAOS-1204 Create protected GitHub action test
- [ ] RAOS-1205 Create project export test
- [ ] RAOS-1206 Run security review
- [ ] RAOS-1207 Run backup restore test
- [ ] RAOS-1208 Publish MVP release notes

## MVP priority order

`RAOS-001 to RAOS-110`, then Epics 2 through 10, followed by the narrow GitHub and Drive paths in Epic 11. ClickUp and other connectors are post-MVP unless they become necessary for the first real project.
