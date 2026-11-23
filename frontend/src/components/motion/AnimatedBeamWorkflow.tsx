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
  X,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { BorderBeam } from "./BorderBeam";
import { ShimmerButton } from "./ShimmerButton";
import { StatusBadge } from "../StatusBadge";

export interface BeamNode {
  id: string;
  name: string;
  category: string;
  icon: any;
  latencyMs: number;
  status: "idle" | "running" | "completed" | "escalated";
  description: string;
  data: Record<string, any>;
}

interface AnimatedBeamWorkflowProps {
  prNumber?: number;
  repoName?: string;
  initialEscalated?: boolean;
}

export const AnimatedBeamWorkflow: React.FC<AnimatedBeamWorkflowProps> = ({
  prNumber = 42,
  repoName = "octocat/payment-service",
  initialEscalated = false,
}) => {
  const [isEscalated, setIsEscalated] = useState<boolean>(initialEscalated);
  const [activeStep, setActiveStep] = useState<number>(12); // All finished by default
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [selectedNode, setSelectedNode] = useState<BeamNode | null>(null);

  const nodes: BeamNode[] = [
    {
      id: "node_pr",
      name: "GitHub Webhook & Diff",
      category: "Ingestion",
      icon: GitPullRequest,
      latencyMs: 120,
      status: activeStep >= 0 ? "completed" : "idle",
      description: "Ingested webhook & extracted unified git diff and modified line numbers.",
      data: {
        pr_number: `#${prNumber}`,
        repository: repoName,
        base_branch: "main",
        head_branch: "fix-discount-handling",
        files_modified: 1,
        added_lines: 6,
        deleted_lines: 1,
      },
    },
    {
      id: "node_ast",
      name: "AST Function Slicer",
      category: "Code Analysis",
      icon: FileCode2,
      latencyMs: 45,
      status: activeStep >= 1 ? "completed" : "idle",
      description: "Isolated modified functions and computed McCabe cyclomatic complexity via Python AST.",
      data: {
        functions_sliced: ["process_payment"],
        mccabe_complexity: 2,
        arguments: ["amount: float", "currency: str"],
        return_type: "float",
      },
    },
    {
      id: "node_static",
      name: "Ruff & Bandit Scanner",
      category: "Static Linter",
      icon: ShieldAlert,
      latencyMs: 280,
      status: activeStep >= 2 ? "completed" : "idle",
      description: "Scanned for runtime bugs (Ruff) and security vulnerabilities (Bandit AST visitor).",
      data: {
        ruff_violations: 0,
        bandit_vulnerabilities: 0,
        code_risk_level: "LOW",
        patterns_flagged: ["unhandled_discount_zero_division"],
      },
    },
    {
      id: "node_slm",
      name: "Local SLM Review",
      category: "Ollama 1.5B (CUDA)",
      icon: Cpu,
      latencyMs: 1420,
      status: activeStep >= 3 ? "completed" : "idle",
      description: "Local Small Language Model reviewed isolated function diff and proposed hypothesis.",
      data: {
        model: "qwen2.5-coder:1.5b",
        provider: "Ollama (Local CUDA)",
        raw_confidence: isEscalated ? 0.61 : 0.88,
        token_count: 382,
        hypothesis: isEscalated
          ? "Potential division by zero if currency is non-USD"
          : "ZeroDivisionError in calculate_discount",
      },
    },
    {
      id: "node_calib",
      name: "Confidence Calibration",
      category: "Research Evaluator",
      icon: Activity,
      latencyMs: 15,
      status: activeStep >= 4 ? "completed" : "idle",
      description: "Evaluated calibrated confidence against AST complexity and static corroboration.",
      data: {
        formula: "Confidence_calibrated = (Raw * 0.40) + (Corroboration * 0.35) - (Complexity_discount * 0.25)",
        calibrated_score: isEscalated ? 0.58 : 0.85,
        decision_threshold: 0.75,
        sufficiency: isEscalated ? "FALLBACK_REQUIRED" : "SUFFICIENT",
      },
    },
    {
      id: "node_router",
      name: isEscalated ? "LLM Escalation" : "Direct SLM Path",
      category: isEscalated ? "Cloud Escalation" : "Cost-Free Route",
      icon: isEscalated ? AlertTriangle : CheckCircle2,
      latencyMs: isEscalated ? 1850 : 5,
      status: activeStep >= 5 ? (isEscalated ? "escalated" : "completed") : "idle",
      description: isEscalated
        ? "Calibrated score (0.58) < 0.75 threshold: Escalated to Cloud LLM for complex edge cases."
        : "Calibrated score (0.85) >= 0.75 threshold: Accepted local SLM review directly with $0 cloud cost.",
      data: {
        escalation_triggered: isEscalated,
        model_used: isEscalated ? "Cloud LLM (DeepSeek/GPT)" : "qwen2.5-coder:1.5b",
        cost_saved_usd: isEscalated ? "$0.00" : "$0.042",
      },
    },
    {
      id: "node_testgen",
      name: "pytest Test Synthesis",
      category: "Test Generation",
      icon: Terminal,
      latencyMs: 820,
      status: activeStep >= 6 ? "completed" : "idle",
      description: "Synthesized targeted pytest edge-case test function exercising the suspected defect.",
      data: {
        test_function: "test_process_payment_zero_division",
        test_framework: "pytest",
        target_function: "process_payment",
        input_args: 'amount=100.0, currency="EUR"',
      },
    },
    {
      id: "node_oracle",
      name: "Test Oracle Protection",
      category: "Invariant Guard",
      icon: ShieldCheck,
      latencyMs: 32,
      status: activeStep >= 7 ? "completed" : "idle",
      description: "Verified AST invariant assertion locking: assertions cannot be weakened, mutated, or deleted.",
      data: {
        assertion_count: 1,
        syntax_valid: true,
        anti_tampering_check: "PASSED",
        allowed_auto_repairs: ["import_insertion"],
      },
    },
    {
      id: "node_docker",
      name: "Docker Execution Sandbox",
      category: "Network: None",
      icon: Server,
      latencyMs: 2450,
      status: activeStep >= 8 ? "completed" : "idle",
      description: "Executed test inside a sealed, restricted container (--network none, 512MB RAM, 1 CPU).",
      data: {
        container_id: "rp-sandbox-7b3f9c",
        isolation: "network:none",
        memory_limit: "512MB",
        cpu_quota: "1.0",
        exit_code: 1,
      },
    },
    {
      id: "node_results",
      name: "pytest Output Classifier",
      category: "Execution Evidence",
      icon: Terminal,
      latencyMs: 12,
      status: activeStep >= 9 ? "completed" : "idle",
      description: "Captured and classified test execution: ZeroDivisionError traceback on line 37.",
      data: {
        verdict: "CODE_DEFECT",
        exception_type: "ZeroDivisionError",
        traceback_line: "fee = amount / discount_ratio",
      },
    },
    {
      id: "node_repro",
      name: "Reproducibility Grounding",
      category: "Evidence Verifier",
      icon: CheckCircle2,
      latencyMs: 25,
      status: activeStep >= 10 ? "completed" : "idle",
      description: "Verified the defect is 100% deterministic and grounded in concrete execution evidence.",
      data: {
        flakiness_score: 0.0,
        grounding_level: "EVIDENCE_SUPPORTED",
        reproducible: true,
      },
    },
    {
      id: "node_github",
      name: "GitHub Review Dispatch",
      category: "Reporting",
      icon: Send,
      latencyMs: 310,
      status: activeStep >= 11 ? "completed" : "idle",
      description: "Posted inline GitHub review comment on line 37 with reproduction steps and isolated pytest case.",
      data: {
        file_path: "services/payment.py",
        target_line: 37,
        markdown_review_comment_posted: true,
      },
    },
  ];

  // Playback timer
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setActiveStep((prev) => {
          if (prev >= nodes.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 650);
    }
    return () => clearInterval(interval);
  }, [isPlaying, nodes.length]);

  return (
    <div className="relative surface-card p-6 sm:p-8 overflow-hidden">
      {/* Signature Motion AI Border Beam */}
      <BorderBeam
        size={250}
        duration={12}
        colorFrom={isEscalated ? "#f59e0b" : "#6366f1"}
        colorTo={isEscalated ? "#ef4444" : "#06b6d4"}
      />

      {/* Header & Controls Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-rule mb-6 relative z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-accent" />
            </span>
            <h3 className="text-base sm:text-lg font-bold tracking-tight text-ink font-display">
              Neural Review & Routing Pipeline
            </h3>
            <span className="px-2 py-0.5 text-[10px] font-mono font-medium rounded-pill bg-accent-subtle text-accent border border-accent/30">
              Motion AI Powered
            </span>
          </div>
          <p className="text-xs text-muted mt-1">
            Real-time visual dataflow tracking AST slicing, calibrated model routing, and Docker verification.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5">
          {/* Escalation Toggle */}
          <button
            onClick={() => setIsEscalated(!isEscalated)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
              isEscalated
                ? "bg-warning-bg text-warning-ink border-warning/40 shadow-sm"
                : "bg-paper-2 text-ink-2 border-rule hover:border-accent"
            }`}
          >
            {isEscalated ? (
              <>
                <Zap className="w-3.5 h-3.5 text-warning" />
                <span>LLM Escalation Route</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-3.5 h-3.5 text-success" />
                <span>Direct SLM Route</span>
              </>
            )}
          </button>

          {/* Simulate Button */}
          <ShimmerButton
            onClick={() => {
              setActiveStep(0);
              setIsPlaying(true);
            }}
            className="text-xs"
          >
            <Play className={`w-3.5 h-3.5 fill-current ${isPlaying ? "animate-spin" : ""}`} />
            <span>{isPlaying ? "Processing..." : "Simulate Flow"}</span>
          </ShimmerButton>

          <button
            onClick={() => {
              setIsPlaying(false);
              setActiveStep(nodes.length - 1);
            }}
            className="p-2 rounded-lg border border-rule hover:bg-paper-2 text-muted hover:text-ink transition-colors"
            title="Reset flow"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* SVG Animated Connecting Beams */}
      <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {nodes.map((node, idx) => {
          const isDone = activeStep >= idx;
          const isCurrent = activeStep === idx && isPlaying;
          const Icon = node.icon;
          const isRouterNode = node.id === "node_router";

          return (
            <motion.div
              key={node.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.03 }}
              onClick={() => setSelectedNode(node)}
              className={`group relative rounded-xl p-4 border transition-all cursor-pointer select-none text-left overflow-hidden ${
                isCurrent
                  ? "bg-accent-subtle/40 border-accent shadow-hover ring-2 ring-accent/30"
                  : isDone
                  ? isRouterNode && isEscalated
                    ? "bg-warning-bg/30 border-warning/40 shadow-subtle hover:border-warning"
                    : "bg-paper-2/90 border-rule hover:border-accent hover:shadow-subtle"
                  : "bg-paper-2/30 border-rule-subtle opacity-40"
              }`}
            >
              {/* Active Traveling Beam Effect on currently active node */}
              {isCurrent && (
                <div className="absolute inset-0 bg-gradient-to-r from-accent/0 via-accent/15 to-accent/0 animate-shimmer-slide" />
              )}

              {/* Top metadata strip */}
              <div className="flex items-center justify-between mb-3 relative z-10">
                <div
                  className={`p-2 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110 ${
                    isCurrent
                      ? "bg-accent text-accent-ink animate-pulse"
                      : isDone
                      ? isRouterNode && isEscalated
                        ? "bg-warning text-paper font-bold"
                        : "bg-accent-subtle text-accent"
                      : "bg-paper-3 text-muted"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-mono text-muted">
                    0{idx + 1}
                  </span>
                  {isDone && (
                    <span
                      className={`w-2 h-2 rounded-full ${
                        isRouterNode && isEscalated ? "bg-warning animate-pulse" : "bg-success"
                      }`}
                    />
                  )}
                </div>
              </div>

              {/* Node Details */}
              <div className="relative z-10">
                <span className="text-[10px] font-mono text-muted uppercase tracking-wider block">
                  {node.category}
                </span>
                <h4 className="text-xs font-semibold text-ink font-display truncate mt-0.5 group-hover:text-accent transition-colors">
                  {node.name}
                </h4>

                {/* Latency Footer */}
                {isDone && (
                  <div className="mt-3 pt-2.5 border-t border-rule-subtle flex items-center justify-between text-[11px] font-mono">
                    <span className="text-muted">Latency</span>
                    <span className="text-ink-2 font-medium">
                      {node.latencyMs} ms
                    </span>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Routing Path Banner */}
      <div className="mt-6 p-4 rounded-xl bg-paper-2/80 border border-rule-subtle flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs relative z-10">
        <div className="flex items-center gap-3">
          <span
            className={`w-3 h-3 rounded-full shrink-0 ${
              isEscalated ? "bg-warning shadow-sm" : "bg-success shadow-sm"
            }`}
          />
          <div>
            <span className="font-semibold text-ink">
              {isEscalated ? "Cloud LLM Escalation Route Active:" : "Direct Local SLM Route Active:"}
            </span>{" "}
            <span className="text-muted">
              {isEscalated
                ? "Calibrated confidence fell below 0.75 → Cloud model escalated for complex edge verification."
                : "Calibrated confidence ≥ 0.75 → Verified locally with Ollama (1.5B) at $0 inference cost."}
            </span>
          </div>
        </div>
        <span className="text-muted font-mono text-[11px]">
          Click any stage node to inspect runtime evidence
        </span>
      </div>

      {/* Stage Inspection Side Drawer */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end"
            onClick={() => setSelectedNode(null)}
          >
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 250 }}
              className="w-full max-w-lg bg-paper-3 h-full shadow-2xl border-l border-rule p-6 overflow-y-auto flex flex-col justify-between"
              onClick={(e) => e.stopPropagation()}
            >
              <div>
                <div className="flex items-center justify-between pb-4 border-b border-rule mb-5">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-lg bg-accent-subtle text-accent">
                      <selectedNode.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-ink font-display">
                        {selectedNode.name}
                      </h3>
                      <p className="text-xs text-muted font-mono">
                        {selectedNode.category} · {selectedNode.latencyMs} ms
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedNode(null)}
                    className="p-1.5 rounded-lg border border-rule hover:bg-paper-2 text-muted hover:text-ink transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="mb-5">
                  <span className="text-[11px] font-mono font-semibold text-muted uppercase tracking-wider">
                    Pipeline Description
                  </span>
                  <p className="text-xs text-ink-2 mt-1 leading-relaxed">
                    {selectedNode.description}
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono font-semibold text-muted uppercase tracking-wider">
                      Execution Telemetry Payload
                    </span>
                    <span className="text-[11px] font-mono text-accent">JSON Live</span>
                  </div>
                  <div className="p-4 rounded-xl bg-paper-2 border border-rule font-mono text-xs text-ink-2 overflow-x-auto leading-relaxed">
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(selectedNode.data, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-rule mt-6 flex justify-end">
                <button
                  onClick={() => setSelectedNode(null)}
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

