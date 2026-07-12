# ADR-0004: Foundation implementation choices

- Status: Accepted
- Date: 2026-07-13

## Context

The approved architecture calls for a modular monolith with a Next.js web app, FastAPI API, PostgreSQL, Redis, object storage, workers, authentication, and audit events.

## Decision

1. Use npm workspaces for the initial monorepo because only one JavaScript package exists today.
2. Use SQLAlchemy async sessions and Alembic migrations.
3. Use a minimal Redis list queue before adopting a larger workflow engine. The queue interface is isolated so it can be replaced later.
4. Use a one-owner JWT bootstrap for local MVP authentication.
5. Use S3-compatible storage through a small adapter, with MinIO locally.
6. Implement UUIDv7 in application code because Python 3.13 does not expose it in the standard library.
7. Add a thin Capture Inbox slice during foundation work to prove the platform end to end.

## Consequences

- The system can run locally with one command once Docker is installed.
- Authentication is functional but not the final production identity design.
- The worker is intentionally simple and must not be mistaken for the future agent orchestration engine.
- Core interfaces remain replaceable without changing domain routes.
