# Scope and Functional Requirements

## MVP boundary

The MVP is a governed execution manager. It does not need to solve every downstream task itself. It must reliably decide what work exists, organize it, route it, and prove what happened.

## Module 1: Capture Inbox

### Capabilities

- Paste text or Markdown
- Upload supported files
- Add URLs
- Save source metadata
- Tag domain and sensitivity
- Process input asynchronously
- Display extraction errors
- Archive irrelevant captures

### Required states

`received -> extracting -> classified -> reviewed -> converted | linked | archived | failed`

## Module 2: Project Registry

Each project contains:

- Name and stable identifier
- Domain
- Problem statement
- Desired outcome
- Status
- Priority
- Impact score
- Effort score
- Confidence score
- Owner
- Current phase
- Next action
- Blockers
- Source captures
- Deliverables
- Tasks
- Decisions
- Risks
- Artifacts
- Related projects

## Module 3: Implementation Queue

### Default ranking model

```text
priority_score =
  strategic_value * 0.30
  + urgency * 0.20
  + unblock_value * 0.15
  + completion_proximity * 0.15
  + staleness * 0.10
  + confidence * 0.10
  - effort_penalty
```

Scores use a normalized 0-100 scale. Ryan can override the system ranking at any time.

### Views

- Today
- High impact
- Quick wins
- Blocked
- Waiting for approval
- Agent running
- Needs review
- Stale
- Completed

## Module 4: Execution Pack Builder

### Planning modes

- Lightweight: outcome, deliverables, tasks, next action
- Standard: adds risks, decisions, dependencies, acceptance criteria
- Deep: adds alternatives, architecture, estimates, evaluation plan, rollout, rollback

### Review behavior

The generated pack is never considered approved by default. Ryan can edit, regenerate a section, accept all, or reject the recommendation.

## Module 5: Task Graph

### Task fields

- Title
- Description
- Type
- Status
- Priority
- Owner type and owner ID
- Parent task
- Dependencies
- Blockers
- Input references
- Expected outputs
- Acceptance criteria
- Required approvals
- Execution policy
- Evidence
- Retry count
- Start and completion timestamps

### Statuses

`backlog, ready, blocked, awaiting_approval, running, needs_review, verified, failed, cancelled`

## Module 6: Agent Run Console

The console must show:

- Agent identity and role
- Task and objective
- Context package
- Tools allowed
- Model used
- Prompt version
- Live state
- Tool calls
- Output preview
- Cost and token information when available
- Error and retry history
- Stop control

## Module 7: Approval Center

Approval is required for:

- Sending email or messages
- Creating or modifying calendar events with attendees
- Publishing content
- Deleting or moving external files
- Merging pull requests
- Deploying production code
- Spending money
- Changing advertising campaigns or budgets
- Sharing files outside approved domains
- Exporting sensitive data to external providers

## Module 8: Artifact Library

Artifacts can include:

- Markdown
- PDF
- DOCX
- PPTX
- XLSX
- CSV
- Images
- Source code
- Repositories
- Links
- Reports
- Test evidence

Each artifact must be versioned and linked to its producer and sources.

## Module 9: Decision and Evidence Log

### Decisions

Important decisions include:

- Scope choices
- Architecture decisions
- Tool selection
- Naming rules
- Approval outcomes
- User overrides
- Accepted risks

### Evidence

Evidence can include:

- Test output
- Screenshots
- File checksums
- External API responses
- Review comments
- Validation reports
- User approval

## Module 10: Search and Memory

Search must support:

- Exact term search
- Semantic similarity
- Filters
- Related records
- Source previews
- Date ranges
- Project-scoped search

Memory writes must be explicit, categorized, and reversible.
