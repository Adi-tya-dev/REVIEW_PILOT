"""API endpoints for Docker test execution and evidence grounding."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.docker_execution import DockerExecution
from backend.app.models.generated_test import GeneratedTest
from backend.app.models.reproducibility import Reproducibility
from backend.app.schemas.ai import DefectHypothesis
from backend.app.schemas.execution import EvidenceRecord, ExecutionRequest, ExecutionResult
from backend.app.services.evidence.evaluator import evaluate_evidence
from backend.app.services.evidence.github_reporter import format_github_review_comment
from backend.app.services.sandbox.docker_runner import DockerSandboxRunner

router = APIRouter(prefix="/executions", tags=["Docker Executions"])


class RunTestInDockerRequest(BaseModel):
    generated_test_id: int
    source_filename: str
    source_code: str


class EvaluateEvidenceRequest(BaseModel):
    hypothesis: DefectHypothesis
    execution_result: Optional[ExecutionResult] = None


@router.post("/run-test", response_model=ExecutionResult)
async def run_test_in_sandbox(
    payload: RunTestInDockerRequest,
    db: AsyncSession = Depends(get_db),
) -> ExecutionResult:
    """Run a generated test case in an isolated Docker container with CPU, memory, and timeout limits."""
    stmt = select(GeneratedTest).where(GeneratedTest.id == payload.generated_test_id)
    result = await db.execute(stmt)
    test_record = result.scalar_one_or_none()

    if not test_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated test not found")

    test_code_to_run = test_record.repaired_test_code or test_record.original_test_code

    runner = DockerSandboxRunner()
    req = ExecutionRequest(
        test_code=test_code_to_run,
        target_filename=payload.source_filename,
        source_files={payload.source_filename: payload.source_code},
    )

    exec_result = runner.execute_test(req)

    # Persist DockerExecution record
    db_exec = DockerExecution(
        generated_test_id=test_record.id,
        container_id=exec_result.container_id,
        execution_status=exec_result.execution_status,
        exit_code=exec_result.exit_code,
        execution_time_ms=exec_result.execution_time_ms,
        stdout=exec_result.stdout,
        stderr=exec_result.stderr,
        exception_name=exec_result.exception_name,
        exception_details=exec_result.exception_details,
        timeout_reached=exec_result.timeout_reached,
    )
    db.add(db_exec)
    await db.flush()

    return exec_result


@router.post("/evaluate-evidence", response_model=EvidenceRecord)
async def evaluate_evidence_endpoint(payload: EvaluateEvidenceRequest) -> EvidenceRecord:
    """Evaluate reproducibility status and generate formatted GitHub markdown comment."""
    evidence = evaluate_evidence(
        hypothesis=payload.hypothesis,
        execution_result=payload.execution_result,
    )
    evidence.comment_markdown = format_github_review_comment(
        hypothesis=payload.hypothesis,
        evidence=evidence,
        execution_result=payload.execution_result,
    )
    return evidence
