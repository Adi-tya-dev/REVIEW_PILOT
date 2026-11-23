import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Bug,
  ChevronDown,
  ChevronRight,
  FileCode2,
  GitBranch,
  GitCommit,
  GitPullRequest,
  RefreshCw,
  ShieldAlert,
  Terminal,
} from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { PageId } from "../components/Sidebar";
import { fetchPullRequestDetails, fetchPullRequests } from "../services/api";
import { PullRequest } from "../types";
import { BorderBeam } from "../components/motion/BorderBeam";

interface PullRequestReviewProps {
  initialPrId?: number | null;
  onNavigate?: (page: PageId) => void;
}

export const PullRequestReview: React.FC<PullRequestReviewProps> = ({
  initialPrId,
  onNavigate,
}) => {
  const [prs, setPrs] = useState<PullRequest[]>([]);
  const [selectedPrId, setSelectedPrId] = useState<number | null>(initialPrId || null);
  const [prDetails, setPrDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPullRequests()
      .then((data) => {
        setPrs(data);
        if (!selectedPrId && data.length > 0) {
          setSelectedPrId(data[0].id);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (initialPrId) {
      setSelectedPrId(initialPrId);
    }
  }, [initialPrId]);

  useEffect(() => {
    if (!selectedPrId) return;
    setLoading(true);
    fetchPullRequestDetails(selectedPrId)
      .then((data) => setPrDetails(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [selectedPrId]);

  const activePr = prs.find((p) => p.id === selectedPrId);

  // Render unified diff lines with GitHub-style styling
  const renderDiffLines = (diffText: string) => {
    if (!diffText) return null;
    const lines = diffText.split("\n");

    return (
      <div className="font-mono text-xs leading-relaxed overflow-x-auto divide-y divide-rule-subtle">
        {lines.map((line, idx) => {
          let lineType = "context";
          let bgClass = "hover:bg-paper-2";
          let textClass = "text-ink-2";

          if (line.startsWith("+") && !line.startsWith("+++")) {
            lineType = "add";
            bgClass = "diff-add font-medium";
            textClass = "text-[var(--color-diff-add-text)]";
          } else if (line.startsWith("-") && !line.startsWith("---")) {
            lineType = "del";
            bgClass = "diff-del";
            textClass = "text-[var(--color-diff-del-text)]";
          } else if (line.startsWith("@@")) {
            lineType = "hunk";
            bgClass = "bg-accent-subtle/50 text-accent font-semibold";
            textClass = "text-accent";
          }

          return (
            <div key={idx} className={`flex items-stretch py-1 px-3 ${bgClass}`}>
              <span className="w-10 shrink-0 text-right pr-4 text-muted select-none text-[11px]">
                {idx + 1}
              </span>
              <span className="w-4 shrink-0 select-none font-bold">
                {line.startsWith("+") && !line.startsWith("+++")
                  ? "+"
                  : line.startsWith("-") && !line.startsWith("---")
                  ? "-"
                  : " "}
              </span>
              <span className={`flex-1 whitespace-pre ${textClass}`}>{line}</span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header with PR Selector */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-rule">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-ink font-display">
              Pull Request Inspection
            </h1>
            {activePr && <StatusBadge status={activePr.state || "OPEN"} />}
          </div>
          <p className="text-sm text-ink-2 mt-1">
            Structured unified diff, AST sliced functions, and localized defect hypotheses.
          </p>
        </div>

        {prs.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-muted">Switch PR:</span>
            <select
              value={selectedPrId || ""}
              onChange={(e) => setSelectedPrId(Number(e.target.value))}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-paper-3 border border-rule text-ink outline-none focus:border-accent shadow-subtle cursor-pointer"
            >
              {prs.map((p) => (
                <option key={p.id} value={p.id}>
                  #{p.pr_number} - {p.title.slice(0, 32)}...
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading ? (
        <div className="surface-card p-12 text-center text-muted font-mono text-xs">
          Loading pull request review session...
        </div>
      ) : !prDetails ? (
        <div className="surface-card p-12 text-center text-muted">
          No pull request selected or found.
        </div>
      ) : (
        <div className="space-y-6">
          {/* PR Metadata Strip */}
          <div className="surface-card p-5">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-ink font-display">
                  #{prDetails.pr_number} {prDetails.title}
                </h2>
                <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-muted mt-2">
                  <span className="text-ink-2">by {prDetails.author}</span>
                  <span className="flex items-center gap-1">
                    <GitBranch className="w-3.5 h-3.5" />
                    <span>{prDetails.head_branch}</span>
                    <span>→</span>
                    <span>{prDetails.base_branch}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <GitCommit className="w-3.5 h-3.5" />
                    <span>{prDetails.head_sha.slice(0, 7)}</span>
                  </span>
                </div>
              </div>

              {/* Review Session Stats Pill */}
              {prDetails.review_session && (
                <div className="flex items-center gap-4 p-3 rounded-xl bg-paper-2 border border-rule-subtle text-xs font-mono">
                  <div>
                    <div className="text-muted text-[10px] uppercase">Latency</div>
                    <div className="font-semibold text-ink">
                      {prDetails.review_session.total_latency_ms} ms
                    </div>
                  </div>
                  <div className="border-l border-rule pl-4">
                    <div className="text-muted text-[10px] uppercase">Routing</div>
                    <div className="font-semibold text-accent">
                      {prDetails.review_session.escalated_to_llm ? "LLM Escalated" : "SLM Direct"}
                    </div>
                  </div>
                  <div className="border-l border-rule pl-4">
                    <div className="text-muted text-[10px] uppercase">Cost</div>
                    <div className="font-semibold text-ink">
                      ${prDetails.review_session.estimated_cost_usd?.toFixed(4) || "0.0000"}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Unified Diff Viewer */}
          <div className="surface-card overflow-hidden relative">
            <BorderBeam size={220} duration={14} colorFrom="#6366f1" colorTo="#06b6d4" />
            <div className="p-4 bg-paper-2 border-b border-rule flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCode2 className="w-4 h-4 text-accent" />
                <span className="text-xs font-mono font-semibold text-ink">
                  services/payment.py
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-pill bg-paper-3 text-muted border border-rule">
                  Python Diff
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="text-success font-medium">+6 additions</span>
                <span className="text-muted">·</span>
                <span className="text-error font-medium">-1 deletions</span>
              </div>
            </div>

            {/* Code Diff Display */}
            {renderDiffLines(prDetails.raw_diff)}
          </div>

          {/* Findings & Hypotheses List */}
          <div className="surface-card p-6">
            <div className="flex items-center justify-between pb-4 border-b border-rule mb-4">
              <div className="flex items-center gap-2">
                <Bug className="w-4 h-4 text-accent" />
                <h3 className="text-base font-semibold text-ink font-display">
                  Identified Findings & Hypotheses
                </h3>
              </div>
              <span className="text-xs font-mono text-muted">
                {prDetails.findings?.length || 0} findings recorded
              </span>
            </div>

            {prDetails.findings?.length === 0 ? (
              <div className="text-center py-8 text-muted text-xs font-mono">
                No defects or vulnerabilities detected in this patch.
              </div>
            ) : (
              <div className="space-y-3">
                {prDetails.findings?.map((f: any) => (
                  <div
                    key={f.id}
                    className="p-4 rounded-xl bg-paper-2 border border-rule-subtle hover:border-accent transition-colors flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
                  >
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-accent">
                          {f.rule_id}
                        </span>
                        <StatusBadge status={f.evidence_status} />
                        <span className="text-[11px] font-mono text-muted">
                          {f.file_path}:{f.line_number}
                        </span>
                      </div>
                      <p className="text-xs text-ink-2 leading-relaxed font-sans">
                        {f.description}
                      </p>
                      <div className="flex items-center gap-3 text-[11px] font-mono text-muted">
                        <span>Source: {f.tool}</span>
                        <span>·</span>
                        <span>Confidence: {(f.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </div>

                    {onNavigate && (
                      <button
                        onClick={() => onNavigate("test-cases")}
                        className="px-3 py-1.5 rounded-lg bg-paper-3 hover:bg-accent hover:text-accent-ink text-xs font-medium border border-rule text-ink-2 transition-colors flex items-center gap-1 shrink-0"
                      >
                        <span>View Generated Test</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
