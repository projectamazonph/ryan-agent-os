"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { AgentRun } from "@/lib/types";
import AgentRunTrace from "./agent-run-trace";

export default function AgentRunConsole({ runs }: { runs: AgentRun[] }) {
  const router = useRouter();
  const [busyRun, setBusyRun] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  async function action(runId: string, verb: "execute" | "cancel" | "retry" | "verify") {
    setBusyRun(runId);
    setMessage("");
    const options: RequestInit = { method: "POST" };
    if (verb === "cancel") {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify({ reason: "Stopped from the run console" });
    }
    if (verb === "retry") {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify({});
    }
    const response = await fetch(`/api/agent-runs/${runId}/${verb}`, options);
    setBusyRun(null);
    setMessage(response.ok ? "Run updated." : "Run action failed.");
    if (response.ok) router.refresh();
  }

  if (runs.length === 0) {
    return <div className="empty">No agent runs yet. Launch one from the implementation queue.</div>;
  }

  return (
    <div className="agent-run-list">
      {runs.map((run) => {
        const summary = typeof run.output?.summary === "string" ? run.output.summary : null;
        return (
          <article className="agent-run-card" key={run.id}>
            <div className="agent-run-top">
              <div>
                <Link className="queue-project" href={`/dashboard/projects/${run.project_id}`}>{run.project_title}</Link>
                <h2>{run.task_title}</h2>
                <p><span>{run.agent_name} v{run.agent_version}</span> · attempt {run.attempt_number}</p>
              </div>
              <span className={`run-state run-state-${run.state}`}>{run.state.replaceAll("_", " ")}</span>
            </div>
            <div className="run-meta-grid">
              <span>Model <strong>{run.model_provider}:{run.model_name}</strong></span>
              <span>Prompt <strong>{run.usage.prompt_tokens}</strong></span>
              <span>Completion <strong>{run.usage.completion_tokens}</strong></span>
              <span>Cost <strong>{run.usage.estimated_cost_cents}¢</strong></span>
            </div>
            {summary ? <div className="run-output"><strong>Output:</strong> {summary}</div> : null}
            {run.error ? <div className="task-dependencies">{run.error}</div> : null}
            <div className="queue-actions">
              {run.state === "queued" ? (
                <button className="button" type="button" disabled={busyRun !== null} onClick={() => action(run.id, "execute")}>Execute run</button>
              ) : null}
              {run.state === "needs_review" ? (
                <button className="button" type="button" disabled={busyRun !== null} onClick={() => action(run.id, "verify")}>Run QA verification</button>
              ) : null}
              {["queued", "preparing_context", "running", "waiting_for_tool", "waiting_for_approval", "needs_review"].includes(run.state) ? (
                <button className="button secondary-button" type="button" disabled={busyRun !== null} onClick={() => action(run.id, "cancel")}>Cancel run</button>
              ) : null}
              {["failed", "cancelled"].includes(run.state) ? (
                <button className="button secondary-button" type="button" disabled={busyRun !== null} onClick={() => action(run.id, "retry")}>Retry run</button>
              ) : null}
            </div>
            <AgentRunTrace runId={run.id} />
          </article>
        );
      })}
      {message ? <span className="message">{message}</span> : null}
    </div>
  );
}
