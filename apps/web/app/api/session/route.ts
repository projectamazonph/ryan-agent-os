import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  const payload = await request.json();
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) return NextResponse.json({ error: "Invalid credentials" }, { status: response.status });
  const data = (await response.json()) as { access_token: string; expires_in: number };
  const outgoing = NextResponse.json({ ok: true });
  outgoing.cookies.set("raos_token", data.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.COOKIE_SECURE === "true",
    maxAge: data.expires_in,
    path: "/",
  });
  return outgoing;
}

export async function DELETE() {
  const response = NextResponse.json({ ok: true });
  response.cookies.set("raos_token", "", { httpOnly: true, maxAge: 0, path: "/" });
  return response;
}
