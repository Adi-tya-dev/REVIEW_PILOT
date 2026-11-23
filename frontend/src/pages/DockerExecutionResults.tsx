import React, { useState } from "react";
import {
  AlertCircle,
  Box,
  CheckCircle2,
  Clock,
  Cpu,
  HardDrive,
  Radio,
  Server,
  ShieldCheck,
  Terminal,
  XCircle,
} from "lucide-react";
import { StatusBadge } from "../components/StatusBadge";
import { BorderBeam } from "../components/motion/BorderBeam";

const SAMPLE_EXECUTIONS = [
  {
    id: 1,
    test_name: "test_process_payment_zero_division",
    container_id: "c9b1f482a0d1",
    execution_status: "RUNTIME_EXCEPTION",
    exit_code: 1,
    execution_time_ms: 184,
    exception_name: "ZeroDivisionError",
    exception_details: "float division by zero at services/payment.py:37",
    timeout_reached: false,
    memory_limit: "512 MB",
    cpu_limit: "1.0 core",
    network_mode: "none (isolated)",
    category: "CODE_DEFECT",
    stdout: `============================= test session starts ==============================
platform linux -- Python 3.11.8, pytest-8.1.1, pluggy-1.4.0
rootdir: /sandbox, configfile: pytest.ini
collected 1 item

test_payment.py F                                                        [100%]

=================================== FAILURES ===================================
_________________ test_process_payment_zero_division _________________

    def test_process_payment_zero_division():
        amount = 100.0
        currency = "EUR"
        discount_ratio = calculate_discount(currency)
>       fee = amount / discount_ratio
E       ZeroDivisionError: float division by zero

services/payment.py:37: ZeroDivisionError
============================== 1 failed in 0.18s ===============================
`,
  },
  {
    id: 2,
    test_name: "test_execute_system_command_shell_injection",
    container_id: "7a2e8810cbf3",
    execution_status: "SECURITY_VIOLATION",
    exit_code: 1,
    execution_time_ms: 215,
    exception_name: "SubprocessCallDisallowed",
    exception_details: "Security sandbox intercepted shell=True invocation",
    timeout_reached: false,
    memory_limit: "512 MB",
    cpu_limit: "1.0 core",
    network_mode: "none (isolated)",
    category: "SECURITY_DEFECT",
    stdout: `============================= test session starts ==============================
collected 1 item

test_security.py F                                                       [100%]

=================================== FAILURES ===================================
_____________ test_execute_system_command_shell_injection _____________

>       assert return_code != 0
E       AssertionError: subprocess executed successfully under shell=True!

core/runner.py:7: AssertionError
============================== 1 failed in 0.21s ===============================
`,
  },
  {
    id: 3,
    test_name: "test_format_user_display_clean",
    container_id: "4d9f1a238e55",
    execution_status: "PASS",
    exit_code: 0,
    execution_time_ms: 64,
    exception_name: null,
    exception_details: null,
    timeout_reached: false,
    memory_limit: "512 MB",
    cpu_limit: "1.0 core",
    network_mode: "none (isolated)",
    category: "SAFE",
    stdout: `============================= test session starts ==============================
collected 1 item

test_formatters.py .                                                     [100%]

============================== 1 passed in 0.06s ===============================
`,
  },
];

export const DockerExecutionResults: React.FC = () => {
  const [selectedExec, setSelectedExec] = useState(SAMPLE_EXECUTIONS[0]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-ink font-display">
          Docker Execution Sandbox
        </h1>
        <p className="text-sm text-ink-2 mt-1">
          Isolated containerized test execution with network cutoff, memory limits, and cgroups enforcement.
        </p>
      </div>

      {/* Sandbox Isolation Guarantees Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div className="surface-card p-3.5 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-success-bg text-success">
            <Radio className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-muted">Network</div>
            <div className="text-xs font-semibold text-ink font-mono">--network none</div>
          </div>
        </div>

        <div className="surface-card p-3.5 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-accent-subtle text-accent">
            <HardDrive className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-muted">Memory Limit</div>
            <div className="text-xs font-semibold text-ink font-mono">512 MB (RAM)</div>
          </div>
        </div>

        <div className="surface-card p-3.5 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-accent-subtle text-accent">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-muted">CPU Quota</div>
            <div className="text-xs font-semibold text-ink font-mono">1.0 Cores</div>
          </div>
        </div>

        <div className="surface-card p-3.5 flex items-center gap-3">
          <div className="p-2 rounded-lg bg-warning-bg text-warning-ink">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-muted">Timeout</div>
            <div className="text-xs font-semibold text-ink font-mono">15.0 Seconds</div>
          </div>
        </div>
      </div>

      {/* Main Container View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Execution History */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-semibold text-ink font-display">
              Execution Runs
            </span>
            <span className="text-xs font-mono text-muted">{SAMPLE_EXECUTIONS.length} completed</span>
          </div>

          <div className="space-y-2">
            {SAMPLE_EXECUTIONS.map((ex) => {
              const isSelected = selectedExec.id === ex.id;
              return (
                <div
                  key={ex.id}
                  onClick={() => setSelectedExec(ex)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer text-left select-none ${
                    isSelected
                      ? "bg-accent-subtle/50 border-accent shadow-subtle ring-1 ring-accent/30"
                      : "surface-card hover:border-accent hover:shadow-subtle"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <StatusBadge status={ex.execution_status} />
                    <span className="text-[11px] font-mono text-muted">
                      {ex.execution_time_ms} ms
                    </span>
                  </div>
                  <div className="font-semibold text-xs text-ink font-mono truncate">
                    {ex.test_name}
                  </div>
                  <div className="text-[11px] text-muted font-mono mt-1">
                    Container: {ex.container_id} · Exit code {ex.exit_code}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Terminal Console Log Viewer */}
        <div className="lg:col-span-2 space-y-6">
          <div className="surface-card overflow-hidden relative">
            <BorderBeam size={240} duration={14} colorFrom="#10b981" colorTo="#6366f1" />
            {/* Terminal Top Bar */}
            <div className="p-3 bg-paper-2 border-b border-rule flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-error/70" />
                  <span className="w-2.5 h-2.5 rounded-full bg-warning/70" />
                  <span className="w-2.5 h-2.5 rounded-full bg-success/70" />
                </div>
                <span className="text-xs font-mono font-medium text-ink-2 ml-2">
                  container://{selectedExec.container_id}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="text-muted">Exit: {selectedExec.exit_code}</span>
                <span className="text-muted">·</span>
                <span className="text-ink font-medium">{selectedExec.execution_time_ms} ms</span>
              </div>
            </div>

            {/* Terminal Body */}
            <div className="p-4 bg-paper-2 font-mono text-xs text-ink leading-relaxed overflow-x-auto min-h-[260px]">
              <pre className="whitespace-pre">{selectedExec.stdout}</pre>
            </div>
          </div>

          {/* Classification & Verdict */}
          <div className="surface-card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-accent" />
                <h3 className="text-sm font-semibold text-ink font-display">
                  Execution Output Classification
                </h3>
              </div>
              <StatusBadge status={selectedExec.category} />
            </div>

            <p className="text-xs text-ink-2 leading-relaxed">
              {selectedExec.exception_details || "No runtime exceptions or assertion errors detected. All test assertions passed successfully inside container."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
