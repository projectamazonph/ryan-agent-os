"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Project } from "@/lib/types";

type BusyAction = "project" | "archive" | "retry" | "link" | null;

export default function CaptureReviewActions({
  captureId,
  reviewStatus,
  sourceStatus = null,
  projects = [],
}: {
  captureId: string;
  reviewStatus: string;
  sourceStatus?: string | null;
  projects?: Project[];
}) {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState<BusyAction>(null);
  const [projectId, setProjectId] = useState(projects[0]?.id ?? "");

  async function runAction(
    action: Exclude<BusyAction, null>,
    request: () => Promise<Response>,
    successMessage: string,
  ) {
    setBusy(action);
    setMessage("");
    setError(false);
    try {
      const response = await request();
      if (!response.ok) {
        setError(true);
        setMessage(`${successMessage.replace(/\.$/, "")} failed.`);
        return;
      }
      setMessage(successMessage);
      router.refresh();
    } finally {
      setBusy(null);
    }
  }

  async function createProject() {
    await runAction(
      "project",
      () =>
        fetch(`/api/captures/${captureId}/projects`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "planned" }),
        }),
      "Project created and linked.",
    );
  }

  async function archiveCapture() {
    await runAction(
      "archive",
      () => fetch(`/api/captures/${captureId}/archive`, { method: "POST" }),
      "Capture archived.",
    );
  }

  async function retryExtraction() {
    await runAction(
      "retry",
      () => fetch(`/api/captures/${captureId}/retry`, { method: "POST" }),
      "Extraction queued for retry.",
    );
  }

  async function linkProject() {
    if (!projectId) return;
    await runAction(
      "link",
      () => fetch(`/api/projects/${projectId}/captures/${captureId}`, { method: "POST" }),
      "Capture linked to project.",
    );
  }

  return (
    <div className="review-actions">
      <button
        className="button"
        type="button"
        disabled={busy !== null || reviewStatus === "linked"}
        onClick={createProject}
      >
        {busy === "project" ? "Creating..." : reviewStatus === "linked" ? "Project linked" : "Create project"}
      </button>
      {projects.length > 0 ? (
        <div className="inline-action-group">
          <label className="sr-only" htmlFor={`project-${captureId}`}>Existing project</label>
          <select
            id={`project-${captureId}`}
            aria-label="Existing project"
            className="action-select"
            value={projectId}
            onChange={(event) => setProjectId(event.target.value)}
            disabled={busy !== null}
          >
            {projects.map((project) => (
              <option value={project.id} key={project.id}>{project.title}</option>
            ))}
          </select>
          <button
            className="button secondary-button"
            type="button"
            disabled={busy !== null || !projectId}
            onClick={linkProject}
          >
            {busy === "link" ? "Linking..." : "Link project"}
          </button>
        </div>
      ) : null}
      {sourceStatus === "failed" ? (
        <button
          className="button secondary-button"
          type="button"
          disabled={busy !== null}
          onClick={retryExtraction}
        >
          {busy === "retry" ? "Queueing..." : "Retry extraction"}
        </button>
      ) : null}
      <button
        className="button secondary-button"
        type="button"
        disabled={busy !== null || reviewStatus === "archived"}
        onClick={archiveCapture}
      >
        {busy === "archive" ? "Archiving..." : reviewStatus === "archived" ? "Archived" : "Archive capture"}
      </button>
      <span className={`message action-message ${error ? "error" : ""}`}>{message}</span>
    </div>
  );
}
