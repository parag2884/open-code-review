// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

export type Job = {
  id: string;
  status: string;
  source_type: string;
  source: string;
  branch?: string | null;
  mode: string;
  from_ref?: string | null;
  to_ref?: string | null;
  python_only: boolean;
  effort: string;
  actor: string;
  actor_oid?: string | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  error?: string | null;
  files_reviewed?: number | null;
  comments?: number | null;
  total_tokens?: number | null;
  elapsed?: string | null;
};

export type Finding = {
  id: number;
  job_id: string;
  path: string;
  content: string;
  suggestion_code?: string | null;
  existing_code?: string | null;
  start_line?: number | null;
  end_line?: number | null;
  category?: string | null;
  severity?: string | null;
};

export type ReviewRequest = {
  source_type: "git" | "local";
  source: string;
  branch?: string;
  from_ref?: string;
  to_ref?: string;
  python_only: boolean;
  effort: "low" | "medium" | "high";
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  const raw = await response.text();
  if (!response.ok) {
    let detail = raw || response.statusText;
    try {
      const body = JSON.parse(raw);
      if (body && (body.detail || body.message)) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body);
      }
    } catch {
      detail = raw || response.statusText;
    }
    throw new Error(detail);
  }
  if (!raw) {
    return undefined as T;
  }
  return JSON.parse(raw) as T;
}

export const api = {
  me: () => request<{ name: string; oid?: string; auth_mode: string }>("/api/auth/me"),
  settings: () => request<Record<string, unknown>>("/api/settings"),
  llmTest: () => request<{ ok: boolean; output: string; exit_code: number }>("/api/settings/llm-test", { method: "POST" }),
  createReview: (payload: ReviewRequest) =>
    request<Job>("/api/reviews", { method: "POST", body: JSON.stringify(payload) }),
  jobs: () => request<Job[]>("/api/jobs"),
  job: (id: string) =>
    request<{ job: Job; findings: Finding[]; logs: Array<{ id: number; line: string }> }>(`/api/jobs/${id}`),
  findings: (jobId?: string) =>
    request<Finding[]>(jobId ? `/api/findings?job_id=${encodeURIComponent(jobId)}` : "/api/findings"),
  audit: () => request<Array<Record<string, string>>>("/api/audit"),
};
