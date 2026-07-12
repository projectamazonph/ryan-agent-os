import Link from "next/link";
import { redirect } from "next/navigation";
import ImplementationQueue from "../implementation-queue";
import { getAgentDefinitions, getImplementationQueue, getToken } from "@/lib/api";

export default async function QueuePage() {
  const token = await getToken();
  if (!token) redirect("/login");
  const [tasks, agents] = await Promise.all([getImplementationQueue(), getAgentDefinitions()]);
  const ready = tasks.filter((task) => task.is_ready).length;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <div><div className="brand-title">Ryan Agent OS</div><div className="brand-subtitle">Execution control plane</div></div>
        </div>
        <nav className="nav">
          <Link className="nav-item" href="/dashboard">Capture Inbox</Link>
          <Link className="nav-item active" href="/dashboard/queue">Implementation Queue</Link>
          <Link className="nav-item" href="/dashboard/projects">Projects</Link>
          <Link className="nav-item" href="/dashboard/runs">Agent Runs</Link>
          <div className="nav-item">Approvals</div>
          <div className="nav-item">Artifacts</div>
        </nav>
        <div className="sidebar-footer">Phase 5 online<br />Asia/Manila workspace</div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">Implementation Queue</div>
            <h1>Do the right work next.</h1>
            <p className="lede">Ready tasks rise above blocked work using impact, urgency, confidence, effort, and dependency state.</p>
          </div>
          <div className="status-pill">{ready} ready / {tasks.length} open</div>
        </header>
        <section className="card">
          <div className="card-header">
            <div><h2 className="card-title">Ranked work</h2><p className="card-copy">Only active task graphs contribute work to this queue.</p></div>
          </div>
          <div className="card-body"><ImplementationQueue tasks={tasks} agents={agents} /></div>
        </section>
      </main>
    </div>
  );
}
