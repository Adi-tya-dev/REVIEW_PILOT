import React from "react";

interface StatusBadgeProps {
  status: string;
  className?: string;
  showDot?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className = "",
  showDot = true,
}) => {
  const norm = status.toUpperCase().replace(/\s+/g, "_");

  let containerClass = "bg-paper-2 text-ink-2 border-rule";
  let dotClass = "bg-muted";

  if (norm.includes("CONFIRMED") || norm.includes("CRITICAL") || norm.includes("DEFECT") || norm.includes("FAIL")) {
    containerClass = "bg-error-bg text-error-ink border-error/30";
    dotClass = "bg-error";
  } else if (norm.includes("PASS") || norm.includes("VALID") || norm.includes("SAFE") || norm.includes("COMPLETED")) {
    containerClass = "bg-success-bg text-success-ink border-success/30";
    dotClass = "bg-success";
  } else if (norm.includes("WARN") || norm.includes("HIGH") || norm.includes("ESCALAT") || norm.includes("ASSERTION")) {
    containerClass = "bg-warning-bg text-warning-ink border-warning/30";
    dotClass = "bg-warning";
  } else if (norm.includes("SLM") || norm.includes("OPEN") || norm.includes("ACTIVE") || norm.includes("ROUTED")) {
    containerClass = "bg-accent-subtle text-accent border-accent/25";
    dotClass = "bg-accent";
  } else if (norm.includes("LLM")) {
    containerClass = "bg-accent-subtle text-accent-hover border-accent/40 font-semibold";
    dotClass = "bg-accent";
  } else if (norm.includes("TIMEOUT") || norm.includes("ERROR") || norm.includes("TAMPER")) {
    containerClass = "bg-error-bg text-error-ink border-error/40";
    dotClass = "bg-error";
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-pill border ${containerClass} ${className}`}
    >
      {showDot && <span className={`w-1.5 h-1.5 rounded-full ${dotClass} animate-pulse`} />}
      <span>{status}</span>
    </span>
  );
};
