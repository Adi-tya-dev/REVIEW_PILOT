"""GitHub Webhook API route handler."""

import json
from typing import Any, Dict
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.pull_request import PullRequest
from backend.app.models.repository import Repository
from backend.app.models.review_session import ReviewSession
from backend.app.services.github.diff_parser import parse_diff
from backend.app.services.github.webhook_verifier import verify_signature

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/github", status_code=status.HTTP_200_OK)
async def github_webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Receive and securely process incoming GitHub Webhook events.

    Verifies HMAC-SHA256 signature and handles 'pull_request' events.
    """
    raw_body = await request.body()

    # Verify webhook signature if secret is configured
    if settings.GITHUB_WEBHOOK_SECRET:
        if not verify_signature(
            payload_bytes=raw_body,
            signature_header=x_hub_signature_256,
            secret=settings.GITHUB_WEBHOOK_SECRET,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid HMAC SHA-256 webhook signature",
            )

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    # We only process 'pull_request' events
    if x_github_event != "pull_request":
        return {
            "status": "ignored",
            "message": f"Event '{x_github_event}' is not handled; ReviewPilot listens for 'pull_request'",
        }

    action = payload.get("action")
    pr_data = payload.get("pull_request")
    repo_data = payload.get("repository")

    if not pr_data or not repo_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing PR or repository payload data")

    # Ingest repository
    repo_full_name = repo_data["full_name"]
    stmt = select(Repository).where(Repository.full_name == repo_full_name)
    result = await db.execute(stmt)
    repo = result.scalar_one_or_none()

    if not repo:
        repo = Repository(
            name=repo_data["name"],
            owner=repo_data["owner"]["login"],
            full_name=repo_full_name,
            html_url=repo_data["html_url"],
            default_branch=repo_data.get("default_branch", "main"),
            is_private=repo_data.get("private", False),
            webhook_configured=True,
        )
        db.add(repo)
        await db.flush()

    # Ingest or update Pull Request
    pr_number = pr_data["number"]
    stmt = select(PullRequest).where(
        PullRequest.repository_id == repo.id, PullRequest.pr_number == pr_number
    )
    result = await db.execute(stmt)
    pr = result.scalar_one_or_none()

    if not pr:
        pr = PullRequest(
            repository_id=repo.id,
            pr_number=pr_number,
            title=pr_data["title"],
            state=pr_data.get("state", "open"),
            author=pr_data["user"]["login"],
            html_url=pr_data["html_url"],
            diff_url=pr_data.get("diff_url", f"{pr_data['html_url']}.diff"),
            base_branch=pr_data["base"]["ref"],
            head_branch=pr_data["head"]["ref"],
            base_sha=pr_data["base"]["sha"],
            head_sha=pr_data["head"]["sha"],
            changed_files_count=pr_data.get("changed_files", 0),
        )
        db.add(pr)
        await db.flush()
    else:
        # Update existing PR state and head sha
        pr.title = pr_data["title"]
        pr.state = pr_data.get("state", "open")
        pr.head_sha = pr_data["head"]["sha"]
        pr.changed_files_count = pr_data.get("changed_files", pr.changed_files_count)

    # Spawn new review session for relevant PR actions
    if action in ("opened", "synchronize", "reopened"):
        review_session = ReviewSession(
            pull_request_id=pr.id,
            status="PENDING",
        )
        db.add(review_session)
        await db.flush()

        return {
            "status": "accepted",
            "action": action,
            "pr_number": pr_number,
            "repository": repo_full_name,
            "review_session_id": review_session.id,
        }

    return {
        "status": "acknowledged",
        "action": action,
        "pr_number": pr_number,
    }

