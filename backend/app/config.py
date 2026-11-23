"""Application configuration settings for ReviewPilot."""

from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """ReviewPilot configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "dev_secret_key_reviewpilot_2026_secure_random_seed"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'reviewpilot.db'}"

    # GitHub Integration
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = "reviewpilot_webhook_secret_2026"
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # Local SLM (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    SLM_MODEL_NAME: str = "qwen2.5-coder:1.5b"
    SLM_TIMEOUT_SECONDS: int = 120

    # LLM Escalation
    LLM_PROVIDER: str = "ollama"  # 'ollama', 'openai', 'openrouter', 'anthropic'
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "qwen2.5-coder:7b"
    LLM_BASE_URL: str = "http://localhost:11434/v1"

    # Hybrid Router Parameters
    ROUTER_COMPLEXITY_THRESHOLD: int = 10
    ROUTER_CONFIDENCE_THRESHOLD: float = 0.75
    ROUTER_MAX_ESCALATION_ATTEMPTS: int = 2

    # Docker Sandbox Parameters
    DOCKER_IMAGE: str = "python:3.11-slim"
    DOCKER_EXECUTION_TIMEOUT_SECONDS: int = 15
    DOCKER_MEMORY_LIMIT: str = "512m"
    DOCKER_CPU_LIMIT: float = 1.0
    DOCKER_NETWORK_MODE: str = "none"

    @property
    def cors_origins(self) -> List[str]:
        """Return allowed CORS origins as a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def has_github_token(self) -> bool:
        """Check if a valid GitHub personal access token is configured."""
        return bool(self.GITHUB_TOKEN and self.GITHUB_TOKEN.strip() and not self.GITHUB_TOKEN.startswith("ghp_your"))


# Singleton settings instance
settings = Settings()
