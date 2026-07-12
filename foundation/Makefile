SHELL := /bin/sh

.PHONY: setup up down logs api-test api-lint web-build web-lint web-test check migrate migration-check worker contracts

setup:
	cp .env.example .env
	npm install
	python3 -m venv apps/api/.venv
	apps/api/.venv/bin/pip install -r apps/api/requirements-dev.txt

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

migrate:
	cd apps/api && .venv/bin/alembic upgrade head

worker:
	cd apps/api && .venv/bin/python -m app.worker

api-test:
	cd apps/api && .venv/bin/pytest

api-lint:
	cd apps/api && .venv/bin/ruff check . && .venv/bin/mypy app

contracts:
	apps/api/.venv/bin/python scripts/generate_contracts.py

web-build:
	CI=1 NEXT_TELEMETRY_DISABLED=1 npm run build:web

web-test:
	npm run test:web

web-lint:
	npm run lint:web && npm run typecheck:web

migration-check:
	rm -f /tmp/raos-migration-check.db
	cd apps/api && RAOS_DATABASE_URL=sqlite+aiosqlite:////tmp/raos-migration-check.db .venv/bin/alembic upgrade head
	cd apps/api && RAOS_DATABASE_URL=sqlite+aiosqlite:////tmp/raos-migration-check.db .venv/bin/alembic downgrade base
	cd apps/api && RAOS_DATABASE_URL=sqlite+aiosqlite:////tmp/raos-migration-check.db .venv/bin/alembic upgrade head

check: api-lint api-test migration-check web-lint web-test web-build
