import Link from "next/link";
import type { CaptureReview, Project } from "@/lib/types";
import CaptureReviewActions from "./capture-review-actions";
import RelatedCaptureActions from "./related-capture-actions";

function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export default function CaptureReviewPanel({ review, availableProjects = [] }: { review: CaptureReview; availableProjects?: Project[] }) {
  const { capture, source, related, projects } = review;
  const classification = capture.classification;

  return (
    <div className="review-grid">
      <section className="card review-main">
        <div className="card-header">
          <div>
            <div className="eyebrow">Capture review</div>
            <h1 className="review-title">{capture.title}</h1>
            <p className="card-copy">
              {capture.type} / {capture.sensitivity} / {capture.status}
            </p>
          </div>
          <span className="badge">{capture.status}</span>
        </div>
        <div className="card-body review-body">
          <CaptureReviewActions captureId={capture.id} reviewStatus={capture.review_status} sourceStatus={source?.extraction_status} projects={availableProjects.filter((candidate) => !projects.some((linked) => linked.id === candidate.id))} />
          <section>
            <h2 className="section-title">Working summary</h2>
            <p className="review-copy">{capture.summary ?? "Processing has not produced a summary yet."}</p>
          </section>
          <section>
            <h2 className="section-title">Captured context</h2>
            <pre className="context-block">{capture.content || "Text extraction is pending."}</pre>
          </section>
        </div>
      </section>

      <aside className="review-side">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Classification</h2></div>
          <div className="card-body">
            {classification ? (
              <dl className="detail-list">
                <div><dt>Domain</dt><dd>{classification.domain}</dd></div>
                <div><dt>Intent</dt><dd>{classification.intent}</dd></div>
                <div><dt>Confidence</dt><dd>{Math.round(classification.confidence * 100)}% confidence</dd></div>
                <div><dt>Engine</dt><dd>{classification.engine}</dd></div>
              </dl>
            ) : <div className="empty compact">Classification is pending.</div>}
          </div>
        </section>

        <section className="card">
          <div className="card-header"><h2 className="card-title">Source provenance</h2></div>
          <div className="card-body">
            {source ? (
              <dl className="detail-list">
                <div><dt>File</dt><dd>{source.original_filename}</dd></div>
                <div><dt>Type</dt><dd>{source.content_type}</dd></div>
                <div><dt>Size</dt><dd>{formatBytes(source.size_bytes)}</dd></div>
                <div><dt>Extraction</dt><dd>{source.extraction_status}</dd></div>
                <div><dt>Checksum</dt><dd className="mono">{source.checksum_sha256.slice(0, 16)}…</dd></div>
              </dl>
            ) : <div className="empty compact">This capture was entered as text.</div>}
          </div>
        </section>


        <section className="card">
          <div className="card-header"><h2 className="card-title">Linked projects</h2></div>
          <div className="card-body related-list">
            {projects.length === 0 ? <div className="empty compact">No project is linked yet.</div> : projects.map((project) => (
              <Link aria-label={project.title} className="related-item" href={`/dashboard/projects/${project.id}`} key={project.id}>
                <strong>{project.title}</strong>
                <span>{project.status} / priority {project.priority}</span>
              </Link>
            ))}
          </div>
        </section>

        <section className="card">
          <div className="card-header"><h2 className="card-title">Related context</h2></div>
          <div className="card-body related-list">
            {related.length === 0 ? <div className="empty compact">No related captures crossed the current threshold.</div> : related.map((item) => (
              <div className="related-item" key={item.capture.id}>
                <Link aria-label={item.capture.title} href={`/dashboard/captures/${item.capture.id}`}>
                  <strong>{item.capture.title}</strong>
                  <span>{Math.round(item.score * 100)}% related / {item.reasons.join(", ")}</span>
                </Link>
                <RelatedCaptureActions captureId={capture.id} targetCaptureId={item.capture.id} />
              </div>
            ))}
          </div>
        </section>
      </aside>
    </div>
  );
}
