"""Normalized token and latency metrics for model-backed turns."""

from __future__ import annotations

from typing import Any


def build_model_metrics(
    response: dict[str, Any],
    *,
    model: str,
    model_profile_id: str,
    prompt_profile_id: str,
    transport_trace: dict[str, Any],
) -> dict[str, Any]:
    usage = response.get("usage") or {}
    output_details = usage.get("output_tokens_details") or {}
    input_details = usage.get("input_tokens_details") or {}
    attempts = list(transport_trace.get("attempts") or [])
    latency_ms = round(
        sum(float(attempt.get("elapsed_ms") or 0) for attempt in attempts),
        3,
    )
    return {
        "provider": "openai",
        "model": response.get("model") or model,
        "model_profile_id": model_profile_id,
        "prompt_profile_id": prompt_profile_id,
        "response_id": response.get("id"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "reasoning_tokens": output_details.get("reasoning_tokens"),
        "cached_input_tokens": input_details.get("cached_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "latency_ms": latency_ms,
        "attempt_count": len(attempts),
    }
