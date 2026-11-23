"""Findings API endpoints for querying static and security results."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.finding import Finding
from backend.app.services.ast_analyzer.extractor import analyze_python_source
from backend.app.services.static_analysis.aggregator import analyze_python_content

router = APIRouter(prefix="/findings", tags=["Findings"])


class AnalyzeSnippetRequest(BaseModel):
    """Payload to analyze a standalone Python code snippet."""
    filename: str = "snippet.py"
    code: str


@router.get("/review/{review_session_id}", response_model=List[Dict[str, Any]])
async def get_findings_for_review(
    review_session_id: int,
    category: Optional[str] = Query(None, description="Filter: 'security', 'quality', 'bug'"),
    severity: Optional[str] = Query(None, description="Filter: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'"),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Retrieve all static analysis findings for a specific review session."""
    query = select(Finding).where(Finding.review_session_id == review_session_id)

    if category:
        query = query.where(Finding.category == category)
    if severity:
        query = query.where(Finding.severity == severity)

    result = await db.execute(query)
    findings = result.scalars().all()

    return [
        {
            "id": f.id,
            "rule_id": f.rule_id,
            "tool": f.tool,
            "category": f.category,
            "severity": f.severity,
            "file_path": f.file_path,
            "line_number": f.line_number,
            "end_line_number": f.end_line_number,
            "description": f.description,
            "code_snippet": f.code_snippet,
            "confidence": f.confidence,
            "evidence_status": f.evidence_status,
        }
        for f in findings
    ]


@router.post("/analyze-snippet", response_model=Dict[str, Any])
async def analyze_snippet(payload: AnalyzeSnippetRequest) -> Dict[str, Any]:
    """Test AST extraction, Ruff linting, and Bandit security scanning directly on a Python snippet."""
    # Run AST extraction
    ast_summary = analyze_python_source(
        file_path=payload.filename,
        source_code=payload.code,
    )

    # Run Static Analysis (Ruff + Bandit)
    report = await analyze_python_content(
        file_path=payload.filename,
        source_code=payload.code,
    )

    return {
        "filename": payload.filename,
        "ast_summary": {
            "functions_count": len(ast_summary.functions),
            "functions": [
                {
                    "name": fn.qualified_name,
                    "parameters": fn.parameters,
                    "return_annotation": fn.return_annotation,
                    "cyclomatic_complexity": fn.cyclomatic_complexity,
                    "has_exceptions": fn.has_exceptions,
                    "start_line": fn.start_line,
                    "end_line": fn.end_line,
                }
                for fn in ast_summary.functions
            ],
            "classes": ast_summary.classes,
            "imports": ast_summary.imports,
            "has_syntax_error": ast_summary.has_syntax_error,
        },
        "static_report": {
            "total_findings": report.total_findings,
            "security_findings_count": report.security_findings_count,
            "quality_findings_count": report.quality_findings_count,
            "bug_findings_count": report.bug_findings_count,
            "highest_severity": report.highest_severity,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "tool": f.tool,
                    "category": f.category,
                    "severity": f.severity,
                    "line_number": f.line_number,
                    "description": f.description,
                }
                for f in report.findings
            ],
        },
    }

