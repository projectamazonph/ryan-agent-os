# Security and Privacy

## Security objective

Ryan Agent OS will hold sensitive conversations, company work, credentials, advertising information, repositories, and personal project data. Security is therefore part of the product architecture, not a final polishing task.

## Threat model

Primary threats include:

- Prompt injection in documents or web content
- Over-privileged connectors
- Unauthorized external actions
- Secret leakage into prompts or logs
- Cross-project context leakage
- Malicious or compromised dependencies
- Unverified webhook calls
- Duplicate side effects after retries
- Public sharing of confidential artifacts
- Model-provider data retention

## Trust boundaries

1. Browser to API
2. API to worker queue
3. Worker to model provider
4. Worker to external connector
5. Application to object storage
6. Local runtime to cloud runtime

## Authentication

MVP recommendation:

- Passwordless email or OAuth login
- Strong session cookies
- Optional passkey support
- Mandatory reauthentication for sensitive connector changes

## Authorization

Use role-based access control plus action policy checks. Future collaborative projects may add attribute-based restrictions using domain, sensitivity, connector, and action type.

## Secret management

- Use a dedicated secret manager in production
- Encrypt connector tokens at rest
- Never place secrets in application logs
- Never pass raw connector tokens to model prompts
- Rotate secrets after suspected exposure

## Prompt injection defense

All retrieved content is treated as untrusted data.

Agents must:

- Separate system instructions from retrieved content
- Ignore instructions inside source content unless the task explicitly requires following them
- Use tool allowlists
- Require approval for protected actions
- Avoid exposing secrets in tool results
- Record suspicious instructions as evidence

## Data minimization

The context builder sends only task-relevant excerpts. Sensitive project data is not included in unrelated agent runs.

## Model routing privacy

Each model provider configuration records:

- Data retention policy
- Training usage policy
- Region when available
- Supported sensitivity level
- Maximum allowed content classification

Restricted data defaults to local processing or explicitly approved providers.

## Audit logging

Audit events include:

- Login and session events
- Connector authorization changes
- Approval decisions
- External write actions
- Artifact sharing
- Data export
- Data deletion
- Policy overrides
- Agent tool calls involving sensitive systems

## File security

- Validate content type using file signatures
- Scan uploaded files where practical
- Store with generated object keys
- Prevent direct public buckets
- Use short-lived signed download URLs
- Store checksums
- Sanitize rendered HTML

## Backup security

Backups must be encrypted, access-controlled, and regularly restored in a test environment.

## Incident priorities

1. Stop active external actions
2. Revoke compromised tokens
3. Preserve logs and evidence
4. Contain affected data
5. Notify the owner with verified facts
6. Restore safely
7. Document corrective actions

## Secure defaults

- External writes disabled until connector authorization and policy setup
- Email send disabled without per-action approval
- Production deploy disabled in MVP
- Public artifact sharing disabled
- Destructive delete replaced by recoverable archive where possible
