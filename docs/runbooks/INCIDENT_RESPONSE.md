# Incident Response Runbook

## Severity

- SEV-1: Active data exposure, unauthorized external action, or production loss
- SEV-2: Major workflow unavailable or repeated destructive failure
- SEV-3: Degraded feature with a workaround
- SEV-4: Minor defect

## Immediate actions

1. Stop affected workers or connectors.
2. Revoke exposed credentials.
3. Preserve logs and correlation IDs.
4. Identify affected projects and external systems.
5. Communicate verified facts to the owner.
6. Restore service through the safest path.

## Post-incident

- Write timeline
- Identify root cause
- Add regression tests
- Update policies or documentation
- Record corrective owners and due dates
