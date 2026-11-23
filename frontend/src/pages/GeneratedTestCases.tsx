import React, { useState } from "react";
import {
  Check,
  CheckCircle2,
  Code2,
  Copy,
  FileCheck2,
  Lock,
  ShieldCheck,
  Terminal,
  Zap,
} from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { BorderBeam } from "../components/motion/BorderBeam";

const SAMPLE_GENERATED_TESTS = [
  {
    id: 1,
    test_name: "test_process_payment_zero_division",
    target_function: "process_payment",
    file_path: "services/payment.py",
    input_values: 'amount=100.0, currency="EUR"',
    expected_behavior: "Safe handling of 0 discount ratio without ZeroDivisionError",
    reason: "Verifies division by zero risk flagged by SLM at line 37",
    generator_model: "qwen2.5-coder:1.5b (SLM)",
    validation_status: "VALID",
    assertions_count: 1,
    anti_tampering_status: "PASSED",
    code: `import pytest
from services.payment import process_payment

def test_process_payment_zero_division():
    """Reproduction test for ZERO_DIVISION in process_payment"""
    # When currency has no discount (0.0 ratio), payment calculation must not throw ZeroDivisionError
    fee = process_payment(100.0, "EUR")
    assert fee >= 0.0
`,
  },
  {
    id: 2,
    test_name: "test_execute_system_command_shell_injection",
    target_function: "execute_system_command",
    file_path: "core/runner.py",
    input_values: 'user_payload="; cat /etc/passwd"',
    expected_behavior: "Command should not execute through subshell",
    reason: "Corroborated by Bandit rule B602 (subprocess with shell=True)",
    generator_model: "qwen2.5-coder:1.5b (SLM)",
    validation_status: "SAFE_REPAIR",
    assertions_count: 1,
    anti_tampering_status: "PASSED",
    code: `import pytest
from core.runner import execute_system_command

def test_execute_system_command_shell_injection():
    """Verify system command runner prevents shell injection attacks"""
    return_code = execute_system_command("; echo 1")
    assert return_code != 0
`,
  },
  {
    id: 3,
    test_name: "test_format_user_display_empty_name",
    target_function: "format_user_display",
    file_path: "utils/formatters.py",
    input_values: 'first_name="", last_name=""',
    expected_behavior: "Raises ValueError on empty name strings",
    reason: "Boundary edge case on input verification",
    generator_model: "Cloud LLM (Escalated)",
    validation_status: "VALID",
    assertions_count: 1,
    anti_tampering_status: "PASSED",
    code: `import pytest
from utils.formatters import format_user_display

def test_format_user_display_empty_name():
    """Verify empty first and last name triggers ValueError exception"""
    with pytest.raises(ValueError, match="cannot be empty"):
        format_user_display("", "")
`,
  },
];

export const GeneratedTestCases: React.FC = () => {
  const [tests, setTests] = useState(SAMPLE_GENERATED_TESTS);
  const [selectedTest, setSelectedTest] = useState(SAMPLE_GENERATED_TESTS[0]);
  const [copied, setCopied] = useState(false);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(selectedTest.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-ink font-display">
          Generated Test Cases & Oracle Protection
        </h1>
        <p className="text-sm text-ink-2 mt-1">
          Automated pytest test generation with invariant Test Oracle validation: assertions are locked against mutation or deletion.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Test Case Selector List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-semibold text-muted uppercase tracking-wider font-mono">
              Synthesized Test Suites
            </span>
            <span className="text-xs font-mono text-muted">{tests.length} tests</span>
          </div>

          <div className="space-y-2">
            {tests.map((t) => {
              const isSelected = selectedTest.id === t.id;
              return (
                <div
                  key={t.id}
                  onClick={() => setSelectedTest(t)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer text-left select-none ${
                    isSelected
                      ? "bg-accent-subtle/50 border-accent shadow-subtle ring-1 ring-accent/30"
                      : "surface-card hover:border-accent hover:shadow-subtle"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <StatusBadge status={t.validation_status} />
                    <span className="text-[11px] font-mono text-muted">
                      {t.generator_model.split(" ")[0]}
                    </span>
                  </div>
                  <div className="font-semibold text-xs text-ink font-mono truncate">
                    {t.test_name}
                  </div>
                  <div className="text-[11px] text-muted font-mono mt-1 truncate">
                    Target: {t.target_function}() in {t.file_path}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Code & Oracle Protection Inspector */}
        <div className="lg:col-span-2 space-y-6">
          {/* Test Oracle Guard Banner */}
          <div className="surface-card p-5 space-y-3">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-success-bg text-success">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-ink font-display">
                    Test Oracle Protection Guard
                  </h3>
                  <p className="text-xs text-muted">
                    AST invariant locking prevents AI models from weakening assertions.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="flex items-center gap-1 text-success font-medium">
                  <Lock className="w-3.5 h-3.5" />
                  Assertions Locked
                </span>
                <span className="text-muted">·</span>
                <span className="text-ink-2">
                  {selectedTest.assertions_count} invariant assert
                </span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-paper-2 border border-rule-subtle grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
              <div>
                <span className="text-muted text-[10px] uppercase">Framework</span>
                <div className="font-semibold text-ink">pytest</div>
              </div>
              <div>
                <span className="text-muted text-[10px] uppercase">Syntax Valid</span>
                <div className="font-semibold text-success">Verified</div>
              </div>
              <div>
                <span className="text-muted text-[10px] uppercase">Anti-Tamper</span>
                <div className="font-semibold text-success">Passed</div>
              </div>
              <div>
                <span className="text-muted text-[10px] uppercase">Auto Repair</span>
                <div className="font-semibold text-ink">Imports Safe</div>
              </div>
            </div>
          </div>

          {/* Pytest Code Viewer */}
          <div className="surface-card overflow-hidden relative">
            <BorderBeam size={220} duration={14} colorFrom="#6366f1" colorTo="#06b6d4" />
            <div className="p-4 bg-paper-2 border-b border-rule flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-accent" />
                <span className="text-xs font-mono font-semibold text-ink">
                  {selectedTest.test_name}.py
                </span>
              </div>
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-paper-3 hover:bg-paper text-ink text-xs font-mono border border-rule transition-colors shadow-subtle"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? "Copied" : "Copy Test"}</span>
              </button>
            </div>

            <div className="p-4 bg-paper-3 font-mono text-xs text-ink-2 leading-relaxed overflow-x-auto">
              <pre className="whitespace-pre">{selectedTest.code}</pre>
            </div>
          </div>

          {/* Test Hypothesis Context */}
          <div className="surface-card p-5 space-y-2 text-xs">
            <span className="text-[11px] font-mono font-semibold text-muted uppercase tracking-wider">
              Reproduction Objective
            </span>
            <p className="text-ink-2 leading-relaxed font-sans">
              {selectedTest.reason}. Expected behavior: <span className="font-mono text-ink">{selectedTest.expected_behavior}</span>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
