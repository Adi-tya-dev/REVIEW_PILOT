import React, { useState } from "react";
import {
  FolderGit2,
  GitBranch,
  Key,
  Plus,
  RefreshCw,
  Send,
  ShieldCheck,
  Code2,
  CheckCircle2,
  Copy,
  ExternalLink,
  ArrowRight,
} from "lucide-react";
import { analyzeLocalDiff } from "../services/api";
import { BorderBeam } from "../components/motion/BorderBeam";
import { ShimmerButton } from "../components/motion/ShimmerButton";

const PRESET_DIFFS = {
  payment: {
    title: "Fix currency discount calculation and edge-case validation",
    diff: `diff --git a/services/payment.py b/services/payment.py
--- a/services/payment.py
+++ b/services/payment.py
@@ -1,8 +1,14 @@
 def calculate_discount(currency: str) -> float:
     if currency == "USD":
         return 0.15
     return 0.0

 def process_payment(amount: float, currency: str) -> float:
+    if amount <= 0:
+        raise ValueError("Invalid amount")
+    discount_ratio = calculate_discount(currency)
+    # Potential Bug: Zero division if currency != 'USD'
+    fee = amount / discount_ratio
+    return fee
`,
  },
  security: {
    title: "Add dynamic shell command execution runner",
    diff: `diff --git a/core/runner.py b/core/runner.py
--- a/core/runner.py
+++ b/core/runner.py
@@ -1,5 +1,9 @@
 import subprocess

 def execute_system_command(user_payload: str) -> int:
+    # Security flaw: subprocess with shell=True on untrusted user_payload
+    proc = subprocess.Popen(user_payload, shell=True)
+    proc.wait()
+    return proc.returncode
`,
  },
  strings: {
    title: "Refactor string formatting helper for user profile",
    diff: `diff --git a/utils/formatters.py b/utils/formatters.py
--- a/utils/formatters.py
+++ b/utils/formatters.py
@@ -1,6 +1,11 @@
 def format_user_display(first_name: str, last_name: str, prefix: str = None) -> str:
+    if not first_name or not last_name:
+        raise ValueError("Name components cannot be empty")
+    if prefix:
+        return f"{prefix} {first_name} {last_name}"
+    return f"{first_name} {last_name}"
`,
  },
};

interface RepositoryManagementProps {
  onSelectPr?: (prId: number) => void;
}

