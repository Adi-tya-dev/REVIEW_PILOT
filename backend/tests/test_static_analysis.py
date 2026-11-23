"""Integration tests executing Ruff and Bandit against real Python defect fixtures."""

import pytest
from backend.app.services.static_analysis.aggregator import analyze_python_content

# Code with both Ruff (F821 undefined variable) and Bandit (B602 shell=True, B307 eval) defects
VULNERABLE_CODE = '''import subprocess

def execute_user_command(user_cmd: str):
    # Security vulnerability: subprocess with shell=True
    subprocess.Popen(user_cmd, shell=True)

def evaluate_expression(expr: str):
    # Security vulnerability: unsafe eval
    return eval(expr)

def compute_total(items):
    # Bug: undefined variable 'tax_rate'
    return items * tax_rate
'''


@pytest.mark.asyncio
async def test_static_analysis_detects_bugs_and_vulnerabilities():
    report = await analyze_python_content(
        file_path="security_flaws.py",
        source_code=VULNERABLE_CODE,
        modified_line_numbers={5, 9, 13},
    )

    assert report.total_findings > 0
    assert report.security_findings_count >= 1

    rule_ids = [f.rule_id for f in report.findings]

    # Verify Bandit found subprocess shell=True (B602) or eval (B307)
    has_security_rule = any("B602" in r or "B307" in r or "S602" in r or "S307" in r for r in rule_ids)
    assert has_security_rule, f"Expected Bandit findings, got rules: {rule_ids}"

    # Verify Ruff found undefined variable tax_rate (F821)
    has_undefined_var = any("F821" in r for r in rule_ids)
    assert has_undefined_var, f"Expected F821 undefined variable, got rules: {rule_ids}"

    # Verify findings in diff are flagged
    in_diff_findings = [f for f in report.findings if f.is_in_diff]
    assert len(in_diff_findings) >= 1

