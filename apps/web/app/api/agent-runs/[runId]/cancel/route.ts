import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest, context: { params: Promise<{ runId: string }> }) {
  const { runId } = await context.params;
  const token = (await cookies()).get("raos_token")?.value;
  if (!token) return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  const response = await fetch(`${API_URL}/api/v1/agent-runs/${runId}/cancel`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: await request.text(),
  });
  const body = await response.json();
  return NextResponse.json(body, { status: response.status });
}
