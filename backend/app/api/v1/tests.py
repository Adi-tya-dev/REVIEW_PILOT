"""API endpoints for edge-case pytest generation and Test Oracle protection."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.generated_test import GeneratedTest
from backend.app.schemas.ai import DefectHypothesis
from backend.app.schemas.ast_nodes import FunctionSlice
from backend.app.schemas.tests import TestCaseDraft
from backend.app.services.test_gen.generator import generate_edge_case_tests_for_function, generate_test_from_hypothesis

router = APIRouter(prefix="/tests", tags=["Test Generation"])


class GenerateFunctionTestsRequest(BaseModel):
    module_path: str
    function_name: str
    source_code: str
    parameters: List[str]


class GenerateHypothesisTestRequest(BaseModel):
    module_path: str
    target_function: str
    hypothesis: DefectHypothesis
    review_session_id: int


@router.post("/generate-function-edge-cases", response_model=List[TestCaseDraft])
async def generate_function_edge_cases(
    payload: GenerateFunctionTestsRequest,
) -> List[TestCaseDraft]:
    """Generate systematic edge-case pytest tests for a given function signature."""
    func_slice = FunctionSlice(
        name=payload.function_name,
        start_line=1,
        end_line=len(payload.source_code.splitlines()),
        parameters=payload.parameters,
        source_code=payload.source_code,
    )
    return generate_edge_case_tests_for_function(func_slice, payload.module_path)


@router.post("/generate-from-hypothesis", response_model=TestCaseDraft)
async def generate_from_hypothesis(
    payload: GenerateHypothesisTestRequest,
    db: AsyncSession = Depends(get_db),
) -> TestCaseDraft:
    """Generate and Oracle-validate a pytest test case targeting a specific defect hypothesis."""
    test_draft = generate_test_from_hypothesis(
        hypothesis=payload.hypothesis,
        module_path=payload.module_path,
        target_function_name=payload.target_function,
    )

    # Persist generated test to database
    db_test = GeneratedTest(
        review_session_id=payload.review_session_id,
        test_name=test_draft.test_name,
        target_function=payload.target_function,
        file_path=payload.module_path,
        input_values=test_draft.input_values,
        expected_behavior=test_draft.expected_behavior,
        reason=test_draft.reason,
        generator_model=test_draft.generator_model,
        original_test_code=test_draft.original_test_code,
        repaired_test_code=test_draft.repaired_test_code,
        validation_status=test_draft.validation_status,
    )
    db.add(db_test)
    await db.flush()

    return test_draft


@router.get("/review/{review_session_id}", response_model=List[Dict[str, Any]])
async def list_generated_tests_for_review(
    review_session_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List all generated tests and their validation statuses for a given review session."""
    stmt = select(GeneratedTest).where(GeneratedTest.review_session_id == review_session_id)
    result = await db.execute(stmt)
    tests = result.scalars().all()

    return [
        {
            "id": t.id,
            "test_name": t.test_name,
            "target_function": t.target_function,
            "file_path": t.file_path,
            "input_values": t.input_values,
            "expected_behavior": t.expected_behavior,
            "validation_status": t.validation_status,
            "generator_model": t.generator_model,
            "original_test_code": t.original_test_code,
            "repaired_test_code": t.repaired_test_code,
        }
        for t in tests
    ]

