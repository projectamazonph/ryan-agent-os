# Test-Driven Development and Loop Engineering

## Decision

Ryan Agent OS uses Test-Driven Development and Loop Engineering as mandatory delivery practices.

A feature is not considered implemented merely because the code runs. It must be introduced through a controlled loop that produces repeatable evidence.

## Core development loop

Every behavior change follows this sequence:

1. **Frame**
   - Define one observable behavior and its acceptance criteria.
   - Identify the smallest test boundary that can prove it.
2. **Red**
   - Write or update the test before implementation.
   - Run it and confirm that it fails for the expected reason.
   - A test that passes before the change does not prove the new behavior.
3. **Green**
   - Implement the smallest correct change that satisfies the test.
   - Avoid unrelated refactors or speculative abstractions.
4. **Refactor**
   - Improve naming, structure, duplication, and boundaries while the focused tests remain green.
5. **Observe**
   - Run the focused suite, adjacent regression tests, static checks, migrations, and build checks that apply.
   - Inspect logs, state transitions, API contracts, and generated artifacts where relevant.
6. **Adjust**
   - Record defects, unexpected behavior, design friction, and the next smallest loop.
   - Convert every corrected defect into a regression test.

## Loop levels

### Micro loop

Used for a domain rule, parser, schema, component interaction, or state transition.

Expected duration: one tightly scoped change.

Evidence:

- One initially failing test
- Minimal passing implementation
- Focused test result

### Vertical-slice loop

Used for behavior that crosses UI, API, service, persistence, queue, or storage boundaries.

Evidence:

- Contract or integration test
- Relevant unit and component tests
- Migration validation when the data model changes
- API or browser smoke evidence

### Release loop

Used before packaging or publishing a release.

Required command:

```bash
make check
```

The release loop includes:

- Ruff
- Strict MyPy
- Backend tests
- Alembic upgrade, downgrade, and re-upgrade
- ESLint
- TypeScript
- Frontend component tests
- Optimized Next.js production build

Dependency integrity and generated-contract checks are also required for a packaged release.

## Test boundaries

Use the lowest boundary that proves the behavior, then add broader coverage only where integration risk exists.

- **Unit tests:** deterministic business rules, parsers, ranking, schemas, and state transitions
- **Service tests:** database behavior, idempotency, extraction, queue handling, and storage boundaries
- **API tests:** authorization, validation, response contracts, and error behavior
- **Component tests:** user interactions, multipart submission, review actions, loading, and error states
- **End-to-end tests:** critical multi-system workflows once the supporting infrastructure is stable
- **Contract tests:** model gateways, connectors, generated schemas, and external adapters

## Rules

1. Never delete or weaken a valid test merely to make a build pass.
2. Never mock the behavior under test.
3. Mock external boundaries, not domain logic.
4. Tests must assert outcomes, not implementation trivia.
5. Every migration must be tested in both directions when reversible.
6. Every production defect must add a regression test.
7. A flaky test is a defect and blocks release until fixed or quarantined with a documented owner and reason.
8. Generated files must be validated, not only checked for existence.
9. External side effects require approval-path tests before connector execution is enabled.
10. Documentation and generated contracts must be updated in the same loop as behavior changes.

## Evidence record

Each completed loop should record:

- Behavior targeted
- Initial failing test and failure reason
- Minimal implementation
- Refactor performed
- Focused result
- Full regression result
- Defects found during observation
- Deferred work and next loop

The build logs are the release-level evidence record. Pull requests or task records should preserve micro-loop evidence through commits, test names, or attached command output.

## Definition of complete

A change is complete only when:

- Acceptance criteria are mapped to tests or other concrete evidence.
- The relevant test was observed failing before implementation.
- The focused tests pass.
- The full applicable regression gate passes.
- Documentation reflects actual behavior.
- Deferred scope is explicit.
- No test, warning, or known failure is misrepresented as green.
