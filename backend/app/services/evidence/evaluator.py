"""Evidence Grounding Evaluator: Correlates static findings, AI hypotheses, and Docker execution."""

from typing import Optional
from backend.app.schemas.ai import DefectHypothesis
from backend.app.schemas.execution import EvidenceRecord, ExecutionResult
from backend.app.schemas.findings import StaticFinding


def evaluate_evidence(
    hypothesis: Optional[DefectHypothesis] = None,
    static_finding: Optional[StaticFinding] = None,
    execution_result: Optional[ExecutionResult] = None,
) -> EvidenceRecord:
    """Assess reproducibility and evidence grounding for a reported defect.

    Evidence Hierarchy:
    1. CONFIRMED_REPRODUCIBLE: Test executed in Docker and reproduced the exact failure.
    2. STATIC_WARNING: Corroborated by static analysis (Ruff / Bandit).
    3. AI_HYPOTHESIS: Model proposed bug that was not confirmed by execution failure.
    4. TEST_GENERATION_ERROR: The test itself had syntax/import issues (never blame code).
    5. ENVIRONMENT_ERROR: Sandbox timed out or Docker daemon was unreachable.
    6. ABSTAINED: Model abstained from making an uncalibrated claim.
    """
    # Case 1: Docker execution results available
    if execution_result:
        # Check for test generation flaws
        if execution_result.execution_status in ("TEST_SYNTAX_ERROR", "TEST_IMPORT_ERROR"):
            return EvidenceRecord(
                status="TEST_GENERATION_ERROR",
                confidence_score=0.10,
                evidence_summary=f"Generated test failed to compile/import: {execution_result.exception_details or execution_result.execution_status}",
                input_trigger=hypothesis.suspected_trigger_input if hypothesis else None,
                expected_vs_actual="Test setup failure; no code defect confirmed.",
            )

        # Check for environment / timeout failures
        if execution_result.execution_status in ("TIMEOUT", "ENVIRONMENT_ERROR"):
            return EvidenceRecord(
                status="ENVIRONMENT_ERROR",
                confidence_score=0.30,
                evidence_summary=f"Sandbox execution could not complete: {execution_result.execution_status}",
                input_trigger=hypothesis.suspected_trigger_input if hypothesis else None,
                expected_vs_actual="Execution timed out or environment was restricted.",
            )

        # Case: Test produced assertion failure or runtime exception (Confirmed bug!)
        if execution_result.execution_status in ("ASSERTION_FAILURE", "RUNTIME_EXCEPTION"):
            exc_desc = f"{execution_result.exception_name}: {execution_result.exception_details}" if execution_result.exception_name else "Assertion failed"
            return EvidenceRecord(
                status="CONFIRMED_REPRODUCIBLE",
                confidence_score=0.98,
                evidence_summary=f"Defect verified in isolated Docker sandbox: {exc_desc}",
                input_trigger=hypothesis.suspected_trigger_input if hypothesis else "Edge case input",
                expected_vs_actual=f"Expected safe execution, but encountered: {exc_desc}",
                failing_assertion=hypothesis.suggested_test_assertion if hypothesis else None,
            )

        # Case: Test passed (The hypothetical bug did not trigger in execution)
        if execution_result.execution_status == "PASS":
            if static_finding:
                return EvidenceRecord(
                    status="STATIC_WARNING",
                    confidence_score=0.75,
                    evidence_summary=f"Static warning [{static_finding.rule_id}] flagged, though test passed.",
                    input_trigger=hypothesis.suspected_trigger_input if hypothesis else None,
                    expected_vs_actual="No runtime crash reproduced.",
                )
            return EvidenceRecord(
                status="AI_HYPOTHESIS",
                confidence_score=0.45,
                evidence_summary="AI proposed defect hypothesis, but test passed without reproducing failure.",
                input_trigger=hypothesis.suspected_trigger_input if hypothesis else None,
                expected_vs_actual="Test passed.",
            )

    # Case 2: No execution results, only static analysis
    if static_finding and not hypothesis:
        return EvidenceRecord(
            status="STATIC_WARNING",
            confidence_score=0.85,
            evidence_summary=f"Detected by {static_finding.tool} ({static_finding.rule_id}): {static_finding.description}",
        )

    # Case 3: AI hypothesis without execution
    if hypothesis:
        return EvidenceRecord(
            status="AI_HYPOTHESIS",
            confidence_score=hypothesis.self_confidence,
            evidence_summary=f"Unverified model hypothesis: {hypothesis.description}",
            input_trigger=hypothesis.suspected_trigger_input,
            expected_vs_actual=hypothesis.expected_behavior,
            failing_assertion=hypothesis.suggested_test_assertion,
        )

    return EvidenceRecord(
        status="ABSTAINED",
        confidence_score=0.0,
        evidence_summary="Insufficient evidence to report finding.",
    )

