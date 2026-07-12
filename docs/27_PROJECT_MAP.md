# Ryan Agent OS - Project Map

**Version:** 0.4.0-task-graph-queue  
**Generated:** 2026-07-13  
**Repository:** https://github.com/projectamazonph/ryan-agent-os

---

## 🗂️ Repository Structure

```
ryan-agent-os/
├── README.md                    # Project entry point
├── manifest.json               # Version manifest (v0.4.0)
├── docs/                       # Documentation root
│   ├── 00_INDEX.md             # Full documentation index
│   ├── 18_MVP_BACKLOG.md      # Priority backlog
│   ├── 21_IMPLEMENTATION_STATUS.md  # Current status
│   ├── 26_PHASE4_BUILD_LOG.md # Phase 4 build log
│   ├── adr/                    # Architecture Decision Records
│   │   └── 0008-approved-task-graphs.md
│   └── api/
│       └── openapi.json        # API specification
└── foundation/                 # Source code root
    ├── .github/
    │   └── workflows/
    │       └── ci.yml          # CI/CD pipeline (175 lines)
    ├── apps/
    │   ├── api/                # FastAPI backend
    │   └── web/                # Next.js frontend
    ├── docs/                   # Foundation docs (authoritative)
    ├── alembic/versions/      # DB migrations (0001-0006)
    ├── package.json
    ├── package-lock.json
    ├── Makefile
    ├── docker-compose.yml
    └── scripts/
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Ryan Agent OS                          │
│                 Personal AI Orchestration                   │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
    ┌───────────────┐                 ┌───────────────┐
    │   Frontend    │                 │    Backend    │
    │   (Next.js)   │  ←──── API ──→  │   (FastAPI)   │
    └───────────────┘                 └───────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                               ▼
                      ┌───────────────┐               ┌───────────────┐
                      │  PostgreSQL   │               │    Redis      │
                      │   (15)       │               │    (7)        │
                      └───────────────┘               └───────────────┘
```

---

## 🖥️ Frontend Architecture (Next.js)

**Location:** `foundation/apps/web/`

### Directory Structure
```
foundation/apps/web/
├── app/
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Landing page
│   ├── login/
│   │   └── page.tsx                  # Auth page
│   ├── dashboard/
│   │   ├── page.tsx                  # Main dashboard
│   │   ├── capture-form.tsx
│   │   ├── capture-review-panel.tsx  # Review captures
│   │   ├── execution-pack-panel.tsx  # Pack management
│   │   ├── task-graph-panel.tsx      # Visual task graphs ⭐
│   │   ├── implementation-queue.tsx  # Ranked task queue ⭐
│   │   ├── project-list.tsx
│   │   ├── queue/
│   │   │   └── page.tsx              # Queue page
│   │   ├── captures/
│   │   │   └── [captureId]/
│   │   │       └── page.tsx          # Capture detail
│   │   └── projects/
│   │       ├── page.tsx              # Projects list
│   │       └── [projectId]/
│   │           └── page.tsx          # Project detail
│   └── api/                         # API routes
│       ├── session/route.ts
│       ├── captures/
│       ├── projects/
│       └── tasks/
├── lib/
│   ├── types.ts                     # TypeScript types ⭐
│   └── api.ts                       # API client
├── test/
│   └── setup.ts                     # Test setup
├── vitest.config.ts
├── next.config.ts
└── package.json
```

### Frontend Key Types (`lib/types.ts`)
```typescript
// Core Types
Capture, Project, ProjectDetail, SourceObject
RelatedCapture, CaptureReview

// Classification
ClassificationResult {
  domain, intent, confidence,
  evidence[], engine, needs_review
}

// Execution Packs
ExecutionPack, ExecutionPackVersion, ExecutionPackContent
  - objective, problem_statement, success_criteria
  - in_scope[], out_of_scope[], assumptions[]
  - deliverables[], workstreams[], risks[]
  - recommended_agents[]

// Task Graph ⭐ (Phase 4 Feature)
Task {
  id, key, title, description, verification
  status: "planned" | "in_progress" | "blocked" | "done" | "skipped"
  impact, urgency, confidence, effort (0-100)
  rank_score, position
  dependency_keys[], blocked_by[], is_ready
}

TaskGraph {
  id, project_id, status
  source_execution_pack_version_id, version_number, approved_at
  tasks: Task[]
}
```

