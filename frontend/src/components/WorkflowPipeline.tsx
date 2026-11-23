import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  GitPullRequest,
  FileCode2,
  ShieldAlert,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Server,
  Terminal,
  Activity,
  Send,
  Play,
  RotateCcw,
  Info,
  X,
  ExternalLink,
  ChevronRight,
  ArrowRight,
} from "lucide-react";
import { StatusBadge } from "./StatusBadge";

export interface PipelineStageData {
  id: string;
  label: string;
  sublabel: string;
  icon: any;
  status: "idle" | "running" | "completed" | "error" | "escalated";
  executionTimeMs?: number;
  data: Record<string, any>;
  description: string;
}

interface WorkflowPipelineProps {
  prNumber?: number;
  repoName?: string;
  escalated?: boolean;
  onStageSelect?: (stageId: string) => void;
}

export const WorkflowPipeline: React.FC<WorkflowPipelineProps> = ({
  prNumber = 42,
  repoName = "octocat/payment-service",
  escalated = false,
  onStageSelect,
}) => {
  const [activeStepIndex, setActiveStepIndex] = useState<number>(12); // All finished by default
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [selectedStage, setSelectedStage] = useState<PipelineStageData | null>(null);
  const [isEscalatedMode, setIsEscalatedMode] = useState<boolean>(escalated);

  const stages: PipelineStageData[] = [
    {
      id: "pr_ingest",
      label: "GitHub Pull Request",
      sublabel: `PR #${prNumber} · ${repoName}`,
      icon: GitPullRequest,
      status: activeStepIndex >= 0 ? "completed" : "idle",
      executionTimeMs: 120,
      description: "Ingested webhook & extracted unified git diff and modified line numbers.",
      data: {
        pr: `#${prNumber}`,
        repo: repoName,
        base_branch: "main",
        head_branch: "fix-discount-handling",
        files_modified: 1,
        hunks: 1,
        added_lines: 6,
        deleted_lines: 1,
      },
    },
    {
      id: "ast_extract",
      label: "Python AST Slicer",
      sublabel: "Function extraction & McCabe",
      icon: FileCode2,
      status: activeStepIndex >= 1 ? "completed" : "idle",
      executionTimeMs: 45,
      description: "Parsed Python Abstract Syntax Tree to slice modified functions and isolate dependencies.",
      data: {
        functions_sliced: ["process_payment"],
        parameters: ["amount: float", "currency: str"],
        return_type: "float",
        mccabe_cyclomatic_complexity: 2,
        is_isolated: true,
      },
    },
    {
      id: "static_analysis",
      label: "Ruff + Bandit",
      sublabel: "Static bug & security scan",
      icon: ShieldAlert,
      status: activeStepIndex >= 2 ? "completed" : "idle",
      executionTimeMs: 280,
      description: "Executed native linters: Ruff for runtime errors and Bandit for AST security vulnerabilities.",
      data: {
        ruff_violations: 0,
        bandit_issues: 0,
        security_risk: "LOW",
        code_patterns: ["potential_zero_division", "unhandled_currency_fallback"],
      },
    },
    {
      id: "slm_review",
      label: "SLM Analysis",
      sublabel: "qwen2.5-coder:1.5b (Ollama)",
      icon: Cpu,
      status: activeStepIndex >= 3 ? "completed" : "idle",
      executionTimeMs: 1420,
      description: "Local Small Language Model reviewed isolated function diff and proposed hypothesis.",
      data: {
        model: "qwen2.5-coder:1.5b",
        provider: "Ollama (Local CUDA)",
        raw_confidence: isEscalatedMode ? 0.61 : 0.88,
        hypothesis: isEscalatedMode
          ? "Possible division by zero if discount ratio returns 0.0 for non-USD currencies"
          : "ZeroDivisionError when currency is not USD",
        token_count: 382,
        prompt_latency_ms: 81,
      },
    },
    {
      id: "quality_eval",
      label: "Quality Evaluation",
      sublabel: "Calibrated confidence & sufficiency",
      icon: Activity,
      status: activeStepIndex >= 4 ? "completed" : "idle",
      executionTimeMs: 15,
      description: "Calibrated raw SLM confidence against AST complexity and static analysis corroboration.",
      data: {
        formula: "Confidence_calibrated = (Raw_conf * 0.40) + (Corroboration * 0.35) - (Complexity_discount * 0.25)",
        calibrated_score: isEscalatedMode ? 0.58 : 0.85,
        threshold: 0.75,
        decision: isEscalatedMode ? "FAIL_THRESHOLD" : "SUFFICIENT",
      },
    },
    {
      id: "routing_decision",
      label: "SLM Sufficient?",
      sublabel: isEscalatedMode ? "Escalate to LLM (Score 0.58 < 0.75)" : "SLM Accepted (Score 0.85 >= 0.75)",
      icon: isEscalatedMode ? AlertTriangle : CheckCircle2,
      status: activeStepIndex >= 5 ? (isEscalatedMode ? "escalated" : "completed") : "idle",
      executionTimeMs: 5,
      description: isEscalatedMode
        ? "Routing Engine escalated to Cloud LLM fallback due to low confidence and complex edge-case condition."
        : "Routing Engine accepted SLM finding directly without calling expensive LLM.",
      data: {
        escalation_triggered: isEscalatedMode,
        reason: isEscalatedMode
          ? "Calibrated confidence (0.58) below research threshold (0.75)"
          : "High confidence with AST corroboration",
        cost_saved_usd: isEscalatedMode ? "$0.00" : "$0.042",
      },
    },
    {
      id: "test_gen",
      label: "Test Generation",
      sublabel: "pytest targeted edge cases",
      icon: Terminal,
      status: activeStepIndex >= 6 ? "completed" : "idle",
      executionTimeMs: 820,
      description: "Generated synthetic pytest test function designed to exercise the suspected flaw.",
      data: {
        test_name: "test_process_payment_zero_division_currency_eur",
        test_framework: "pytest",
        target_function: "process_payment",
        input_values: 'amount=100.0, currency="EUR"',
        expected_behavior: "Proper fee calculation without ZeroDivisionError",
      },
    },
    {
      id: "oracle_protection",
      label: "Oracle Validation",
      sublabel: "Invariant assertion locking",
      icon: ShieldAlert,
      status: activeStepIndex >= 7 ? "completed" : "idle",
      executionTimeMs: 32,
      description: "AST-based validator verified test assertions are preserved and cannot be tampered with.",
      data: {
        assertion_count: 1,
        syntax_valid: true,
        anti_tampering_passed: true,
        allowed_auto_repairs: ["import_insertion"],
      },
    },
    {
      id: "docker_exec",
      label: "Docker Sandbox",
      sublabel: "Isolated container execution",
      icon: Server,
      status: activeStepIndex >= 8 ? "completed" : "idle",
      executionTimeMs: 2450,
      description: "Executed test inside a sealed, restricted container (--network none, 512MB RAM, 1 CPU).",
      data: {
        container_id: "rp-sandbox-7b3f9c",
        isolation: "network:none",
        memory_limit: "512MB",
        cpu_quota: "1.0",
        exit_code: 1,
        duration_ms: 2450,
      },
    },
    {
      id: "pytest_results",
      label: "pytest Results",
      sublabel: "Captured stdout / stderr",
      icon: Terminal,
      status: activeStepIndex >= 9 ? "completed" : "idle",
      executionTimeMs: 12,
      description: "Classified test output: captured ZeroDivisionError traceback during execution.",
      data: {
        tests_run: 1,
        failures: 1,
        error_type: "ZeroDivisionError",
        traceback_line: "fee = amount / discount_ratio",
        category: "CODE_DEFECT",
      },
    },
    {
      id: "reproducibility",
      label: "Reproducibility Check",
      sublabel: "Execution evidence confirmed",
      icon: CheckCircle2,
      status: activeStepIndex >= 10 ? "completed" : "idle",
      executionTimeMs: 25,
      description: "Verified the failure is deterministic and stems from actual PR code, not test or environment flake.",
      data: {
        verdict: "CONFIRMED_DEFECT",
        flakiness_score: 0.0,
        grounding: "EVIDENCE_SUPPORTED",
      },
    },
    {
      id: "github_reporting",
      label: "GitHub Review Comment",
      sublabel: "Inline report with evidence",
      icon: Send,
      status: activeStepIndex >= 11 ? "completed" : "idle",
      executionTimeMs: 310,
      description: "Posted inline GitHub comment on line 37 with reproduction steps and isolated pytest case.",
      data: {
        file: "services/payment.py",
        line: 37,
        comment_posted: true,
        markdown_body: "### ⚠️ ReviewPilot Finding: Potential ZeroDivisionError...",
      },
    },
  ];

  // Playback timer
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setActiveStepIndex((prev) => {
          if (prev >= stages.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 700);
    }
    return () => clearInterval(interval);
  }, [isPlaying, stages.length]);

  const handleReset = () => {
    setIsPlaying(false);
    setActiveStepIndex(0);
  };

  const handlePlay = () => {
    if (activeStepIndex >= stages.length - 1) {
      setActiveStepIndex(0);
    }
    setIsPlaying(true);
  };

  const handleStageClick = (stage: PipelineStageData) => {
    setSelectedStage(stage);
    if (onStageSelect) onStageSelect(stage.id);
  };

  return (
    <div className="surface-card p-6 relative overflow-hidden">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-rule mb-6">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-ink tracking-tight font-display">
              Evidence-Grounded Review Pipeline
            </h3>
            <span className="px-2 py-0.5 text-xs font-mono font-medium rounded-pill bg-accent-subtle text-accent border border-accent/20">
              Live Architecture
            </span>
          </div>
          <p className="text-xs text-muted mt-1">
            Interactive visualization of Python AST extraction, hybrid SLM–LLM calibration, and Docker verification.
          </p>
        </div>

        {/* Playback Controls & Mode Toggle */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsEscalatedMode(!isEscalatedMode)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md border transition-colors ${
              isEscalatedMode
                ? "bg-warning-bg text-warning-ink border-warning/40 font-semibold"
                : "bg-paper-2 text-ink-2 border-rule hover:border-accent"
            }`}
            title="Toggle simulation of low-confidence PR that triggers LLM escalation"
          >
            {isEscalatedMode ? "Escalation Path (Active)" : "Direct SLM Path"}
          </button>

          <button
            onClick={isPlaying ? () => setIsPlaying(false) : handlePlay}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md bg-accent text-accent-ink hover:bg-accent-hover transition-colors shadow-subtle"
          >
            <Play className={`w-3.5 h-3.5 ${isPlaying ? "animate-spin" : ""}`} />
            {isPlaying ? "Running..." : activeStepIndex >= stages.length - 1 ? "Replay Flow" : "Simulate Run"}
          </button>

          <button
            onClick={handleReset}
            className="p-1.5 rounded-md border border-rule hover:bg-paper-2 text-muted hover:text-ink transition-colors"
            title="Reset pipeline animation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Workflow Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 relative">
        {stages.map((stage, idx) => {
          const isCurrent = activeStepIndex === idx && isPlaying;
          const isDone = activeStepIndex >= idx;
          const Icon = stage.icon;

          // Branch styling for decision node
          const isDecisionNode = stage.id === "routing_decision";

          return (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: idx * 0.04 }}
              onClick={() => handleStageClick(stage)}
              className={`relative rounded-xl p-4 border transition-all cursor-pointer select-none text-left ${
                isCurrent
                  ? "bg-accent-subtle/40 border-accent shadow-hover ring-2 ring-accent/20"
                  : isDone
                  ? isDecisionNode && isEscalatedMode
                    ? "bg-warning-bg/40 border-warning/40 shadow-subtle"
                    : "bg-paper-3 border-rule hover:border-accent hover:shadow-subtle"
                  : "bg-paper-2/60 border-rule-subtle opacity-50"
              }`}
            >
              {/* Top metadata row */}
              <div className="flex items-center justify-between mb-2.5">
                <div
                  className={`p-2 rounded-lg flex items-center justify-center ${
                    isCurrent
                      ? "bg-accent text-accent-ink animate-pulse"
                      : isDone
                      ? isDecisionNode && isEscalatedMode
                        ? "bg-warning text-paper font-bold"
                        : "bg-paper-2 text-accent"
                      : "bg-paper-2 text-muted"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] font-mono text-muted">
                    0{idx + 1}
                  </span>
                  {isDone && (
                    <span
                      className={`w-2 h-2 rounded-full ${
                        isDecisionNode && isEscalatedMode
                          ? "bg-warning"
                          : "bg-success"
                      }`}
                    />
                  )}
                </div>
              </div>

              {/* Node Title & Subtitle */}
              <h4 className="text-sm font-semibold text-ink tracking-tight font-display">
                {stage.label}
              </h4>
              <p className="text-xs text-muted font-mono mt-0.5 truncate">
                {stage.sublabel}
              </p>

              {/* Execution time pill */}
              {isDone && stage.executionTimeMs !== undefined && (
                <div className="mt-3 pt-2.5 border-t border-rule-subtle flex items-center justify-between text-[11px]">
                  <span className="text-muted">Duration</span>
                  <span className="font-mono font-medium text-ink-2">
                    {stage.executionTimeMs} ms
                  </span>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Decision Path Explanation Banner */}
      <div className="mt-6 p-4 rounded-xl border border-rule-subtle bg-paper-2 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <span
            className={`w-3 h-3 rounded-full flex-shrink-0 ${
              isEscalatedMode ? "bg-warning" : "bg-success"
            }`}
          />
          <div>
            <span className="font-semibold text-ink">
              {isEscalatedMode ? "Escalation Branch Active:" : "Direct SLM Path Active:"}
            </span>{" "}
            <span className="text-muted">
              {isEscalatedMode
                ? "Calibrated confidence fell below 0.75 → Cloud LLM invoked for complex multi-branch logic → Test synthesized."
                : "Calibrated confidence ≥ 0.75 → Small Local Model (Ollama) verified the bug → LLM skipped, 100% cost saved."}
            </span>
          </div>
        </div>
        <div className="text-muted font-mono whitespace-nowrap">
          Click any card to inspect stage payload & trace
        </div>
      </div>

      {/* Stage Inspection Drawer / Modal */}
      <AnimatePresence>
        {selectedStage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-ink/20 backdrop-blur-sm flex justify-end"
            onClick={() => setSelectedStage(null)}
          >
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 250 }}
              className="w-full max-w-lg bg-paper-3 h-full shadow-hover border-l border-rule p-6 overflow-y-auto flex flex-col justify-between"
              onClick={(e) => e.stopPropagation()}
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between pb-4 border-b border-rule mb-5">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-lg bg-accent-subtle text-accent">
                      <selectedStage.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-ink font-display">
                        {selectedStage.label}
                      </h3>
                      <p className="text-xs text-muted font-mono">
                        Stage ID: {selectedStage.id}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedStage(null)}
                    className="p-1.5 rounded-lg border border-rule hover:bg-paper-2 text-muted hover:text-ink transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Description */}
                <div className="mb-5">
                  <span className="text-xs font-semibold text-ink uppercase tracking-wider font-mono">
                    Overview
                  </span>
                  <p className="text-sm text-ink-2 mt-1 leading-relaxed">
                    {selectedStage.description}
                  </p>
                </div>

                {/* Execution Data JSON Tree */}
                <div className="mb-5">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-semibold text-ink uppercase tracking-wider font-mono">
                      Runtime Evidence Payload
                    </span>
                    {selectedStage.executionTimeMs && (
                      <span className="text-xs font-mono text-muted">
                        Latency: {selectedStage.executionTimeMs} ms
                      </span>
                    )}
                  </div>
                  <div className="p-4 rounded-xl bg-paper-2 border border-rule font-mono text-xs overflow-x-auto text-ink-2">
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(selectedStage.data, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>

              {/* Bottom Dismiss */}
              <div className="pt-4 border-t border-rule mt-6 flex justify-end">
                <button
                  onClick={() => setSelectedStage(null)}
                  className="px-4 py-2 text-xs font-medium rounded-lg bg-paper-2 hover:bg-paper text-ink border border-rule transition-colors"
                >
                  Close Stage Inspector
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

