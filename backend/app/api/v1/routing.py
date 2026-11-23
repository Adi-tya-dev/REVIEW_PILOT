"""API routes for SLM–LLM routing decisions, cost metrics, and model stats."""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.review_session import ReviewSession
from backend.app.schemas.ai import ReviewRoutingRequest, RoutingDecision
from backend.app.services.router.hybrid_router import HybridModelRouter

router = APIRouter(prefix="/routing", tags=["Model Routing"])


@router.post("/review-slice", response_model=RoutingDecision)
async def route_and_review_slice(request: ReviewRoutingRequest) -> RoutingDecision:
    """Execute hybrid SLM–LLM routing on a Python code snippet with calibrated evaluation."""
    router_engine = HybridModelRouter()
    return await router_engine.route_and_review(request)


@router.get("/metrics", response_model=Dict[str, Any])
async def get_routing_metrics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve aggregate statistics on SLM usage, LLM escalation rate, and estimated savings."""
    total_sessions_stmt = select(func.count(ReviewSession.id))
    total_sessions = (await db.execute(total_sessions_stmt)).scalar() or 0

    escalated_stmt = select(func.count(ReviewSession.id)).where(ReviewSession.escalated_to_llm == True)
    escalated_count = (await db.execute(escalated_stmt)).scalar() or 0

    slm_calls_stmt = select(func.sum(ReviewSession.slm_calls))
    total_slm_calls = (await db.execute(slm_calls_stmt)).scalar() or 0

    llm_calls_stmt = select(func.sum(ReviewSession.llm_calls))
    total_llm_calls = (await db.execute(llm_calls_stmt)).scalar() or 0

    total_cost_stmt = select(func.sum(ReviewSession.estimated_cost_usd))
    total_cost = (await db.execute(total_cost_stmt)).scalar() or 0.0

    slm_only_count = max(0, total_sessions - escalated_count)
    escalation_rate = (escalated_count / total_sessions * 100.0) if total_sessions > 0 else 0.0
    slm_retention_rate = (slm_only_count / total_sessions * 100.0) if total_sessions > 0 else 100.0

    # Theoretical cost if all reviews had been sent to LLM:
    # avg cost per LLM call ~ $0.003
    hypothetical_llm_only_cost = (total_slm_calls + total_llm_calls) * 0.003
    cost_savings_usd = max(0.0, hypothetical_llm_only_cost - total_cost)

    return {
        "total_review_sessions": total_sessions,
        "slm_only_sessions": slm_only_count,
        "escalated_sessions": escalated_count,
        "escalation_rate_percent": round(escalation_rate, 2),
        "slm_retention_rate_percent": round(slm_retention_rate, 2),
        "total_slm_calls": total_slm_calls,
        "total_llm_calls": total_llm_calls,
        "total_cost_usd": round(total_cost, 4),
        "estimated_savings_vs_llm_only_usd": round(cost_savings_usd, 4),
    }

