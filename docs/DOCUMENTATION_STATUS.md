# Documentation Status

## Baseline version

0.1.0

## Current implementation release

`0.5.0-agent-execution`, validated on 2026-07-13.

## Status

The documentation remains the build contract. The repository now implements the foundation, immutable ingestion, extraction, typed classification, hybrid related-context retrieval, capture-review actions, project registry, versioned execution packs, approval-traceable task graphs, guarded task transitions, ranked implementation queue, versioned agent definitions, immutable context packages, auditable runs, tool-policy receipts, QA verification, and resumable live run traces.

Test-Driven Development and Loop Engineering remain mandatory through ADR-0007. Task-graph rules are recorded in ADR-0008. Agent-run identity, lineage, policy, verification, and trace decisions are recorded in ADR-0009. Release evidence is recorded in the Phase 5 build log.

## Resolved decisions

1. Foundation queue: minimal Redis list abstraction behind a replaceable interface
2. Local object storage: MinIO through an S3-compatible adapter
3. Private MVP authentication: environment-managed owner credentials and JWT bearer tokens
4. Identifier strategy: application-generated UUIDv7
5. Model boundary: provider-agnostic typed gateway
6. Model transport: OpenAI-compatible contract for cloud and Hermes adapters
7. Development embedding baseline: deterministic local hash projection
8. Embedding persistence: pgvector-compatible capture vectors
9. Related-context retrieval: lexical and semantic score fusion with lexical fallback
10. Engineering method: tests first, then smallest passing implementation and full-loop validation
11. Execution planning baseline: typed deterministic planner with immutable versions and explicit approval
12. Task-graph provenance: one graph per approved execution-pack version
13. Active-work policy: a newer graph supersedes older graphs without deleting history
14. Readiness policy: readiness is derived from live dependency state, not manually assigned
15. Ranking baseline: 35% impact, 25% urgency, 20% confidence, and 20% inverse effort
16. Agent policy identity: immutable definitions with explicit integer versions
17. Agent context identity: canonical checksum-addressed packages tied to exact task and approval provenance
18. Run history: append-only sequenced events and immutable retry or verification lineage
19. Completion policy: execution reaches review; a QA run is required for success
20. Tool policy baseline: persist both allowed and denied authorization decisions
21. Event transport baseline: resumable SSE with query cursors and `Last-Event-ID`
22. Agent execution baseline: deterministic bounded executor until live providers are certified

## Open decisions before affected production work

1. Final authentication provider
2. Long-running workflow engine for agent orchestration
3. Production cloud model provider and model selection
4. Certified Hermes deployment endpoint and authentication contract
5. Production semantic embedding model, vector dimensions, index type, and benchmark thresholds
6. First GitHub authorization method
7. Initial production hosting platform
8. Production secret manager
9. Queue filters, manual ranking override policy, and stale-work thresholds
10. Human-versus-agent task assignment policy
11. Protected-action policy language and approval expiry defaults
12. Artifact storage, renderer isolation, and validation service boundaries
13. Distributed run-event transport and retention limits
14. QA benchmark suites and minimum pass thresholds per agent type

These decisions do not invalidate the current local MVP slice. They block the relevant production orchestration, connector, artifact, evaluation, or deployment work.
