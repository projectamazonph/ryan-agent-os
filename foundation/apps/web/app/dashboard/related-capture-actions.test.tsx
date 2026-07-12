import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import RelatedCaptureActions from "./related-capture-actions";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

describe("RelatedCaptureActions", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("creates an explicit reference relation", async () => {
    const user = userEvent.setup();
    render(<RelatedCaptureActions captureId="cap-1" targetCaptureId="cap-2" />);

    await user.click(screen.getByRole("button", { name: "Reference" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/captures/cap-1/relations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_capture_id: "cap-2", action: "reference" }),
    });
  });

  it("merges a duplicate capture into the selected target", async () => {
    const user = userEvent.setup();
    render(<RelatedCaptureActions captureId="cap-1" targetCaptureId="cap-2" />);

    await user.click(screen.getByRole("button", { name: "Merge into this" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/captures/cap-1/relations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_capture_id: "cap-2", action: "merge" }),
    });
    expect(refresh).toHaveBeenCalledOnce();
  });
});
