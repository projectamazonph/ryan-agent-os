# Deployment and Operations

## Environments

- Local
- Development
- Staging
- Production

Each environment uses separate databases, storage buckets, secrets, and connector credentials.

## Local stack

Docker Compose services:

- `web`
- `api`
- `worker`
- `postgres`
- `redis`
- `minio`
- `mailpit`
- Optional `hermes`

## Configuration

Configuration follows environment variables validated at startup. The application fails fast if required production settings are missing.

## Database migrations

- Use Alembic
- Run migrations as an explicit release step
- Back up production before destructive migrations
- Include rollback notes
- Do not allow application instances to race migrations at startup

## Release process

1. Update code and documentation.
2. Pass lint, type, unit, integration, and end-to-end tests.
3. Build immutable images.
4. Deploy to staging.
5. Run smoke tests.
6. Review database migration plan.
7. Create release notes.
8. Deploy production.
9. Verify health and critical workflows.
10. Record the release in the build log.

## Health checks

### Liveness
Confirms the process is running.

### Readiness
Confirms database, Redis, storage, and critical configuration are available.

### Worker health
Confirms workers are consuming jobs and not stuck.

### Connector health
Reports provider-specific connection and authorization state.

## Backups

- PostgreSQL daily full backup with point-in-time recovery where available
- Object storage versioning
- Weekly encrypted export of critical configuration and manifests
- Monthly restore test

## Disaster recovery targets

- Recovery point objective: 24 hours for MVP
- Recovery time objective: 4 hours for MVP

## Cost controls

- Per-agent-run budget
- Per-project budget
- Daily model-spend cap
- File-size limits
- Queue concurrency limits
- Provider usage dashboard

## Feature flags

Use feature flags for:

- New agents
- New model providers
- Protected connector actions
- Automatic memory writes
- Experimental ranking algorithms

## Operational ownership

Ryan is the initial product owner and final approver. Automated operations should reduce routine work but never make system ownership ambiguous.
