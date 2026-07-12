# Memory and Context

## Purpose

Memory allows Ryan Agent OS to avoid repeated explanations while preventing the uncontrolled accumulation of unreliable AI-generated facts.

## Memory types

### Preference memory
Stable user preferences such as writing standards, artifact rules, naming conventions, and preferred tools.

### Domain memory
Reusable operational knowledge such as Amazon PPC frameworks, campaign taxonomy, or internal process standards.

### Project memory
Decisions, constraints, entities, and state specific to a project.

### Episodic memory
A concise record of what happened during a meaningful interaction or agent run.

### Procedural memory
Reusable workflows, checklists, and agent instructions.

## Memory lifecycle

```text
candidate -> reviewed | auto-approved-by-policy -> active -> superseded | revoked
```

## Memory write requirements

A memory item must include:

- Statement
- Type
- Scope
- Source
- Confidence
- Sensitivity
- Effective date
- Optional expiry
- Supersedes relationship
- Creation actor

## Retrieval strategy

Context assembly combines:

1. Explicit task inputs
2. Approved project decisions
3. Relevant active memories
4. Selected source excerpts
5. Related artifact metadata
6. Recent run state

Retrieval uses hybrid search with scope and permission filters before similarity ranking.

## Conflict handling

When memories conflict:

- Prefer explicit user decisions over inferred preferences
- Prefer newer accepted decisions over older ones
- Prefer project-specific rules over global defaults
- Show the conflict when confidence remains low
- Never silently merge contradictory facts

## Context budgets

Each agent has a context budget. The context builder must summarize lower-priority material and preserve direct excerpts for critical constraints and acceptance criteria.

## Memory controls

Ryan can:

- View why a memory was retrieved
- Edit it
- Revoke it
- Change its scope
- Mark it as sensitive
- Supersede it
- Prevent it from being sent to cloud providers

## Initial persistent preferences for Ryan Agent OS

- Preserve existing content during revisions unless a specific change requires replacement.
- Retain artifact formatting unless instructed otherwise.
- Avoid placeholders in final deliverables.
- Prefer complete, production-usable outputs.
- Keep Amazon PPC naming machine-parsable and consistent.
- Treat MerchantSpring as the main reporting hub and Adbrew as the automation backbone when those systems apply.
- Prefer practical, direct documentation suitable for both operators and newer learners.
