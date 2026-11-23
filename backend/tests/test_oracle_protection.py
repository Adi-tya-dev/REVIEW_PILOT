"""Unit tests verifying Test Oracle Protection invariants and test generation."""

import pytest
from backend.app.schemas.ai import DefectHypothesis
from backend.app.schemas.ast_nodes import FunctionSlice
from backend.app.services.test_gen.generator import generate_edge_case_tests_for_function, generate_test_from_hypothesis
from backend.app.services.test_gen.oracle_protector import (
    extract_assertion_expressions,
    safe_scaffolding_repair,
    validate_test_oracle,
)


def test_extract_assertion_expressions():
    code = """
import pytest
def test_calc():
    assert add(2, 3) == 5
    assert multiply(2, 0) == 0
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
"""
    assertions = extract_assertion_expressions(code)
    assert len(assertions) == 3
    assert "add(2, 3) == 5" in assertions
    assert "multiply(2, 0) == 0" in assertions
    assert any("pytest.raises(ZeroDivisionError)" in a for a in assertions)


def test_oracle_rejects_assertion_mutation():
    original_code = """
def test_value():
    # Expect 42
    assert compute_magic() == 42
"""
    # LLM cheated: mutated 42 to None so the test passes
    tampered_code = """
def test_value():
    assert compute_magic() is None
"""
    result = validate_test_oracle(original_code, tampered_code)
    assert result.is_valid is False
    assert result.status == "ORACLE_TAMPERING_DETECTED"
    assert "Assertion condition altered" in (result.tampering_reason or "")


def test_oracle_rejects_assertion_deletion():
    original_code = """
def test_multi():
    assert check_a() is True
    assert check_b() == "expected_b"
"""
    # Cheated: deleted failing check_b assertion
    deleted_code = """
def test_multi():
    assert check_a() is True
"""
    result = validate_test_oracle(original_code, deleted_code)
    assert result.is_valid is False
    assert result.status == "ORACLE_TAMPERING_DETECTED"
    assert "Assertion deletion" in (result.tampering_reason or "")


def test_oracle_rejects_exception_suppression():
    original_code = """
def test_crash():
    assert risky_operation() == "success"
"""
    # Cheated: wrapped in try-except pass
    suppressed_code = """
def test_crash():
    try:
        assert risky_operation() == "success"
    except Exception:
        pass
"""
    result = validate_test_oracle(original_code, suppressed_code)
    assert result.is_valid is False
    assert result.status == "ORACLE_TAMPERING_DETECTED"
    assert "Exception suppression detected" in (result.tampering_reason or "")


def test_safe_scaffolding_repair_preserves_assertions():
    original_code = """
def test_missing_imports():
    with pytest.raises(ValueError):
        parse_number("abc")
"""
    # Needs import pytest and from parser import parse_number
    repaired = safe_scaffolding_repair(original_code, "parser", "parse_number")
    assert "import pytest" in repaired
    assert "from parser import parse_number" in repaired

    # Validating original against repaired must succeed as SAFE_REPAIR
    result = validate_test_oracle(original_code, repaired)
    assert result.is_valid is True
    assert result.status == "SAFE_REPAIR"


def test_generate_edge_case_tests():
    func = FunctionSlice(
        name="transfer_funds",
        start_line=10,
        end_line=25,
        parameters=["account_id: str", "amount: float"],
        source_code="def transfer_funds(account_id, amount):\n    pass",
        cyclomatic_complexity=3,
    )
    tests = generate_edge_case_tests_for_function(func, "banking/service.py")
    assert len(tests) >= 1
    # Check that tests are valid
    for t in tests:
        assert t.validation_status == "VALID"
        assert t.target_function == "transfer_funds"


def test_generate_test_from_hypothesis():
    hyp = DefectHypothesis(
        rule_id="ZERO_DIVISION",
        category="bug",
        severity="HIGH",
        file_path="math_ops.py",
        line_number=14,
        description="Division by zero when denominator is 0",
        self_confidence=0.9,
        suspected_trigger_input="b = 0",
        suggested_test_assertion="assert divide(10, 0) != None",
    )
    test_draft = generate_test_from_hypothesis(hyp, "math_ops.py", "divide")
    assert test_draft.validation_status == "VALID"
    assert "divide" in test_draft.original_test_code
    assert "assert divide(10, 0) != None" in test_draft.original_test_code

