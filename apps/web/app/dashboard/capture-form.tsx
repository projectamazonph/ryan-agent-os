"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function CaptureForm() {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setError(false);
    const form = event.currentTarget;
    const data = new FormData(form);
    const response = await fetch("/api/captures", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: data.get("type"),
        title: data.get("title"),
        content: data.get("content"),
        domain_hint: data.get("domain_hint") || null,
        sensitivity: data.get("sensitivity"),
      }),
    });
    setLoading(false);
    if (!response.ok) {
      setError(true);
      setMessage("Capture failed. The context escaped; the API did not.");
      return;
    }
    form.reset();
    setMessage("Captured and queued for processing.");
    router.refresh();
  }

  return (
    <form className="form" onSubmit={submit}>
      <div className="form-row">
        <div className="field"><label htmlFor="type">Input type</label><select className="select" id="type" name="type" defaultValue="conversation"><option value="conversation">Conversation</option><option value="note">Note</option><option value="markdown">Markdown</option><option value="url">URL</option><option value="repository">Repository</option></select></div>
        <div className="field"><label htmlFor="sensitivity">Sensitivity</label><select className="select" id="sensitivity" name="sensitivity" defaultValue="confidential"><option value="public">Public</option><option value="internal">Internal</option><option value="confidential">Confidential</option><option value="restricted">Restricted</option></select></div>
      </div>
      <div className="field"><label htmlFor="title">Title</label><input className="input" id="title" name="title" required maxLength={300} placeholder="What is this context about?" /></div>
      <div className="field"><label htmlFor="domain_hint">Domain hint</label><select className="select" id="domain_hint" name="domain_hint" defaultValue=""><option value="">Let the system decide</option><option value="amazon_ppc">Amazon PPC</option><option value="software">Software</option><option value="training">Training</option><option value="operations">Operations</option><option value="personal_ai">Personal AI</option></select></div>
      <div className="field"><label htmlFor="content">Raw context</label><textarea className="textarea" id="content" name="content" required placeholder="Paste the conversation, notes, request, or source material here." /></div>
      <button className="button" disabled={loading}>{loading ? "Capturing..." : "Capture context"}</button>
      <div className={`message ${error ? "error" : ""}`}>{message}</div>
    </form>
  );
}
