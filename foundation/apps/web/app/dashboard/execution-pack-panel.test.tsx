import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ExecutionPackPanel from "./execution-pack-panel";

const refresh = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ refresh }) }));

const pack = {
  id: "pack-1",
  project_id: "project-1",
  status: "draft",
  current_version_number: 1,
  current_version: {
    id: "version-1",
    version_number: 1,
    change_summary: "Initial plan",
    created_at: "2026-07-13T00:00:00Z",
    approved_at: null,
    content: {
      objective: "Ship the implementation queue.",
      problem_statement: "Ideas are not consistently converted into work.",
      success_criteria: ["Tasks are ranked", "Dependencies are visible"],
      in_scope: ["Task graph", "Ranking"],
      out_of_scope: ["External connector writes"],
      assumptions: ["One-owner workspace"],
      deliverables: [
        {
          name: "Task graph",
          description: "Versioned dependency-aware task plan.",
          format: "application/json",
          acceptance_criteria: ["No dependency cycles"],
        },
      ],
      workstreams: [
        {
          name: "Queue engine",
          goal: "Rank executable work.",
          steps: ["Define model", "Implement ranking", "Test transitions"],
        },
      ],
      risks: ["Ranking may reward noisy urgency"],
      recommended_agents: ["planner", "qa"],
    },
  },
  versions: [],
};

describe("ExecutionPackPanel", () => {
  beforeEach(() => {
    refresh.mockReset();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  it("renders the current execution plan and approves it", async () => {
    const user = userEvent.setup();
    render(<ExecutionPackPanel projectId="project-1" pack={pack} />);

    expect(screen.getByText("Ship the implementation queue.")).toBeVisible();
    expect(screen.getAllByText("Task graph")[0]).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Approve version 1" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith(
      "/api/projects/project-1/execution-pack/approve",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version_number: 1 }),
      },
    );
  });

  it("generates the first execution pack when none exists", async () => {
    const user = userEvent.setup();
    render(<ExecutionPackPanel projectId="project-2" pack={null} />);

    await user.click(screen.getByRole("button", { name: "Generate execution pack" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledOnce());
    expect(fetch).toHaveBeenCalledWith("/api/projects/project-2/execution-pack", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ change_summary: "Generated from current project context" }),
    });
  });
});
