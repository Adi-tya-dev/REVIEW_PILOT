# ReviewPilot – Project Status & Implementation Plan

> **Evidence-Grounded, Cost-Aware SLM–LLM Routing for Python GitHub Pull Requests**  
> *Research-oriented Automated Code Review & Test Generation Platform*

---

## 1. Project Overview & Research Hypothesis

- **Core Contribution**: Intelligently route Python Pull Request review tasks between a Small Language Model (SLM) and a Large Language Model (LLM) based on AST complexity, static analysis signals, and calibrated confidence, backed by Dockerized execution evidence.
- **Main Hypothesis**: At a fixed review quality (precision/recall of actionable defects), hybrid SLM–LLM routing reduces large-model calls, latency, and inference cost while preserving actionable findings, demonstrated through rigorous empirical benchmarking.

---

## 2. Environment Status & Toolchain Audit

| Tool | Version / Status | Notes |
| :--- | :--- | :--- |
| **Python** | 3.13.9 | Active virtual environment at `.venv` |
| **Node.js** | 24.11.0 | Frontend build verified (Vite v6.4.5, React 18, TypeScript 5.6) |
| **npm** | 11.6.2 | All frontend dependencies installed without vulnerabilities (`framer-motion` integrated) |
| **Git** | 2.54.0.windows.1 | Initialized repository |
| **Ruff** | 0.17.4 | Installed in `.venv`, integrated into static analysis pipeline |
| **Bandit** | 1.9.4 | Installed in `.venv`, integrated into security pipeline |
| **Ollama** | 0.40.15 | Installed with CUDA GPU acceleration (`$env:LOCALAPPDATA\Programs\Ollama\ollama.exe`) |
| **Active SLM Model**| `qwen2.5-coder:1.5b` | Downloaded, verified with live inference (1.5B params, GGUF Q4_K_M) |
| **pytest** | 9.2.0 | **40/40 tests passing** (`backend/tests/`) across all test suites |
| **Docker Engine** | 29.8.0 CLI installed | `sandbox.Dockerfile` built; Docker runner & classifier operational |
| **Hallmark Skill**| v2.0.0 (`.agents/skills/hallmark`) | Verified via `sloplint.mjs`: **clean (0 FAIL, 0 REFLEX, 0 WARN)** |

---

## 3. Priority Progress & Verification Records

| Priority | Description | Status | Evidence / Test Verification |
| :--- | :--- | :--- | :--- |
| **Priority 1: Real GitHub PR Integration** | Webhook HMAC-SHA256 signature verification, unified git diff parser, line-mapping, async GitHub REST client, local & remote PR ingestion | ✅ **COMPLETED** | Tested in `test_webhook_verification.py`, `test_diff_parser.py`, `test_api_endpoints.py` |
| **Priority 2: Static Code Analysis** | Python AST parser (McCabe complexity, function slicer, decorator/docstring/type extraction), Ruff linting & bug detection, Bandit security analyzer | ✅ **COMPLETED** | Tested in `test_ast_extractor.py`, `test_static_analysis.py` on real vulnerable Python code (B602, B307, F821 detected) |
| **Priority 3: SLM–LLM Hybrid Routing** | Ollama local SLM inference (`qwen2.5-coder:1.5b` running via CUDA), LLM fallback, calibrated confidence scoring, AST/static escalation heuristics, cost/latency tracking | ✅ **COMPLETED** | Tested in `test_router.py` (9 tests passing) + live local model inference verified |
| **Priority 4: Test Generation & Oracle Protection** | Targeted edge-case pytest generator, Test Oracle protection (lock assertions, no mutation to pass, anti-suppression), safe scaffolding repairs | ✅ **COMPLETED** | Tested in `test_oracle_protection.py` (7 tests passing) |
| **Priority 5: Docker Sandbox & Reproducibility** | Ephemeral Docker container execution (`--network none`, 512MB, 1.0 CPU, 15s), result classifier (`PASS`, `ASSERTION_FAILURE`, `RUNTIME_EXCEPTION`, `TEST_SYNTAX_ERROR`, `TEST_IMPORT_ERROR`, `TIMEOUT`), evidence evaluator, GitHub inline review formatter | ✅ **COMPLETED** | Tested in `test_docker_execution.py` (9 tests passing) |
| **Priority 6: Hallmark-Designed Frontend (Animated Redesign)** | Premium modern AI developer platform redesign (Linear/Refero/Hallmark v2.0.0 inspired): Albert Sans display + Inter body + JetBrains Mono code, refined 20px intentional canvas dot grid, compact Linear-style operational command header, unified solid Royal Indigo primary buttons, compact 4-card metric grid, precision dual-segment SLM–LLM workload allocation bar (Royal Indigo + Muted Violet), independent scrolling architecture, and full Hallmark compliance | ✅ **COMPLETED** | `npm run build` passed in 8.22s; `sloplint: clean. 0 FAIL, 0 REFLEX, 0 WARN` |
| **Priority 7: Experimental Evaluation** | Empirical benchmarking: Static-only vs LLM-only vs Hybrid SLM–LLM on precision, recall, F1, cost, latency | ✅ **COMPLETED** | Benchmark runner executed; real results saved to `benchmark_results.json` & `benchmark_summary.csv` |

