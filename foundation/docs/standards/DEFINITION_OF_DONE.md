# Definition of Done

A product change is done only when:

- Acceptance criteria are explicit and mapped to evidence.
- The relevant test was written or updated before implementation.
- The test was observed failing for the expected reason.
- The smallest correct implementation made the focused test pass.
- Refactoring preserved green tests.
- Relevant unit, service, API, component, contract, and end-to-end tests pass.
- Code is formatted, linted, and type checked.
- Database migrations are included and tested in both directions when reversible.
- Security, permission, privacy, and external-side-effect impacts are reviewed.
- Documentation and generated contracts reflect actual behavior.
- Observability is sufficient to diagnose failure.
- No unresolved placeholders, hidden failures, or misleading completion claims remain.
- Evidence and deferred scope are recorded in the task, pull request, or build log.
- The full applicable release gate passes.

An agent completion message is not evidence by itself. A test that was never observed failing is not sufficient evidence of test-driven development.
