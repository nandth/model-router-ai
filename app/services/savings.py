"""Helpers for estimating router savings.

Note: The model router primarily saves *cost* by using cheaper models for easy prompts.
Token counts themselves don't meaningfully change just because the model changes, so the
`tokens_saved` metric is computed as a *baseline-token-equivalent* savings based on
model pricing.
"""

from __future__ import annotations

import os
from typing import Iterable, Mapping, Optional

from app.services.model_router import MODEL_CONFIGS

_DEFAULT_BASELINE_MODEL = "gpt-4"


def get_savings_baseline_model() -> str:
    """Return the baseline model used for savings calculations."""
    return os.getenv("SAVINGS_BASELINE_MODEL", _DEFAULT_BASELINE_MODEL)


def _pricing_by_model() -> dict[str, dict]:
    """Build a model->pricing mapping from ModelRouter's config."""
    by_model: dict[str, dict] = {}
    for cfg in MODEL_CONFIGS.values():
        model = cfg.get("model")
        if model:
            by_model[str(model)] = cfg
    return by_model


_PRICING_BY_MODEL = _pricing_by_model()


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost for a call given token usage."""
    cfg = _PRICING_BY_MODEL.get(model)
    if cfg is None:
        return 0.0

    in_cost = (prompt_tokens / 1000.0) * float(cfg["cost_per_1k_input"])
    out_cost = (completion_tokens / 1000.0) * float(cfg["cost_per_1k_output"])
    return in_cost + out_cost


def estimate_tokens_saved(
    calls: Iterable[Mapping[str, object]],
    *,
    baseline_model: Optional[str] = None,
) -> int:
    """
    Estimate baseline-token-equivalent savings across one or more LLM calls.

    Each call mapping must include:
    - model: str
    - prompt_tokens: int
    - completion_tokens: int

    Returns a non-negative integer token count (rounded).
    """
    baseline = baseline_model or get_savings_baseline_model()

    tokens_saved_total = 0.0
    for call in calls:
        model = str(call.get("model") or "")
        prompt_tokens = int(call.get("prompt_tokens") or 0)
        completion_tokens = int(call.get("completion_tokens") or 0)

        total_tokens = prompt_tokens + completion_tokens
        if total_tokens <= 0:
            continue

        baseline_cost = estimate_cost_usd(baseline, prompt_tokens, completion_tokens)
        if baseline_cost <= 0:
            # Unknown baseline pricing -> can't compute a meaningful savings.
            continue

        actual_cost = estimate_cost_usd(model, prompt_tokens, completion_tokens)
        cost_saved = baseline_cost - actual_cost
        if cost_saved <= 0:
            continue

        # Convert cost savings into "baseline token equivalents" using the effective
        # baseline $/token for this call's input/output mix.
        avg_baseline_cost_per_token = baseline_cost / total_tokens
        tokens_saved_total += cost_saved / avg_baseline_cost_per_token

    return max(0, int(round(tokens_saved_total)))