---

## 4. Test Execution Summary

```text
============================= 40 passed in 8.10s ==============================
- backend/tests/test_api_endpoints.py (3 passed)
- backend/tests/test_ast_extractor.py (2 passed)
- backend/tests/test_benchmarks.py (1 passed)
- backend/tests/test_diff_parser.py (3 passed)
- backend/tests/test_docker_execution.py (9 passed)
- backend/tests/test_oracle_protection.py (7 passed)
- backend/tests/test_router.py (9 passed)
- backend/tests/test_static_analysis.py (1 passed)
- backend/tests/test_webhook_verification.py (5 passed)
```

---

## 5. Frontend Redesign Highlights (Hallmark v2.0.0)

1. **Design System & Elevation**: Replaced rigid brutalist borders with soft surfaces (`--color-paper: oklch(98.8% 0.003 260)`), subtle rounded elevations (`--radius-card: 14px`, `--shadow-card`), and Linear-inspired indigo accents (`--color-accent: oklch(52% 0.23 265)`).
2. **Typography**: Paired Google Fonts `Albert Sans` (display headers), `Inter` (body prose), and `JetBrains Mono` (code diffs and AST tables).
3. **Animated AI Workflow (`WorkflowPipeline.tsx`)**: Signature 12-stage interactive visualization covering GitHub PR → AST Slicer → Ruff + Bandit → SLM Review → Quality Evaluation → SLM Sufficient? Branch (Direct SLM vs LLM Escalation) → Test Generation → Oracle Validation → Docker Execution → pytest Results → Reproducibility Check → GitHub Reporting. Features live execution time badges, playback controls, and stage inspection drawer.
4. **All 9 Pages Fully Redesigned**:
   - `OverviewDashboard.tsx`: Animated KPI count-up metrics, hybrid model distribution bar, embedded workflow pipeline, real ingested PR queue.
   - `RepositoryManagement.tsx`: Webhook endpoint instructions with copy helper, connected repositories list, unified git diff ingestion with presets (payment, security, strings).
   - `PullRequestReview.tsx`: GitHub-style unified diff viewer with addition/deletion styling, commit metadata strip, inline defect hypotheses.
   - `StaticAnalysis.tsx`: Dual-pane editor with live snippet testing, AST function extraction table, McCabe complexity indicators, and category-filtered Ruff & Bandit findings.
   - `AIModelRouting.tsx`: Live code slice testing console, mathematical calibration formula visualizer, latency and cost breakdown.
   - `GeneratedTestCases.tsx`: Test Oracle invariant protection guard with assertion lock indicators, copy-ready pytest code viewer.
   - `DockerExecutionResults.tsx`: Sandbox isolation guarantee indicators (`--network none`, 512MB RAM, 1.0 CPU), macOS-styled terminal console with pytest tracebacks.
   - `ReproducibilityEvidence.tsx`: Side-by-side evidence triad (code slice vs generated test vs container output) and GitHub inline comment payload preview.
   - `BenchmarkComparison.tsx`: Three breakthrough metric banners, animated horizontal comparative performance bars, and scientific metric comparison matrix.
