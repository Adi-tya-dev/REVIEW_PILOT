"""Pull Request database model."""

from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin


class PullRequest(Base, TimestampMixin):
    """GitHub Pull Request ingested for review."""

    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), index=True)
    pr_number: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    html_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    diff_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    base_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    head_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    base_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    head_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    changed_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    raw_diff: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository", back_populates="pull_requests")
    review_sessions: Mapped[List["ReviewSession"]] = relationship(
        "ReviewSession", back_populates="pull_request", cascade="all, delete-orphan"
    )

