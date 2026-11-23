"""Quality evaluation engine deciding whether SLM output is sufficient or requires escalation."""

from typing import List, Optional, Tuple
from backend.app.schemas.ai import DefectHypothesis, ModelReviewResponse
from backend.app.schemas.findings import StaticFinding
from backend.app.services.router.calibration import calibrate_hypothesis_confidence


def evaluate_slm_sufficiency(
    slm_response: ModelReviewResponse,
    cyclomatic_complexity: int = 1,
    static_findings: Optional[List[StaticFinding]] = None,
    confidence_threshold: float = 0.75,
    complexity_threshold: int = 10,
) -> Tuple[bool, Optional[str], float]:
    """Evaluate whether the SLM's review output is sufficient or requires LLM escalation.

    Returns:
        (is_sufficient: bool, escalation_reason: Optional[str], aggregate_calibrated_confidence: float)
    """
    if static_findings is None:
        static_findings = []

    # 1. Structural parse failure: SLM output could not be parsed into valid schema
    if not slm_response.parse_success:
        return False, f"SLM JSON parsing failed: {slm_response.error_message or 'Invalid JSON'}", 0.0

    # 2. Case: SLM returned zero hypotheses
    if not slm_response.hypotheses:
        # If code has high cyclomatic complexity, zero findings is a likely false negative
        if cyclomatic_complexity > complexity_threshold:
            return (
                False,
                f"SLM found 0 defects, but code has high complexity ({cyclomatic_complexity} > {complexity_threshold})",
                0.50,
            )
        # If static analysis already found severe security/bug findings, but SLM found none, escalate
        severe_static = [f for f in static_findings if f.severity in ("CRITICAL", "HIGH")]
        if severe_static:
            return (
                False,
                f"SLM found 0 defects, but static analysis detected {len(severe_static)} high/critical issues",
                0.40,
            )

        # Simple code with no defects found: SLM is sufficient
        return True, None, 0.90

    # 3. Case: SLM returned one or more hypotheses
    calibrated_scores = []
    for h in slm_response.hypotheses:
        score = calibrate_hypothesis_confidence(
            hypothesis=h,
            cyclomatic_complexity=cyclomatic_complexity,
            static_findings=static_findings,
            complexity_threshold=complexity_threshold,
        )
        calibrated_scores.append(score)

    avg_calibrated = sum(calibrated_scores) / len(calibrated_scores)

    # Check if any hypothesis falls below the required confidence threshold
    low_confidence_items = [
        h for h, score in zip(slm_response.hypotheses, calibrated_scores) if score < confidence_threshold
    ]

    if low_confidence_items:
        reasons = [
            f"Rule {h.rule_id} at line {h.line_number} has low calibrated confidence ({score:.2f} < {confidence_threshold:.2f})"
            for h, score in zip(slm_response.hypotheses, calibrated_scores)
            if score < confidence_threshold
        ]
        return False, "; ".join(reasons), avg_calibrated

    # All hypotheses met calibrated threshold
    return True, None, avg_calibrated

