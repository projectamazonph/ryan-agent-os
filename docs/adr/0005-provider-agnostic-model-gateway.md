# ADR-0005: Provider-Agnostic Model Gateway

## Status
Accepted

## Context
Ryan wants local Hermes support while retaining access to stronger cloud models. Model capabilities, costs, and privacy policies change quickly.

## Decision
All model calls pass through an internal gateway with shared request, response, usage, and policy contracts.

## Consequences

- Provider switching and fallback become possible
- Evaluation can compare models consistently
- Provider-specific advanced features require adapter extensions
