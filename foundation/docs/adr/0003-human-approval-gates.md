# ADR-0003: Human Approval for External Side Effects

## Status
Accepted

## Context
Ryan Agent OS can connect to systems where actions may communicate externally, alter production work, spend money, or delete information.

## Decision
Protected external actions require explicit human approval for a specific action preview and scope.

## Consequences

- Agents remain useful without receiving unrestricted authority.
- Approval records become part of audit evidence.
- Some workflows require an additional interaction before completion.
