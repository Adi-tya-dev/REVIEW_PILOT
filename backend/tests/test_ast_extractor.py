"""Unit tests for Python AST parsing, function slicing, and complexity metrics."""

import pytest
from backend.app.services.ast_analyzer.extractor import analyze_python_source

SAMPLE_CODE = '''"""Module docstring."""
import os

@decorator_one
def compute_risk(score: float, flags: list[str]) -> bool:
    """Calculate whether transaction is high risk."""
    if score > 0.8:
        for flag in flags:
            if flag == "SUSPICIOUS":
                return True
    return False

class PaymentGateway:
    def execute(self, user_id: str) -> None:
        try:
            call_bank(user_id)
        except Exception:
            raise RuntimeError("Bank failed")
'''


def test_analyze_python_source_functions_and_classes():
    summary = analyze_python_source("gateway.py", SAMPLE_CODE, modified_line_numbers={7, 8})

    assert summary.has_syntax_error is False
    assert len(summary.classes) == 1
    assert summary.classes[0] == "PaymentGateway"
    assert len(summary.functions) == 2

    # Test standalone function
    fn1 = summary.functions[0]
    assert fn1.name == "compute_risk"
    assert fn1.parent_class is None
    assert fn1.qualified_name == "compute_risk"
    assert "score: float" in fn1.parameters
    assert fn1.return_annotation == "bool"
    assert fn1.decorators == ["decorator_one"]
    assert fn1.docstring == "Calculate whether transaction is high risk."
    # McCabe complexity: 1 + 1 (if) + 1 (for) + 1 (if) = 4
    assert fn1.cyclomatic_complexity == 4
    assert fn1.is_modified is True
    assert fn1.modified_lines == [7, 8]

    # Test class method
    fn2 = summary.functions[1]
    assert fn2.name == "execute"
    assert fn2.parent_class == "PaymentGateway"
    assert fn2.qualified_name == "PaymentGateway.execute"
    assert fn2.has_exceptions is True
    assert fn2.is_modified is False


def test_analyze_python_syntax_error():
    broken_code = "def broken_func(\n    return 42"
    summary = analyze_python_source("broken.py", broken_code)
    assert summary.has_syntax_error is True
    assert "SyntaxError" in (summary.syntax_error_message or "")

