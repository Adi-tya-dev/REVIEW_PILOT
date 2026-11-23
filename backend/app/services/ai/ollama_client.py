"""Async client for local Small Language Model (SLM) inference via Ollama."""

import json
import time
from typing import Any, Dict, List, Optional
import httpx
from backend.app.config import settings
from backend.app.schemas.ai import DefectHypothesis, ModelReviewResponse
from backend.app.services.ai.prompts import REVIEW_SYSTEM_PROMPT, build_review_user_prompt
from backend.app.schemas.findings import StaticFinding
from backend.app.services.router.cost_tracker import calculate_cost, estimate_tokens_from_text


class OllamaClient:
    """Async client connecting to local Ollama instance for SLM code review."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.SLM_MODEL_NAME
        self.timeout = timeout or settings.SLM_TIMEOUT_SECONDS

    async def is_available(self) -> bool:
        """Check if Ollama service is reachable and running."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def review_code(
        self,
        file_path: str,
        source_code: str,
        modified_lines: List[int],
        static_findings: Optional[List[StaticFinding]] = None,
    ) -> ModelReviewResponse:
        """Execute SLM code review using Ollama."""
        user_prompt = build_review_user_prompt(
            file_path=file_path,
            source_code=source_code,
            modified_lines=modified_lines,
            static_findings=static_findings,
        )

        prompt_tokens_est = estimate_tokens_from_text(REVIEW_SYSTEM_PROMPT + user_prompt)
        start_time = time.perf_counter()

        payload = {
            "model": self.model_name,
            "system": REVIEW_SYSTEM_PROMPT,
            "prompt": user_prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for deterministic, factual review
                "top_p": 0.9,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)

                if resp.status_code != 200:
                    return ModelReviewResponse(
                        model_name=self.model_name,
                        model_type="slm",
                        hypotheses=[],
                        raw_response=resp.text,
                        latency_ms=elapsed_ms,
                        parse_success=False,
                        error_message=f"Ollama returned HTTP {resp.status_code}: {resp.text}",
                    )

                data = resp.json()
                raw_text = data.get("response", "").strip()

                # Parse JSON output from Ollama
                hypotheses = self._parse_hypotheses(raw_text, file_path)
                eval_count = data.get("eval_count", estimate_tokens_from_text(raw_text))
                prompt_eval_count = data.get("prompt_eval_count", prompt_tokens_est)

                return ModelReviewResponse(
                    model_name=self.model_name,
                    model_type="slm",
                    hypotheses=hypotheses,
                    raw_response=raw_text,
                    prompt_tokens=prompt_eval_count,
                    completion_tokens=eval_count,
                    latency_ms=elapsed_ms,
                    estimated_cost_usd=calculate_cost(self.model_name, prompt_eval_count, eval_count),
                    parse_success=True,
                )

        except httpx.ConnectError:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ModelReviewResponse(
                model_name=self.model_name,
                model_type="slm",
                hypotheses=[],
                raw_response="",
                latency_ms=elapsed_ms,
                parse_success=False,
                error_message=f"Cannot connect to Ollama at {self.base_url}. Service may not be running.",
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ModelReviewResponse(
                model_name=self.model_name,
                model_type="slm",
                hypotheses=[],
                raw_response="",
                latency_ms=elapsed_ms,
                parse_success=False,
                error_message=f"Error during Ollama inference: {str(e)}",
            )

    def _parse_hypotheses(self, raw_text: str, default_file_path: str) -> List[DefectHypothesis]:
        """Safely parse model JSON output into DefectHypothesis models."""
        if not raw_text:
            return []

        # Strip markdown code blocks if the model included them despite instructions
        clean_text = raw_text
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`")
            if clean_text.startswith("json"):
                clean_text = clean_text[4:].strip()

        parsed = json.loads(clean_text)
        items = parsed.get("hypotheses", []) if isinstance(parsed, dict) else parsed

        hypotheses: List[DefectHypothesis] = []
        for item in items:
            if not isinstance(item, dict):
                continue

            rule_id = str(item.get("rule_id", "CODE_DEFECT")).upper()
            line_no = int(item.get("line_number", 1))
            desc = str(item.get("description", "Potential bug detected."))
            conf = float(item.get("self_confidence", 0.7))

            hypotheses.append(
                DefectHypothesis(
                    rule_id=rule_id,
                    category=item.get("category", "bug"),
                    severity=item.get("severity", "HIGH").upper(),
                    file_path=item.get("file_path", default_file_path),
                    line_number=line_no,
                    end_line_number=item.get("end_line_number"),
                    description=desc,
                    self_confidence=max(0.1, min(1.0, conf)),
                    suspected_trigger_input=item.get("suspected_trigger_input"),
                    expected_behavior=item.get("expected_behavior"),
                    suggested_test_assertion=item.get("suggested_test_assertion"),
                )
            )

        return hypotheses
