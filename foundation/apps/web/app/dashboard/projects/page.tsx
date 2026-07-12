import Link from "next/link";
import { redirect } from "next/navigation";
import ProjectList from "../project-list";
import { getProjects, getToken } from "@/lib/api";

export default async function ProjectsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const token = await getToken();
  if (!token) redirect("/login");
  const { q } = await searchParams;
  const projects = await getProjects(q);

  return (
    <div className="main standalone-main">
      <div className="review-toolbar">
        <Link className="back-link" href="/dashboard">← Capture Inbox</Link>
        <span className="status-pill">Project registry</span>
      </div>
      <header className="topbar project-header">
        <div>
          <div className="eyebrow">Projects</div>
          <h1>Execution starts after the idea survives review.</h1>
          <p className="lede">
            Search durable project records, see the next action, and spot blockers before they become decorative furniture.
          </p>
        </div>
      </header>
      <section className="card">
        <div className="card-header project-list-header">
          <div>
            <h2 className="card-title">Project registry</h2>
            <p className="card-copy">{projects.length} project{projects.length === 1 ? "" : "s"} in this view.</p>
          </div>
          <form className="project-search" method="get">
            <input
              aria-label="Search projects"
              className="input"
              defaultValue={q ?? ""}
              name="q"
              placeholder="Search title, domain, summary, or next action"
            />
            <button className="button" type="submit">Search</button>
          </form>
        </div>
        <div className="card-body"><ProjectList projects={projects} /></div>
      </section>
    </div>
  );
}
