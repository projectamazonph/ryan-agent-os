"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function FileCaptureForm() {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const fileInput = form.elements.namedItem("file");
    if (fileInput instanceof HTMLInputElement && fileInput.files?.[0]) {
      data.set("file", fileInput.files[0]);
    }
    setLoading(true);
    setMessage("");
    setError(false);

    const response = await fetch("/api/captures/files", {
      method: "POST",
      body: data,
    });

    setLoading(false);
    if (!response.ok) {
      setError(true);
      setMessage("Upload failed. The source stayed local, which is at least polite.");
      return;
    }

    form.reset();
    setMessage("Source stored and queued for extraction.");
    router.refresh();
  }

  return (
    <form className="form" onSubmit={submit}>
      <div className="field">
        <label htmlFor="source_file">Source file</label>
        <input
          className="input file-input"
          id="source_file"
          name="file"
          type="file"
          required
          accept=".txt,.md,.csv,.html,.json,.pdf,.docx,text/plain,text/markdown,text/csv,text/html,application/json,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        />
      </div>
      <div className="field">
        <label htmlFor="file_title">File title</label>
        <input
          className="input"
          id="file_title"
          name="title"
          maxLength={300}
          placeholder="Optional. The filename is used when blank."
        />
      </div>
      <div className="form-row">
        <div className="field">
          <label htmlFor="file_domain_hint">Domain hint</label>
          <select className="select" id="file_domain_hint" name="domain_hint" defaultValue="">
            <option value="">Let the system decide</option>
            <option value="amazon_ppc">Amazon PPC</option>
            <option value="software">Software</option>
            <option value="training">Training</option>
            <option value="operations">Operations</option>
            <option value="personal_ai">Personal AI</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="file_sensitivity">Sensitivity</label>
          <select
            className="select"
            id="file_sensitivity"
            name="sensitivity"
            defaultValue="confidential"
          >
            <option value="public">Public</option>
            <option value="internal">Internal</option>
            <option value="confidential">Confidential</option>
            <option value="restricted">Restricted</option>
          </select>
        </div>
      </div>
      <button className="button" disabled={loading}>
        {loading ? "Uploading..." : "Upload source"}
      </button>
      <div className={`message ${error ? "error" : ""}`}>{message}</div>
    </form>
  );
}
