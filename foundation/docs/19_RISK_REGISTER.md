# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Trigger |
|---|---|---:|---:|---|---|
| R-01 | Scope expands into a general autonomous platform before the core loop works | High | High | Enforce MVP acceptance criteria and phase gates | New module proposed without supporting capture-to-delivery loop |
| R-02 | Agents generate convincing plans but do not complete work | High | High | Require task evidence and QA verification | Completion claims lack artifacts or checks |
| R-03 | Context retrieval introduces stale or conflicting instructions | Medium | High | Scope memories, version decisions, expose retrieval sources | User corrects a supposedly known rule |
| R-04 | External actions are duplicated after retries | Medium | High | Idempotency keys, connector event records, transaction boundaries | Duplicate issues, uploads, or messages |
| R-05 | Sensitive data is sent to an unsuitable model provider | Medium | Critical | Sensitivity labels and model-routing policies | Restricted capture selected for cloud processing |
| R-06 | Documentation and implementation drift | High | Medium | Docs checks in pull requests, ADR discipline, release notes | API or behavior differs from docs |
| R-07 | Local model quality is insufficient for planning | Medium | Medium | Evaluation-driven routing and cloud fallback | Repeated schema repair or high rework |
| R-08 | Too many notifications create avoidance | Medium | Medium | Action-centered briefs, configurable thresholds | Briefs are dismissed without action |
| R-09 | Project ranking feels arbitrary | Medium | Medium | Explain score components and allow overrides | Ryan repeatedly reorders items manually |
| R-10 | Artifact generation becomes brittle across formats | Medium | High | Separate renderers, validation, golden files | Files fail to open or lose formatting |
| R-11 | Connector permissions are broader than necessary | Medium | High | Least privilege and per-action approval | Connector requests administrative scopes |
| R-12 | Single-user assumptions block future collaboration | Low | Medium | Keep workspace, actor, role, and ownership fields from the start | Team access requested |
| R-13 | Cost grows invisibly | Medium | High | Per-run budgets, daily caps, cost dashboard | Daily spend exceeds threshold |
| R-14 | Search returns semantically similar but irrelevant work | Medium | Medium | Hybrid search, type filters, recency, user feedback | Wrong project linkage accepted by default |
| R-15 | Build becomes dependent on one model vendor | Medium | High | Provider-agnostic gateway and contract tests | Provider outage or pricing change |
