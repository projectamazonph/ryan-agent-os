import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ImplementationQueue from "./implementation-queue";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh }) }));

const readyTask = {
  id: "task-1",
  task_graph_id: "graph-1",
  project_id: "project-1",
  project_title: "Queue engine",
  key: "ws-1-step-1",
  title: "Write failing tests",
  description: "Create acceptance tests first",
  verification: "The tests fail for the intended reason",
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

const blockedTask = {
  ...readyTask,
  id: "task-2",
  key: "ws-1-step-2",
  title: "Implement queue",
  position: 2,
  dependency_keys: ["ws-1-step-1"],
  blocked_by: ["ws-1-step-1"],
  is_ready: false,
  rank_score: 78,
};

describe("ImplementationQueue", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("starts the highest-ranked ready task", async () => {
    const user = userEvent.setup();
    render(<ImplementationQueue tasks={[readyTask, blockedTask]} />);

    await user.click(screen.getByRole("button", { name: "Start task" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/tasks/task-1", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "in_progress" }),
    });
    expect(screen.getByText("Blocked by ws-1-step-1")).toBeVisible();
  });
});
