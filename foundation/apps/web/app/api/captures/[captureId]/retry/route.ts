import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ captureId: string }> },
) {
  const token = request.cookies.get("raos_token")?.value;
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  const { captureId } = await context.params;
  const response = await fetch(`${API_URL}/api/v1/captures/${captureId}/retry`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
