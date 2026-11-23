"""Static & AI Analysis Finding database model."""

from typing import Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin


class Finding(Base, TimestampMixin):
    """A detected bug, security risk, or code quality issue."""

    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_session_id: Mapped[int] = mapped_column(
        ForeignKey("review_sessions.id", ondelete="CASCADE"), index=True
    )
    rule_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    tool: Mapped[str] = mapped_column(String(50), nullable=False)  # 'ruff', 'bandit', 'ast', 'slm', 'llm'
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 'security', 'quality', 'bug'
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    code_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_status: Mapped[str] = mapped_column(
        String(50), default="STATIC_WARNING", nullable=False
    )  # CONFIRMED_REPRODUCIBLE, STATIC_WARNING, AI_HYPOTHESIS, etc.

    # Relationships
    review_session: Mapped["ReviewSession"] = relationship("ReviewSession", back_populates="findings")
    generated_test: Mapped[Optional["GeneratedTest"]] = relationship(
        "GeneratedTest", back_populates="finding", uselist=False
    )

