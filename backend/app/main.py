"""ReviewPilot FastAPI Application Entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.benchmarks import router as benchmarks_router
from backend.app.api.v1.executions import router as executions_router
from backend.app.api.v1.findings import router as findings_router
from backend.app.api.v1.pull_requests import router as pr_router
from backend.app.api.v1.routing import router as routing_router
from backend.app.api.v1.tests import router as tests_router
from backend.app.api.v1.webhooks import router as webhooks_router
from backend.app.config import settings
from backend.app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager to initialize DB tables on startup."""
    await init_db()
    yield


app = FastAPI(
    title="ReviewPilot API",
    description="Evidence-Grounded, Cost-Aware SLM–LLM Routing for Python GitHub Pull Requests",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API Routers
app.include_router(webhooks_router, prefix="/api/v1")
app.include_router(pr_router, prefix="/api/v1")
app.include_router(findings_router, prefix="/api/v1")
app.include_router(routing_router, prefix="/api/v1")
app.include_router(tests_router, prefix="/api/v1")
app.include_router(executions_router, prefix="/api/v1")
app.include_router(benchmarks_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint displaying system configuration."""
    return {
        "status": "healthy",
        "app": "ReviewPilot",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "has_github_token": settings.has_github_token,
        "webhook_secret_configured": bool(settings.GITHUB_WEBHOOK_SECRET),
        "slm_model": settings.SLM_MODEL_NAME,
        "llm_provider": settings.LLM_PROVIDER,
    }

