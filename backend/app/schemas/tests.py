"""Pydantic schemas for generated pytest cases and Test Oracle validation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TestCaseDraft(BaseModel):
    """An edge-case pytest test case generated to test a function or hypothesis."""

    test_name: str
    target_function: str
    file_path: str
    original_test_code: str
    repaired_test_code: Optional[str] = None
    input_values: Optional[str] = None
    expected_behavior: Optional[str] = None
    reason: Optional[str] = None
    generator_model: str = "slm"  # 'slm' or 'llm'
    validation_status: str = "VALID"  # VALID, SYNTAX_REPAIRED, INVALID_ORACLE_MUTATION, INVALID_SYNTAX


class AssertionInvariant(BaseModel):
    """Normalized invariant representing an assertion statement in a test."""

    expression_str: str
    comparator: Optional[str] = None
    expected_val_str: Optional[str] = None


class OracleValidationResult(BaseModel):
    """Result of validating test repairs against Test Oracle protection rules."""

    is_valid: bool
    status: str  # 'VALID', 'SAFE_REPAIR', 'ORACLE_TAMPERING_DETECTED', 'SYNTAX_ERROR'
    original_assertions: List[str] = Field(default_factory=list)
    repaired_assertions: List[str] = Field(default_factory=list)
    tampering_reason: Optional[str] = None
    repaired_code: Optional[str] = None

