"""Generated Test database model."""

from typing import Optional
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin


class GeneratedTest(Base, TimestampMixin):
    """An edge-case pytest test generated for an identified issue or function."""

    __tablename__ = "generated_tests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_session_id: Mapped[int] = mapped_column(
        ForeignKey("review_sessions.id", ondelete="CASCADE"), index=True
    )
    finding_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("findings.id", ondelete="SET NULL"), nullable=True, index=True
    )
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_function: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    input_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generator_model: Mapped[str] = mapped_column(String(50), nullable=False)  # 'slm' or 'llm'
    original_test_code: Mapped[str] = mapped_column(Text, nullable=False)
    repaired_test_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validation_status: Mapped[str] = mapped_column(
        String(50), default="VALID", nullable=False
    )  # VALID, SYNTAX_REPAIRED, INVALID_ORACLE_MUTATION, INVALID_SYNTAX

    # Relationships
    review_session: Mapped["ReviewSession"] = relationship("ReviewSession", back_populates="generated_tests")
    finding: Mapped[Optional["Finding"]] = relationship("Finding", back_populates="generated_test")
    docker_execution: Mapped[Optional["DockerExecution"]] = relationship(
        "DockerExecution", back_populates="generated_test", uselist=False
    )

