"""Configuration owned by the model-call boundary."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RemediationModelSettings:
    """Versionable model settings independent of policy and prompt content."""

    model: str
    reasoning_effort: str = "minimal"
    verbosity: str = "low"
    minimum_output_tokens: int = 400
    maximum_output_tokens: int = 1600
    output_tokens_per_case: int = 120

    @classmethod
    def from_environment(
        cls,
        *,
        model: str | None = None,
    ) -> "RemediationModelSettings":
        selected_model = model or os.getenv(
            "OPENAI_REMEDIATION_MODEL",
            "gpt-5-nano",
        )
        return cls(model=selected_model)

    def max_output_tokens(self, case_count: int) -> int:
        requested = 160 + self.output_tokens_per_case * case_count
        return max(
            self.minimum_output_tokens,
            min(self.maximum_output_tokens, requested),
        )
