# Integrations

## Integration strategy

External tools remain systems of engagement. Ryan Agent OS remains the system of record for project intent, approvals, provenance, and execution state.

## GitHub

### MVP capabilities

- Read repositories, issues, pull requests, branches, files, and checks
- Create issues
- Create branches and commits through an approved workflow
- Open draft pull requests
- Read review comments
- Record CI status

### Protected actions

- Pushing code
- Opening a pull request
- Merging a pull request
- Deleting branches
- Changing repository settings

### Stored references

- Repository owner and name
- External object ID
- URL
- Last synchronized state
- Commit SHA
- Connector account

## Google Drive

### MVP capabilities

- Search files and folders
- Create project folders
- Upload artifacts
- Create Google Docs from approved content
- Export supported file types
- Record sharing state

### Folder convention

```text
Ryan Agent OS/
  Projects/
    <Domain>/
      <Project Name>/
        01 Source
        02 Planning
        03 Working
        04 Deliverables
        05 Archive
```

### Protected actions

- Deleting files
- Moving files outside the project folder
- Sharing externally
- Changing ownership

## ClickUp

### MVP capabilities

- Create tasks from approved execution packs
- Sync status, owner, due date, and external URL
- Import comments and completion state
- Link ClickUp tasks back to Ryan Agent OS tasks

Ryan Agent OS remains authoritative for agent runs, evidence, and artifact provenance. ClickUp can remain authoritative for human-team operational scheduling when configured per project.

## Gmail

### MVP capabilities

- Search and read relevant email when explicitly requested
- Draft project-related email
- Link messages to projects

Sending email always requires explicit approval.

## Google Calendar

### MVP capabilities

- Read availability
- Propose events
- Create approved events
- Link events to projects

Inviting attendees or modifying existing events requires approval.

## Hermes and local agents

### Role

Hermes can run private or routine agent tasks locally.

### Requirements

- Stable local endpoint
- Health check
- Model inventory
- Context-window metadata
- Structured output support or repair layer
- Tool permission mapping
- Run logs returned to Ryan Agent OS

## Model providers

Provider adapters must expose:

- Generate structured output
- Stream output
- Tool calls
- Embeddings
- Image understanding where supported
- File context where supported
- Usage and cost metadata

## Connector health

The settings screen shows:

- Connection state
- Granted scopes
- Last successful call
- Last error
- Rate-limit state
- Token expiry
- Reauthorization action
