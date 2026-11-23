import React, { useState } from "react";
import {
  Bug,
  CheckCircle2,
  Code2,
  FileCode2,
  Play,
  RotateCcw,
  SearchCode,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { analyzeSnippet } from "../services/api";
import { BorderBeam } from "../components/motion/BorderBeam";
import { ShimmerButton } from "../components/motion/ShimmerButton";

const SAMPLE_SNIPPETS = {
  injection: `import subprocess

def execute_user_task(cmd_string: str) -> int:
    # Security Flaw: Shell injection detected by Bandit B602
    proc = subprocess.Popen(cmd_string, shell=True)
    proc.wait()
    return proc.returncode
`,
  undefined_var: `def compute_order_total(items: list) -> float:
    # Bug: Undefined variable tax_rate detected by Ruff F821
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
`,
  zero_div: `def calculate_fee(amount: float, ratio: float) -> float:
    # Potential ZeroDivisionError on edge-case ratio == 0.0
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    fee = amount / ratio
    return fee
`,
  clean: `def safe_add(a: int, b: int) -> int:
    """Safely adds two integers together."""
    return a + b
`,
};

export const StaticAnalysis: React.FC = () => {
  const [code, setCode] = useState(SAMPLE_SNIPPETS.injection);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<"all" | "security" | "bug" | "quality">("all");

  const handleRunScan = async () => {
    setLoading(true);
    try {
      const data = await analyzeSnippet(code, "target_module.py");
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredFindings =
    results?.static_report?.findings?.filter((f: any) => {
      if (filter === "all") return true;
      return f.category === filter;
    }) || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-rule">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-ink font-display">
            Static Code Analysis
          </h1>
          <p className="text-sm text-ink-2 mt-1">
            Deterministic Python AST slicing, Ruff linter analysis, and Bandit security scans.
          </p>
        </div>

        <ShimmerButton
          onClick={handleRunScan}
          disabled={loading}
          className="text-xs"
        >
          <Play className={`w-3.5 h-3.5 fill-current ${loading ? "animate-spin" : ""}`} />
          <span>{loading ? "Analyzing AST & Rules..." : "Execute Static Scan"}</span>
        </ShimmerButton>
      </div>

      {/* Main Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Code Editor & Presets */}
        <div className="surface-card p-6 space-y-4 relative overflow-hidden">
          <BorderBeam size={200} duration={14} colorFrom="#6366f1" colorTo="#06b6d4" />
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-rule">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-accent" />
              <h3 className="text-sm font-semibold text-ink font-display">
                Python Source Buffer
              </h3>
            </div>

            {/* Presets */}
            <div className="flex items-center gap-1 p-1 rounded-lg bg-paper-2 border border-rule text-xs">
              {(["injection", "undefined_var", "zero_div", "clean"] as const).map((key) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => {
                    setCode(SAMPLE_SNIPPETS[key]);
                    setResults(null);
                  }}
                  className="px-2 py-0.5 rounded text-[11px] font-mono text-muted hover:text-ink transition-colors capitalize"
                >
                  {key.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          <textarea
            rows={16}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="w-full p-4 text-xs font-mono rounded-xl bg-paper-2 border border-rule focus:border-accent text-ink outline-none transition-colors leading-relaxed selection:bg-accent-subtle selection:text-accent"
          />

          <div className="flex items-center justify-between text-xs text-muted font-mono pt-1">
            <span>Buffer: target_module.py</span>
            <span>{code.split("\n").length} lines</span>
          </div>
        </div>

        {/* Right Column: AST Extraction & Findings */}
        <div className="space-y-6">
          {/* AST Extracted Functions */}
          <div className="surface-card p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-rule">
              <div className="flex items-center gap-2">
                <FileCode2 className="w-4 h-4 text-accent" />
                <h3 className="text-sm font-semibold text-ink font-display">
                  AST Sliced Functions
                </h3>
              </div>
              <span className="text-xs font-mono text-muted">
                {results?.ast_summary?.functions?.length || 0} functions detected
              </span>
            </div>

            {!results ? (
              <div className="text-center py-6 text-xs font-mono text-muted">
                Click "Execute Static Scan" to inspect AST functions & McCabe complexity.
              </div>
            ) : results.ast_summary?.functions?.length === 0 ? (
              <div className="text-center py-6 text-xs font-mono text-muted">
                No function definitions found in source.
              </div>
            ) : (
              <div className="space-y-2">
                {results.ast_summary?.functions?.map((fn: any, i: number) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl bg-paper-2 border border-rule-subtle flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-semibold text-ink font-mono">{fn.name}</div>
                      <div className="text-[11px] text-muted font-mono mt-0.5">
                        Lines {fn.start_line}–{fn.end_line} · Params: {fn.params.join(", ") || "none"}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-pill bg-paper-3 border border-rule text-ink-2">
                        McCabe: {fn.cyclomatic_complexity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Static Findings List */}
          <div className="surface-card p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-rule">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-accent" />
                <h3 className="text-sm font-semibold text-ink font-display">
                  Linter & Security Findings
                </h3>
              </div>

              {/* Category Filter */}
              <div className="flex items-center gap-1 text-[11px] font-mono">
                {(["all", "security", "bug"] as const).map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setFilter(cat)}
                    className={`px-2 py-0.5 rounded capitalize transition-colors ${
                      filter === cat
                        ? "bg-accent text-accent-ink font-semibold"
                        : "text-muted hover:text-ink"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {!results ? (
              <div className="text-center py-6 text-xs font-mono text-muted">
                Static scans detect runtime bugs (Ruff) and security flaws (Bandit).
              </div>
            ) : filteredFindings.length === 0 ? (
              <div className="p-6 rounded-xl bg-success-bg border border-success/30 text-center text-xs text-success-ink flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-success" />
                <span>Zero static violations detected in selected category!</span>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredFindings.map((f: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-paper-2 border border-rule-subtle space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-accent">
                          {f.rule_id}
                        </span>
                        <StatusBadge status={f.severity} />
                      </div>
                      <span className="text-[11px] font-mono text-muted">
                        Line {f.line_number} · {f.tool}
                      </span>
                    </div>
                    <p className="text-xs text-ink-2 font-sans">{f.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
