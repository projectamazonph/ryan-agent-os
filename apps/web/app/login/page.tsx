"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
    });
    setLoading(false);
    if (!response.ok) {
      setError("Those credentials did not open the airlock.");
      return;
    }
    router.push("/dashboard");
    router.refresh();
  }

  return (
    <main className="login-wrap">
      <section className="card login-card">
        <div className="login-brand">
          <div className="kicker">PRIVATE EXECUTION SYSTEM</div>
          <h1>Ryan Agent OS</h1>
          <p className="lede">Turn conversations and loose ideas into governed, traceable execution.</p>
        </div>
        <form className="form" onSubmit={submit}>
          <div className="field">
            <label htmlFor="email">Owner email</label>
            <input className="input" id="email" name="email" type="email" required autoComplete="email" />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input className="input" id="password" name="password" type="password" required autoComplete="current-password" />
          </div>
          <button className="button" disabled={loading}>{loading ? "Opening..." : "Enter Ryan Agent OS"}</button>
          <div className={`message ${error ? "error" : ""}`}>{error}</div>
        </form>
      </section>
    </main>
  );
}
