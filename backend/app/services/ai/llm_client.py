"""Async client for configurable Large Language Model (LLM) escalation."""

import json
import time
from typing import Any, Dict, List, Optional
import httpx
from backend.app.config import settings
from backend.app.schemas.ai import DefectHypothesis, ModelReviewResponse
from backend.app.schemas.findings import StaticFinding
from backend.app.services.ai.prompts import REVIEW_SYSTEM_PROMPT, build_review_user_prompt
from backend.app.services.router.cost_tracker import calculate_cost, estimate_tokens_from_text


class LLMClient:
    """Async client connecting to an OpenAI-compatible API for LLM review escalation."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 60,
    ):
        self.base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.LLM_API_KEY
        self.model_name = model_name or settings.LLM_MODEL_NAME
        self.timeout = timeout

    async def review_code(
        self,
        file_path: str,
        source_code: str,
        modified_lines: List[int],
        static_findings: Optional[List[StaticFinding]] = None,
    ) -> ModelReviewResponse:
        """Execute LLM escalation review."""
        user_prompt = build_review_user_prompt(
            file_path=file_path,
            source_code=source_code,
            modified_lines=modified_lines,
            static_findings=static_findings,
        )

        headers: Dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self.api_key and self.api_key.strip():
            headers["Authorization"] = f"Bearer {self.api_key.strip()}"

        endpoint = f"{self.base_url}/chat/completions" if not self.base_url.endswith("/chat/completions") else self.base_url

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        prompt_tokens_est = estimate_tokens_from_text(REVIEW_SYSTEM_PROMPT + user_prompt)
        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout), headers=headers) as client:
                resp = await client.post(endpoint, json=payload)
                elapsed_ms = int((time.perf_counter() - start_time) * 1000)

                if resp.status_code != 200:
                    return ModelReviewResponse(
                        model_name=self.model_name,
                        model_type="llm",
                        hypotheses=[],
                        raw_response=resp.text,
                        latency_ms=elapsed_ms,
                        parse_success=False,
                        error_message=f"LLM API returned HTTP {resp.status_code}: {resp.text}",
                    )

                data = resp.json()
                choice = data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "").strip()

                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", prompt_tokens_est)
                completion_tokens = usage.get("completion_tokens", estimate_tokens_from_text(content))

                hypotheses = self._parse_hypotheses(content, file_path)

                return ModelReviewResponse(
                    model_name=self.model_name,
                    model_type="llm",
                    hypotheses=hypotheses,
                    raw_response=content,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=elapsed_ms,
                    estimated_cost_usd=calculate_cost(self.model_name, prompt_tokens, completion_tokens),
                    parse_success=True,
                )

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ModelReviewResponse(
                model_name=self.model_name,
                model_type="llm",
                hypotheses=[],
                raw_response="",
                latency_ms=elapsed_ms,
                parse_success=False,
                error_message=f"Error communicating with LLM endpoint: {str(e)}",
            )

    def _parse_hypotheses(self, raw_text: str, default_file_path: str) -> List[DefectHypothesis]:
        """Parse LLM JSON response into structured DefectHypothesis models."""
        if not raw_text:
            return []

        clean_text = raw_text
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`")
            if clean_text.startswith("json"):
                clean_text = clean_text[4:].strip()

        try:
            parsed = json.loads(clean_text)
        except json.JSONDecodeError:
            return []

        items = parsed.get("hypotheses", []) if isinstance(parsed, dict) else parsed
        hypotheses: List[DefectHypothesis] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            rule_id = str(item.get("rule_id", "CODE_DEFECT")).upper()
            line_no = int(item.get("line_number", 1))
            desc = str(item.get("description", "Potential bug detected."))
            conf = float(item.get("self_confidence", 0.8))

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

