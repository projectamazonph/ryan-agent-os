import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CaptureReviewActions from "./capture-review-actions";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

describe("CaptureReviewActions", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("creates a planned project from an unreviewed capture", async () => {
    const user = userEvent.setup();
    render(<CaptureReviewActions captureId="cap-1" reviewStatus="unreviewed" />);

    await user.click(screen.getByRole("button", { name: "Create project" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/captures/cap-1/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "planned" }),
    });
    expect(await screen.findByText("Project created and linked.")).toBeVisible();
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("archives a capture from the review queue", async () => {
    const user = userEvent.setup();
    render(<CaptureReviewActions captureId="cap-2" reviewStatus="unreviewed" />);

    await user.click(screen.getByRole("button", { name: "Archive capture" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/captures/cap-2/archive", { method: "POST" });
    expect(await screen.findByText("Capture archived.")).toBeVisible();
  });

  it("retries a failed file extraction", async () => {
    const user = userEvent.setup();
    render(
      <CaptureReviewActions
        captureId="cap-3"
        reviewStatus="unreviewed"
        sourceStatus="failed"
      />,
    );

    await user.click(screen.getByRole("button", { name: "Retry extraction" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/captures/cap-3/retry", { method: "POST" });
    expect(await screen.findByText("Extraction queued for retry.")).toBeVisible();
  });

  it("links a capture to an existing project", async () => {
    const user = userEvent.setup();
    render(
      <CaptureReviewActions
        captureId="cap-4"
        reviewStatus="unreviewed"
        projects={[
          {
            id: "project-9",
            workspace_id: "ws-1",
            title: "Agent runtime",
            summary: null,
            domain: "software",
            status: "active",
            priority: 70,
            next_action: null,
            blocker: null,
            created_at: "2026-07-13T00:00:00Z",
            updated_at: "2026-07-13T00:00:00Z",
          },
        ]}
      />,
    );

    await user.selectOptions(screen.getByLabelText("Existing project"), "project-9");
    await user.click(screen.getByRole("button", { name: "Link project" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith(
      "/api/projects/project-9/captures/cap-4",
      { method: "POST" },
    );
    expect(await screen.findByText("Capture linked to project.")).toBeVisible();
  });
});
