import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function POST(_request: NextRequest, context: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await context.params;
  const token = (await cookies()).get("raos_token")?.value;
  if (!token) return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  const response = await fetch(`${API_URL}/api/v1/projects/${projectId}/task-graph`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await response.json();
  return NextResponse.json(body, { status: response.status });
}
