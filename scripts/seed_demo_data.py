"""Seed script to ingest real Python PR diffs and populate ReviewPilot database."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database import AsyncSessionLocal, init_db
from backend.app.models.finding import Finding
from backend.app.models.generated_test import GeneratedTest
from backend.app.models.pull_request import PullRequest
from backend.app.models.repository import Repository
from backend.app.models.review_session import ReviewSession
from backend.app.schemas.ai import ReviewRoutingRequest
from backend.app.services.ast_analyzer.extractor import analyze_python_source
from backend.app.services.github.diff_parser import parse_diff
from backend.app.services.router.hybrid_router import HybridModelRouter
from backend.app.services.static_analysis.aggregator import analyze_python_content
from backend.app.services.test_gen.generator import generate_test_from_hypothesis

DIFF_PAYMENT = """diff --git a/services/payment.py b/services/payment.py
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
"""

DIFF_SECURITY = """diff --git a/core/runner.py b/core/runner.py
--- a/core/runner.py
+++ b/core/runner.py
@@ -1,5 +1,9 @@
 import subprocess

 def execute_system_command(user_payload: str) -> int:
+    # Security flaw: subprocess with shell=True on untrusted user_payload
+    proc = subprocess.Popen(user_payload, shell=True)
+    proc.wait()
+    return proc.returncode
"""

DIFF_CLEAN = """diff --git a/utils/formatter.py b/utils/formatter.py
--- a/utils/formatter.py
+++ b/utils/formatter.py
@@ -1,4 +1,8 @@
 def format_user_title(first_name: str, last_name: str) -> str:
+    if not first_name or not last_name:
+        raise ValueError("Names must not be empty")
+    return f"{first_name.strip().title()} {last_name.strip().title()}"
"""


async def seed_data():
    print("Initializing database tables...")
    await init_db()

    router = HybridModelRouter()

    prs_to_ingest = [
        ("octocat/payment-service", 42, "Fix currency discount calculation", DIFF_PAYMENT),
        ("octocat/task-runner", 108, "Add dynamic command execution utility", DIFF_SECURITY),
        ("octocat/common-utils", 215, "Sanitize user names in title formatter", DIFF_CLEAN),
    ]

    async with AsyncSessionLocal() as db:
        for repo_name, pr_num, title, diff_text in prs_to_ingest:
            owner, repo_short = repo_name.split("/")

            # Create or find repo
            repo = Repository(
                name=repo_short,
                owner=owner,
                full_name=repo_name,
                html_url=f"https://github.com/{repo_name}",
                default_branch="main",
            )
            db.add(repo)
            await db.flush()

            # Parse diff
            parsed_diff = parse_diff(diff_text)

            pr = PullRequest(
                repository_id=repo.id,
                pr_number=pr_num,
                title=title,
                state="open",
                author=owner,
                html_url=f"https://github.com/{repo_name}/pull/{pr_num}",
                diff_url=f"https://github.com/{repo_name}/pull/{pr_num}.diff",
                base_branch="main",
                head_branch="feature",
                base_sha="0000000000000000000000000000000000000000",
                head_sha="1111111111111111111111111111111111111111",
                changed_files_count=len(parsed_diff.files),
                raw_diff=diff_text,
            )
            db.add(pr)
            await db.flush()

            review_session = ReviewSession(
                pull_request_id=pr.id,
                status="COMPLETED",
            )
            db.add(review_session)
            await db.flush()

            for modified_file in parsed_diff.python_files:
                code_content = "\n".join(
                    [l.content for hunk in modified_file.hunks for l in hunk.lines if l.line_type in ("add", "context")]
                )
                if not code_content:
                    continue

                # Run AST extraction
                ast_summary = analyze_python_source(
                    file_path=modified_file.filename,
                    source_code=code_content,
                    modified_line_numbers=set(modified_file.added_line_numbers),
                )

                # Run static analysis
                static_report = await analyze_python_content(
                    file_path=modified_file.filename,
                    source_code=code_content,
                    modified_line_numbers=set(modified_file.added_line_numbers),
                )

                for sf in static_report.findings:
                    f = Finding(
                        review_session_id=review_session.id,
                        rule_id=sf.rule_id,
                        tool=sf.tool,
                        category=sf.category,
                        severity=sf.severity,
                        file_path=sf.file_path,
                        line_number=sf.line_number,
                        end_line_number=sf.end_line_number,
                        description=sf.description,
                        confidence=sf.confidence,
                        evidence_status="STATIC_WARNING",
                    )
                    db.add(f)

                # Run Hybrid Model Review
                decision = await router.route_and_review(
                    ReviewRoutingRequest(
                        file_path=modified_file.filename,
                        source_code=code_content,
                        modified_line_numbers=modified_file.added_line_numbers,
                        static_findings=static_report.findings,
                        ast_summary=ast_summary,
                    )
                )

                review_session.slm_calls += 1
                review_session.total_latency_ms += decision.total_latency_ms
                review_session.estimated_cost_usd += decision.total_cost_usd
                if decision.escalation_triggered:
                    review_session.escalated_to_llm = True
                    review_session.llm_calls += 1

                for hyp in decision.final_hypotheses:
                    f = Finding(
                        review_session_id=review_session.id,
                        rule_id=hyp.rule_id,
                        tool=decision.selected_model,
                        category=hyp.category,
                        severity=hyp.severity,
                        file_path=hyp.file_path,
                        line_number=hyp.line_number,
                        end_line_number=hyp.end_line_number,
                        description=hyp.description,
                        confidence=hyp.self_confidence,
                        evidence_status="AI_HYPOTHESIS",
                    )
                    db.add(f)
                    await db.flush()

                    # Generate Test Draft
                    target_func = ast_summary.functions[0].name if ast_summary.functions else "target"
                    test_draft = generate_test_from_hypothesis(hyp, modified_file.filename, target_func)
                    db_test = GeneratedTest(
                        review_session_id=review_session.id,
                        finding_id=f.id,
                        test_name=test_draft.test_name,
                        target_function=target_func,
                        file_path=modified_file.filename,
                        input_values=test_draft.input_values,
                        expected_behavior=test_draft.expected_behavior,
                        reason=test_draft.reason,
                        generator_model=test_draft.generator_model,
                        original_test_code=test_draft.original_test_code,
                        repaired_test_code=test_draft.repaired_test_code,
                        validation_status=test_draft.validation_status,
                    )
                    db.add(db_test)

            await db.commit()
            print(f"Ingested {repo_name} PR #{pr_num} ('{title}') successfully!")

    print("\nDatabase seeding completed with real analysis data!")


if __name__ == "__main__":
    asyncio.run(seed_data())

