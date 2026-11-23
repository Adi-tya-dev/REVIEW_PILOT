import React, { useState } from "react";
import {
  CheckCircle2,
  Code2,
  ExternalLink,
  FileSearch,
  MessageSquare,
  Send,
  ShieldAlert,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { BorderBeam } from "../components/motion/BorderBeam";

const SAMPLE_EVIDENCE_CASES = [
  {
    id: 1,
    rule_id: "ZERO_DIVISION",
    status: "CONFIRMED_REPRODUCIBLE",
    confidence_score: 0.98,
    file_path: "services/payment.py",
    line_number: 37,
    description: "Division by zero occurs when currency discount ratio returns 0.0 for non-USD currencies.",
    input_trigger: 'process_payment(100.0, "EUR")',
    expected_behavior: "Safe handling of 0 discount ratio without ZeroDivisionError crash",
    actual_output: "ZeroDivisionError: float division by zero",
    reproduction_evidence: "Verified inside Docker container c9b1f482a0d1 (Exit code 1, reproducible in 0.18s)",
    source_snippet: `35 |     discount_ratio = calculate_discount(currency)
36 |     # Potential Bug: Zero division if currency != 'USD'
37 |     fee = amount / discount_ratio`,
    generated_test_snippet: `def test_process_payment_zero_division():
    amount = 100.0
    currency = "EUR"
    discount_ratio = calculate_discount(currency)
    fee = amount / discount_ratio
    assert fee >= 0.0`,
    github_comment_preview: `### ⚠️ ReviewPilot Finding: Potential ZeroDivisionError Detected

**Location**: \`services/payment.py:37\`
**Rule**: \`ZERO_DIVISION\` (Severity: HIGH)
**Confidence**: 98% (Corroborated by Docker execution)

#### Concrete Execution Evidence:
A targeted edge-case test (\`test_process_payment_zero_division\`) was synthesized and executed in an isolated Docker container with zero network egress:

\`\`\`python
# Reproduction input:
fee = process_payment(amount=100.0, currency="EUR")
\`\`\`

**Actual Container Output:**
\`\`\`text
ZeroDivisionError: float division by zero at services/payment.py:37
\`\`\`

#### Suggested Fix:
Add a safeguard check before performing division:
\`\`\`python
if discount_ratio <= 0.0:
    fee = amount  # or appropriate fallback
else:
    fee = amount / discount_ratio
\`\`\`
`,
  },
  {
    id: 2,
    rule_id: "B602_SHELL_INJECTION",
    status: "STATIC_WARNING",
    confidence_score: 0.95,
    file_path: "core/runner.py",
    line_number: 5,
    description: "subprocess call with shell=True on untrusted user argument identified by Bandit AST visitor.",
    input_trigger: 'execute_system_command("; id")',
    expected_behavior: "Commands must be passed as argument vectors without shell execution",
    actual_output: "Bandit AST rule trigger B602 (Confidence: HIGH)",
    reproduction_evidence: "Corroborated by Bandit AST rule B602",
    source_snippet: `4 | def execute_system_command(user_payload: str) -> int:
5 |     proc = subprocess.Popen(user_payload, shell=True)`,
    generated_test_snippet: `# Static analysis corroborated prior to model escalation
proc = subprocess.Popen(user_payload, shell=False)`,
    github_comment_preview: `### 🛡️ ReviewPilot Finding: Shell Injection Vulnerability (B602)

**Location**: \`core/runner.py:5\`
**Rule**: \`Bandit B602\` (Severity: HIGH)

\`subprocess.Popen\` invoked with \`shell=True\`. Untrusted input in \`user_payload\` can lead to arbitrary command execution. Replace with list argument vector.`,
  },
];

export const ReproducibilityEvidence: React.FC = () => {
  const [selectedCase, setSelectedCase] = useState(SAMPLE_EVIDENCE_CASES[0]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-ink font-display">
          Reproducibility & Evidence Assessment
        </h1>
        <p className="text-sm text-ink-2 mt-1">
          Every reported defect is grounded in concrete execution evidence, distinguishing verified defects from speculative hypotheses.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Evidence Case List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-semibold text-muted uppercase tracking-wider font-mono">
              Evidence Cases
            </span>
            <span className="text-xs font-mono text-muted">{SAMPLE_EVIDENCE_CASES.length} cases</span>
          </div>

          <div className="space-y-2">
            {SAMPLE_EVIDENCE_CASES.map((c) => {
              const isSelected = selectedCase.id === c.id;
              return (
                <div
                  key={c.id}
                  onClick={() => setSelectedCase(c)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer text-left select-none ${isSelected
                    ? "bg-accent-subtle/50 border-accent shadow-subtle ring-1 ring-accent/30"
                    : "surface-card hover:border-accent hover:shadow-subtle"
                    }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <StatusBadge status={c.status} />
                    <span className="text-[11px] font-mono text-muted">
                      {(c.confidence_score * 100).toFixed(0)}% conf
                    </span>
                  </div>
                  <div className="font-semibold text-xs text-ink font-mono truncate">
                    {c.rule_id}
                  </div>
                  <div className="text-[11px] text-muted font-mono mt-1 truncate">
                    {c.file_path}:{c.line_number}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Grounded Evidence Triad & GitHub Comment Preview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Grounding Header Card */}
          <div className="surface-card p-5 space-y-3">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-success-bg text-success">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-ink font-display">
                    {selectedCase.rule_id} · Grounded Execution Evidence
                  </h3>
                  <p className="text-xs text-muted">
                    {selectedCase.file_path}:{selectedCase.line_number}
                  </p>
                </div>
              </div>
              <StatusBadge status={selectedCase.status} />
            </div>

            <p className="text-xs text-ink-2 leading-relaxed">
              {selectedCase.description}
            </p>

            <div className="p-3 rounded-lg bg-paper-2 border border-rule-subtle text-xs font-mono text-ink-2">
              <span className="text-muted">Evidence Provenance: </span>
              {selectedCase.reproduction_evidence}
            </div>
          </div>

          {/* Triad: Code Slice vs Generated Test vs Container Output */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Box 1: Code Slice */}
            <div className="surface-card p-4 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-ink font-display">
                <Code2 className="w-3.5 h-3.5 text-accent" />
                <span>1. Modified Python Code</span>
              </div>
              <div className="p-3 rounded-lg bg-paper-2 border border-rule font-mono text-[11px] text-ink-2 overflow-x-auto">
                <pre className="whitespace-pre">{selectedCase.source_snippet}</pre>
              </div>
            </div>

            {/* Box 2: Synthesized Test */}
            <div className="surface-card p-4 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-ink font-display">
                <Terminal className="w-3.5 h-3.5 text-accent" />
                <span>2. Synthesized pytest Test</span>
              </div>
              <div className="p-3 rounded-lg bg-paper-2 border border-rule font-mono text-[11px] text-ink-2 overflow-x-auto">
                <pre className="whitespace-pre">{selectedCase.generated_test_snippet}</pre>
              </div>
            </div>
          </div>

          {/* Box 3: GitHub Inline Review Comment Formatter */}
          <div className="surface-card p-6 space-y-4 relative overflow-hidden">
            <BorderBeam size={240} duration={14} colorFrom="#10b981" colorTo="#6366f1" />
            <div className="flex items-center justify-between pb-3 border-b border-rule">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-accent" />
                <h3 className="text-sm font-semibold text-ink font-display">
                  GitHub Inline Review Comment Payload
                </h3>
              </div>
              <span className="text-xs font-mono text-muted">
                Line {selectedCase.line_number}
              </span>
            </div>

            <div className="p-4 rounded-xl bg-paper-2 border border-rule text-xs font-mono text-ink-2 leading-relaxed overflow-x-auto">
              <pre className="whitespace-pre-wrap">{selectedCase.github_comment_preview}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
