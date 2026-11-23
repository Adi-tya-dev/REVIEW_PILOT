"""Integration test for benchmark API endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_get_benchmark_comparison_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/api/v1/benchmarks/comparison")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        approaches = [d["approach"] for d in data]
        assert "Static-only" in approaches
        assert "LLM-only" in approaches
        assert "Hybrid SLM-LLM" in approaches

