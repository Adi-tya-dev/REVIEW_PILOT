"""Confidence calibration and uncertainty estimation for model review hypotheses."""

import re
from typing import List, Optional
from backend.app.schemas.ai import DefectHypothesis
from backend.app.schemas.findings import StaticFinding

VAGUE_PATTERNS = [
    re.compile(r"\b(might|could potentially|possibly|maybe|seems like|appears to)\b", re.IGNORECASE),
    re.compile(r"\b(best practice|clean code|readability)\b", re.IGNORECASE),
]


def calibrate_hypothesis_confidence(
    hypothesis: DefectHypothesis,
    cyclomatic_complexity: int = 1,
    static_findings: Optional[List[StaticFinding]] = None,
    complexity_threshold: int = 10,
) -> float:
    """Calibrate a model's self-reported confidence against AST and static evidence.

    Formula:
      Calibrated = SelfConfidence * ComplexityDiscount * StaticOverlapBonus * SpecificityFactor

    Args:
        hypothesis: Model's raw defect hypothesis.
        cyclomatic_complexity: McCabe complexity of the target function.
        static_findings: Prior findings from Ruff / Bandit on this file.
        complexity_threshold: Complexity score above which SLM confidence is discounted.

    Returns:
        Calibrated confidence float between 0.0 and 1.0.
    """
    confidence = hypothesis.self_confidence

    # 1. Complexity discount: high branching complexity discounts SLM certainty
    if cyclomatic_complexity > complexity_threshold:
        excess = cyclomatic_complexity - complexity_threshold
        # Decay by 5% per point of excess complexity, capped at a minimum 0.4 multiplier
        complexity_factor = max(0.4, 1.0 - (excess * 0.05))
        confidence *= complexity_factor

    # 2. Static analysis corroboration bonus
    if static_findings:
        # Check if any static finding matches on line number (+/- 2 lines)
        corroborated = any(
            abs(f.line_number - hypothesis.line_number) <= 2 for f in static_findings
        )
        if corroborated:
            confidence = min(1.0, confidence * 1.20)  # 20% corroboration boost

    # 3. Specificity evaluation
    specificity_multiplier = 1.0
    # Penalty if missing concrete trigger input
    if not hypothesis.suspected_trigger_input or len(hypothesis.suspected_trigger_input.strip()) < 3:
        specificity_multiplier *= 0.80

    # Penalty if missing concrete expected behavior
    if not hypothesis.expected_behavior or len(hypothesis.expected_behavior.strip()) < 5:
        specificity_multiplier *= 0.85

    # Penalty if description uses speculative / vague language
    for pattern in VAGUE_PATTERNS:
        if pattern.search(hypothesis.description):
            specificity_multiplier *= 0.80
            break

    confidence *= specificity_multiplier

    # Clamp to [0.05, 1.0]
    return round(max(0.05, min(1.0, confidence)), 4)

