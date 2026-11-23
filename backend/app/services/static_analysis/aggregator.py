"""Aggregator service running AST extraction, Ruff, and Bandit into a unified report."""

import tempfile
from pathlib import Path
from typing import List, Optional, Set
from backend.app.schemas.findings import StaticAnalysisReport, StaticFinding
from backend.app.services.ast_analyzer.extractor import analyze_python_source
from backend.app.services.static_analysis.bandit_runner import run_bandit_on_path
from backend.app.services.static_analysis.ruff_runner import run_ruff_on_path


async def analyze_python_content(
    file_path: str,
    source_code: str,
    modified_line_numbers: Optional[Set[int]] = None,
) -> StaticAnalysisReport:
    """Run full static analysis (AST, Ruff, Bandit) on in-memory Python content.

    Args:
        file_path: Relative or display path of the file.
        source_code: Complete source code content.
        modified_line_numbers: Set of 1-based line numbers changed in the PR diff.

    Returns:
        Consolidated StaticAnalysisReport.
    """
    if modified_line_numbers is None:
        modified_line_numbers = set()

    all_findings: List[StaticFinding] = []

    # 1. AST Analysis for syntax check
    ast_summary = analyze_python_source(
        file_path=file_path,
        source_code=source_code,
        modified_line_numbers=modified_line_numbers,
    )
    if ast_summary.has_syntax_error:
        all_findings.append(
            StaticFinding(
                rule_id="PYTHON_SYNTAX_ERROR",
                tool="ast",
                category="bug",
                severity="CRITICAL",
                file_path=file_path,
                line_number=1,
                description=ast_summary.syntax_error_message or "Python SyntaxError detected",
                confidence=1.0,
                is_in_diff=True,
            )
        )
        report = StaticAnalysisReport(findings=all_findings)
        report.compute_summary()
        return report

    # 2. Write to temporary file for CLI tool execution
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", encoding="utf-8", delete=False
    ) as temp_file:
        temp_file.write(source_code)
        temp_path = Path(temp_file.name)

    try:
        # Run Ruff
        ruff_findings = await run_ruff_on_path(
            target_path=temp_path,
            modified_line_numbers=modified_line_numbers,
        )
        for rf in ruff_findings:
            rf.file_path = file_path  # Restore original file path
            all_findings.append(rf)

        # Run Bandit
        bandit_findings = await run_bandit_on_path(
            target_path=temp_path,
            modified_line_numbers=modified_line_numbers,
        )
        for bf in bandit_findings:
            bf.file_path = file_path  # Restore original file path
            all_findings.append(bf)

    finally:
        # Clean up temporary file
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass

    # Deduplicate findings on (rule_id, line_number)
    seen = set()
    deduped: List[StaticFinding] = []
    for f in all_findings:
        key = (f.rule_id, f.line_number, f.category)
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    report = StaticAnalysisReport(findings=deduped)
    report.compute_summary()
    return report

