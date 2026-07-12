# ADR-0008: Approved Task Graphs and Deterministic Queue Ranking

## Status

Accepted

## Context

Ryan Agent OS must turn an approved execution-pack version into actionable work without losing provenance, creating duplicate graphs, allowing dependency cycles, or ranking blocked work as immediately executable.

## Decision

1. Each task graph references exactly one approved execution-pack version.
2. Repeating generation for the same version returns the existing graph.
3. Generating a graph from a newer approved version supersedes the prior active graph but does not delete it.
4. Task dependencies form a directed acyclic graph and are validated before persistence.
5. Readiness is derived from dependency states and is not stored as an independently editable status.
6. A task cannot start or complete while any dependency is neither done nor skipped.
7. Only tasks from active graphs appear in the implementation queue.
8. The initial rank score is deterministic:

   `0.35 impact + 0.25 urgency + 0.20 confidence + 0.20 inverse effort`

## Consequences

- Approval provenance remains auditable from plan to task.
- Queue output is reproducible and testable.
- Historical graphs remain available for later diff and audit work.
- The deterministic planner is conservative and currently sequences work linearly.
- Manual ranking overrides and learned prioritization remain future work.
