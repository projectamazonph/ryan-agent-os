# Artifact System

## Goal

The artifact system produces, versions, validates, stores, and delivers the concrete outputs of projects.

## Supported categories

- Documents: Markdown, DOCX, PDF
- Presentations: PPTX, Google Slides
- Spreadsheets: XLSX, CSV, Google Sheets
- Code: files, patches, repositories, pull requests
- Visuals: PNG, JPEG, SVG
- Structured exports: JSON, ZIP
- Evidence: screenshots, logs, test reports

## Artifact record

Each artifact includes:

- Name
- Type
- Project
- Deliverable
- Current version
- Status
- Sensitivity
- Storage location
- Destination
- Producer
- Source references
- Checksum
- Validation status

## Versioning

Artifact versions are immutable. Editing creates a new version with:

- Parent version
- Change summary
- Producer
- Source changes
- Validation results
- Creation timestamp

## Statuses

`draft, generated, validating, needs_review, approved, delivered, superseded, rejected`

## Validation

### Common checks

- File exists and opens
- Expected file type matches signature
- Size is non-zero
- Checksum generated
- Required sections present
- No unresolved placeholders
- No broken internal links when applicable

### Documents

- Heading hierarchy
- Table integrity
- Page rendering
- Font availability
- Metadata correctness

### Presentations

- No overflowing text
- No blank required slides
- Images render
- Notes and speaker content preserved when required

### Spreadsheets

- Formulas calculate
- Named ranges are valid
- No broken references
- Numeric formats are correct
- Required tabs exist

### Code

- Formatting
- Type checking
- Unit tests
- Integration tests where relevant
- Dependency audit
- Build success

## Delivery

Delivery is a separate action from generation. A file can be generated but not yet approved for upload, sharing, publishing, or sending.

## Naming convention

```text
<project-slug>_<artifact-purpose>_v<major.minor>_<YYYY-MM-DD>.<ext>
```

Example:

```text
ryan-agent-os_product-requirements_v1.0_2026-07-13.pdf
```

## Project export package

A complete project export contains:

```text
manifest.json
README.md
sources/
planning/
tasks/
decisions/
artifacts/
evidence/
audit-summary.json
```
