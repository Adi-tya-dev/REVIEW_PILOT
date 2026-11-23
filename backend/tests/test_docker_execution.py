"""Unit and integration tests for Docker execution classification and evidence evaluation."""

import pytest
from backend.app.schemas.ai import DefectHypothesis
from backend.app.schemas.execution import ExecutionResult
from backend.app.schemas.findings import StaticFinding
from backend.app.services.evidence.evaluator import evaluate_evidence
from backend.app.services.evidence.github_reporter import format_github_review_comment
from backend.app.services.sandbox.docker_runner import classify_pytest_output


def test_classify_pytest_output_pass():
    status, exc_name, details = classify_pytest_output(0, "1 passed in 0.05s", "", False)
    assert status == "PASS"
    assert exc_name is None


def test_classify_pytest_output_assertion_failure():
    stdout = """
def test_div():
>       assert calculate(10, 0) == 42
E       AssertionError: assert None == 42
"""
    status, exc_name, details = classify_pytest_output(1, stdout, "", False)
    assert status == "ASSERTION_FAILURE"
    assert exc_name == "AssertionError"
    assert "assert" in (details or "")


def test_classify_pytest_output_runtime_exception():
    stdout = """
def test_zero():
>       return a / b
E       ZeroDivisionError: division by zero
"""
    status, exc_name, details = classify_pytest_output(1, stdout, "", False)
    assert status == "RUNTIME_EXCEPTION"
    assert exc_name == "ZeroDivisionError"
    assert "division by zero" in (details or "")


def test_classify_pytest_output_syntax_error():
    stdout = """
E     File "test_gen.py", line 4
E       assert ( == 5
E                ^
E   SyntaxError: invalid syntax
"""
    status, exc_name, details = classify_pytest_output(1, stdout, "", False)
    assert status == "TEST_SYNTAX_ERROR"
    assert exc_name == "SyntaxError"


def test_classify_pytest_output_import_error():
    stdout = """
E   ModuleNotFoundError: No module named 'nonexistent_lib'
"""
    status, exc_name, details = classify_pytest_output(1, stdout, "", False)
    assert status == "TEST_IMPORT_ERROR"
    assert exc_name == "ImportError"


def test_classify_pytest_output_timeout():
    status, exc_name, details = classify_pytest_output(124, "", "", True)
    assert status == "TIMEOUT"
    assert exc_name == "TimeoutError"


def test_evaluate_evidence_confirmed_reproducible():
    hyp = DefectHypothesis(
        rule_id="ZERO_DIVISION",
        category="bug",
        severity="HIGH",
        file_path="math.py",
        line_number=5,
        description="Division by zero when divisor is 0",
        self_confidence=0.9,
        suspected_trigger_input="divide(10, 0)",
        expected_behavior="Handle zero safely",
    )
    exec_res = ExecutionResult(
        execution_status="RUNTIME_EXCEPTION",
        exit_code=1,
        execution_time_ms=85,
        stdout="E   ZeroDivisionError: division by zero",
        exception_name="ZeroDivisionError",
        exception_details="division by zero",
    )

    evidence = evaluate_evidence(hypothesis=hyp, execution_result=exec_res)
    assert evidence.status == "CONFIRMED_REPRODUCIBLE"
    assert evidence.confidence_score >= 0.95
    assert "ZeroDivisionError" in evidence.evidence_summary

    # Verify formatted markdown comment
    comment = format_github_review_comment(hyp, evidence, exec_res)
    assert "[CONFIRMED REPRODUCIBLE DEFECT]" in comment
    assert "divide(10, 0)" in comment
    assert "ZeroDivisionError" in comment


def test_evaluate_evidence_test_generation_error():
    hyp = DefectHypothesis(
        rule_id="BUG",
        category="bug",
        severity="HIGH",
        file_path="math.py",
        line_number=5,
        description="Bug",
    )
    exec_res = ExecutionResult(
        execution_status="TEST_SYNTAX_ERROR",
        exit_code=1,
        exception_name="SyntaxError",
        exception_details="invalid syntax in test",
    )

    evidence = evaluate_evidence(hypothesis=hyp, execution_result=exec_res)
    # Must never blame developer code for a test syntax error
    assert evidence.status == "TEST_GENERATION_ERROR"
    assert evidence.confidence_score <= 0.20


def test_evaluate_evidence_environment_error():
    hyp = DefectHypothesis(
        rule_id="BUG",
        category="bug",
        severity="HIGH",
        file_path="math.py",
        line_number=5,
        description="Bug",
    )
    exec_res = ExecutionResult(
        execution_status="TIMEOUT",
        exit_code=124,
        timeout_reached=True,
    )

    evidence = evaluate_evidence(hypothesis=hyp, execution_result=exec_res)
    assert evidence.status == "ENVIRONMENT_ERROR"

