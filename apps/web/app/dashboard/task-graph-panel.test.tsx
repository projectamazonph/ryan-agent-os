import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TaskGraphPanel from "./task-graph-panel";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh }) }));

const approvedPack = {
  id: "pack-1",
  project_id: "project-1",
  status: "approved",
  current_version_number: 2,
  current_version: {
    id: "version-2",
    version_number: 2,
    change_summary: "Approved plan",
    created_at: "2026-07-13T00:00:00Z",
    approved_at: "2026-07-13T00:05:00Z",
    content: {
      objective: "Ship the queue",
      problem_statement: "Work needs sequencing",
      success_criteria: ["Queue works"],
      in_scope: ["Task graph"],
      out_of_scope: [],
      assumptions: [],
      deliverables: [{ name: "Queue", description: "Ranked work", format: "json", acceptance_criteria: ["No cycles"] }],
      workstreams: [{ name: "Build", goal: "Create queue", steps: ["Write tests", "Implement queue"] }],
      risks: [],
      recommended_agents: ["implementer"],
    },
  },
  versions: [],
};

const graph = {
  id: "graph-1",
  project_id: "project-1",
  status: "active",
  source_execution_pack_version_id: "version-2",
  source_execution_pack_version_number: 2,
  source_execution_pack_approved_at: "2026-07-13T00:05:00Z",
  created_at: "2026-07-13T00:06:00Z",
  tasks: [
    {
      id: "task-1",
      task_graph_id: "graph-1",
      project_id: "project-1",
      project_title: "Queue engine",
      key: "ws-1-step-1",
      title: "Write tests",
      description: "Create failing tests",
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
    },
  ],
};

describe("TaskGraphPanel", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("creates a task graph only from the approved execution pack", async () => {
    const user = userEvent.setup();
    render(<TaskGraphPanel projectId="project-1" executionPack={approvedPack} graph={null} />);

    await user.click(screen.getByRole("button", { name: "Create task graph" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/projects/project-1/task-graph", { method: "POST" });
  });

  it("shows approval traceability and task readiness", () => {
    render(<TaskGraphPanel projectId="project-1" executionPack={approvedPack} graph={graph} />);

    expect(screen.getByText("Approved execution pack v2")).toBeVisible();
    expect(screen.getByText("Write tests")).toBeVisible();
    expect(screen.getByText("Ready")).toBeVisible();
    expect(screen.getByText("Score 83")).toBeVisible();
  });
});
