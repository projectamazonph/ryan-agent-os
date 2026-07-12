import { NextRequest } from "next/server";
import { cookies } from "next/headers";

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function GET(request: NextRequest, context: { params: Promise<{ runId: string }> }) {
  const { runId } = await context.params;
  const token = (await cookies()).get("raos_token")?.value;
  if (!token) return Response.json({ detail: "Unauthorized" }, { status: 401 });

  const upstreamUrl = new URL(`${API_URL}/api/v1/agent-runs/${runId}/events/stream`);
  upstreamUrl.searchParams.set("follow_seconds", request.nextUrl.searchParams.get("follow_seconds") ?? "60");
  const afterSequence = request.nextUrl.searchParams.get("after_sequence");
  if (afterSequence) upstreamUrl.searchParams.set("after_sequence", afterSequence);

  const lastEventId = request.headers.get("last-event-id");
  const response = await fetch(upstreamUrl, {
    cache: "no-store",
    headers: {
      Accept: "text/event-stream",
      Authorization: `Bearer ${token}`,
      ...(lastEventId ? { "Last-Event-ID": lastEventId } : {}),
    },
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Cache-Control": "no-cache, no-transform",
      "Content-Type": response.headers.get("content-type") ?? "text/event-stream",
      "X-Accel-Buffering": "no",
    },
  });
}
