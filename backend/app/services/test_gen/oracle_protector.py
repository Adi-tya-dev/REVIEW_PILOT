"""Test Oracle Protection Engine: Preserves assertion semantics and rejects mutation."""

import ast
from typing import List, Optional, Set
from backend.app.schemas.tests import OracleValidationResult


def extract_assertion_expressions(source_code: str) -> List[str]:
    """Extract canonical unparsed string representations of all assertions in code.

    Includes both `assert expr` statements and `pytest.raises(Exc)` context managers.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    assertions: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            try:
                assertions.append(ast.unparse(node.test).strip())
            except Exception:
                pass
        elif isinstance(node, ast.With):
            for item in node.items:
                try:
                    expr_str = ast.unparse(item.context_expr).strip()
                    if "pytest.raises" in expr_str:
                        assertions.append(expr_str)
                except Exception:
                    pass

    return assertions


def check_for_exception_suppression(source_code: str) -> bool:
    """Detect if the test suppresses exceptions using bare `except: pass` or `except Exception: pass`."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            # Check if body consists of only `pass`
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                # Suppresses all exceptions without asserting
                if node.type is None:
                    return True
                try:
                    exc_type = ast.unparse(node.type)
                    if exc_type in ("Exception", "BaseException"):
                        return True
                except Exception:
                    pass
    return False


def validate_test_oracle(
    original_code: str,
    repaired_code: Optional[str] = None,
) -> OracleValidationResult:
    """Validate that test repairs have not altered expected assertions, removed tests, or suppressed failures.

    Strict Invariants:
    1. Assertions must never be relaxed or mutated to force a test to pass.
    2. Failing assertions must never be deleted.
    3. Unexpected exceptions must not be suppressed via catch-all try/except.
    """
    if repaired_code is None or repaired_code.strip() == original_code.strip():
        # Validate original code syntax
        try:
            ast.parse(original_code)
        except SyntaxError as e:
            return OracleValidationResult(
                is_valid=False,
                status="SYNTAX_ERROR",
                original_assertions=[],
                repaired_assertions=[],
                tampering_reason=f"SyntaxError in generated test: {str(e)}",
            )

        orig_assertions = extract_assertion_expressions(original_code)
        if not orig_assertions:
            return OracleValidationResult(
                is_valid=False,
                status="ORACLE_TAMPERING_DETECTED",
                original_assertions=[],
                repaired_assertions=[],
                tampering_reason="Test case contains no assertions or pytest.raises blocks.",
            )

        return OracleValidationResult(
            is_valid=True,
            status="VALID",
            original_assertions=orig_assertions,
            repaired_assertions=orig_assertions,
            repaired_code=original_code,
        )

    # 1. Parse repaired code
    try:
        ast.parse(repaired_code)
    except SyntaxError as e:
        return OracleValidationResult(
            is_valid=False,
            status="SYNTAX_ERROR",
            original_assertions=extract_assertion_expressions(original_code),
            repaired_assertions=[],
            tampering_reason=f"Repaired code has SyntaxError: {str(e)}",
        )

    # 2. Check for exception suppression
    if check_for_exception_suppression(repaired_code):
        return OracleValidationResult(
            is_valid=False,
            status="ORACLE_TAMPERING_DETECTED",
            original_assertions=extract_assertion_expressions(original_code),
            repaired_assertions=extract_assertion_expressions(repaired_code),
            tampering_reason="Exception suppression detected (try ... except Exception: pass).",
        )

    orig_assertions = extract_assertion_expressions(original_code)
    rep_assertions = extract_assertion_expressions(repaired_code)

    # 3. Assertions count check: Never allow assertion removal
    if len(rep_assertions) < len(orig_assertions):
        return OracleValidationResult(
            is_valid=False,
            status="ORACLE_TAMPERING_DETECTED",
            original_assertions=orig_assertions,
            repaired_assertions=rep_assertions,
            tampering_reason=f"Assertion deletion: {len(orig_assertions)} originally, but only {len(rep_assertions)} in repaired test.",
        )

    # 4. Invariant check: Every original assertion expression must be preserved
    orig_set = set(orig_assertions)
    rep_set = set(rep_assertions)
    missing_assertions = orig_set - rep_set

    if missing_assertions:
        return OracleValidationResult(
            is_valid=False,
            status="ORACLE_TAMPERING_DETECTED",
            original_assertions=orig_assertions,
            repaired_assertions=rep_assertions,
            tampering_reason=f"Assertion condition altered: {list(missing_assertions)} was modified or removed.",
        )

    return OracleValidationResult(
        is_valid=True,
        status="SAFE_REPAIR",
        original_assertions=orig_assertions,
        repaired_assertions=rep_assertions,
        repaired_code=repaired_code,
    )


def safe_scaffolding_repair(
    test_code: str,
    module_import_path: Optional[str] = None,
    function_name: Optional[str] = None,
) -> str:
    """Safely repair missing imports and boilerplate without mutating any assertions."""
    lines = test_code.splitlines()

    has_pytest_import = any("import pytest" in line for line in lines)
    needs_pytest = "pytest" in test_code

    header_lines: List[str] = []
    if needs_pytest and not has_pytest_import:
        header_lines.append("import pytest")

    if module_import_path and function_name:
        import_stmt = f"from {module_import_path} import {function_name}"
        if not any(function_name in line and "import" in line for line in lines):
            header_lines.append(import_stmt)

    if header_lines:
        return "\n".join(header_lines) + "\n\n" + test_code.strip()
    return test_code

