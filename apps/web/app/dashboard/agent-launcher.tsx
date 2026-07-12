"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { AgentDefinition, Task } from "@/lib/types";

export default function AgentLauncher({ task, agents }: { task: Task; agents: AgentDefinition[] }) {
  const router = useRouter();
  const [agentKey, setAgentKey] = useState(agents[0]?.key ?? "developer");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function createRun() {
    setBusy(true);
    setMessage("");
    const response = await fetch(`/api/tasks/${task.id}/agent-runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_key: agentKey }),
    });
    setBusy(false);
    setMessage(response.ok ? "Agent run queued." : "Agent run could not be created.");
    if (response.ok) router.refresh();
  }

  if (!task.is_ready || agents.length === 0) return null;

  return (
    <div className="agent-launcher">
      <label className="sr-only" htmlFor={`agent-${task.id}`}>Agent</label>
      <select
        aria-label="Agent"
        className="action-select"
        id={`agent-${task.id}`}
        value={agentKey}
        onChange={(event) => setAgentKey(event.target.value)}
      >
        {agents.map((agent) => (
          <option key={`${agent.key}-${agent.version}`} value={agent.key}>
            {agent.name} v{agent.version}
          </option>
        ))}
      </select>
      <button className="button secondary-button" type="button" disabled={busy} onClick={createRun}>
        {busy ? "Creating..." : "Create agent run"}
      </button>
      {message ? <span className="message">{message}</span> : null}
    </div>
  );
}
