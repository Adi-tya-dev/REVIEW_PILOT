"""Async GitHub REST API client for repository and pull request operations."""

from typing import Any, Dict, List, Optional
import httpx
from backend.app.config import settings
from backend.app.schemas.github import GitHubPullRequestPayload, GitHubUser, GitHubBranchRef, GitHubRepoRef


class GitHubAPIError(Exception):
    """Custom exception raised when a GitHub API request fails."""

    def __init__(self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"GitHub API [{status_code}]: {message}")
        self.status_code = status_code
        self.message = message
        self.details = details or {}


class GitHubClient:
    """Async client communicating with the GitHub v3 REST API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token if token is not None else settings.GITHUB_TOKEN
        self.base_url = settings.GITHUB_API_BASE_URL.rstrip("/")
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ReviewPilot-Research-Tool/0.1.0",
        }
        if self.token and self.token.strip() and not self.token.startswith("ghp_your"):
            self._headers["Authorization"] = f"Bearer {self.token.strip()}"

    async def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository details."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with httpx.AsyncClient(headers=self._headers, timeout=15.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise GitHubAPIError(resp.status_code, resp.text)
            return resp.json()

    async def get_pull_request(self, owner: str, repo: str, pull_number: int) -> GitHubPullRequestPayload:
        """Fetch Pull Request details."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        async with httpx.AsyncClient(headers=self._headers, timeout=15.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise GitHubAPIError(resp.status_code, resp.text)
            data = resp.json()
            return GitHubPullRequestPayload(
                id=data.get("id"),
                number=data["number"],
                title=data["title"],
                state=data["state"],
                html_url=data["html_url"],
                diff_url=data["diff_url"],
                user=GitHubUser(
                    login=data["user"]["login"],
                    id=data["user"].get("id"),
                    avatar_url=data["user"].get("avatar_url"),
                    html_url=data["user"].get("html_url"),
                ),
                base=GitHubBranchRef(
                    label=data["base"].get("label"),
                    ref=data["base"]["ref"],
                    sha=data["base"]["sha"],
                ),
                head=GitHubBranchRef(
                    label=data["head"].get("label"),
                    ref=data["head"]["ref"],
                    sha=data["head"]["sha"],
                ),
                body=data.get("body"),
                changed_files=data.get("changed_files", 0),
            )

    async def get_pull_request_diff(self, owner: str, repo: str, pull_number: int) -> str:
        """Fetch the raw unified git diff for a Pull Request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        diff_headers = dict(self._headers)
        diff_headers["Accept"] = "application/vnd.github.v3.diff"

        async with httpx.AsyncClient(headers=diff_headers, timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise GitHubAPIError(resp.status_code, resp.text)
            return resp.text

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str:
        """Fetch raw file content from a repository at a given ref/commit."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        raw_headers = dict(self._headers)
        raw_headers["Accept"] = "application/vnd.github.v3.raw"

        async with httpx.AsyncClient(headers=raw_headers, timeout=20.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise GitHubAPIError(resp.status_code, resp.text)
            return resp.text

    async def post_review_comment(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: int,
        side: str = "RIGHT",
    ) -> Dict[str, Any]:
        """Post an inline review comment on a specific line of a Pull Request.

        Never automatically approves or merges the PR.
        """
        if not self.token or self.token.startswith("ghp_your"):
            raise GitHubAPIError(
                401, "A valid GitHub Personal Access Token is required to post review comments."
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/comments"
        payload = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line,
            "side": side,
        }
        async with httpx.AsyncClient(headers=self._headers, timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code not in (200, 201):
                raise GitHubAPIError(resp.status_code, resp.text)
            return resp.json()

