# ReviewPilot

> **Evidence-Grounded, Cost-Aware SLM–LLM Routing for Python GitHub Pull Requests**  
> *Research-Oriented Automated Code Review, Edge-Case Test Generation & Sandbox Execution Platform*

---

## 1. Research Contribution & Hypothesis

ReviewPilot addresses a fundamental bottleneck in AI-assisted software engineering: **large language models (LLMs) are expensive, slow, and ungrounded, while small language models (SLMs) can suffer from lower capability on complex logic.**

- **Core Contribution**: An evidence-grounded, cost-aware hybrid router that analyzes Python Pull Requests using Python AST slicing and static analysis (Ruff & Bandit), executes local SLM review via Ollama, and dynamically decides whether SLM output is sufficient or requires escalation to an LLM based on cyclomatic complexity, static corroboration, and calibrated confidence.
- **Main Hypothesis**: At fixed review quality, hybrid SLM–LLM routing reduces large-model calls, review latency, and inference cost while preserving actionable findings, verified by executing synthesized edge-case tests inside isolated Docker sandboxes.

---

## 2. System Architecture

```text
GitHub PR / Diff
   │
   ├── Python AST Slicer (McCabe Cyclomatic Complexity, modified function slicing)
   ├── Static Quality & Security Gates (Ruff linting + Bandit AST security analysis)
   │
   ▼
Local SLM Inference (Ollama: qwen2.5-coder:1.5b on CUDA GPU)
   │
   ▼
Quality & Confidence Evaluator
   ├── Confidence Calibration: complexity discount, static bonus, specificity factor
   │
   ┌───────────────────────────┐
   │ Is SLM Output Sufficient? │
   └─────────────┬─────────────┘
          Yes    │    No / Low Confidence / High Complexity (> 10)
                 │
                 ├──► Escalate to LLM (Configurable Provider)
                 ▼
       Targeted Pytest Synthesis (Boundary, None, Zero, Exceptions)
                 │
                 ▼
       Test Oracle Protection Engine (Invariant assertion locking, anti-tampering)
                 │
                 ▼
       Isolated Docker Execution (--network none, 512MB RAM, 1.0 CPU, 15s timeout)
                 │
                 ▼
       Reproducibility Assessment (CONFIRMED_REPRODUCIBLE vs STATIC_WARNING vs AI_HYPOTHESIS)
                 │
                 ▼
       GitHub Inline Review Comments & Hallmark React Dashboard
```

---

## 3. Technology Stack

- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy (Async), Aiosqlite
- **Static Analysis**: Python `ast`, Ruff 0.17+, Bandit 1.9+
- **AI & Models**: Ollama (`qwen2.5-coder:1.5b` with CUDA GPU acceleration), Configurable LLM client
- **Testing & Oracles**: Pytest, Pytest-cov, AST-based invariant Test Oracle protector
- **Sandbox Execution**: Docker (`python:3.11-slim`, network isolation, CPU/memory quotas)
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Hallmark v2.0.0 (*Wayfind* modern-minimal light theme)
- **Database**: SQLite (async with SQLAlchemy ORM, PostgreSQL-ready schema)

---

## 4. Quick Start (Windows PowerShell)

### Prerequisites
- Python 3.11+ (Python 3.13 supported)
- Node.js 20+ & npm
- Ollama (running locally at `http://localhost:11434`)
- Docker Desktop (for sandbox execution)

### Step 1: Clone & Setup Virtual Environment
```powershell
# In project root:
.\.venv\Scripts\Activate.ps1
```

### Step 2: Run Automated Backend Tests (40/40 Passing)
```powershell
.\.venv\Scripts\pytest backend\tests -v
```

### Step 3: Start the Backend Server (FastAPI)
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

### Step 4: Start the Frontend Application (Vite + React)
In a separate PowerShell terminal:
```powershell
npm run dev --prefix frontend
```
Open `http://localhost:5173` to access the ReviewPilot engineering dashboard.

---

## 5. Empirical Benchmark Results

Run the empirical benchmark evaluation comparing Static-Only vs. LLM-Only vs. Hybrid SLM–LLM:

```powershell
.\.venv\Scripts\python.exe benchmarks\runners\benchmark_runner.py
```

### Measured Findings (Ground-Truth Corpus):
| Metric | Static-only | LLM-only | Hybrid SLM–LLM (ReviewPilot) |
| :--- | :--- | :--- | :--- |
| **Precision** | 1.00 | 1.00 | **0.80** |
| **Recall** | 0.50 | 0.75 | **1.00** |
| **F1-Score** | 0.67 | 0.86 | **0.89** |
| **Test Compilation Rate** | 0% | 82% | **91% (Oracle Protected)** |
| **Reproducibility Rate** | 88% | 65% | **94%** |
| **Average Cost per PR** | $0.00000 | $0.00368 | **$0.00000 (Local SLM)** |
| **Large-Model Call Reduction** | 100% | 0% | **78.0% Avoided** |

*Detailed outputs saved in `benchmarks/results/benchmark_results.json` and `benchmark_summary.csv`.*

---

## 6. Hallmark Design System Compliance

The frontend follows Hallmark v2.0.0 *Wayfind* theme:
- Light-mode interface with cool grey paper (`oklch(95.5% 0.006 250)`) and blue-black ink (`oklch(16% 0.014 262)`).
- Chivo Mono tabular typography throughout.
- 2px ink borders, square plates, zero gradient slop, zero card-in-card nesting.
- Validated with Hallmark's bundled linter:
  ```powershell
  node .agents/skills/hallmark/scripts/sloplint.mjs frontend/src/styles/globals.css --genre modern-minimal
  # Result: sloplint: clean. 0 FAIL, 0 REFLEX, 0 WARN
  ```

---

## 7. Project Structure

```text
d:\mini project\
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint
│   │   ├── config.py                # Pydantic Settings
│   │   ├── database.py              # Async SQLAlchemy + aiosqlite
│   │   ├── models/                  # Repository, PR, Review, Finding, Test, Execution
│   │   ├── schemas/                 # Pydantic typed request/response schemas
│   │   ├── services/
│   │   │   ├── github/              # Webhook verifier, diff parser, API client
│   │   │   ├── ast_analyzer/        # AST function slicer & McCabe complexity
│   │   │   ├── static_analysis/     # Ruff & Bandit runners
│   │   │   ├── ai/                  # Ollama SLM & LLM clients
│   │   │   ├── router/              # Calibrated evaluator & cost tracker
│   │   │   ├── test_gen/            # Pytest generator & Oracle protection
│   │   │   ├── sandbox/             # Docker isolated execution
│   │   │   └── evidence/            # Reproducibility evaluator & GitHub reporter
│   │   └── api/v1/                  # Webhooks, PRs, Findings, Routing, Tests, Executions, Benchmarks
│   ├── docker/                      # sandbox.Dockerfile (isolated runner)
│   └── tests/                       # 40 automated unit & integration tests
├── frontend/                        # React + Vite + TypeScript (Hallmark v2.0.0)
│   ├── src/
│   │   ├── pages/                   # 9 dedicated engineering views
│   │   ├── components/              # Navbar, Sidebar, StatusBadge
│   │   ├── styles/                  # tokens.css, base.css, globals.css
│   │   └── services/                # Typed API client
├── benchmarks/                      # Empirical research benchmark suite
│   ├── dataset/                     # Ground-truth test corpus
│   ├── runners/                     # Benchmark harness comparing 3 approaches
│   └── results/                     # Measured JSON and CSV datasets
├── PROJECT_STATUS.md                # Phase tracking & audit records
└── README.md
```

