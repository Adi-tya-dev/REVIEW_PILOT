"""Unit and integration tests for confidence calibration, quality evaluation, and hybrid routing."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.database import init_db
from backend.app.main import app
from backend.app.schemas.ai import DefectHypothesis, ModelReviewResponse, ReviewRoutingRequest
from backend.app.schemas.findings import StaticFinding
from backend.app.services.router.calibration import calibrate_hypothesis_confidence
from backend.app.services.router.cost_tracker import calculate_cost, estimate_tokens_from_text
from backend.app.services.router.evaluator import evaluate_slm_sufficiency
from backend.app.services.router.hybrid_router import HybridModelRouter


def test_confidence_calibration_complexity_discount():
    hypothesis = DefectHypothesis(
        rule_id="NULL_PTR",
        category="bug",
        severity="HIGH",
        file_path="service.py",
        line_number=20,
        description="Possible None dereference on item.value",
        self_confidence=0.90,
        suspected_trigger_input="item = None",
        expected_behavior="Should check item is not None",
    )

    # Low complexity (<= 10): no discount
    conf_low = calibrate_hypothesis_confidence(hypothesis, cyclomatic_complexity=3, complexity_threshold=10)
    assert conf_low >= 0.85

    # High complexity (18 > 10): 8 points excess * 5% = 40% discount
    conf_high = calibrate_hypothesis_confidence(hypothesis, cyclomatic_complexity=18, complexity_threshold=10)
    assert conf_high < conf_low
    assert conf_high <= 0.60


def test_confidence_calibration_static_corroboration():
    hypothesis = DefectHypothesis(
        rule_id="SECURITY_INJECTION",
        category="security",
        severity="CRITICAL",
        file_path="service.py",
        line_number=45,
        description="Command injection risk",
        self_confidence=0.70,
        suspected_trigger_input="cmd = '; rm -rf /'",
        expected_behavior="Should sanitize inputs",
    )

    # Corroborating finding at line 46 (+/- 2 lines)
    static_finding = StaticFinding(
        rule_id="B602",
        tool="bandit",
        category="security",
        severity="HIGH",
        file_path="service.py",
        line_number=46,
        description="subprocess call with shell=True",
    )

    conf_isolated = calibrate_hypothesis_confidence(hypothesis, cyclomatic_complexity=4, static_findings=[])
    conf_corroborated = calibrate_hypothesis_confidence(hypothesis, cyclomatic_complexity=4, static_findings=[static_finding])

    assert conf_corroborated > conf_isolated


def test_confidence_calibration_vague_wording_penalty():
    vague_hyp = DefectHypothesis(
        rule_id="CLEAN_CODE",
        category="quality",
        severity="LOW",
        file_path="service.py",
        line_number=10,
        description="This might potentially be a clean code issue according to best practices",
        self_confidence=0.80,
    )
    conf = calibrate_hypothesis_confidence(vague_hyp, cyclomatic_complexity=2)
    # Penalized for vague wording and missing triggers
    assert conf < 0.60


def test_evaluate_slm_sufficiency_acceptance():
    slm_resp = ModelReviewResponse(
        model_name="qwen2.5-coder:1.5b",
        model_type="slm",
        hypotheses=[
            DefectHypothesis(
                rule_id="ZERO_DIVISION",
                category="bug",
                severity="HIGH",
                file_path="math.py",
                line_number=10,
                description="Zero division error if count is 0",
                self_confidence=0.95,
                suspected_trigger_input="count = 0",
                expected_behavior="Raise ValueError when count is 0",
            )
        ],
        raw_response='{"hypotheses": [...]}',
        parse_success=True,
    )

    is_sufficient, reason, score = evaluate_slm_sufficiency(
        slm_response=slm_resp,
        cyclomatic_complexity=3,
        confidence_threshold=0.75,
    )

    assert is_sufficient is True
    assert reason is None
    assert score >= 0.75


def test_evaluate_slm_sufficiency_triggers_escalation_on_low_confidence():
    slm_resp = ModelReviewResponse(
        model_name="qwen2.5-coder:1.5b",
        model_type="slm",
        hypotheses=[
            DefectHypothesis(
                rule_id="UNCERTAIN_BUG",
                category="bug",
                severity="LOW",
                file_path="math.py",
                line_number=10,
                description="Maybe a problem here",
                self_confidence=0.40,  # Below threshold
            )
        ],
        raw_response="{}",
        parse_success=True,
    )

    is_sufficient, reason, score = evaluate_slm_sufficiency(
        slm_response=slm_resp,
        cyclomatic_complexity=3,
        confidence_threshold=0.75,
    )

    assert is_sufficient is False
    assert reason is not None
    assert "low calibrated confidence" in reason


class MockOllamaClient:
    """Mock client returning predetermined responses for test isolation."""

    def __init__(self, response: ModelReviewResponse):
        self._resp = response

    async def review_code(self, *args, **kwargs) -> ModelReviewResponse:
        return self._resp


class MockLLMClient:
    """Mock LLM client returning predetermined responses."""

    def __init__(self, response: ModelReviewResponse):
        self._resp = response

    async def review_code(self, *args, **kwargs) -> ModelReviewResponse:
        return self._resp


@pytest.mark.asyncio
async def test_hybrid_router_accepts_slm_without_llm_call():
    good_slm_resp = ModelReviewResponse(
        model_name="qwen2.5-coder:1.5b",
        model_type="slm",
        hypotheses=[
            DefectHypothesis(
                rule_id="INDEX_OUT_OF_BOUNDS",
                category="bug",
                severity="HIGH",
                file_path="list_util.py",
                line_number=5,
                description="IndexError if items is empty",
                self_confidence=0.92,
                suspected_trigger_input="items = []",
                expected_behavior="Return None or raise empty list error",
            )
        ],
        raw_response="{}",
        latency_ms=120,
        parse_success=True,
    )

    unused_llm_resp = ModelReviewResponse(
        model_name="gpt-4o-mini",
        model_type="llm",
        hypotheses=[],
        raw_response="",
        latency_ms=800,
        parse_success=True,
    )

    router = HybridModelRouter(
        ollama_client=MockOllamaClient(good_slm_resp),
        llm_client=MockLLMClient(unused_llm_resp),
        confidence_threshold=0.75,
    )

    req = ReviewRoutingRequest(
        file_path="list_util.py",
        source_code="def get_first(items):\n    return items[0]\n",
        modified_line_numbers=[2],
    )

    decision = await router.route_and_review(req)

    assert decision.selected_model == "slm"
    assert decision.escalation_triggered is False
    assert decision.is_sufficient is True
    assert len(decision.final_hypotheses) == 1
    assert decision.final_hypotheses[0].rule_id == "INDEX_OUT_OF_BOUNDS"
    assert decision.llm_response is None  # LLM was never called!


@pytest.mark.asyncio
async def test_hybrid_router_escalates_to_llm_when_slm_uncertain():
    weak_slm_resp = ModelReviewResponse(
        model_name="qwen2.5-coder:1.5b",
        model_type="slm",
        hypotheses=[
            DefectHypothesis(
                rule_id="POSSIBLE_ERROR",
                category="bug",
                severity="LOW",
                file_path="complex.py",
                line_number=12,
                description="might be an issue",
                self_confidence=0.35,  # Too low
            )
        ],
        raw_response="{}",
        latency_ms=150,
        parse_success=True,
    )

    strong_llm_resp = ModelReviewResponse(
        model_name="gpt-4o-mini",
        model_type="llm",
        hypotheses=[
            DefectHypothesis(
                rule_id="DEADLOCK_RISK",
                category="bug",
                severity="CRITICAL",
                file_path="complex.py",
                line_number=12,
                description="Acquires lock A before lock B in reverse order, risking thread deadlock",
                self_confidence=0.95,
                suspected_trigger_input="concurrent threads calling swap()",
                expected_behavior="Acquire locks in consistent hierarchical order",
            )
        ],
        raw_response="{}",
        latency_ms=650,
        estimated_cost_usd=0.0004,
        parse_success=True,
    )

    router = HybridModelRouter(
        ollama_client=MockOllamaClient(weak_slm_resp),
        llm_client=MockLLMClient(strong_llm_resp),
        confidence_threshold=0.75,
    )

    req = ReviewRoutingRequest(
        file_path="complex.py",
        source_code="def lock_sync():\n    pass\n",
        modified_line_numbers=[2],
    )

    decision = await router.route_and_review(req)

    assert decision.selected_model == "llm"
    assert decision.escalation_triggered is True
    assert "low calibrated confidence" in (decision.escalation_reason or "")
    assert decision.llm_response is not None
    assert len(decision.final_hypotheses) == 1
    assert decision.final_hypotheses[0].rule_id == "DEADLOCK_RISK"


def test_cost_calculation():
    # Local model cost is always $0.0
    slm_cost = calculate_cost("qwen2.5-coder:1.5b", 500, 150)
    assert slm_cost == 0.0

    # Cloud model pricing
    llm_cost = calculate_cost("gpt-4o-mini", 1_000_000, 1_000_000)
    assert llm_cost == pytest.approx(0.75, 0.01)


@pytest.mark.asyncio
async def test_routing_metrics_api():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/api/v1/routing/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_review_sessions" in data
        assert "escalation_rate_percent" in data
        assert "slm_retention_rate_percent" in data

