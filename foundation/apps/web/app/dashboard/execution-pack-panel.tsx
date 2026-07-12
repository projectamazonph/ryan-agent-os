"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { ExecutionPack } from "@/lib/types";

export default function ExecutionPackPanel({
  projectId,
  pack,
}: {
  projectId: string;
  pack: ExecutionPack | null;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState<"generate" | "approve" | null>(null);
  const [message, setMessage] = useState("");

  async function generate() {
    setBusy("generate");
    setMessage("");
    const response = await fetch(`/api/projects/${projectId}/execution-pack`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ change_summary: "Generated from current project context" }),
    });
    setBusy(null);
    setMessage(response.ok ? "Execution pack generated." : "Generation failed.");
    if (response.ok) router.refresh();
  }

  async function approve() {
    if (!pack) return;
    setBusy("approve");
    setMessage("");
    const response = await fetch(`/api/projects/${projectId}/execution-pack/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version_number: pack.current_version_number }),
    });
    setBusy(null);
    setMessage(response.ok ? "Execution pack approved." : "Approval failed.");
    if (response.ok) router.refresh();
  }

  if (!pack) {
    return (
      <section className="card execution-pack-card">
        <div className="card-header">
          <div>
            <div className="eyebrow">Execution pack</div>
            <h2 className="card-title">Turn this project into an actionable plan</h2>
            <p className="card-copy">
              Generate a versioned objective, deliverables, workstreams, acceptance criteria, and risks.
            </p>
          </div>
        </div>
        <div className="card-body">
          <button className="button" type="button" disabled={busy !== null} onClick={generate}>
            {busy === "generate" ? "Generating..." : "Generate execution pack"}
          </button>
          <span className="message action-message">{message}</span>
        </div>
      </section>
    );
  }

  const content = pack.current_version.content;
  return (
    <section className="card execution-pack-card">
      <div className="card-header execution-pack-header">
        <div>
          <div className="eyebrow">Execution pack v{pack.current_version_number}</div>
          <h2 className="card-title">{content.objective}</h2>
          <p className="card-copy">{content.problem_statement}</p>
        </div>
        <span className="badge">{pack.status}</span>
      </div>
      <div className="card-body execution-pack-body">
        <div className="execution-pack-actions">
          <button className="button secondary-button" type="button" disabled={busy !== null} onClick={generate}>
            {busy === "generate" ? "Regenerating..." : "Create new version"}
          </button>
          <button className="button" type="button" disabled={busy !== null || pack.status === "approved"} onClick={approve}>
            {busy === "approve" ? "Approving..." : pack.status === "approved" ? `Version ${pack.current_version_number} approved` : `Approve version ${pack.current_version_number}`}
          </button>
          <span className="message action-message">{message}</span>
        </div>

        <div className="execution-section-grid">
          <section>
            <h3 className="section-title">Success criteria</h3>
            <ul className="execution-list">{content.success_criteria.map((item) => <li key={item}>{item}</li>)}</ul>
          </section>
          <section>
            <h3 className="section-title">Scope</h3>
            <ul className="execution-list">{content.in_scope.map((item) => <li key={item}>{item}</li>)}</ul>
          </section>
        </div>

        <section>
          <h3 className="section-title">Deliverables</h3>
          <div className="deliverable-grid">
            {content.deliverables.map((deliverable) => (
              <article className="deliverable-card" key={deliverable.name}>
                <strong>{deliverable.name}</strong>
                <p>{deliverable.description}</p>
                <span>{deliverable.format}</span>
                <ul>{deliverable.acceptance_criteria.map((criterion) => <li key={criterion}>{criterion}</li>)}</ul>
              </article>
            ))}
          </div>
        </section>

        <section>
          <h3 className="section-title">Workstreams</h3>
          <div className="workstream-list">
            {content.workstreams.map((workstream) => (
              <article className="workstream-card" key={workstream.name}>
                <strong>{workstream.name}</strong>
                <p>{workstream.goal}</p>
                <ol>{workstream.steps.map((step) => <li key={step}>{step}</li>)}</ol>
              </article>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
