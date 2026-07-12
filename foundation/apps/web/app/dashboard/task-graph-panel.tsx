"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { ExecutionPack, TaskGraph } from "@/lib/types";

export default function TaskGraphPanel({
  projectId,
  executionPack,
  graph,
}: {
  projectId: string;
  executionPack: ExecutionPack | null;
  graph: TaskGraph | null;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function createGraph() {
    setBusy(true);
    setMessage("");
    const response = await fetch(`/api/projects/${projectId}/task-graph`, { method: "POST" });
    setBusy(false);
    setMessage(response.ok ? "Task graph created." : "Task graph creation failed.");
    if (response.ok) router.refresh();
  }

  if (!graph) {
    const approved = executionPack?.status === "approved" && executionPack.current_version.approved_at;
    return (
      <section className="card task-graph-card">
        <div className="card-header">
          <div>
            <div className="eyebrow">Task graph</div>
            <h2 className="card-title">Convert the approved plan into executable work</h2>
            <p className="card-copy">
              Tasks inherit approval traceability, dependency rules, ranking signals, and verification evidence.
            </p>
          </div>
        </div>
        <div className="card-body task-graph-empty">
          <button className="button" type="button" disabled={!approved || busy} onClick={createGraph}>
            {busy ? "Creating..." : "Create task graph"}
          </button>
          {!approved ? <span className="message">Approve the current execution pack first.</span> : null}
          <span className="message">{message}</span>
        </div>
      </section>
    );
  }

  return (
    <section className="card task-graph-card">
      <div className="card-header task-graph-header">
        <div>
          <div className="eyebrow">Task graph</div>
          <h2 className="card-title">Approved execution pack v{graph.source_execution_pack_version_number}</h2>
          <p className="card-copy">
            Approved {new Date(graph.source_execution_pack_approved_at).toLocaleString()} · {graph.tasks.length} tasks
          </p>
        </div>
        <span className="badge">{graph.status}</span>
      </div>
      <div className="card-body task-graph-list">
        {graph.tasks.map((task) => (
          <article className="task-graph-item" key={task.id}>
            <div className="task-graph-item-top">
              <div>
                <span className="task-key">{task.key}</span>
                <h3>{task.title}</h3>
              </div>
              <div className="task-signal-row">
                <span className={task.is_ready ? "ready-pill" : "blocked-pill"}>
                  {task.is_ready ? "Ready" : "Blocked"}
                </span>
                <span className="score-pill">Score {task.rank_score}</span>
              </div>
            </div>
            <p>{task.description}</p>
            <div className="task-verification"><strong>Verify:</strong> {task.verification}</div>
            {task.blocked_by.length > 0 ? (
              <div className="task-dependencies">Blocked by {task.blocked_by.join(", ")}</div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
