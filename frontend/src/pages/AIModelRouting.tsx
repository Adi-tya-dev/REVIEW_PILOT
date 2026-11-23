import React, { useState } from "react";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  Cpu,
  DollarSign,
  Layers,
  Network,
  Play,
  ShieldAlert,
  Sparkles,
  Timer,
  Zap,
} from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { AnimatedBeamWorkflow } from "../components/motion/AnimatedBeamWorkflow";
import { BorderBeam } from "../components/motion/BorderBeam";
import { ShimmerButton } from "../components/motion/ShimmerButton";

const PRESET_SLICES = {
  simple: `def divide_positive(a: float, b: float) -> float:
    # High risk of ZeroDivisionError if b == 0
    return a / b
`,
  complex: `def parse_and_dispatch_payload(raw_json: str, config: dict, flag_mode: bool = False):
    import json
    data = json.loads(raw_json)
    if flag_mode:
        for k, v in data.items():
            if k in config and config[k].get("enabled"):
                return config[k]["handler"](v)
    return None
`,
};

export const AIModelRouting: React.FC = () => {
  const [testCode, setTestCode] = useState(PRESET_SLICES.simple);
  const [decision, setDecision] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTestRouting = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/routing/review-slice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_path: "math_utils.py",
          source_code: testCode,
          modified_line_numbers: [3],
        }),
      });
      if (!res.ok) {
        throw new Error(`Routing endpoint returned status ${res.status}`);
      }
      const data = await res.json();
      setDecision(data);
    } catch (err: any) {
      setError(err.message || "Failed to route slice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-ink font-display">
          SLM–LLM Hybrid Model Router
        </h1>
        <p className="text-sm text-ink-2 mt-1">
          Evidence-grounded, cost-aware dispatching between local SLM (Ollama) and cloud LLM fallback.
        </p>
      </div>

      {/* Embedded Full Motion AI Workflow Pipeline */}
      <AnimatedBeamWorkflow
        prNumber={42}
        repoName="octocat/payment-service"
        initialEscalated={decision ? decision.escalation_triggered : false}
      />

      {/* Live Routing Playground */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Code Slice Input */}
        <div className="surface-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-rule">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-accent" />
              <h3 className="text-sm font-semibold text-ink font-display">
                Slice Review Playground
              </h3>
            </div>
            <div className="flex items-center gap-1 p-1 rounded-lg bg-paper-2 border border-rule text-xs">
              <button
                type="button"
                onClick={() => {
                  setTestCode(PRESET_SLICES.simple);
                  setDecision(null);
                }}
                className="px-2.5 py-0.5 rounded text-[11px] font-mono text-muted hover:text-ink transition-colors"
              >
                Simple Slice (SLM)
              </button>
              <button
                type="button"
                onClick={() => {
                  setTestCode(PRESET_SLICES.complex);
                  setDecision(null);
                }}
                className="px-2.5 py-0.5 rounded text-[11px] font-mono text-muted hover:text-ink transition-colors"
              >
                Complex Slice (LLM)
              </button>
            </div>
          </div>

          <textarea
            rows={10}
            value={testCode}
            onChange={(e) => setTestCode(e.target.value)}
            className="w-full p-4 text-xs font-mono rounded-xl bg-paper-2 border border-rule focus:border-accent text-ink outline-none transition-colors leading-relaxed selection:bg-accent-subtle selection:text-accent"
          />

          <div className="flex items-center justify-between pt-1">
            <span className="text-xs text-muted font-mono">
              Threshold: Calibrated Confidence ≥ 0.75
            </span>
            <ShimmerButton
              onClick={handleTestRouting}
              disabled={loading}
              className="text-xs"
            >
              <Play className={`w-3.5 h-3.5 fill-current ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? "Routing through Engine..." : "Evaluate & Route Slice"}</span>
            </ShimmerButton>
          </div>
        </div>

        {/* Right: Decision Output & Calibration */}
        <div className="space-y-6">
          <div className="surface-card p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-rule">
              <div className="flex items-center gap-2">
                <Network className="w-4 h-4 text-accent" />
                <h3 className="text-sm font-semibold text-ink font-display">
                  Routing Decision & Cost Telemetry
                </h3>
              </div>
              {decision && (
                <StatusBadge
                  status={decision.escalation_triggered ? "LLM Escalated" : "SLM Accepted"}
                />
              )}
            </div>

            {error && (
              <div className="p-4 rounded-xl bg-error-bg border border-error/30 text-xs text-error-ink">
                {error}
              </div>
            )}

            {!decision && !error ? (
              <div className="text-center py-8 text-xs font-mono text-muted">
                Execute a slice review to inspect calibrated confidence, model selection, latency, and cost telemetry.
              </div>
            ) : decision && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-paper-2 border border-rule-subtle">
                    <div className="text-[10px] text-muted uppercase">Selected Model</div>
                    <div className="font-bold text-ink mt-1 truncate">
                      {decision.selected_model}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-paper-2 border border-rule-subtle">
                    <div className="text-[10px] text-muted uppercase">Total Latency</div>
                    <div className="font-bold text-accent mt-1">
                      {decision.total_latency_ms} ms
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-paper-2 border border-rule-subtle">
                    <div className="text-[10px] text-muted uppercase">Estimated Cost</div>
                    <div className="font-bold text-ink mt-1">
                      ${decision.total_cost_usd?.toFixed(4) || "0.0000"}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-paper-2 border border-rule-subtle">
                    <div className="text-[10px] text-muted uppercase">Escalation Rationale</div>
                    <div className="font-bold text-ink mt-1 truncate">
                      {decision.escalation_reason || "SLM Sufficient"}
                    </div>
                  </div>
                </div>

                {decision.final_hypotheses?.length > 0 && (
                  <div className="p-4 rounded-xl bg-paper-2 border border-rule-subtle text-xs space-y-2">
                    <div className="text-[11px] font-mono font-semibold text-ink">
                      Proposed Hypothesis:
                    </div>
                    {decision.final_hypotheses.map((h: any, i: number) => (
                      <div key={i} className="text-ink-2 font-mono">
                        • {h.description}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Mathematical Calibration Reference */}
          <div className="surface-card p-5 space-y-2.5">
            <span className="text-[11px] font-mono font-semibold text-muted uppercase tracking-wider">
              Research Calibration Model
            </span>
            <div className="p-3 rounded-lg bg-paper-2 border border-rule text-xs font-mono text-ink-2 leading-relaxed">
              Confidence<sub>calibrated</sub> = (Raw<sub>conf</sub> × 0.40) + (Corroboration × 0.35) − (Complexity<sub>discount</sub> × 0.25)
            </div>
            <p className="text-xs text-muted leading-relaxed">
              When Calibrated Confidence falls below 0.75, ReviewPilot triggers automatic escalation to the cloud LLM, guaranteeing precision without incurring costs on straightforward defects.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
