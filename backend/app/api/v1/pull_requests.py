"""Pull Request API routes for ingestion, listing, and analysis triggers."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.database import get_db
from backend.app.models.finding import Finding
from backend.app.models.pull_request import PullRequest
from backend.app.models.repository import Repository
from backend.app.models.review_session import ReviewSession
from backend.app.services.ast_analyzer.extractor import analyze_python_source
from backend.app.services.github.client import GitHubAPIError, GitHubClient
from backend.app.services.github.diff_parser import parse_diff
from backend.app.services.static_analysis.aggregator import analyze_python_content

router = APIRouter(prefix="/pull-requests", tags=["Pull Requests"])


class AnalyzeLocalDiffRequest(BaseModel):
    """Payload to trigger analysis from a raw git diff directly."""
    title: str
    owner: str = "local"
    repo: str = "test-repo"
    pr_number: int = 1
    raw_diff: str


@router.get("", response_model=List[Dict[str, Any]])
async def list_pull_requests(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List all ingested pull requests."""
    stmt = (
        select(PullRequest)
        .options(selectinload(PullRequest.repository), selectinload(PullRequest.review_sessions))
        .order_by(desc(PullRequest.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    prs = result.scalars().all()

    return [
        {
            "id": pr.id,
            "pr_number": pr.pr_number,
            "title": pr.title,
            "state": pr.state,
            "author": pr.author,
            "html_url": pr.html_url,
            "repository": pr.repository.full_name if pr.repository else "",
            "base_branch": pr.base_branch,
            "head_branch": pr.head_branch,
            "head_sha": pr.head_sha,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "review_sessions_count": len(pr.review_sessions),
        }
        for pr in prs
    ]


@router.get("/{pr_id}", response_model=Dict[str, Any])
async def get_pull_request_details(
    pr_id: int,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get full details of a specific Pull Request including parsed diff."""
    stmt = (
        select(PullRequest)
        .options(selectinload(PullRequest.repository), selectinload(PullRequest.review_sessions))
        .where(PullRequest.id == pr_id)
    )
    result = await db.execute(stmt)
    pr = result.scalar_one_or_none()

    if not pr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pull Request not found")

    parsed_diff = parse_diff(pr.raw_diff or "")

    return {
        "id": pr.id,
        "pr_number": pr.pr_number,
        "title": pr.title,
        "state": pr.state,
        "author": pr.author,
        "html_url": pr.html_url,
        "repository": pr.repository.full_name if pr.repository else "",
        "base_branch": pr.base_branch,
        "head_branch": pr.head_branch,
        "base_sha": pr.base_sha,
        "head_sha": pr.head_sha,
        "changed_files_count": len(parsed_diff.files),
        "python_files": [f.filename for f in parsed_diff.python_files],
        "total_additions": parsed_diff.total_additions,
        "total_deletions": parsed_diff.total_deletions,
        "raw_diff": pr.raw_diff,
        "review_sessions": [
            {
                "id": s.id,
                "status": s.status,
                "slm_calls": s.slm_calls,
                "llm_calls": s.llm_calls,
                "total_latency_ms": s.total_latency_ms,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in pr.review_sessions
        ],
    }


@router.post("/analyze/github/{owner}/{repo}/{pr_number}", status_code=status.HTTP_201_CREATED)
async def analyze_github_pr(
    owner: str,
    repo: str,
    pr_number: int,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Fetch a real Pull Request from GitHub, extract diff & modified Python functions, and execute static analysis."""
    client = GitHubClient()
    try:
        pr_payload = await client.get_pull_request(owner, repo, pr_number)
        raw_diff = await client.get_pull_request_diff(owner, repo, pr_number)
    except GitHubAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    # Ingest or update Repository
    repo_full_name = f"{owner}/{repo}"
    stmt = select(Repository).where(Repository.full_name == repo_full_name)
    result = await db.execute(stmt)
    db_repo = result.scalar_one_or_none()

    if not db_repo:
        db_repo = Repository(
            name=repo,
            owner=owner,
            full_name=repo_full_name,
            html_url=f"https://github.com/{owner}/{repo}",
            default_branch=pr_payload.base.ref or "main",
        )
        db.add(db_repo)
        await db.flush()

    # Ingest Pull Request
    stmt = select(PullRequest).where(
        PullRequest.repository_id == db_repo.id, PullRequest.pr_number == pr_number
    )
    result = await db.execute(stmt)
    db_pr = result.scalar_one_or_none()

    if not db_pr:
        db_pr = PullRequest(
            repository_id=db_repo.id,
            pr_number=pr_number,
            title=pr_payload.title,
            state=pr_payload.state,
            author=pr_payload.user.login,
            html_url=pr_payload.html_url,
            diff_url=pr_payload.diff_url,
            base_branch=pr_payload.base.ref,
            head_branch=pr_payload.head.ref,
            base_sha=pr_payload.base.sha,
            head_sha=pr_payload.head.sha,
            changed_files_count=pr_payload.changed_files or 0,
            raw_diff=raw_diff,
        )
        db.add(db_pr)
        await db.flush()
    else:
        db_pr.raw_diff = raw_diff
        db_pr.title = pr_payload.title

    # Start Review Session
    review_session = ReviewSession(
        pull_request_id=db_pr.id,
        status="RUNNING",
    )
    db.add(review_session)
    await db.flush()

    # Parse unified diff
    parsed_diff = parse_diff(raw_diff)
    total_findings = 0

    # Analyze Python files present in diff
    for modified_file in parsed_diff.python_files:
        # Attempt to fetch modified file content from GitHub head ref
        try:
            content = await client.get_file_content(owner, repo, modified_file.filename, pr_payload.head.sha)
        except Exception:
            # If cannot fetch whole file, reconstruct from patch lines
            content = "\n".join([line.content for hunk in modified_file.hunks for line in hunk.lines if line.line_type in ('add', 'context')])

        if not content:
            continue

        report = await analyze_python_content(
            file_path=modified_file.filename,
            source_code=content,
            modified_line_numbers=set(modified_file.added_line_numbers),
        )

        for finding in report.findings:
            db_finding = Finding(
                review_session_id=review_session.id,
                rule_id=finding.rule_id,
                tool=finding.tool,
                category=finding.category,
                severity=finding.severity,
                file_path=finding.file_path,
                line_number=finding.line_number,
                end_line_number=finding.end_line_number,
                description=finding.description,
                code_snippet=finding.code_snippet,
                confidence=finding.confidence,
                evidence_status="STATIC_WARNING",
            )
            db.add(db_finding)
            total_findings += 1

    review_session.status = "COMPLETED"
    await db.flush()

    return {
        "status": "success",
        "pull_request_id": db_pr.id,
        "review_session_id": review_session.id,
        "python_files_analyzed": len(parsed_diff.python_files),
        "total_static_findings": total_findings,
    }


@router.post("/analyze/local", status_code=status.HTTP_201_CREATED)
async def analyze_local_diff(
    payload: AnalyzeLocalDiffRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Analyze a raw unified git diff without calling GitHub REST API.

    Allows immediate offline testing of Priority 1 and Priority 2 pipelines.
    """
    repo_full_name = f"{payload.owner}/{payload.repo}"
    stmt = select(Repository).where(Repository.full_name == repo_full_name)
    result = await db.execute(stmt)
    db_repo = result.scalar_one_or_none()

    if not db_repo:
        db_repo = Repository(
            name=payload.repo,
            owner=payload.owner,
            full_name=repo_full_name,
            html_url=f"https://github.com/{payload.owner}/{payload.repo}",
            default_branch="main",
        )
        db.add(db_repo)
        await db.flush()

    parsed_diff = parse_diff(payload.raw_diff)

    db_pr = PullRequest(
        repository_id=db_repo.id,
        pr_number=payload.pr_number,
        title=payload.title,
        state="open",
        author="local-dev",
        html_url=f"https://github.com/{payload.owner}/{payload.repo}/pull/{payload.pr_number}",
        diff_url=f"https://github.com/{payload.owner}/{payload.repo}/pull/{payload.pr_number}.diff",
        base_branch="main",
        head_branch="feature",
        base_sha="0000000000000000000000000000000000000000",
        head_sha="1111111111111111111111111111111111111111",
        changed_files_count=len(parsed_diff.files),
        raw_diff=payload.raw_diff,
    )
    db.add(db_pr)
    await db.flush()

    review_session = ReviewSession(
        pull_request_id=db_pr.id,
        status="RUNNING",
    )
    db.add(review_session)
    await db.flush()

    total_findings = 0
    file_ast_summaries = []

    for modified_file in parsed_diff.python_files:
        # Reconstruct file from patch
        content = "\n".join(
            [line.content for hunk in modified_file.hunks for line in hunk.lines if line.line_type in ("add", "context")]
        )
        if not content:
            continue

        # AST analysis
        ast_summary = analyze_python_source(
            file_path=modified_file.filename,
            source_code=content,
            modified_line_numbers=set(modified_file.added_line_numbers),
        )
        file_ast_summaries.append(ast_summary)

        # Static analysis (Ruff + Bandit)
        report = await analyze_python_content(
            file_path=modified_file.filename,
            source_code=content,
            modified_line_numbers=set(modified_file.added_line_numbers),
        )

        for finding in report.findings:
            db_finding = Finding(
                review_session_id=review_session.id,
                rule_id=finding.rule_id,
                tool=finding.tool,
                category=finding.category,
                severity=finding.severity,
                file_path=finding.file_path,
                line_number=finding.line_number,
                end_line_number=finding.end_line_number,
                description=finding.description,
                code_snippet=finding.code_snippet,
                confidence=finding.confidence,
                evidence_status="STATIC_WARNING",
            )
            db.add(db_finding)
            total_findings += 1

    review_session.status = "COMPLETED"
    await db.flush()

    return {
        "status": "success",
        "pull_request_id": db_pr.id,
        "review_session_id": review_session.id,
        "python_files_count": len(parsed_diff.python_files),
        "total_static_findings": total_findings,
        "functions_detected": sum(len(s.functions) for s in file_ast_summaries),
    }

