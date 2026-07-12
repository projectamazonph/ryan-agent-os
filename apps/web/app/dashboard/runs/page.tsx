import Link from "next/link";
import { redirect } from "next/navigation";
import AgentRunConsole from "../agent-run-console";
import { getAgentDefinitions, getAgentRuns, getToken } from "@/lib/api";

export default async function AgentRunsPage() {
  const token = await getToken();
  if (!token) redirect("/login");
  const [runs, agents] = await Promise.all([getAgentRuns(), getAgentDefinitions()]);
  const active = runs.filter((run) => !["succeeded", "failed", "cancelled"].includes(run.state)).length;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <div><div className="brand-title">Ryan Agent OS</div><div className="brand-subtitle">Execution control plane</div></div>
        </div>
        <nav className="nav">
          <Link className="nav-item" href="/dashboard">Capture Inbox</Link>
          <Link className="nav-item" href="/dashboard/queue">Implementation Queue</Link>
          <Link className="nav-item" href="/dashboard/projects">Projects</Link>
          <Link className="nav-item active" href="/dashboard/runs">Agent Runs</Link>
          <div className="nav-item">Approvals</div>
          <div className="nav-item">Artifacts</div>
        </nav>
        <div className="sidebar-footer">Phase 5 online<br />Asia/Manila workspace</div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">Agent Runs</div>
            <h1>Bounded agents. Complete receipts.</h1>
            <p className="lede">Every run carries an immutable context checksum, versioned agent definition, tool policy, state history, usage record, retry lineage, and QA verdict.</p>
          </div>
          <div className="status-pill">{active} active / {runs.length} total</div>
        </header>
        <section className="card agent-registry-summary">
          <div className="card-header">
            <div><h2 className="card-title">Agent registry</h2><p className="card-copy">The latest active version of each bounded specialist.</p></div>
            <span className="badge">{agents.length} agents</span>
          </div>
          <div className="card-body agent-chip-list">
            {agents.map((agent) => <span className="agent-chip" key={`${agent.key}-${agent.version}`}>{agent.name} v{agent.version}</span>)}
          </div>
        </section>
        <section className="card">
          <div className="card-header">
            <div><h2 className="card-title">Run console</h2><p className="card-copy">Execute, stop, retry, or send completed output through QA.</p></div>
          </div>
          <div className="card-body"><AgentRunConsole runs={runs} /></div>
        </section>
      </main>
    </div>
  );
}
