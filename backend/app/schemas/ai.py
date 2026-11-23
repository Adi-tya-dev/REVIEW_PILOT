"""Pydantic schemas for AI review requests, model responses, and routing decisions."""

from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.ast_nodes import FileASTSummary
from backend.app.schemas.findings import StaticFinding


class DefectHypothesis(BaseModel):
    """An AI-generated defect hypothesis for a code section."""

    rule_id: str
    category: str = "bug"  # 'bug', 'security', 'quality'
    severity: str = "HIGH"  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    file_path: str
    line_number: int
    end_line_number: Optional[int] = None
    description: str
    self_confidence: float = Field(0.7, ge=0.0, le=1.0)
    suspected_trigger_input: Optional[str] = None
    expected_behavior: Optional[str] = None
    suggested_test_assertion: Optional[str] = None


class ModelReviewResponse(BaseModel):
    """Structured response from a single model (SLM or LLM)."""

    model_name: str
    model_type: str  # 'slm' or 'llm'
    hypotheses: List[DefectHypothesis] = Field(default_factory=list)
    raw_response: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    estimated_cost_usd: float = 0.0
    parse_success: bool = True
    error_message: Optional[str] = None


class RoutingDecision(BaseModel):
    """Routing and escalation outcome for a review unit."""

    task_id: str
    selected_model: str  # 'slm' or 'llm'
    escalation_triggered: bool = False
    escalation_reason: Optional[str] = None
    slm_response: Optional[ModelReviewResponse] = None
    llm_response: Optional[ModelReviewResponse] = None
    calibrated_confidence: float = 0.0
    is_sufficient: bool = True
    abstained: bool = False
    abstention_reason: Optional[str] = None
    total_latency_ms: int = 0
    total_cost_usd: float = 0.0
    final_hypotheses: List[DefectHypothesis] = Field(default_factory=list)


class ReviewRoutingRequest(BaseModel):
    """Input payload to analyze a Python code slice via the hybrid router."""

    file_path: str
    source_code: str
    modified_line_numbers: List[int] = Field(default_factory=list)
    static_findings: List[StaticFinding] = Field(default_factory=list)
    ast_summary: Optional[FileASTSummary] = None
    force_model: Optional[str] = None  # None, 'slm_only', 'llm_only', 'hybrid'