---

## ⚙️ Backend Architecture (FastAPI)

**Location:** `foundation/apps/api/`

### Directory Structure
```
foundation/apps/api/
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 0001_foundation.py
│       ├── 0002_capture_sources.py
│       ├── 0003_project_registry.py
│       ├── 0004_intelligence_layer.py
│       ├── 0005_execution_packs.py
│       └── 0006_task_graphs.py      # ⭐ Phase 4
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── deps.py                  # Dependencies
│   │   ├── router.py
│   │   └── v1/routes/
│   │       ├── health.py
│   │       ├── auth.py
│   │       ├── captures.py
│   │       ├── projects.py
│   │       ├── task_graphs.py       # ⭐ Phase 4
│   │       └── tasks.py             # ⭐ Phase 4
│   ├── core/
│   │   ├── config.py
│   │   ├── auth.py
│   │   ├── logging.py
│   │   ├── request_id.py
│   │   └── uuid7.py                 # Time-ordered UUIDs
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── identity.py             # Workspace, Owner
│   │   ├── capture.py
│   │   ├── source.py                # SourceObject
│   │   ├── project.py
│   │   ├── embedding.py
│   │   ├── relation.py
│   │   ├── execution_pack.py
│   │   ├── task.py                  # ⭐ TaskGraph, Task, TaskDependency
│   │   ├── audit.py
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── capture.py
│   │   ├── source.py
│   │   ├── classification.py
│   │   ├── project.py
│   │   ├── relation.py
│   │   ├── execution_pack.py
│   │   ├── task_graph.py            # ⭐ Phase 4
│   │   └── __init__.py
│   └── services/
│       ├── workspace.py
│       ├── audit.py
│       ├── execution_pack.py
│       ├── task_graph.py             # ⭐ Phase 4
│       └── __init__.py
└── main.py
```

---

## 📊 Database Schema (PostgreSQL)

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `workspaces` | Multi-tenant isolation | id, owner_id, name |
| `owners` | User authentication | id, email, hashed_password |
| `captures` | User input/memory | id, workspace_id, type, content, classification |
| `source_objects` | File attachments | id, capture_id, storage_key, extraction_status |
| `projects` | Work containers | id, workspace_id, title, status, priority |
| `relations` | Capture→Project links | capture_id, project_id, score, reasons |
| `execution_packs` | Project planning | id, project_id, status, current_version_number |
| `execution_pack_versions` | Plan versions | id, pack_id, version_number, content_json, approved_at |
| `task_graphs` ⭐ | Project task DAGs | id, project_id, execution_pack_version_id, status |
| `tasks` ⭐ | Individual tasks | id, graph_id, key, status, impact/urgency/confidence/effort, rank_score |
| `task_dependencies` ⭐ | Task edges | task_id, depends_on_task_id |
| `audit_events` | Action logging | id, workspace_id, actor, action, resource_type, metadata |

### Task States ⭐
```
planned ──→ in_progress ──→ done
    │              │
    ▼              ▼
 blocked      skipped
```

### Rank Score Formula ⭐
```
rank_score = (0.35 × impact) + (0.25 × urgency) + (0.20 × confidence) - (0.20 × effort)
```

---

## 🔗 API Endpoints