export const RepositoryManagement: React.FC<RepositoryManagementProps> = ({ onSelectPr }) => {
  const [selectedPreset, setSelectedPreset] = useState<"payment" | "security" | "strings">("payment");
  const [diffTitle, setDiffTitle] = useState(PRESET_DIFFS.payment.title);
  const [customDiff, setCustomDiff] = useState(PRESET_DIFFS.payment.diff);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ prId: number; findingsCount: number; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiedWebhook, setCopiedWebhook] = useState(false);

  const handleSelectPreset = (key: "payment" | "security" | "strings") => {
    setSelectedPreset(key);
    setDiffTitle(PRESET_DIFFS[key].title);
    setCustomDiff(PRESET_DIFFS[key].diff);
    setResult(null);
    setError(null);
  };

  const handleSubmitDiff = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await analyzeLocalDiff(diffTitle, customDiff);
      setResult({
        prId: res.pull_request_id,
        findingsCount: res.total_static_findings,
        message: `Pull Request #${res.pull_request_id} created and queued for automated AST, hybrid SLM analysis, and Docker verification!`,
      });
    } catch (err: any) {
      setError(err.message || "Failed to ingest diff.");
    } finally {
      setLoading(false);
    }
  };

  const copyWebhookUrl = () => {
    navigator.clipboard.writeText("http://localhost:8000/api/v1/webhooks/github");
    setCopiedWebhook(true);
    setTimeout(() => setCopiedWebhook(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-ink font-display">
          Repositories & Ingestion
        </h1>
        <p className="text-sm text-ink-2 mt-1">
          Configure real GitHub webhooks or ingest unified git diffs directly into the ReviewPilot engine.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Webhook & Connected Repos */}
        <div className="space-y-6">
          {/* GitHub Webhook Card */}
          <div className="surface-card p-5 space-y-4">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-accent-subtle text-accent">
                <Key className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-semibold text-ink font-display">
                GitHub Webhook Endpoint
              </h3>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              ReviewPilot verifies incoming webhook payloads via HMAC-SHA256 signature against your configured secret.
            </p>

            <div className="space-y-2">
              <label className="text-[11px] font-mono font-medium text-muted uppercase">
                Payload URL
              </label>
              <div className="flex items-center gap-1.5 p-2 rounded-lg bg-paper-2 border border-rule text-xs font-mono text-ink-2">
                <span className="truncate flex-1">
                  http://localhost:8000/api/v1/webhooks/github
                </span>
                <button
                  onClick={copyWebhookUrl}
                  className="p-1 hover:text-accent transition-colors"
                  title="Copy Webhook URL"
                >
                  {copiedWebhook ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-success" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-paper-2 border border-rule-subtle text-xs space-y-1.5">
              <div className="flex justify-between font-mono text-[11px]">
                <span className="text-muted">Content type:</span>
                <span className="text-ink font-medium">application/json</span>
              </div>
              <div className="flex justify-between font-mono text-[11px]">
                <span className="text-muted">Secret verify:</span>
                <span className="text-success font-medium">HMAC SHA-256</span>
              </div>
              <div className="flex justify-between font-mono text-[11px]">
                <span className="text-muted">Event triggers:</span>
                <span className="text-ink font-medium">Pull requests</span>
              </div>
            </div>
          </div>

          {/* Connected Repositories */}
          <div className="surface-card p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-accent" />
                <h3 className="text-sm font-semibold text-ink font-display">
                  Monitored Repositories
                </h3>
              </div>
              <span className="text-xs font-mono text-muted">3 active</span>
            </div>

            <div className="space-y-2">
              {[
                { name: "octocat/payment-service", branch: "main", prs: 1 },
                { name: "octocat/task-runner", branch: "main", prs: 1 },
                { name: "octocat/common-utils", branch: "main", prs: 1 },
              ].map((r, i) => (
                <div
                  key={i}
                  className="p-3 rounded-xl bg-paper-2 border border-rule-subtle flex items-center justify-between text-xs"
                >
                  <div>
                    <div className="font-semibold text-ink font-mono">{r.name}</div>
                    <div className="text-[11px] text-muted flex items-center gap-1 mt-0.5">
                      <GitBranch className="w-3 h-3" />
                      <span>{r.branch}</span>
                    </div>
                  </div>
                  <span className="px-2 py-0.5 text-[10px] font-mono rounded-pill bg-paper-3 border border-rule text-ink-2">
                    {r.prs} PR
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Unified Git Diff Ingestion Console */}
        <div className="lg:col-span-2">
          <div className="surface-card p-6 space-y-6 relative overflow-hidden">
            <BorderBeam size={220} duration={14} colorFrom="#6366f1" colorTo="#06b6d4" />
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-rule">
              <div>
                <h3 className="text-base font-semibold text-ink font-display">
                  Live Unified Git Diff Ingestion
                </h3>
                <p className="text-xs text-muted mt-0.5">
                  Submit a patch to execute the full pipeline offline without configuring remote webhooks.
                </p>
              </div>

              {/* Presets */}
              <div className="flex items-center gap-1.5 p-1 rounded-lg bg-paper-2 border border-rule">
                {(["payment", "security", "strings"] as const).map((key) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleSelectPreset(key)}
                    className={`px-2.5 py-1 text-xs font-medium rounded-md transition-all capitalize ${
                      selectedPreset === key
                        ? "bg-paper-3 text-accent shadow-subtle font-semibold"
                        : "text-muted hover:text-ink"
                    }`}
                  >
                    {key}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmitDiff} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-ink mb-1.5 font-mono">
                  Pull Request Title
                </label>
                <input
                  type="text"
                  value={diffTitle}
                  onChange={(e) => setDiffTitle(e.target.value)}
                  className="w-full px-3.5 py-2 text-xs rounded-lg bg-paper-2 border border-rule focus:border-accent text-ink outline-none transition-colors"
                  placeholder="e.g. Fix currency discount calculation edge-case"
                  required
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-medium text-ink font-mono">
                    Unified Git Diff (.diff / .patch)
                  </label>
                  <span className="text-[11px] font-mono text-muted">
                    {customDiff.split("\n").length} lines
                  </span>
                </div>
                <textarea
                  rows={12}
                  value={customDiff}
                  onChange={(e) => setCustomDiff(e.target.value)}
                  className="w-full p-4 text-xs font-mono rounded-xl bg-paper-2 border border-rule focus:border-accent text-ink outline-none transition-colors leading-relaxed selection:bg-accent-subtle selection:text-accent"
                  required
                />
              </div>

              {/* Feedback Notifications */}
              {result && (
                <div className="p-4 rounded-xl bg-success-bg border border-success/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-2.5 text-success-ink">
                    <CheckCircle2 className="w-4 h-4 shrink-0 text-success" />
                    <span>{result.message}</span>
                  </div>
                  {onSelectPr && (
                    <button
                      type="button"
                      onClick={() => onSelectPr(result.prId)}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-success text-paper font-semibold hover:opacity-90 transition-opacity whitespace-nowrap"
                    >
                      <span>Inspect PR #{result.prId}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              )}

              {error && (
                <div className="p-4 rounded-xl bg-error-bg border border-error/30 text-xs text-error-ink">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <div className="pt-2 flex justify-end">
                <ShimmerButton
                  type="submit"
                  disabled={loading}
                  className="text-xs"
                >
                  <Send className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                  <span>{loading ? "Ingesting & Analyzing..." : "Run Review Pipeline"}</span>
                </ShimmerButton>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
