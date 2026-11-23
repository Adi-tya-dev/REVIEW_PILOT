"""Hybrid SLM–LLM Router with calibrated confidence evaluation and cost tracking."""

import uuid
from typing import List, Optional
from backend.app.config import settings
from backend.app.schemas.ai import DefectHypothesis, ModelReviewResponse, ReviewRoutingRequest, RoutingDecision
from backend.app.services.ai.llm_client import LLMClient
from backend.app.services.ai.ollama_client import OllamaClient
from backend.app.services.ast_analyzer.extractor import analyze_python_source
from backend.app.services.router.evaluator import evaluate_slm_sufficiency


class HybridModelRouter:
    """Intelligent, cost-aware router dispatching review tasks between SLM and LLM."""

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        llm_client: Optional[LLMClient] = None,
        complexity_threshold: Optional[int] = None,
        confidence_threshold: Optional[float] = None,
    ):
        self.slm_client = ollama_client or OllamaClient()
        self.llm_client = llm_client or LLMClient()
        self.complexity_threshold = complexity_threshold or settings.ROUTER_COMPLEXITY_THRESHOLD
        self.confidence_threshold = confidence_threshold or settings.ROUTER_CONFIDENCE_THRESHOLD

    async def route_and_review(self, request: ReviewRoutingRequest) -> RoutingDecision:
        """Route code review request through the hybrid SLM-LLM pipeline."""
        task_id = str(uuid.uuid4())[:8]

        # 1. Determine cyclomatic complexity from AST
        complexity = 1
        if request.ast_summary and request.ast_summary.functions:
            complexity = max(fn.cyclomatic_complexity for fn in request.ast_summary.functions)
        else:
            summary = analyze_python_source(
                file_path=request.file_path,
                source_code=request.source_code,
                modified_line_numbers=set(request.modified_line_numbers),
            )
            if summary.functions:
                complexity = max(fn.cyclomatic_complexity for fn in summary.functions)

        # 2. Check for explicit forced modes (for empirical benchmarking)
        if request.force_model == "llm_only":
            llm_resp = await self.llm_client.review_code(
                file_path=request.file_path,
                source_code=request.source_code,
                modified_lines=request.modified_line_numbers,
                static_findings=request.static_findings,
            )
            return RoutingDecision(
                task_id=task_id,
                selected_model="llm",
                escalation_triggered=False,
                llm_response=llm_resp,
                calibrated_confidence=0.85 if llm_resp.hypotheses else 0.90,
                is_sufficient=llm_resp.parse_success,
                total_latency_ms=llm_resp.latency_ms,
                total_cost_usd=llm_resp.estimated_cost_usd,
                final_hypotheses=llm_resp.hypotheses,
            )

        if request.force_model == "slm_only":
            slm_resp = await self.slm_client.review_code(
                file_path=request.file_path,
                source_code=request.source_code,
                modified_lines=request.modified_line_numbers,
                static_findings=request.static_findings,
            )
            is_suff, reason, cal_conf = evaluate_slm_sufficiency(
                slm_response=slm_resp,
                cyclomatic_complexity=complexity,
                static_findings=request.static_findings,
                confidence_threshold=self.confidence_threshold,
                complexity_threshold=self.complexity_threshold,
            )
            return RoutingDecision(
                task_id=task_id,
                selected_model="slm",
                escalation_triggered=False,
                slm_response=slm_resp,
                calibrated_confidence=cal_conf,
                is_sufficient=is_suff,
                total_latency_ms=slm_resp.latency_ms,
                total_cost_usd=slm_resp.estimated_cost_usd,
                final_hypotheses=slm_resp.hypotheses,
            )

        # 3. Hybrid Routing: Stage 1 - Initial SLM review
        slm_resp = await self.slm_client.review_code(
            file_path=request.file_path,
            source_code=request.source_code,
            modified_lines=request.modified_line_numbers,
            static_findings=request.static_findings,
        )

        is_sufficient, escalation_reason, calibrated_conf = evaluate_slm_sufficiency(
            slm_response=slm_resp,
            cyclomatic_complexity=complexity,
            static_findings=request.static_findings,
            confidence_threshold=self.confidence_threshold,
            complexity_threshold=self.complexity_threshold,
        )

        # 4. If SLM review is sufficient, accept without escalating to LLM
        if is_sufficient:
            return RoutingDecision(
                task_id=task_id,
                selected_model="slm",
                escalation_triggered=False,
                slm_response=slm_resp,
                calibrated_confidence=calibrated_conf,
                is_sufficient=True,
                abstained=False,
                total_latency_ms=slm_resp.latency_ms,
                total_cost_usd=slm_resp.estimated_cost_usd,
                final_hypotheses=slm_resp.hypotheses,
            )

        # 5. Stage 2 - Escalation to LLM
        llm_resp = await self.llm_client.review_code(
            file_path=request.file_path,
            source_code=request.source_code,
            modified_lines=request.modified_line_numbers,
            static_findings=request.static_findings,
        )

        total_latency = slm_resp.latency_ms + llm_resp.latency_ms
        total_cost = slm_resp.estimated_cost_usd + llm_resp.estimated_cost_usd

        # Check if both models failed or produced no actionable hypotheses
        if not llm_resp.parse_success and not slm_resp.parse_success:
            return RoutingDecision(
                task_id=task_id,
                selected_model="llm",
                escalation_triggered=True,
                escalation_reason=f"Both SLM and LLM failed to produce valid outputs. SLM: {escalation_reason}",
                slm_response=slm_resp,
                llm_response=llm_resp,
                calibrated_confidence=0.0,
                is_sufficient=False,
                abstained=True,
                abstention_reason="Dual model parse failure; code marked for manual developer review.",
                total_latency_ms=total_latency,
                total_cost_usd=total_cost,
                final_hypotheses=[],
            )

        return RoutingDecision(
            task_id=task_id,
            selected_model="llm",
            escalation_triggered=True,
            escalation_reason=escalation_reason,
            slm_response=slm_resp,
            llm_response=llm_resp,
            calibrated_confidence=0.88 if llm_resp.hypotheses else 0.50,
            is_sufficient=llm_resp.parse_success,
            abstained=False,
            total_latency_ms=total_latency,
            total_cost_usd=total_cost,
            final_hypotheses=llm_resp.hypotheses if llm_resp.parse_success else slm_resp.hypotheses,
        )

