import Link from "next/link";
import type { Project } from "@/lib/types";

export default function ProjectList({ projects }: { projects: Project[] }) {
  if (projects.length === 0) {
    return <div className="empty">No projects match the current view.</div>;
  }

  return (
    <div className="project-list">
      {projects.map((project) => (
        <article className="project-card" key={project.id}>
          <div className="project-card-top">
            <div>
              <Link
                aria-label={project.title}
                className="project-title-link"
                href={`/dashboard/projects/${project.id}`}
              >
                {project.title}
              </Link>
              <div className="capture-meta">
                {project.domain ?? "unclassified"} / {project.status}
              </div>
            </div>
            <span className="badge">{project.priority} priority</span>
          </div>
          <p className="capture-summary">
            {project.summary ?? "No project summary has been written yet."}
          </p>
          <div className="project-signal-grid">
            <div>
              <span>Next action</span>
              <strong>{project.next_action ?? "Not set"}</strong>
            </div>
            <div>
              <span>Blocker</span>
              <strong>{project.blocker ?? "None"}</strong>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
