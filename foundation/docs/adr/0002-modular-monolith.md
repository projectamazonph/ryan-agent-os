# ADR-0002: Modular Monolith for the MVP

## Status
Accepted

## Context
The system has several domains but a single initial user and modest expected volume. Microservices would add deployment, tracing, and data-consistency costs before scale requires them.

## Decision
Use a modular monolith for the API with background workers and explicit module boundaries.

## Consequences

- Faster local development and deployment
- Easier transactions and migrations
- Modules must avoid direct cross-domain table manipulation
- Services can be extracted later when measured pressure justifies it
