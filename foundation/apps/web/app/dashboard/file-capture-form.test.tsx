import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import FileCaptureForm from "./file-capture-form";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

describe("FileCaptureForm", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("submits the selected file as multipart form data", async () => {
    const user = userEvent.setup();
    render(<FileCaptureForm />);
    const file = new File(["# Brief\nBuild extraction."], "brief.md", {
      type: "text/markdown",
    });

    await user.type(screen.getByLabelText("File title"), "Extraction brief");
    await user.upload(screen.getByLabelText("Source file"), file);
    fireEvent.submit(screen.getByRole("button", { name: "Upload source" }).closest("form")!);

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    const [url, options] = vi.mocked(fetch).mock.calls[0];
    expect(url).toBe("/api/captures/files");
    expect(options?.method).toBe("POST");
    expect(options?.body).toBeInstanceOf(FormData);
    const body = options?.body as FormData;
    expect(body.get("title")).toBe("Extraction brief");
    expect((body.get("file") as File).name).toBe("brief.md");
    expect(await screen.findByText("Source stored and queued for extraction.")).toBeVisible();
    expect(refresh).toHaveBeenCalledOnce();
  });
});
