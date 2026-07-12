# Documentation Index

This folder defines the product, architecture, operating model, and build sequence for Ryan Agent OS.

## Read in this order

1. [Product Vision](01_PRODUCT_VISION.md)
2. [Product Requirements Document](02_PRD.md)
3. [Users, Jobs, and Operating Context](03_USERS_AND_JOBS.md)
4. [Scope and Functional Requirements](04_SCOPE_AND_REQUIREMENTS.md)
5. [System Architecture](05_SYSTEM_ARCHITECTURE.md)
6. [Domain and Data Model](06_DOMAIN_AND_DATA_MODEL.md)
7. [Agent Architecture](07_AGENT_ARCHITECTURE.md)
8. [Core Workflows](08_CORE_WORKFLOWS.md)
9. [API Contracts](09_API_CONTRACTS.md)
10. [Integrations](10_INTEGRATIONS.md)
11. [Security and Privacy](11_SECURITY_PRIVACY.md)
12. [Memory and Context](12_MEMORY_AND_CONTEXT.md)
13. [Artifact System](13_ARTIFACT_SYSTEM.md)
14. [Observability and Evaluation](14_OBSERVABILITY_AND_EVALUATION.md)
15. [Deployment and Operations](15_DEPLOYMENT_AND_OPERATIONS.md)
16. [Test Strategy](16_TEST_STRATEGY.md)
17. [Roadmap](17_ROADMAP.md)
18. [MVP Backlog](18_MVP_BACKLOG.md)
19. [Risk Register](19_RISK_REGISTER.md)
20. [Glossary](20_GLOSSARY.md)
21. [Implementation Status](21_IMPLEMENTATION_STATUS.md)
22. [Foundation Build Log](22_FOUNDATION_BUILD_LOG.md)
23. [TDD and Loop Engineering](23_TDD_AND_LOOP_ENGINEERING.md)
24. [Phase 2 Core Build Log](24_PHASE2_BUILD_LOG.md)
25. [Phase 3 Intelligence and Execution Build Log](25_PHASE3_BUILD_LOG.md)
26. [Phase 4 Task Graph and Queue Build Log](26_PHASE4_BUILD_LOG.md)

## Architecture decisions

- [ADR-0001: Documentation-first development](adr/0001-documentation-first.md)
- [ADR-0002: Modular monolith for the MVP](adr/0002-modular-monolith.md)
- [ADR-0003: Human approval for external side effects](adr/0003-human-approval-gates.md)
- [ADR-0004: PostgreSQL as the system of record](adr/0004-postgresql-system-of-record.md)
- [ADR-0005: Provider-agnostic model gateway](adr/0005-provider-agnostic-model-gateway.md)
- [ADR-0006: Foundation implementation choices](adr/0006-foundation-implementation.md)
- [ADR-0007: TDD and Loop Engineering](adr/0007-tdd-loop-engineering.md)
- [ADR-0008: Approved task graphs and queue ranking](adr/0008-approved-task-graphs.md)

## Runbooks

- [Local Development](runbooks/LOCAL_DEVELOPMENT.md)
- [Incident Response](runbooks/INCIDENT_RESPONSE.md)
- [Backup and Restore](runbooks/BACKUP_AND_RESTORE.md)
- [Release Process](runbooks/RELEASE_PROCESS.md)

## Standards and templates

- [Documentation Style Guide](standards/DOCUMENTATION_STYLE_GUIDE.md)
- [Definition of Done](standards/DEFINITION_OF_DONE.md)
- [Prompt Specification Standard](standards/PROMPT_SPECIFICATION_STANDARD.md)
- [Architecture Decision Record Template](templates/ADR_TEMPLATE.md)
- [Build Log Template](templates/BUILD_LOG_TEMPLATE.md)
- [Evaluation Record Template](templates/EVALUATION_RECORD_TEMPLATE.md)

## Generated contracts

- [Current OpenAPI specification](api/openapi.json)
- [Capture JSON Schema](schemas/capture.schema.json)
- [Classification JSON Schema](schemas/classification.schema.json)
- [Source Object JSON Schema](schemas/source-object.schema.json)
- [File Capture JSON Schema](schemas/file-capture.schema.json)
- [Capture Review JSON Schema](schemas/capture-review.schema.json)
- [Project JSON Schema](schemas/project.schema.json)
- [Project Detail JSON Schema](schemas/project-detail.schema.json)
- [Capture Relation JSON Schema](schemas/capture-relation.schema.json)
- [Execution Pack Content JSON Schema](schemas/execution-pack-content.schema.json)
- [Execution Pack Version JSON Schema](schemas/execution-pack-version.schema.json)
- [Execution Pack JSON Schema](schemas/execution-pack.schema.json)

- [Task JSON Schema](schemas/task.schema.json)
- [Task Graph JSON Schema](schemas/task-graph.schema.json)
- [Implementation Queue JSON Schema](schemas/implementation-queue.schema.json)
