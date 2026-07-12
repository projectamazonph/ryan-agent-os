# Agent Architecture

## Operating model

Ryan Agent OS uses a supervised multi-agent model. Agents have narrow responsibilities, explicit tools, typed outputs, and measurable acceptance criteria.

The system does not rely on a single giant prompt pretending to be an entire company. That trick is fun until the imaginary company loses the receipts.

## Agent hierarchy

### 1. Executive Orchestrator

Responsibilities:

- Interpret the approved execution pack
- Build the task graph
- Select specialist agents
- Sequence work
- Request approvals
- Monitor progress
- Escalate blockers
- Compile delivery status

Restrictions:

- Cannot bypass approval policy
- Cannot directly alter external systems unless the relevant tool is explicitly allowed
- Cannot mark work verified without evidence

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
- Add tests
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

Each agent definition must include:

- Stable agent name
- Version
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

## Context package

An agent receives only the context required for its task:

- Task objective
- Acceptance criteria
- Relevant project summary
- Selected source excerpts
- Applicable decisions and constraints
- Tool permissions
- Output schema
- Time and cost limits

The full workspace history is not dumped into every prompt.

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

## Agent lifecycle

```text
created -> queued -> preparing_context -> running -> waiting_for_tool
-> waiting_for_approval -> needs_review -> succeeded | failed | cancelled
```

## Failure policy

- First transient failure: automatic retry with the same model
- Second transient failure: retry with adjusted context or fallback model
- Validation failure: return to the responsible agent with explicit defects
- Policy failure: stop and request human intervention
- Repeated failure: mark blocked and summarize attempts

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
