import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  BookOpen,
  CheckCircle2,
  Cpu,
  FileCode2,
  GitPullRequest,
  HelpCircle,
  Layers,
  Lock,
  Play,
  Server,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Terminal,
  Zap,
  ArrowRight,
  ChevronRight,
  ExternalLink,
} from "lucide-react";
import { BorderBeam } from "../components/motion/BorderBeam";
import { ShimmerButton } from "../components/motion/ShimmerButton";
import { PageId } from "../components/Sidebar";

interface WebsiteManualProps {
  onNavigate?: (page: PageId) => void;
}

export const WebsiteManual: React.FC<WebsiteManualProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState<"pipeline" | "routing" | "oracle" | "docker" | "faq">("pipeline");

  const steps = [
    {
      num: "01",
      title: "GitHub Webhook & PR Diff Ingestion",
      icon: GitPullRequest,
      desc: "ReviewPilot listens for incoming GitHub pull request events or manual diff submissions. Every webhook is verified using constant-time HMAC-SHA256 signature verification. The git diff is parsed into structured hunks and mapped to exact modified line numbers.",
      pageLink: "repos" as PageId,
      linkText: "Configure Ingestion",
    },
    {
      num: "02",
      title: "Python AST Extraction & Complexity",
      icon: FileCode2,
      desc: "The Python Abstract Syntax Tree (AST) parser isolates modified functions, extracts parameters, return types, and docstrings, and calculates McCabe Cyclomatic Complexity to measure structural branching.",
      pageLink: "static-analysis" as PageId,
      linkText: "Inspect AST Slicer",
    },
    {
      num: "03",
      title: "Static Linter & Security Scan (Ruff + Bandit)",
      icon: ShieldAlert,
      desc: "Deterministic linters run concurrently: Ruff detects runtime bugs (e.g. F821 undefined variables) while Bandit scans AST nodes for security vulnerabilities (e.g. B602 shell injections and B307 eval calls).",
      pageLink: "static-analysis" as PageId,
      linkText: "View Static Rules",
    },
    {
      num: "04",
      title: "Local SLM Inference (Ollama 1.5B)",
      icon: Cpu,
      desc: "An isolated code slice is sent to the local Small Language Model (qwen2.5-coder:1.5b) running via Ollama with CUDA GPU acceleration. The SLM proposes defect hypotheses along with a raw confidence score.",
      pageLink: "model-routing" as PageId,
      linkText: "Review SLM Config",
    },
    {
      num: "05",
      title: "Calibrated Confidence & Sufficiency Decision",
      icon: Zap,
      desc: "The router applies the research calibration equation: Confidence_calibrated = (Raw_conf * 0.40) + (Corroboration * 0.35) - (Complexity * 0.25). If calibrated confidence >= 0.75, the local SLM review is accepted directly (0 LLM cost). If < 0.75, the request is escalated to the cloud LLM.",
      pageLink: "model-routing" as PageId,
      linkText: "Explore Routing Matrix",
    },
    {
      num: "06",
      title: "Targeted Test Synthesis & Test Oracle Protection",
      icon: Lock,
      desc: "The engine synthesizes a targeted pytest reproduction test. The Test Oracle Protection guard locks assertions, rejecting any AI attempt to weaken tests with assert True, deleted assertions, or try/except suppression.",
      pageLink: "test-cases" as PageId,
      linkText: "View Generated Tests",
    },
    {
      num: "07",
      title: "Isolated Docker Sandbox Execution",
      icon: Server,
      desc: "Tests run inside an ephemeral Docker container with strict constraints: network isolated (--network none), 512MB RAM memory limit, 1.0 CPU quota, and a 15-second timeout.",
      pageLink: "docker-results" as PageId,
      linkText: "Inspect Docker Sandbox",
    },
    {
      num: "08",
      title: "Reproducibility Verification & GitHub Comment",
      icon: CheckCircle2,
      desc: "Test results are classified. A finding is marked as a CONFIRMED_DEFECT only when backed by genuine container failure. An inline review comment formatted in Markdown is dispatched to the GitHub PR.",
      pageLink: "evidence" as PageId,
      linkText: "Inspect Evidence Triad",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="relative surface-card p-6 sm:p-8 overflow-hidden">
        <BorderBeam size={260} duration={14} colorFrom="#6366f1" colorTo="#06b6d4" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-accent-subtle text-accent">
                <BookOpen className="w-4 h-4" />
              </span>
              <span className="text-[11px] font-mono font-medium text-accent uppercase tracking-wider">
                System Guide & Documentation
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-ink font-display">
              ReviewPilot Operation Manual
            </h1>
            <p className="text-xs sm:text-sm text-ink-2 leading-relaxed">
              Complete technical walkthrough explaining evidence-grounded pull request reviews, calibrated SLM–LLM routing, and containerized pytest verification.
            </p>
          </div>

          {onNavigate && (
            <ShimmerButton
              onClick={() => onNavigate("overview")}
              className="text-xs font-semibold"
            >
              <span>Back to Dashboard</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </ShimmerButton>
          )}
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-2xl bg-paper-2 border border-rule">
        {[
          { id: "pipeline", label: "Review Pipeline (8 Steps)", icon: Layers },
          { id: "routing", label: "SLM–LLM Routing Formula", icon: Zap },
          { id: "oracle", label: "Test Oracle Protection", icon: Lock },
          { id: "docker", label: "Docker Sandbox Isolation", icon: Server },
          { id: "faq", label: "Frequently Asked Questions", icon: HelpCircle },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all ${
                isActive
                  ? "bg-paper-3 text-ink shadow-sm font-semibold border border-rule"
                  : "text-muted hover:text-ink hover:bg-paper-hover"
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? "text-accent" : ""}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: 8-Step Pipeline */}
      {activeTab === "pipeline" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div
                  key={idx}
                  className="surface-card p-5 space-y-3 relative overflow-hidden group hover:border-accent transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-lg bg-accent-subtle text-accent font-bold">
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="font-mono text-xs font-bold text-accent">
                        STEP {step.num}
                      </span>
                    </div>

                    {onNavigate && (
                      <button
                        onClick={() => onNavigate(step.pageLink)}
                        className="flex items-center gap-1 text-[11px] font-mono text-muted hover:text-accent transition-colors"
                      >
                        <span>{step.linkText}</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  <h3 className="text-sm font-bold text-ink font-display">
                    {step.title}
                  </h3>

                  <p className="text-xs text-ink-2 leading-relaxed">
                    {step.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 2: Routing Formula */}
      {activeTab === "routing" && (
        <div className="space-y-6">
          <div className="surface-card p-6 space-y-4 relative overflow-hidden">
            <BorderBeam size={220} duration={12} colorFrom="#6366f1" colorTo="#06b6d4" />

            <h3 className="text-lg font-bold text-ink font-display">
              Confidence Calibration & Escalation Equation
            </h3>

            <p className="text-xs sm:text-sm text-ink-2 leading-relaxed">
              ReviewPilot does not guess which model to invoke. It computes a calibrated confidence metric that discounts overconfidence on complex code and boosts findings corroborated by static linters.
            </p>

            <div className="p-4 rounded-xl bg-paper-2 border border-rule font-mono text-xs sm:text-sm text-ink leading-relaxed">
              Confidence<sub>calibrated</sub> = (Raw<sub>conf</sub> × 0.40) + (Corroboration × 0.35) − (Complexity<sub>discount</sub> × 0.25)
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono pt-2">
              <div className="p-3 rounded-lg bg-paper-2 border border-rule-subtle">
                <span className="text-muted text-[10px] uppercase block">Raw Confidence (40%)</span>
                <span className="text-ink font-semibold">Self-reported by SLM</span>
              </div>
              <div className="p-3 rounded-lg bg-paper-2 border border-rule-subtle">
                <span className="text-muted text-[10px] uppercase block">Static Corroboration (35%)</span>
                <span className="text-success font-semibold">+0.35 if Ruff/Bandit agrees</span>
              </div>
              <div className="p-3 rounded-lg bg-paper-2 border border-rule-subtle">
                <span className="text-muted text-[10px] uppercase block">McCabe Complexity (25%)</span>
                <span className="text-warning font-semibold">Discounted if complexity &gt; 5</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-accent-subtle/40 border border-accent/30 text-xs space-y-2">
              <span className="font-semibold text-ink font-display">
                Decision Threshold Rule:
              </span>
              <ul className="list-disc list-inside space-y-1 text-ink-2 font-mono text-[11px]">
                <li><strong className="text-success font-semibold">Score &ge; 0.75:</strong> Accepted by local SLM (Ollama). Zero cloud API cost.</li>
                <li><strong className="text-warning font-semibold">Score &lt; 0.75:</strong> Escalated to Cloud LLM with full context.</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Test Oracle Protection */}
      {activeTab === "oracle" && (
        <div className="space-y-6">
          <div className="surface-card p-6 space-y-4">
            <h3 className="text-lg font-bold text-ink font-display flex items-center gap-2">
              <Lock className="w-5 h-5 text-accent" />
              <span>Test Oracle Invariant Protection</span>
            </h3>

            <p className="text-xs sm:text-sm text-ink-2 leading-relaxed">
              Standard LLM-generated tests often cheat: when faced with a failing test, models modify assertions (e.g. changing <code>assert result == expected</code> to <code>assert True</code>) or wrap failures in <code>try/except: pass</code> so tests report passing.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-4 rounded-xl bg-error-bg border border-error/30 space-y-2">
                <span className="text-xs font-bold font-mono text-error uppercase">
                  ✕ Strictly Prohibited & Rejected
                </span>
                <ul className="text-xs text-ink-2 space-y-1 list-disc list-inside">
                  <li>Mutating expected assert values to match buggy output</li>
                  <li>Deleting assertions to avoid test failures</li>
                  <li>Adding <code>try/except: pass</code> blocks that swallow genuine errors</li>
                  <li>Changing function return type comparisons</li>
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-success-bg border border-success/30 space-y-2">
                <span className="text-xs font-bold font-mono text-success uppercase">
                  ✓ Permitted Safe Auto-Repairs
                </span>
                <ul className="text-xs text-ink-2 space-y-1 list-disc list-inside">
                  <li>Adding missing imports (e.g. <code>import pytest</code>)</li>
                  <li>Fixing indentation and syntax errors</li>
                  <li>Instantiating mock fixture parameters</li>
                  <li>Setting up temporary execution files</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Docker Sandbox */}
      {activeTab === "docker" && (
        <div className="space-y-6">
          <div className="surface-card p-6 space-y-4">
            <h3 className="text-lg font-bold text-ink font-display flex items-center gap-2">
              <Server className="w-5 h-5 text-accent" />
              <span>Isolated Execution Sandbox Architecture</span>
            </h3>

            <p className="text-xs sm:text-sm text-ink-2 leading-relaxed">
              Untrusted code and AI-generated tests are never executed on the host system. They are dispatched into isolated ephemeral containers.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono pt-2">
              <div className="p-3 rounded-lg bg-paper-2 border border-rule">
                <span className="text-muted text-[10px] uppercase block">Network</span>
                <span className="text-success font-semibold">--network none</span>
              </div>
              <div className="p-3 rounded-lg bg-paper-2 border border-rule">
                <span className="text-muted text-[10px] uppercase block">Memory Limit</span>
                <span className="text-ink font-semibold">512 MB cgroups</span>
              </div>
              <div className="p-3 rounded-lg bg-paper-2 border border-rule">
                <span className="text-muted text-[10px] uppercase block">CPU Quota</span>
                <span className="text-ink font-semibold">1.0 Core</span>
              </div>
              <div className="p-3 rounded-lg bg-paper-2 border border-rule">
                <span className="text-muted text-[10px] uppercase block">Execution Timeout</span>
                <span className="text-warning font-semibold">15 Seconds</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: FAQ */}
      {activeTab === "faq" && (
        <div className="space-y-4">
          {[
            {
              q: "Can ReviewPilot review PRs without sending private code to external cloud APIs?",
              a: "Yes. When the local SLM achieves a calibrated confidence score >= 0.75, the entire analysis, test generation, and verification completes locally with zero egress to cloud LLMs.",
            },
            {
              q: "What local SLM is used by default?",
              a: "Ollama running `qwen2.5-coder:1.5b`. It is lightweight (986 MB), fast (~80ms prompt evaluation on GPU), and performs targeted Python code reviews.",
            },
            {
              q: "How does ReviewPilot prevent false positives in PR reviews?",
              a: "By grounding every finding in execution evidence: ReviewPilot runs a synthesized pytest test in Docker. If the test cannot reproduce the defect, the finding is suppressed and not reported to GitHub.",
            },
            {
              q: "Can I use ReviewPilot for local diffs without connecting a GitHub account?",
              a: "Yes. Go to 'Repositories' in the sidebar and use the Live Unified Git Diff Ingestion console. You can paste any .diff or .patch file and review it immediately.",
            },
          ].map((item, idx) => (
            <div key={idx} className="surface-card p-5 space-y-2">
              <h4 className="text-sm font-bold text-ink font-display flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-accent" />
                <span>{item.q}</span>
              </h4>
              <p className="text-xs text-ink-2 leading-relaxed pl-6">
                {item.a}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

