"""Reproducibility Assessment database model."""

from typing import Optional
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin


class Reproducibility(Base, TimestampMixin):
    """Reproducibility and evidence grounding record for a finding."""

    __tablename__ = "reproducibility_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    docker_execution_id: Mapped[int] = mapped_column(
        ForeignKey("docker_executions.id", ondelete="CASCADE"), unique=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # CONFIRMED_REPRODUCIBLE, STATIC_WARNING, AI_HYPOTHESIS, TEST_GENERATION_ERROR, ENVIRONMENT_ERROR, NEEDS_REVIEW, ABSTAINED
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    input_trigger: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_vs_actual: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    docker_execution: Mapped["DockerExecution"] = relationship("DockerExecution", back_populates="reproducibility")

