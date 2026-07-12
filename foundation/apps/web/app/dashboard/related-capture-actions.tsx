"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RelatedCaptureActions({
  captureId,
  targetCaptureId,
}: {
  captureId: string;
  targetCaptureId: string;
}) {
  const router = useRouter();
  const [busy, setBusy] = useState<"reference" | "merge" | null>(null);
  const [message, setMessage] = useState("");

  async function relate(action: "reference" | "merge") {
    setBusy(action);
    setMessage("");
    const response = await fetch(`/api/captures/${captureId}/relations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target_capture_id: targetCaptureId, action }),
    });
    setBusy(null);
    if (!response.ok) {
      setMessage("Action failed.");
      return;
    }
    setMessage(action === "merge" ? "Merged." : "Referenced.");
    router.refresh();
  }

  return (
    <div className="related-actions">
      <button
        className="text-button"
        type="button"
        disabled={busy !== null}
        onClick={() => relate("reference")}
      >
        {busy === "reference" ? "Referencing..." : "Reference"}
      </button>
      <button
        className="text-button danger-text"
        type="button"
        disabled={busy !== null}
        onClick={() => relate("merge")}
      >
        {busy === "merge" ? "Merging..." : "Merge into this"}
      </button>
      <span className="message action-message">{message}</span>
    </div>
  );
}
