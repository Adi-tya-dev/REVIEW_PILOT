"""Pydantic schemas for GitHub payloads, diffs, and pull requests."""

from typing import List, Optional
from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """GitHub user summary."""
    login: str
    id: Optional[int] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None


class GitHubRepoRef(BaseModel):
    """Repository reference in PR payload."""
    name: str
    full_name: str
    html_url: str
    private: bool = False
    default_branch: str = "main"
    owner: GitHubUser


class GitHubBranchRef(BaseModel):
    """Branch reference in PR payload (base or head)."""
    label: Optional[str] = None
    ref: str
    sha: str
    repo: Optional[GitHubRepoRef] = None


class GitHubPullRequestPayload(BaseModel):
    """GitHub Pull Request detail payload."""
    id: Optional[int] = None
    number: int
    title: str
    state: str = "open"
    html_url: str
    diff_url: str
    user: GitHubUser
    base: GitHubBranchRef
    head: GitHubBranchRef
    body: Optional[str] = None
    changed_files: Optional[int] = 0


class GitHubWebhookPRAction(BaseModel):
    """GitHub Webhook 'pull_request' event payload."""
    action: str  # opened, synchronize, reopened, closed, etc.
    number: int
    pull_request: GitHubPullRequestPayload
    repository: GitHubRepoRef
    sender: GitHubUser


class ChangedLine(BaseModel):
    """Representation of a single changed line in a diff."""
    line_type: str  # 'add', 'delete', 'context'
    content: str
    old_line_number: Optional[int] = None
    new_line_number: Optional[int] = None


class DiffHunk(BaseModel):
    """A hunk within a unified git diff."""
    header: str
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    lines: List[ChangedLine] = Field(default_factory=list)


class ModifiedFile(BaseModel):
    """A file modified within a Pull Request."""
    filename: str
    status: str = "modified"  # 'added', 'modified', 'removed', 'renamed'
    previous_filename: Optional[str] = None
    is_python: bool = False
    additions: int = 0
    deletions: int = 0
    patch: Optional[str] = None
    hunks: List[DiffHunk] = Field(default_factory=list)
    added_line_numbers: List[int] = Field(default_factory=list)
    raw_content: Optional[str] = None


class ParsedDiff(BaseModel):
    """Structured collection of modified files extracted from a git diff."""
    files: List[ModifiedFile] = Field(default_factory=list)

    @property
    def python_files(self) -> List[ModifiedFile]:
        """Filter only Python files (.py)."""
        return [f for f in self.files if f.is_python]

    @property
    def total_additions(self) -> int:
        return sum(f.additions for f in self.files)

    @property
    def total_deletions(self) -> int:
        return sum(f.deletions for f in self.files)

