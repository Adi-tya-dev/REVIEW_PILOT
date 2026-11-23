"""Targeted pytest edge-case generator for identified functions and defect hypotheses."""

import re
from typing import List, Optional
from backend.app.schemas.ai import DefectHypothesis
from backend.app.schemas.ast_nodes import FunctionSlice
from backend.app.schemas.tests import TestCaseDraft
from backend.app.services.test_gen.oracle_protector import safe_scaffolding_repair, validate_test_oracle


def generate_edge_case_tests_for_function(
    func: FunctionSlice,
    module_path: str,
) -> List[TestCaseDraft]:
    """Generate systematic edge-case pytest test drafts for a Python function."""
    tests: List[TestCaseDraft] = []
    clean_mod_path = module_path.replace(".py", "").replace("/", ".").replace("\\", ".")
    if clean_mod_path.startswith("."):
        clean_mod_path = clean_mod_path.lstrip(".")

    # Heuristic 1: None / Empty input check
    if func.parameters:
        first_param = func.parameters[0].split(":")[0].strip()
        test_name = f"test_{func.name}_none_input"
        code = f"""import pytest
from {clean_mod_path} import {func.name}

def {test_name}():
    # Edge case: pass None as {first_param}
    with pytest.raises((ValueError, TypeError)):
        {func.name}(None)
"""
        tests.append(
            TestCaseDraft(
                test_name=test_name,
                target_function=func.qualified_name,
                file_path=module_path,
                original_test_code=code,
                input_values=f"{first_param}=None",
                expected_behavior="Function should raise ValueError or TypeError on None input",
                reason="Verifies input validation boundary on null/None arguments",
                generator_model="slm",
                validation_status="VALID",
            )
        )

    # Heuristic 2: Empty collection / string test
    if any("str" in p or "list" in p or "dict" in p for p in func.parameters):
        test_name = f"test_{func.name}_empty_collection"
        code = f"""import pytest
from {clean_mod_path} import {func.name}

def {test_name}():
    # Edge case: pass empty container
    result = {func.name}("")
    assert result is not None
"""
        tests.append(
            TestCaseDraft(
                test_name=test_name,
                target_function=func.qualified_name,
                file_path=module_path,
                original_test_code=code,
                input_values="empty string/list",
                expected_behavior="Function should handle empty container safely",
                reason="Verifies empty container boundary handling",
                generator_model="slm",
                validation_status="VALID",
            )
        )

    return tests


def generate_test_from_hypothesis(
    hypothesis: DefectHypothesis,
    module_path: str,
    target_function_name: str,
) -> TestCaseDraft:
    """Generate a targeted pytest test case based on an AI defect hypothesis."""
    clean_mod_path = module_path.replace(".py", "").replace("/", ".").replace("\\", ".").lstrip(".")
    test_slug = re.sub(r"[^a-zA-Z0-9_]", "_", hypothesis.rule_id.lower())
    test_name = f"test_reproduce_{test_slug}_line_{hypothesis.line_number}"

    # Construct test body using hypothesis trigger and expected assertion
    trigger = hypothesis.suspected_trigger_input or "None"
    assertion = hypothesis.suggested_test_assertion or f"assert {target_function_name}(...) != None"

    raw_test_code = f"""import pytest
from {clean_mod_path} import {target_function_name}

def {test_name}():
    \"\"\"Reproduction test for {hypothesis.rule_id}: {hypothesis.description}\"\"\"
    # Input trigger: {trigger}
    {assertion}
"""

    # Validate test through Oracle protector
    val_result = validate_test_oracle(raw_test_code)
    repaired_code = raw_test_code
    if not val_result.is_valid:
        # Attempt safe scaffolding repair
        repaired_code = safe_scaffolding_repair(raw_test_code, clean_mod_path, target_function_name)
        val_result = validate_test_oracle(raw_test_code, repaired_code)

    return TestCaseDraft(
        test_name=test_name,
        target_function=target_function_name,
        file_path=module_path,
        original_test_code=raw_test_code,
        repaired_test_code=repaired_code if val_result.is_valid else None,
        input_values=hypothesis.suspected_trigger_input,
        expected_behavior=hypothesis.expected_behavior,
        reason=f"Generated from defect hypothesis [{hypothesis.rule_id}] at line {hypothesis.line_number}",
        generator_model="slm",
        validation_status=val_result.status,
    )

