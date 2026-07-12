# Foundation Build Log

## Build

- Release: `0.1.0-foundation`
- Date: 2026-07-13
- Scope: Phase 1 plus a thin Capture Inbox vertical slice

## Work completed

1. Preserved the documentation baseline as the source of truth.
2. Created the web, API, worker, database, storage, CI, and local orchestration structure.
3. Implemented one-owner authentication and a default personal workspace.
4. Added UUIDv7 identifiers, structured audit records, request IDs, and JSON logs.
5. Added capture creation, exact duplicate detection, capture listing, and worker processing states.
6. Built the responsive login and Capture Inbox interface.
7. Added deterministic pre-AI classification so the worker path can be exercised before the model gateway exists.
8. Added generated OpenAPI and JSON Schema contracts.

## Decisions made

- The first queue uses a small Redis list abstraction instead of Celery or Dramatiq. It is intentionally replaceable and is not the future agent orchestration engine.
- The private MVP uses owner credentials from environment-managed secrets and short-lived JWTs. Production identity remains a separate decision.
- The web application uses a server-side proxy and an HTTP-only cookie so the browser does not store the API token in local storage.
- Original captures are checksum-addressed and duplicate submissions return the existing record.

## Problems found and corrected

- Added the missing email-validation dependency required by Pydantic.
- Corrected summary truncation so its output never exceeds the configured maximum.
- Replaced the legacy ESLint compatibility wrapper with the Next.js flat configuration.
- Pinned ESLint and TypeScript to versions compatible with the current Next.js toolchain.
- Upgraded the initially scaffolded Next.js version after the package manager reported a critical security advisory.
- Overrode the vulnerable transitive PostCSS version and confirmed a clean production dependency audit.
- Reworked CORS environment parsing so a normal comma-separated environment value works reliably.
- Added an OpenAPI-visible HTTP bearer security scheme.

## Verification result

All implemented checks pass. Docker execution was not tested in this build environment because Docker is unavailable there; the Compose definition is included for local validation on a Docker-capable machine.
