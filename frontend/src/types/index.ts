export interface PullRequest {
  id: number;
  pr_number: number;
  title: string;
  state: string;
  author: string;
  html_url: string;
  repository: string;
  base_branch: string;
  head_branch: string;
  head_sha: string;
  created_at: string;
  review_sessions_count: number;
}

export interface StaticFinding {
  id: number;
  rule_id: string;
  tool: string;
  category: "security" | "quality" | "bug";
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  file_path: string;
  line_number: number;
  end_line_number?: number;
  description: string;
  code_snippet?: string;
  confidence: number;
  evidence_status: string;
}

export interface RoutingMetrics {
  total_review_sessions: number;
  slm_only_sessions: number;
  escalated_sessions: number;
  escalation_rate_percent: number;
  slm_retention_rate_percent: number;
  total_slm_calls: number;
  total_llm_calls: number;
  total_cost_usd: number;
  estimated_savings_vs_llm_only_usd: number;
}

export interface GeneratedTest {
  id: number;
  test_name: string;
  target_function: string;
  file_path: string;
  input_values?: string;
  expected_behavior?: string;
  validation_status: string;
  generator_model: string;
  original_test_code: string;
  repaired_test_code?: string;
}

export interface DockerExecution {
  id: number;
  container_id?: string;
  execution_status: "PASS" | "ASSERTION_FAILURE" | "RUNTIME_EXCEPTION" | "TEST_SYNTAX_ERROR" | "TEST_IMPORT_ERROR" | "TIMEOUT" | "ENVIRONMENT_ERROR";
  exit_code: number;
  execution_time_ms: number;
  stdout?: string;
  stderr?: string;
  exception_name?: string;
  exception_details?: string;
  timeout_reached: boolean;
}

export interface BenchmarkMetrics {
  approach: "Static-only" | "LLM-only" | "Hybrid SLM-LLM";
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;
  bug_detection_rate: number;
  test_compilation_rate: number;
  avg_latency_ms: number;
  model_calls_per_pr: number;
  llm_escalation_rate: number;
  avg_tokens_per_pr: number;
  avg_cost_per_pr_usd: number;
  reproducibility_rate: number;
}

