# ADR-0004: PostgreSQL as the System of Record

## Status
Accepted

## Context
The product requires transactional project state, task dependencies, approvals, provenance, auditability, full-text search, and semantic retrieval.

## Decision
Use PostgreSQL as the authoritative structured data store and pgvector for embeddings. Store large binaries in object storage.

## Consequences

- Strong relational integrity and transaction support
- One operational database for the MVP
- Vector search remains close to permission and metadata filters
- Object lifecycle must be coordinated with database records
