# Local Development Runbook

## Prerequisites

- Docker and Docker Compose
- Node.js current LTS
- Python 3.12
- Git

## Expected setup flow

1. Clone the repository.
2. Copy the checked-in example environment file to a local environment file.
3. Add local-only credentials.
4. Start PostgreSQL, Redis, and MinIO.
5. Run database migrations.
6. Start API and worker services.
7. Start the web application.
8. Run health checks.
9. Run the test suite.

## Local data

Use synthetic development data. Do not import confidential GoodWit or client data into an unencrypted local environment.

## Reset

The repository must provide a documented command that resets local containers and volumes after an explicit confirmation.
