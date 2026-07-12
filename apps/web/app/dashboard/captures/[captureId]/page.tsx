import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import CaptureReviewPanel from "../../capture-review-panel";
import { getCaptureReview, getProjects, getToken } from "@/lib/api";

export default async function CaptureReviewPage({
  params,
}: {
  params: Promise<{ captureId: string }>;
}) {
  const token = await getToken();
  if (!token) redirect("/login");
  const { captureId } = await params;
  const [review, projects] = await Promise.all([getCaptureReview(captureId), getProjects()]);
  if (!review) notFound();

  return (
    <div className="main standalone-main">
      <div className="review-toolbar">
        <Link className="back-link" href="/dashboard">← Capture Inbox</Link>
        <span className="status-pill">Review workspace</span>
      </div>
      <CaptureReviewPanel review={review} availableProjects={projects} />
    </div>
  );
}
