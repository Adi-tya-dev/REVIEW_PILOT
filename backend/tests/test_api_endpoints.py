"""Integration tests for FastAPI endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.database import init_db
from backend.app.main import app


@pytest.fixture(autouse=True)
async def setup_test_database():
    """Ensure database tables exist before running API tests."""
    await init_db()


@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["app"] == "ReviewPilot"


@pytest.mark.asyncio
async def test_analyze_snippet_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        code = "def divide(a: int, b: int) -> float:\n    return a / b\n"
        resp = await client.post(
            "/api/v1/findings/analyze-snippet",
            json={"filename": "calc.py", "code": code},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["filename"] == "calc.py"
        assert data["ast_summary"]["functions_count"] == 1
        fn = data["ast_summary"]["functions"][0]
        assert fn["name"] == "divide"
        assert fn["return_annotation"] == "float"


@pytest.mark.asyncio
async def test_analyze_local_diff_endpoint():
    raw_diff = """diff --git a/vuln.py b/vuln.py
--- a/vuln.py
+++ b/vuln.py
@@ -1,3 +1,5 @@
+import subprocess
+def run_cmd(c):
+    subprocess.Popen(c, shell=True)
"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/v1/pull-requests/analyze/local",
            json={
                "title": "Fix command runner",
                "owner": "testorg",
                "repo": "testrepo",
                "pr_number": 99,
                "raw_diff": raw_diff,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "success"
        assert data["python_files_count"] == 1
        assert data["total_static_findings"] > 0

        # Query pull requests list
        list_resp = await client.get("/api/v1/pull-requests")
        assert list_resp.status_code == 200
        prs = list_resp.json()
        assert any(p["pr_number"] == 99 for p in prs)

