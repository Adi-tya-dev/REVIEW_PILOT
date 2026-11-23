"""Review Session database model."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin


class ReviewSession(Base, TimestampMixin):
    """Execution session for analyzing a Pull Request."""

    __tablename__ = "review_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pull_request_id: Mapped[int] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", nullable=False
    )  # PENDING, RUNNING, COMPLETED, FAILED
    slm_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    llm_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    escalated_to_llm: Mapped[bool] = mapped_column(default=False, nullable=False)
    total_latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="review_sessions")
    findings: Mapped[List["Finding"]] = relationship(
        "Finding", back_populates="review_session", cascade="all, delete-orphan"
    )
    generated_tests: Mapped[List["GeneratedTest"]] = relationship(
        "GeneratedTest", back_populates="review_session", cascade="all, delete-orphan"
    )

