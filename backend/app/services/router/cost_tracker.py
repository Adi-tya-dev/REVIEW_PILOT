"""Token accounting and cost calculation for SLM and LLM models."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelPricing:
    """Pricing per million tokens in USD."""
    prompt_rate_per_million: float
    completion_rate_per_million: float


# Pricing dictionary (USD per 1M tokens)
# Local SLM inference is $0.00
PRICING_TABLE: Dict[str, ModelPricing] = {
    "qwen2.5-coder:1.5b": ModelPricing(0.0, 0.0),
    "qwen2.5-coder:7b": ModelPricing(0.0, 0.0),
    "deepseek-coder:6.7b": ModelPricing(0.0, 0.0),
    "ollama": ModelPricing(0.0, 0.0),
    # Common cloud LLM fallbacks for reference:
    "gpt-4o-mini": ModelPricing(0.15, 0.60),
    "claude-3-haiku": ModelPricing(0.25, 1.25),
    "gemini-1.5-flash": ModelPricing(0.075, 0.30),
    "deepseek-chat": ModelPricing(0.14, 0.28),
    "default_cloud_llm": ModelPricing(0.20, 0.80),
}


def estimate_tokens_from_text(text: str) -> int:
    """Heuristic estimate of token count (approx 4 characters per token for code/text)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def calculate_cost(
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """Calculate the estimated USD cost of a model invocation."""
    pricing = PRICING_TABLE.get(model_name.lower())
    if not pricing:
        # Check if local model name
        if "qwen" in model_name.lower() or "ollama" in model_name.lower() or "deepseek-coder" in model_name.lower():
            pricing = PRICING_TABLE["ollama"]
        else:
            pricing = PRICING_TABLE["default_cloud_llm"]

    prompt_cost = (prompt_tokens / 1_000_000.0) * pricing.prompt_rate_per_million
    completion_cost = (completion_tokens / 1_000_000.0) * pricing.completion_rate_per_million
    return round(prompt_cost + completion_cost, 6)

