import { BenchmarkMetrics, DockerExecution, GeneratedTest, PullRequest, RoutingMetrics, StaticFinding } from "../types";

const API_BASE = "/api/v1";

export async function fetchHealth() {
  const res = await fetch("/health");
  return res.json();
}

export async function fetchPullRequests(): Promise<PullRequest[]> {
  const res = await fetch(`${API_BASE}/pull-requests`);
  if (!res.ok) throw new Error("Failed to fetch pull requests");
  return res.json();
}

export async function fetchPullRequestDetails(id: number) {
  const res = await fetch(`${API_BASE}/pull-requests/${id}`);
  if (!res.ok) throw new Error("Failed to fetch PR details");
  return res.json();
}

export async function fetchFindingsForReview(reviewSessionId: number): Promise<StaticFinding[]> {
  const res = await fetch(`${API_BASE}/findings/review/${reviewSessionId}`);
  if (!res.ok) throw new Error("Failed to fetch findings");
  return res.json();
}

export async function fetchRoutingMetrics(): Promise<RoutingMetrics> {
  const res = await fetch(`${API_BASE}/routing/metrics`);
  if (!res.ok) throw new Error("Failed to fetch routing metrics");
  return res.json();
}

export async function fetchGeneratedTests(reviewSessionId: number): Promise<GeneratedTest[]> {
  const res = await fetch(`${API_BASE}/tests/review/${reviewSessionId}`);
  if (!res.ok) throw new Error("Failed to fetch generated tests");
  return res.json();
}

export async function analyzeSnippet(code: string, filename = "snippet.py") {
  const res = await fetch(`${API_BASE}/findings/analyze-snippet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, filename }),
  });
  if (!res.ok) throw new Error("Failed to analyze snippet");
  return res.json();
}

export async function analyzeLocalDiff(title: string, raw_diff: string) {
  const res = await fetch(`${API_BASE}/pull-requests/analyze/local`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, raw_diff }),
  });
  if (!res.ok) throw new Error("Failed to analyze local diff");
  return res.json();
}

export async function fetchBenchmarkComparison(): Promise<BenchmarkMetrics[]> {
  const res = await fetch(`${API_BASE}/benchmarks/comparison`);
  if (!res.ok) {
    // If benchmark endpoint is not yet loaded, return empty list
    return [];
  }
  return res.json();
}

