# ADR-0007: Test-Driven Development and Loop Engineering

- Status: Accepted
- Date: 2026-07-13

## Context

Ryan Agent OS will coordinate persistent memory, generated artifacts, automation, and eventually protected external actions. Small regressions can therefore corrupt context, duplicate work, or trigger unintended side effects. A test-after implementation style would provide weak evidence and make agent-generated changes difficult to trust.

## Decision

All product behavior will be developed through Test-Driven Development and tight Loop Engineering cycles:

`Frame -> Red -> Green -> Refactor -> Observe -> Adjust`

Tests are written or updated before implementation. The expected failure must be observed. The smallest passing implementation is added, then refactored while tests remain green. Each vertical slice finishes with the full applicable regression gate and a documented outcome.

## Consequences

### Positive

- Behavior is specified before code shape hardens.
- Defects become permanent regression coverage.
- Agent work produces evidence rather than unsupported completion claims.
- Smaller loops reduce the blast radius of changes.
- Refactoring remains safer as the system grows.

### Costs

- Initial delivery may appear slower than untested implementation.
- Test fixtures and boundaries require ongoing maintenance.
- Some browser and external integration paths need dedicated infrastructure.

## Enforcement

- `make check` is the local release gate.
- CI runs backend tests, frontend tests, static checks, reversible migrations, and the production build.
- The Definition of Done requires tests-first evidence.
- Build logs record loop outcomes and deferred gaps.
