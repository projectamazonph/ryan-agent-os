import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AgentLauncher from "./agent-launcher";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh }) }));

const task = {
  id: "task-1",
  task_graph_id: "graph-1",
  project_id: "project-1",
  project_title: "Agent execution foundation",
  key: "ws-1-step-1",
  title: "Write failing tests",
  description: "Create acceptance tests first",
  verification: "Tests fail for the intended reason",
  status: "planned",
  impact: 90,
  urgency: 85,
  confidence: 87,
  effort: 36,
  rank_score: 83,
  position: 1,
  dependency_keys: [],
  blocked_by: [],
  is_ready: true,
  created_at: "2026-07-13T00:06:00Z",
  updated_at: "2026-07-13T00:06:00Z",
  completed_at: null,
};

const agents = [
  { key: "developer", name: "Developer Agent", version: 1 },
  { key: "documentation", name: "Documentation Agent", version: 1 },
];

describe("AgentLauncher", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("launches the selected versioned agent for a ready task", async () => {
    const user = userEvent.setup();
    render(<AgentLauncher task={task} agents={agents} />);

    await user.selectOptions(screen.getByLabelText("Agent"), "documentation");
    await user.click(screen.getByRole("button", { name: "Create agent run" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/tasks/task-1/agent-runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_key: "documentation" }),
    });
  });
});
