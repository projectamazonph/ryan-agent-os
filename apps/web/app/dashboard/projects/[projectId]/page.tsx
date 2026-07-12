import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import ExecutionPackPanel from "../../execution-pack-panel";
import TaskGraphPanel from "../../task-graph-panel";
import { getExecutionPack, getProject, getTaskGraph, getToken } from "@/lib/api";

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const token = await getToken();
  if (!token) redirect("/login");
  const { projectId } = await params;
  const [project, executionPack, taskGraph] = await Promise.all([getProject(projectId), getExecutionPack(projectId), getTaskGraph(projectId)]);
  if (!project) notFound();

  return (
    <div className="main standalone-main">
      <div className="review-toolbar">
        <Link className="back-link" href="/dashboard/projects">← Project registry</Link>
        <span className="status-pill">{project.status}</span>
      </div>
      <ExecutionPackPanel projectId={projectId} pack={executionPack} />
      <TaskGraphPanel projectId={projectId} executionPack={executionPack} graph={taskGraph} />
      <div className="review-grid project-workspace-grid">
        <section className="card review-main">
          <div className="card-header">
            <div>
              <div className="eyebrow">Project workspace</div>
              <h1 className="review-title">{project.title}</h1>
              <p className="card-copy">
                {project.domain ?? "unclassified"} / priority {project.priority}
              </p>
            </div>
          </div>
          <div className="card-body review-body">
            <section>
              <h2 className="section-title">Project summary</h2>
              <p className="review-copy">{project.summary ?? "No summary yet."}</p>
            </section>
            <section>
              <h2 className="section-title">Source captures</h2>
              <div className="related-list">
                {project.captures.length === 0 ? (
                  <div className="empty compact">No captures are linked.</div>
                ) : project.captures.map((capture) => (
                  <Link
                    aria-label={capture.title}
                    className="related-item"
                    href={`/dashboard/captures/${capture.id}`}
                    key={capture.id}
                  >
                    <strong>{capture.title}</strong>
                    <span>{capture.type} / {capture.review_status}</span>
                  </Link>
                ))}
              </div>
            </section>
          </div>
        </section>
        <aside className="review-side">
          <section className="card">
            <div className="card-header"><h2 className="card-title">Execution signals</h2></div>
            <div className="card-body">
              <dl className="detail-list">
                <div><dt>Next action</dt><dd>{project.next_action ?? "Not set"}</dd></div>
                <div><dt>Blocker</dt><dd>{project.blocker ?? "None"}</dd></div>
                <div><dt>Priority</dt><dd>{project.priority}</dd></div>
                <div><dt>Updated</dt><dd>{new Date(project.updated_at).toLocaleString()}</dd></div>
              </dl>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}
