# Ryan Agent OS

Ryan Agent OS is a personal AI execution operating system that converts raw context into governed, traceable work.

## Current release

Version: `0.4.0-task-graph-queue`

The repository now includes:

- Next.js 16 web application
- FastAPI API and background worker
- PostgreSQL with pgvector-compatible models and reversible Alembic migrations
- Redis-backed job queue
- S3-compatible immutable source storage
- One-owner authentication and audit logging
- Text and multipart file capture
- Extraction for text, Markdown, CSV, HTML, JSON, PDF, and DOCX
- Deterministic local embeddings with hybrid lexical-semantic related-context ranking
- OpenAI-compatible cloud and Hermes model adapters for typed classification
- Capture retry, project linking, reference, merge, and archive review actions
- Searchable project registry and project workspaces
- Versioned execution packs with generation, regeneration, and approval
- Approval-traceable, dependency-aware task graphs with cycle rejection
- Ranked cross-project implementation queue with guarded task transitions
- Tests-first release gates and generated API contracts with drift protection

Agent execution, approval-center policies, artifacts, and external connector writes remain intentionally deferred.

## Engineering method

All behavior changes follow:

`Frame -> Red -> Green -> Refactor -> Observe -> Adjust`

See [Test-Driven Development and Loop Engineering](docs/23_TDD_AND_LOOP_ENGINEERING.md).

## Model routing

`RAOS_MODEL_PROVIDER` supports:

- `rules`: deterministic offline baseline and default
- `hermes`: local OpenAI-compatible endpoint
- `cloud`: hosted OpenAI-compatible endpoint; requires `RAOS_MODEL_API_KEY`

The current embedding baseline is a deterministic local hash projection stored in a pgvector-compatible column. It keeps development reproducible and offline, but it is not presented as a production semantic embedding model.

## Run with Docker

1. Copy `.env.example` to `.env`.
2. Replace the owner password and JWT secret.
3. Choose the model provider settings, or keep `RAOS_MODEL_PROVIDER=rules`.
4. Run `docker compose up --build`.
5. Open `http://localhost:3000`.
6. Sign in with `RAOS_OWNER_EMAIL` and `RAOS_OWNER_PASSWORD`.

API documentation is available at `http://localhost:8000/docs`.

## Run without Docker

PostgreSQL, Redis, and S3-compatible storage must be available. Update `.env` to use host addresses, then:

```bash
npm install
cd apps/api
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd apps/api
. .venv/bin/activate
python -m app.worker
```

Then run the web app:

```bash
npm run dev:web
```

## Release gate

```bash
make check
```

Individual commands:

```bash
make api-test
make api-lint
make migration-check
make web-test
make web-lint
make web-build
make contracts
```

## Security note

The owner-password bootstrap is for the private MVP only. Production rollout must replace it with passwordless login or an identity provider, move secrets into a managed secret store, terminate TLS at the edge, and set `COOKIE_SECURE=true`.

## Documentation

Start with the [Documentation Index](docs/00_INDEX.md), [Implementation Status](docs/21_IMPLEMENTATION_STATUS.md), and [Phase 4 Build Log](docs/26_PHASE4_BUILD_LOG.md). Generated OpenAPI and JSON Schemas are stored under `docs/api/` and `docs/schemas/`.
