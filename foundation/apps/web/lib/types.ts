export type ClassificationResult = {
  domain: string;
  intent: string;
  confidence: number;
  evidence: string[];
  engine: string;
  needs_review: boolean;
};

export type Capture = {
  id: string;
  workspace_id: string;
  type: string;
  title: string;
  content: string;
  domain_hint: string | null;
  sensitivity: string;
  status: string;
  review_status: string;
  summary: string | null;
  classification: ClassificationResult | null;
  checksum_sha256: string;
  created_at: string;
  updated_at: string;
};

export type SourceObject = {
  id: string;
  workspace_id: string;
  capture_id: string;
  storage_key: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  checksum_sha256: string;
  extraction_status: string;
  extracted_text: string | null;
  extraction_error: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
  extracted_at: string | null;
  extraction_attempts: number;
  last_attempt_at: string | null;
};

export type RelatedCapture = {
  capture: Capture;
  score: number;
  reasons: string[];
};

export type CaptureReview = {
  capture: Capture;
  source: SourceObject | null;
  related: RelatedCapture[];
  projects: Project[];
};

export type Project = {
  id: string;
  workspace_id: string;
  title: string;
  summary: string | null;
  domain: string | null;
  status: string;
  priority: number;
  next_action: string | null;
  blocker: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectDetail = Project & { captures: Capture[] };

export type DeliverableSpec = {
  name: string;
  description: string;
  format: string;
  acceptance_criteria: string[];
};

export type WorkstreamSpec = {
  name: string;
  goal: string;
  steps: string[];
};

export type ExecutionPackContent = {
  objective: string;
  problem_statement: string;
  success_criteria: string[];
  in_scope: string[];
  out_of_scope: string[];
  assumptions: string[];
  deliverables: DeliverableSpec[];
  workstreams: WorkstreamSpec[];
  risks: string[];
  recommended_agents: string[];
};

export type ExecutionPackVersion = {
  id: string;
  version_number: number;
  content: ExecutionPackContent;
  change_summary: string | null;
  created_at: string;
  approved_at: string | null;
};

export type ExecutionPack = {
  id: string;
  project_id: string;
  status: string;
  current_version_number: number;
  current_version: ExecutionPackVersion;
  versions: ExecutionPackVersion[];
};

export type Task = {
  id: string;
  task_graph_id: string;
  project_id: string;
  project_title: string;
  key: string;
  title: string;
  description: string;
  verification: string;
  status: string;
  impact: number;
  urgency: number;
  confidence: number;
  effort: number;
  rank_score: number;
  position: number;
  dependency_keys: string[];
  blocked_by: string[];
  is_ready: boolean;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type TaskGraph = {
  id: string;
  project_id: string;
  status: string;
  source_execution_pack_version_id: string;
  source_execution_pack_version_number: number;
  source_execution_pack_approved_at: string;
  created_at: string;
  tasks: Task[];
};
