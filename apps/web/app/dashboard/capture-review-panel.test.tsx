import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import CaptureReviewPanel from "./capture-review-panel";
import type { CaptureReview } from "@/lib/types";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

const review: CaptureReview = {
  capture: {
    id: "cap-1",
    workspace_id: "ws-1",
    type: "file",
    title: "Extraction brief",
    content: "Build the extraction pipeline.",
    domain_hint: "software",
    sensitivity: "confidential",
    status: "ready",
    review_status: "linked",
    summary: "A brief for the extraction pipeline.",
    classification: {
      domain: "software",
      intent: "build",
      confidence: 0.92,
      evidence: ["extraction", "pipeline"],
      engine: "rules-v1",
      needs_review: false,
    },
    checksum_sha256: "a".repeat(64),
    created_at: "2026-07-13T00:00:00Z",
    updated_at: "2026-07-13T00:00:00Z",
  },
  source: {
    id: "src-1",
    workspace_id: "ws-1",
    capture_id: "cap-1",
    storage_key: "sources/brief.md",
    original_filename: "brief.md",
    content_type: "text/markdown",
    size_bytes: 128,
    checksum_sha256: "a".repeat(64),
    extraction_status: "ready",
    extracted_text: "Build the extraction pipeline.",
    extraction_error: null,
    metadata_json: { immutable: true },
    created_at: "2026-07-13T00:00:00Z",
    extracted_at: "2026-07-13T00:01:00Z",
    extraction_attempts: 1,
    last_attempt_at: "2026-07-13T00:00:30Z",
  },
  related: [
    {
      capture: {
        id: "cap-2",
        workspace_id: "ws-1",
        type: "note",
        title: "Capture ingestion",
        content: "Implement source ingestion.",
        domain_hint: "software",
        sensitivity: "internal",
        status: "received",
        review_status: "unreviewed",
        summary: null,
        classification: null,
        checksum_sha256: "b".repeat(64),
        created_at: "2026-07-13T00:00:00Z",
        updated_at: "2026-07-13T00:00:00Z",
      },
      score: 0.61,
      reasons: ["shared_terms", "same_domain"],
    },
  ],
  projects: [
    {
      id: "project-1",
      workspace_id: "ws-1",
      title: "Extraction pipeline",
      summary: "Build Phase 2 extraction.",
      domain: "software",
      status: "planned",
      priority: 50,
      next_action: "Finish review UI",
      blocker: null,
      created_at: "2026-07-13T00:00:00Z",
      updated_at: "2026-07-13T00:00:00Z",
    },
  ],
};

describe("CaptureReviewPanel", () => {
  it("shows source provenance, classification, and related context", () => {
    render(<CaptureReviewPanel review={review} />);

    expect(screen.getByRole("heading", { name: "Extraction brief" })).toBeVisible();
    expect(screen.getByText("brief.md")).toBeVisible();
    expect(screen.getByText("software")).toBeVisible();
    expect(screen.getByText("92% confidence")).toBeVisible();
    expect(screen.getByRole("link", { name: "Capture ingestion" })).toHaveAttribute(
      "href",
      "/dashboard/captures/cap-2",
    );
  });
});
