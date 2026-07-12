import Link from "next/link";
import { redirect } from "next/navigation";
import CaptureForm from "./capture-form";
import FileCaptureForm from "./file-capture-form";
import { getCaptures, getToken } from "@/lib/api";

export default async function DashboardPage() {
  const token = await getToken();
  if (!token) redirect("/login");
  const captures = await getCaptures();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <div><div className="brand-title">Ryan Agent OS</div><div className="brand-subtitle">Execution control plane</div></div>
        </div>
        <nav className="nav">
          <Link className="nav-item active" href="/dashboard">Capture Inbox</Link>
          <Link className="nav-item" href="/dashboard/queue">Implementation Queue</Link>
          <Link className="nav-item" href="/dashboard/projects">Projects</Link>
          <div className="nav-item">Agent Runs</div>
          <div className="nav-item">Approvals</div>
          <div className="nav-item">Artifacts</div>
        </nav>
        <div className="sidebar-footer">Phase 4 online<br />Asia/Manila workspace</div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">Capture Inbox</div>
            <h1>Drop the context. Keep the outcome.</h1>
            <p className="lede">Every conversation, note, and source file starts here. The system stores it immutably, detects duplicates, extracts useful text, and prepares it for review.</p>
          </div>
          <div className="status-pill">Phase 4 online</div>
        </header>
        <div className="grid">
          <div className="capture-stack">
            <section className="card">
              <div className="card-header">
                <div><h2 className="card-title">Paste context</h2><p className="card-copy">Conversations, rough notes, Markdown, URLs, and repository references.</p></div>
              </div>
              <div className="card-body"><CaptureForm /></div>
            </section>
            <section className="card">
              <div className="card-header">
                <div><h2 className="card-title">Upload source</h2><p className="card-copy">TXT, Markdown, CSV, HTML, JSON, PDF, and DOCX up to the configured limit.</p></div>
              </div>
              <div className="card-body"><FileCaptureForm /></div>
            </section>
          </div>
          <section className="card">
            <div className="card-header">
              <div><h2 className="card-title">Recent captures</h2><p className="card-copy">Open any item to inspect provenance, classification, and related context.</p></div>
              <span className="badge">{captures.length} stored</span>
            </div>
            <div className="card-body">
              <div className="capture-list">
                {captures.length === 0 ? <div className="empty">No captures yet. The inbox is suspiciously well behaved.</div> : captures.map((capture) => (
                  <Link className="capture" href={`/dashboard/captures/${capture.id}`} key={capture.id}>
                    <div className="capture-top"><div><h3>{capture.title}</h3><div className="capture-meta">{capture.type} / {capture.sensitivity} / {new Date(capture.created_at).toLocaleString()}</div></div><span className="badge">{capture.status}</span></div>
                    <p className="capture-summary">{capture.summary ?? (capture.content.slice(0, 180) || "Extraction pending.")}</p>
                  </Link>
                ))}
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
