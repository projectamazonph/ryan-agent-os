# Test Strategy

## Development policy

Ryan Agent OS uses Test-Driven Development and Loop Engineering.

Every behavior change follows:

`Frame -> Red -> Green -> Refactor -> Observe -> Adjust`

The detailed policy is defined in [Test-Driven Development and Loop Engineering](23_TDD_AND_LOOP_ENGINEERING.md).

## Testing pyramid

### Unit tests

Cover:

- Domain rules
- Ranking calculations
- Policy evaluation
- State transitions
- Agent-definition versioning
- Context checksums and lineage
- Tool allow and deny decisions
- Schema validation
- Context selection
- Idempotency logic

### Service and integration tests

Cover:

- Database repositories
- Queue jobs
- Object storage
- Extraction pipelines
- Model gateway adapters
- Connector adapters using sandboxes or fixtures
- Webhook verification

### API tests

Cover:

- Authentication and authorization
- Input validation and size limits
- Idempotency and duplicate behavior
- State transitions
- Agent-definition versioning
- Context checksums and lineage
- Tool allow and deny decisions
- Error contracts
- Response schemas
- SSE cursors, `Last-Event-ID`, event order, and media type

### Component tests

Cover:

- File and form submission
- Review actions
- Search and filtering
- Loading, success, and failure states
- Client-to-server proxy behavior
- Agent launch, run controls, and mocked EventSource traces

### Contract tests

Each connector and model adapter must pass a shared contract suite. Generated OpenAPI and JSON Schemas must remain synchronized with the implementation.

### End-to-end tests

Critical browser flows:

1. Create or upload a capture
2. Extract and review classification
3. Create or link a project
4. Generate and approve an execution pack
5. Launch, execute, trace, and verify an agent run
6. Approve an external action
7. Review an artifact
8. Verify and complete a project
9. Search and reopen the project

### Artifact tests

Generated files must be opened or rendered by an appropriate validator, not merely checked for existence.

## AI-specific tests

### Deterministic schema tests

All agent outputs must validate against typed schemas.

### Golden-case evaluations

Representative inputs have expected key outcomes rather than brittle exact wording.

### Adversarial tests

Include:

- Prompt injection inside PDF text
- Conflicting instructions
- Hidden requests to expose secrets
- Duplicate external actions
- Oversized context
- Invalid citations
- False claims of test success

### Regression tests

Every corrected defect must produce a test case at the lowest useful boundary.

## Test data

Use synthetic or redacted data. Production content must not enter automated test fixtures without explicit approval.

## CI and release gates

Required before merge or packaging:

- Formatting and linting
- Strict type checks
- Backend tests
- Frontend component tests
- Reversible migration validation
- Dependency integrity and vulnerability scan
- Secret scan when CI infrastructure supports it
- Generated-contract validation
- Optimized production build

The local aggregate gate is:

```bash
make check
```

## Definition of verified

A task is verified only when its acceptance criteria map to evidence. Passing tests that do not cover the stated behavior is not verification. Tests added only after implementation do not satisfy the project's TDD requirement unless the loop is deliberately restarted and the failure is demonstrated.
