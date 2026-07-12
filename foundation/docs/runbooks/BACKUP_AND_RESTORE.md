# Backup and Restore Runbook

## Backup scope

- PostgreSQL
- Object storage
- Prompt and agent definitions
- Application configuration excluding raw secrets
- Audit manifests

## Restore test

1. Create an isolated environment.
2. Restore the latest database backup.
3. Restore object storage versions.
4. Verify checksums for sampled artifacts.
5. Run critical end-to-end flows in read-only mode.
6. Record recovery time and defects.

A backup is not trusted until it has been restored successfully.
