import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AgentRunConsole from "./agent-run-console";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh }) }));

const baseRun = {
  id: "run-1",
  project_id: "project-1",
  project_title: "Agent execution foundation",
  task_id: "task-1",
  task_title: "Write failing tests",
  agent_key: "developer",
  agent_name: "Developer Agent",
  agent_version: 1,
  state: "queued",
  attempt_number: 1,
  retry_of_run_id: null,
  model_provider: "rules",
  model_name: "rules-v1",
  tool_allowlist: ["filesystem.read"],
  output: null,
  error: null,
  usage: { prompt_tokens: 0, completion_tokens: 0, estimated_cost_cents: 0 },
  created_at: "2026-07-13T00:00:00Z",
  started_at: null,
  finished_at: null,
  cancelled_at: null,
};

describe("AgentRunConsole", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("executes a queued run from the console", async () => {
    const user = userEvent.setup();
    render(<AgentRunConsole runs={[baseRun]} />);

    await user.click(screen.getByRole("button", { name: "Execute run" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/agent-runs/run-1/execute", { method: "POST" });
    expect(screen.getByText("Developer Agent v1")).toBeVisible();
  });

  it("offers QA verification only when a run needs review", () => {
    render(<AgentRunConsole runs={[{ ...baseRun, state: "needs_review", output: { summary: "Done", evidence: ["Tests pass"] } }]} />);

    expect(screen.getByRole("button", { name: "Run QA verification" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Execute run" })).not.toBeInTheDocument();
  });
});
