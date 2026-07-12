# Observability and Evaluation

## Objectives

The system must explain what it did, why it did it, what it cost, and whether the result passed verification.

## Telemetry layers

### Application metrics

- Request latency
- Error rate
- Queue depth
- Worker utilization
- Database latency
- Storage failures
- Connector rate limits

### Agent metrics

- Runs by agent and model
- Success and failure rate
- Tool-call count
- Retry count
- Token usage
- Estimated cost
- Time to first output
- Total run duration
- Human intervention rate

### Product metrics

- Capture conversion rate
- Approved execution-pack rate
- Active projects with next actions
- Verified-task rate
- Delivery rate
- Reopened-project rate
- Duplicate detection acceptance

## Trace model

Every user request, job, agent run, tool call, artifact, and external action shares a correlation ID.

## Logs

Logs must be structured JSON and contain:

- Timestamp
- Severity
- Service
- Request or job ID
- Workspace ID
- Actor type
- Event name
- Safe metadata

Logs must exclude secrets and raw sensitive content by default.

## Agent evaluation

### Offline evaluation set

Create a curated dataset from representative Ryan workflows:

- Conversation to PRD
- PPC audit planning
- Codebase review task decomposition
- Course module creation
- Documentation revision preserving existing content
- Duplicate project detection
- Protected connector action

### Scoring dimensions

- Intent accuracy
- Deliverable relevance
- Task decomposition quality
- Constraint retention
- Unsupported assumption rate
- Evidence quality
- Citation accuracy
- Format compliance
- User edit distance

## Quality gates

A new agent or prompt version cannot become default unless it:

- Meets or exceeds the current version on critical cases
- Has no policy regressions
- Keeps cost within the accepted threshold
- Passes structured output validation

## Human feedback

Ryan can rate outputs and identify defects. Feedback is attached to the exact prompt, model, context package, and artifact version to support useful iteration rather than vague prompt astrology.

## Alerts

Alert conditions include:

- Repeated connector failures
- Approval bypass attempt
- Sudden model-cost spike
- Agent retry loop
- Queue backlog above threshold
- Artifact validation failures
- Backup failure
- Storage nearing capacity
