"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Task } from "@/lib/types";

export default function ImplementationQueue({ tasks }: { tasks: Task[] }) {
  const router = useRouter();
  const [busyTask, setBusyTask] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  async function changeStatus(taskId: string, status: "in_progress" | "done" | "blocked") {
    setBusyTask(taskId);
    setMessage("");
    const response = await fetch(`/api/tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    setBusyTask(null);
    setMessage(response.ok ? "Queue updated." : "Task update failed.");
    if (response.ok) router.refresh();
  }

  if (tasks.length === 0) {
    return <div className="empty">No executable tasks yet. Approve a pack and create its task graph.</div>;
  }

  return (
    <div className="implementation-queue">
      {tasks.map((task, index) => (
        <article className={`queue-task ${task.is_ready ? "queue-task-ready" : ""}`} key={task.id}>
          <div className="queue-rank">{index + 1}</div>
          <div className="queue-task-content">
            <div className="queue-task-top">
              <div>
                <Link className="queue-project" href={`/dashboard/projects/${task.project_id}`}>{task.project_title}</Link>
                <h2>{task.title}</h2>
              </div>
              <span className="score-pill">Score {task.rank_score}</span>
            </div>
            <p>{task.description}</p>
            <div className="queue-signals">
              <span>Impact {task.impact}</span>
              <span>Urgency {task.urgency}</span>
              <span>Confidence {task.confidence}</span>
              <span>Effort {task.effort}</span>
            </div>
            <div className="task-verification"><strong>Verification:</strong> {task.verification}</div>
            {task.blocked_by.length > 0 ? (
              <div className="task-dependencies">Blocked by {task.blocked_by.join(", ")}</div>
            ) : null}
            <div className="queue-actions">
              {task.status === "planned" && task.is_ready ? (
                <button className="button" type="button" disabled={busyTask !== null} onClick={() => changeStatus(task.id, "in_progress")}>Start task</button>
              ) : null}
              {task.status === "in_progress" ? (
                <button className="button" type="button" disabled={busyTask !== null} onClick={() => changeStatus(task.id, "done")}>Complete task</button>
              ) : null}
              {task.status === "planned" && task.is_ready ? (
                <button className="button secondary-button" type="button" disabled={busyTask !== null} onClick={() => changeStatus(task.id, "blocked")}>Mark blocked</button>
              ) : null}
              <span className="badge">{task.status}</span>
            </div>
          </div>
        </article>
      ))}
      <span className="message">{message}</span>
    </div>
  );
}
