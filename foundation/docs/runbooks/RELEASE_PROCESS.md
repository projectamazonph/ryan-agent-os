# Release Process Runbook

## Before release

1. Confirm scope and deferred work.
2. Confirm each behavior has tests-first evidence.
3. Review migrations and rollback safety.
4. Run the full local gate:

   ```bash
   make check
   ```

5. Run dependency integrity and vulnerability checks.
6. Regenerate OpenAPI and JSON Schemas.
7. Update implementation status, build log, documentation index, and changelog.
8. Create rollback notes.
9. Deploy and test staging when a staging environment exists.

## Production release

- Take or verify backup.
- Apply migrations.
- Deploy API and workers.
- Deploy web application.
- Run health and smoke checks.
- Verify one capture-to-project flow.
- Monitor errors, queue state, storage access, and audit events.

## Rollback

Rollback application images first when safe. Use migration rollback only when the migration supports it and no newer data would be lost.

## Release evidence

Record:

- Commit or package identifier
- Checksums
- Test counts
- Migration result
- Build result
- Dependency audit result
- Smoke result
- Known limitations
- Rollback procedure