### Core Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/captures` | Create capture |
| GET | `/api/v1/captures/{id}` | Get capture |
| PATCH | `/api/v1/captures/{id}/archive` | Archive capture |
| POST | `/api/v1/captures/{id}/retry` | Retry extraction |
| GET | `/api/v1/captures/{id}/relations` | Related captures |
| POST | `/api/v1/captures/files` | File upload |
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/{id}` | Get project |
| POST | `/api/v1/projects/{id}/captures/{cid}` | Link capture |
| POST | `/api/v1/projects/{id}/execution-pack` | Create pack |
| POST | `/api/v1/projects/{id}/execution-pack/approve` | Approve pack |
| POST | `/api/v1/projects/{id}/task-graph` ⭐ | Generate task graph |
| GET | `/api/v1/projects/{id}/task-graph` ⭐ | Get task graph |
| PATCH | `/api/v1/tasks/{id}` ⭐ | Update task status |

---

## 📁 Documentation Index

**Location:** `foundation/docs/00_INDEX.md`

### ADR (Architecture Decision Records)
| ID | Title | Status |
|----|-------|--------|
| ADR-0001 | Project initialization | Approved |
| ADR-0002 | Capture & classification | Approved |
| ADR-0003 | Workspace isolation | Approved |
| ADR-0004 | Intelligence layer | Approved |
| ADR-0005 | Execution packs | Approved |
| ADR-0006 | Database design | Approved |
| ADR-0007 | TDD Loop Engineering | Approved |
| ADR-0008 ⭐ | Approved task graphs | Approved |

### JSON Schemas (14 total)
| Schema | Purpose |
|--------|---------|
| capture.schema.json | Capture validation |
| classification.schema.json | Classification result |
| source-object.schema.json | File metadata |
| project.schema.json | Project model |
| task-graph.schema.json | Graph structure |
| task.schema.json | Task model |
| implementation-queue.schema.json | Ranked queue |
| execution-pack*.schema.json | Planning documents |

---

## 🧪 Test Coverage

| Layer | Tests | Status |
|-------|-------|--------|
| Backend (Pytest) | 38 passed | ✅ |
| Frontend (Vitest) | 14 passed | ✅ |
| MyPy Type Check | 60 files | ✅ |
| Ruff Lint | All | ✅ |
| ESLint | All | ✅ |
| Alembic Round-trip | 0006 | ✅ |

---

## 🚀 CI/CD Pipeline

**File:** `foundation/.github/workflows/ci.yml` (175 lines)

### Jobs
1. **backend-tests** - Python 3.11/3.12, PostgreSQL 15, Redis 7
2. **frontend-tests** - Node 18/20, npm ci && test
3. **lint** - ESLint + TypeScript check
4. **security-audit** - npm audit (zero high/critical)
5. **release-validation** - SHA256 + manifest verification on tags `v*`

### Triggers
- Push/PR to `main` or `develop`
- Manual dispatch
- Tag push `v*`

---

## 📦 Phase 4 Features (Task Graph & Queue)

### Features Implemented ✅
- Task Graph DAG with cycle detection
- Idempotent graph generation per execution-pack version
- Graph supersession (new version → new graph, old preserved)
- Task state machine with guarded transitions
- Ranked cross-project implementation queue
- Project workspace task-graph panel
- Implementation-queue page with drag-drop

### Features Deferred 🔜
- Queue filters (status, project, assignee)
- Manual rank overrides
- Scheduling and deadlines
- Agent run orchestration
- Approval center UI
- Artifact registry
- External connectors

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 |
| Database | PostgreSQL 15, Alembic migrations |
| Cache | Redis 7 |
| Testing | Pytest, Vitest, MyPy, Ruff, ESLint |
| Container | Docker Compose |
| CI/CD | GitHub Actions |
| API | OpenAPI 3.1 (auto-generated) |

---

## 📍 Local Development

```bash
# Start services
cd foundation
docker-compose up -d postgres redis

# Backend
cd apps/api
pip install -e .
uvicorn app.main:app --reload

# Frontend
cd apps/web
npm install
npm run dev

# Run tests
cd foundation
make test           # All tests
make test-backend    # Backend only
make test-frontend   # Frontend only

# Quality checks
make lint           # Ruff + ESLint
make type-check     # MyPy + TypeScript
```

---

*This map reflects the state of Ryan Agent OS v0.4.0-task-graph-queue*
