# Agent Architecture

## Operating model

Ryan Agent OS uses a supervised multi-agent model. Agents have narrow responsibilities, explicit tools, typed outputs, measurable acceptance criteria, and immutable versions.

The system does not rely on a single giant prompt pretending to be an entire company. That trick is fun until the imaginary company loses the receipts.

## Implemented registry in release 0.5.0

Six versioned built-in definitions are currently seeded idempotently:

1. Orchestrator
2. Developer
3. Documentation
4. Research
5. QA
6. Amazon PPC

Each definition stores its exact purpose, supported task types, input and output schemas, tool allowlist, denied actions, model policy, iteration limit, timeout, cost ceiling, escalation conditions, and evaluation rubric.

Definitions are immutable. A changed policy creates a new integer version. Runs retain the exact definition ID, key, and version used.

The broader catalog below remains the target operating model. Intake, planning, architecture, artifact, and integration responsibilities may become separate definitions when their runtime boundaries are implemented and evaluated.

## Target agent hierarchy

### 1. Executive Orchestrator

Responsibilities:

- Interpret the approved execution pack
- Select specialist agents
- Sequence ready work
- Request approvals
- Monitor progress
- Escalate blockers
- Compile delivery status

Restrictions:

- Cannot bypass approval policy
- Cannot directly alter external systems unless the relevant tool is explicitly allowed and approved
- Cannot mark work verified without QA evidence

### 2. Intake Analyst

Responsibilities:

- Summarize captures
- Identify intent and desired outcome
- Extract entities, constraints, and commitments
- Flag missing information
- Recommend project linkage

### 3. Project Planner

Responsibilities:

- Generate execution packs
- Decompose deliverables
- Define dependencies
- Write acceptance criteria
- Identify risks and decisions

### 4. Research Agent

Responsibilities:

- Gather external or internal evidence
- Cite sources
- Distinguish fact from inference
- Record uncertainty and freshness

### 5. Documentation Agent

Responsibilities:

- Produce and maintain documentation
- Preserve existing content unless changes are requested
- Enforce document structure and cross-links
- Maintain changelogs and decision logs

### 6. Software Architect

Responsibilities:

- Design technical architecture
- Review boundaries and tradeoffs
- Create ADRs
- Define interfaces and data contracts

### 7. Developer Agent

Responsibilities:

- Implement scoped code changes
- Add tests first
- Update documentation
- Produce build evidence

### 8. QA and Verification Agent

Responsibilities:

- Validate acceptance criteria
- Run tests and checks
- Detect regressions
- Reject unsupported completion claims
- Produce verification evidence

### 9. Artifact Specialist

Responsibilities:

- Generate DOCX, PDF, PPTX, XLSX, images, and exports
- Apply templates and formatting rules
- Validate output integrity

### 10. Integration Operator

Responsibilities:

- Execute approved actions in GitHub, Drive, ClickUp, Gmail, or Calendar
- Use idempotency keys
- Record external IDs and responses
- Stop on permission or conflict errors

### 11. Amazon PPC Strategist

Responsibilities:

- Analyze advertising inputs
- Apply Ryan's PPC frameworks and naming rules
- Produce audit, optimization, training, and reporting deliverables
- Separate branded, research, defense, and performance structures correctly

## Agent definition contract

Each implemented definition includes:

- Stable key and display name
- Integer version
- Purpose
- Allowed task types
- Required input schema
- Output schema
- Allowed tools
- Denied actions
- Model routing policy
- Maximum iterations
- Timeout
- Cost ceiling
- Escalation conditions
- Evaluation rubric
- Active status and creation timestamp

## Context package

An agent receives only the context required for its task:

- Task objective
- Verification and success criteria
- Relevant project summary
- Exact active task-graph identity
- Exact approved execution-pack version
- Selected source excerpts
- Applicable decisions, assumptions, and constraints
- Tool permissions
- Output schema
- Time, iteration, and cost limits

The full workspace history is not dumped into every prompt. Context is serialized canonically, hashed with SHA-256, stored immutably, and reused by exact identity during retries.

## Model routing

### Local models

Preferred for:

- Classification
- Extraction
- Summarization of confidential material
- Routine transformations
- Drafting where privacy is important

### Cloud models

Preferred for:

- Complex reasoning
- Large multimodal documents
- High-stakes synthesis
- Advanced code review
- Artifact generation requiring supported cloud capabilities

### Routing inputs

- Sensitivity
- Complexity
- Context size
- Latency requirement
- Cost ceiling
- Tool support
- Historical evaluation score

### Current runtime truth

Agent runs record provider and model selection. The executor in release 0.5.0 is deterministic and bounded. Live Hermes and cloud execution for general agent tasks remains deferred. Existing OpenAI-compatible adapters cover typed classification and are tested with mocked transports.

## Agent-run lifecycle

```text
queued -> preparing_context -> running -> waiting_for_tool
-> waiting_for_approval -> needs_review -> succeeded | failed | cancelled
```

Transitions are explicitly validated. Runs cannot skip from execution to success. A versioned QA verification run must evaluate a `needs_review` source run and issue the pass or fail verdict.

Each transition creates an append-only event with a per-run sequence number. Events are available through JSON and resumable server-sent event endpoints.

## Tool policy

- The definition's tool allowlist is copied to the run.
- A request outside that list is denied.
- Both allow and deny decisions are stored.
- Arguments are stored with a canonical hash.
- A denied request is committed before HTTP 403 is returned.
- External connector execution is not implemented yet.
- Protected writes will require approval-center authorization in addition to the tool allowlist.

## Failure and retry policy

Current behavior:

- Invalid transitions fail with an explicit conflict.
- A queued or active run may be cancelled where its state permits.
- Failed or cancelled runs may be retried manually.
- A retry creates a new run with an incremented attempt number.
- Retry lineage and exact context-package identity are preserved.
- The retry may select a different provider or model route.
- Failed QA leaves the source run failed with defects retained in the QA output.

Automatic transient retries, provider circuit breakers, and workflow-engine recovery remain deferred.

## Evaluation

Agents are evaluated on:

- Accuracy
- Acceptance-criteria coverage
- Evidence quality
- Citation correctness
- Edit precision
- Tool discipline
- Cost
- Latency
- Rework required
- Policy compliance

The current QA baseline checks structured evidence and criteria coverage deterministically. Domain-deep and model-backed evaluation requires later benchmark work.
