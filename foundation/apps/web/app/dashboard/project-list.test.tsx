import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ProjectList from "./project-list";
import type { Project } from "@/lib/types";

const projects: Project[] = [
  {
    id: "project-1",
    workspace_id: "ws-1",
    title: "Extraction pipeline",
    summary: "Turn uploaded sources into reviewed context.",
    domain: "software",
    status: "active",
    priority: 80,
    next_action: "Finish project workspace",
    blocker: null,
    created_at: "2026-07-13T00:00:00Z",
    updated_at: "2026-07-13T01:00:00Z",
  },
  {
    id: "project-2",
    workspace_id: "ws-1",
    title: "Amazon PPC course",
    summary: "Training system for junior VAs.",
    domain: "training",
    status: "planned",
    priority: 60,
    next_action: null,
    blocker: "Needs curriculum review",
    created_at: "2026-07-13T00:00:00Z",
    updated_at: "2026-07-13T00:30:00Z",
  },
];

describe("ProjectList", () => {
  it("renders project status, next action, and workspace links", () => {
    render(<ProjectList projects={projects} />);

    expect(screen.getByRole("link", { name: "Extraction pipeline" })).toHaveAttribute(
      "href",
      "/dashboard/projects/project-1",
    );
    expect(screen.getByText("Finish project workspace")).toBeVisible();
    expect(screen.getByText("Needs curriculum review")).toBeVisible();
    expect(screen.getByText("80 priority")).toBeVisible();
  });
});
