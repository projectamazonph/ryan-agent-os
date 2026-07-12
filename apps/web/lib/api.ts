import { cookies } from "next/headers";
import type { AgentDefinition, AgentRun, Capture, CaptureReview, ExecutionPack, Project, ProjectDetail, Task, TaskGraph } from "./types";

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function getToken(): Promise<string | undefined> {
  const store = await cookies();
  return store.get("raos_token")?.value;
}

export async function getCaptures(): Promise<Capture[]> {
  const token = await getToken();
  if (!token) return [];
  const response = await fetch(`${API_URL}/api/v1/captures`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return [];
  const data = (await response.json()) as { items: Capture[] };
  return data.items;
}

export async function getCaptureReview(captureId: string): Promise<CaptureReview | null> {
  const token = await getToken();
  if (!token) return null;
  const response = await fetch(`${API_URL}/api/v1/captures/${captureId}/review`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return null;
  return (await response.json()) as CaptureReview;
}

export async function getProjects(query?: string): Promise<Project[]> {
  const token = await getToken();
  if (!token) return [];
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  const suffix = params.size ? `?${params.toString()}` : "";
  const response = await fetch(`${API_URL}/api/v1/projects${suffix}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return [];
  const data = (await response.json()) as { items: Project[] };
  return data.items;
}

export async function getProject(projectId: string): Promise<ProjectDetail | null> {
  const token = await getToken();
  if (!token) return null;
  const response = await fetch(`${API_URL}/api/v1/projects/${projectId}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return null;
  return (await response.json()) as ProjectDetail;
}

export async function getExecutionPack(projectId: string): Promise<ExecutionPack | null> {
  const token = await getToken();
  if (!token) return null;
  const response = await fetch(`${API_URL}/api/v1/projects/${projectId}/execution-pack`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return null;
  return (await response.json()) as ExecutionPack;
}

export async function getTaskGraph(projectId: string): Promise<TaskGraph | null> {
  const token = await getToken();
  if (!token) return null;
  const response = await fetch(`${API_URL}/api/v1/projects/${projectId}/task-graph`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return null;
  return (await response.json()) as TaskGraph;
}

export async function getImplementationQueue(): Promise<Task[]> {
  const token = await getToken();
  if (!token) return [];
  const response = await fetch(`${API_URL}/api/v1/queue`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return [];
  const data = (await response.json()) as { items: Task[] };
  return data.items;
}

export async function getAgentDefinitions(): Promise<AgentDefinition[]> {
  const token = await getToken();
  if (!token) return [];
  const response = await fetch(`${API_URL}/api/v1/agents`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return [];
  const data = (await response.json()) as { items: AgentDefinition[] };
  return data.items;
}

export async function getAgentRuns(): Promise<AgentRun[]> {
  const token = await getToken();
  if (!token) return [];
  const response = await fetch(`${API_URL}/api/v1/agent-runs`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) return [];
  const data = (await response.json()) as { items: AgentRun[] };
  return data.items;
}
