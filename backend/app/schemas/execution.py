"""Pydantic schemas for Docker sandbox execution and evidence grounding."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    """Payload to execute generated tests inside an isolated sandbox."""

    test_code: str
    target_filename: str
    source_files: Dict[str, str] = Field(default_factory=dict)  # filename -> code
    timeout_seconds: int = 15
    memory_limit: str = "512m"
    cpu_limit: float = 1.0


class ExecutionResult(BaseModel):
    """Result of running a test suite inside an ephemeral Docker container."""

    execution_status: str  # PASS, ASSERTION_FAILURE, RUNTIME_EXCEPTION, TEST_SYNTAX_ERROR, TEST_IMPORT_ERROR, TIMEOUT, ENVIRONMENT_ERROR
    exit_code: int
    execution_time_ms: int = 0
    stdout: str = ""
    stderr: str = ""
    exception_name: Optional[str] = None
    exception_details: Optional[str] = None
    timeout_reached: bool = False
    container_id: Optional[str] = None


class EvidenceRecord(BaseModel):
    """Evidence assessment correlating findings with actual execution outcomes."""

    status: str  # CONFIRMED_REPRODUCIBLE, STATIC_WARNING, AI_HYPOTHESIS, TEST_GENERATION_ERROR, ENVIRONMENT_ERROR, NEEDS_REVIEW, ABSTAINED
    confidence_score: float = 1.0
    evidence_summary: str
    input_trigger: Optional[str] = None
    expected_vs_actual: Optional[str] = None
    failing_assertion: Optional[str] = None
    comment_markdown: Optional[str] = None

