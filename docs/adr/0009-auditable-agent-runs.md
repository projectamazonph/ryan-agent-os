# ADR-0009: Auditable bounded agent runs

- Status: Accepted
- Date: 2026-07-13

## Context

Ryan Agent OS must execute specialist work without turning agent behavior into an opaque chat transcript. Every run must identify the exact agent policy, task, approved plan, context, model route, tool permissions, events, cost, retry lineage, and verification outcome.

The MVP also needs to remain reproducible while live provider orchestration and protected connector execution are not yet certified.

## Decision

1. Agent definitions are immutable, versioned records.
2. Every run references one exact definition and one checksum-addressed context package.
3. Context packages preserve task-graph and approved execution-pack provenance.
4. Run state changes are guarded and emitted as append-only sequenced events.
5. Tool requests are authorization records. Both allowed and denied decisions are persisted.
6. Retries create new runs and retain the original context-package identity and parent lineage.
7. A source run cannot become `succeeded` directly from execution. A QA verification run must issue the verdict.
8. The initial executor and QA evaluator are deterministic baselines.
9. Run traces are exposed through resumable SSE using sequence IDs and `Last-Event-ID`.
10. Protected external side effects remain unavailable until approval-center enforcement exists.

## Consequences

### Positive

- Completion claims are traceable to exact inputs and policy versions.
- Retry behavior does not erase failed attempts.
- Tool-policy violations remain visible even when rejected.
- Deterministic tests can verify state, lineage, policy, and streaming behavior offline.
- The transport can later be backed by Redis pub/sub or a workflow engine without changing the event contract.

### Costs

- More persistence and serialization than a chat-only agent implementation.
- Agent-definition changes require explicit new versions.
- Context selection becomes a first-class engineering responsibility.
- QA adds a separate run and additional latency.

### Limits

- A policy receipt is not connector execution.
- Model-route metadata is not proof that a live model performed the work.
- Database-polled SSE is suitable for the private MVP, not high-fanout production traffic.
