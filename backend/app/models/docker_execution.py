"""Docker Sandbox Execution database model."""

from typing import Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin


class DockerExecution(Base, TimestampMixin):
    """Execution output from running a generated test inside an isolated Docker sandbox."""

    __tablename__ = "docker_executions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    generated_test_id: Mapped[int] = mapped_column(
        ForeignKey("generated_tests.id", ondelete="CASCADE"), unique=True, index=True
    )
    container_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    execution_status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # PASS, ASSERTION_FAILURE, RUNTIME_EXCEPTION, TEST_SYNTAX_ERROR, TEST_IMPORT_ERROR, TIMEOUT, ENVIRONMENT_ERROR
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stdout: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stderr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exception_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    exception_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timeout_reached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    memory_limit_exceeded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    generated_test: Mapped["GeneratedTest"] = relationship("GeneratedTest", back_populates="docker_execution")
    reproducibility: Mapped[Optional["Reproducibility"]] = relationship(
        "Reproducibility", back_populates="docker_execution", uselist=False
    )

