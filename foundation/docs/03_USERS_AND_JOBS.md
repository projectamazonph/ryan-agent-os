# Users, Jobs, and Operating Context

## Primary user

Ryan is both the product owner and the first operational user. The system should therefore optimize for speed, power, and transparency rather than generic onboarding for a mass market.

## Ryan's recurring work domains

### Amazon PPC operations

- Audits
- Campaign structures
- Decision matrices
- Playbooks and SOPs
- Client reporting
- Training systems
- Adbrew rule design
- MerchantSpring analysis
- ClickUp operating workflows

### Product and software development

- PRDs
- Build specifications
- Agent prompts
- Repository audits
- UI systems
- Documentation
- Testing and production readiness

### Education and ProjectAmazon.PH

- Course design
- Simulator development
- Lesson content
- Assessment systems
- Student-facing documents
- Brand and marketing assets

### Personal AI infrastructure

- Hermes agents
- Local models
- Memory systems
- Skills and plugins
- Orchestration
- Android-first tools

## Jobs to be done

### JTBD-01: Convert a conversation into execution
When a useful AI conversation ends, Ryan wants the system to identify what should be created and organize the work so the conversation produces a finished result instead of disappearing into history.

### JTBD-02: Resume unfinished work
When Ryan returns to a project after days or weeks, he wants an accurate state summary, current blockers, unresolved decisions, and the next action without rereading everything.

### JTBD-03: Prevent duplicate effort
When a new idea resembles earlier work, Ryan wants the system to surface related projects and recommend merge, supersede, reuse, or continue.

### JTBD-04: Coordinate agents safely
When multiple AI agents can contribute, Ryan wants each agent to have a bounded role, the correct context, explicit acceptance criteria, and limited tool permissions.

### JTBD-05: Produce professional artifacts
When a project needs documents, spreadsheets, slides, code, or reports, Ryan wants consistent structure, retained context, proper versioning, and a known storage destination.

### JTBD-06: Know what matters next
When many projects compete for attention, Ryan wants a ranked implementation queue based on strategic value, urgency, effort, dependency, and staleness.

## Secondary users

Secondary users are not required for the MVP, but the architecture should allow them later:

- GoodWit collaborators
- ProjectAmazon.PH contributors
- Students or trainees
- Contractors
- Reviewers and approvers

## User permissions model

The MVP supports one owner account with future-ready role fields:

- Owner
- Admin
- Operator
- Reviewer
- Viewer
- Agent identity

## Usage patterns

Ryan frequently works from Android, desktop browsers, ChatGPT, GitHub, and Google Drive. The web interface must therefore be responsive, quick to scan, and usable on mobile even before a native app exists.
