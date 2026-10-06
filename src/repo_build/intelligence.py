from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any


class BuildIntelligenceProvider(ABC):
    provider_id: str

    @abstractmethod
    def summarize(self, build_result: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class PlaceholderBuildIntelligenceProvider(BuildIntelligenceProvider):
    """Deterministic build summary until a model-backed provider is enabled."""

    provider_id = "placeholder-build-intelligence-v1"

    def summarize(self, build_result: dict[str, Any]) -> dict[str, Any]:
        succeeded = build_result["return_code"] == 0
        diagnostics = build_result["important_diagnostics"]
        artifact_count = len(build_result["artifact_manifest"])

        if succeeded:
            summary = "Build completed successfully."
            next_action = (
                "Review the generated artifacts and continue with the release workflow."
            )
            suggestions = [
                "Confirm the artifact manifest contains the expected deliverables."
            ]
        else:
            summary = "Build failed before a successful artifact set was produced."
            next_action = (
                "Start with the highlighted diagnostics, correct the source or build configuration, then run the build again."
            )
            suggestions = [
                "Review the first error and its referenced source location.",
                "Verify the configured build script and required generated inputs.",
            ]

        return {
            "provider": self.provider_id,
            "summary": summary,
            "next_action": next_action,
            "suggestions": suggestions,
            "diagnostic_count": len(diagnostics),
            "artifact_count": artifact_count,
        }


class FutureOpenAIBuildIntelligenceProvider(BuildIntelligenceProvider):
    provider_id = "openai-build-intelligence-v1"

    def summarize(self, build_result: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("OpenAI build intelligence is not configured.")


_IMPORTANT_DIAGNOSTIC = re.compile(
    r"\b(error|fatal|warning|failed|undefined reference|exception)\b",
    re.IGNORECASE,
)


def select_important_diagnostics(
    stdout: list[str],
    stderr: list[str],
    *,
    limit: int = 12,
) -> list[str]:
    """Select concise, high-signal lines without presenting the full log twice."""
    lines = [line.strip() for line in [*stderr, *stdout] if line.strip()]
    matches = [line for line in lines if _IMPORTANT_DIAGNOSTIC.search(line)]
    if matches:
        return matches[:limit]
    return lines[-limit:]
