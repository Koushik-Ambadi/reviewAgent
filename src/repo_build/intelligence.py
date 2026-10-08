from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
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
        classification = classify_build_failure(build_result) if not succeeded else None

        if succeeded:
            summary = "Build completed successfully."
            next_action = (
                "Review the generated artifacts and continue with the release workflow."
            )
            suggestions = [
                "Confirm the artifact manifest contains the expected deliverables."
            ]
            evidence: list[str] = []
            issue_code = "build-succeeded"
        elif classification:
            summary = classification.primary_issue
            next_action = classification.next_actions[0]
            suggestions = classification.next_actions
            evidence = classification.evidence
            issue_code = classification.issue_code
        else:
            summary = "Build failed before a successful artifact set was produced."
            next_action = (
                "Start with the highlighted diagnostics, correct the source or build configuration, then run the build again."
            )
            suggestions = [
                "Review the first error and its referenced source location.",
                "Verify the configured build script and required generated inputs.",
            ]
            evidence = diagnostics[:3]
            issue_code = "unclassified-build-failure"

        return {
            "provider": self.provider_id,
            "issue_code": issue_code,
            "primary_issue": summary,
            "summary": summary,
            "evidence": evidence,
            "next_action": next_action,
            "next_actions": suggestions,
            "suggestions": suggestions,
            "diagnostic_count": len(diagnostics),
            "artifact_count": artifact_count,
        }


class FutureOpenAIBuildIntelligenceProvider(BuildIntelligenceProvider):
    provider_id = "openai-build-intelligence-v1"

    def summarize(self, build_result: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("OpenAI build intelligence is not configured.")


@dataclass(frozen=True)
class BuildFailureClassification:
    issue_code: str
    primary_issue: str
    evidence: list[str]
    next_actions: list[str]


_GHS_LICENSE = re.compile(
    r"license manager.*cannot be contacted|cannot contact.*license|"
    r"no valid.*license|unable to (?:check out|checkout).*license|ghs_lmhost",
    re.IGNORECASE,
)
_GHS_HOST = re.compile(r"GHS_LMHOST\s*(?:=|is|:)\s*([^\s,;]+)", re.IGNORECASE)
_CMAKE_COMPILER_CHECK = re.compile(
    r"compiler identification is unknown|not able to compile a simple test program|"
    r"cmaketestccompiler|cmake.*compiler.*(?:failed|broken)",
    re.IGNORECASE,
)
_MISSING_BUILD_SCRIPT = re.compile(
    r"(?:build )?script.*(?:not found|does not exist)|cmake-build\.bat.*not found",
    re.IGNORECASE,
)
_LINKER_FAILURE = re.compile(r"undefined reference|unresolved external", re.IGNORECASE)


def classify_build_failure(
    build_result: dict[str, Any],
) -> BuildFailureClassification | None:
    """Classify known failures before any optional model-backed analysis."""
    lines = _unique_lines(
        [
            *build_result.get("stderr", []),
            *build_result.get("stdout", []),
            *build_result.get("important_diagnostics", []),
        ]
    )

    license_lines = [line for line in lines if _GHS_LICENSE.search(line)]
    if license_lines:
        evidence = license_lines[:2]
        host = next(
            (
                match.group(1).rstrip(".")
                for line in lines
                if (match := _GHS_HOST.search(line))
            ),
            None,
        )
        if host:
            evidence.append(f"GHS_LMHOST is configured as {host}.")
        if any(_CMAKE_COMPILER_CHECK.search(line) for line in lines):
            evidence.append(
                "CMake compiler validation failed after the license error."
            )
        return BuildFailureClassification(
            issue_code="ghs-license-unavailable",
            primary_issue="Green Hills toolchain license is unavailable.",
            evidence=_unique_lines(evidence)[:4],
            next_actions=[
                "Confirm network access to the configured license server.",
                "Confirm the license service is running and the user has a valid entitlement.",
                "Retry configuration and build after the license is available.",
            ],
        )

    missing_script = next(
        (line for line in lines if _MISSING_BUILD_SCRIPT.search(line)),
        None,
    )
    if missing_script:
        return BuildFailureClassification(
            issue_code="build-adapter-missing",
            primary_issue="The configured build adapter could not be found.",
            evidence=[missing_script],
            next_actions=[
                "Confirm cmake-build.bat exists at the uploaded repository root.",
                "Confirm the ZIP preserved the repository root layout.",
                "Re-run the review and build after restoring the adapter.",
            ],
        )

    compiler_lines = [line for line in lines if _CMAKE_COMPILER_CHECK.search(line)]
    if compiler_lines:
        return BuildFailureClassification(
            issue_code="cmake-compiler-validation-failed",
            primary_issue="CMake could not validate the configured C compiler.",
            evidence=compiler_lines[:3],
            next_actions=[
                "Review the compiler diagnostic immediately before the CMake validation failure.",
                "Confirm the compiler path, environment, and required toolchain configuration.",
                "Retry CMake configuration before running the build again.",
            ],
        )

    linker_lines = [line for line in lines if _LINKER_FAILURE.search(line)]
    if linker_lines:
        return BuildFailureClassification(
            issue_code="linker-symbol-resolution-failed",
            primary_issue="The linker could not resolve one or more symbols.",
            evidence=linker_lines[:3],
            next_actions=[
                "Confirm the missing symbols are implemented and included in the link target.",
                "Check library order and target-specific conditional compilation.",
                "Re-run the build after correcting the target inputs.",
            ],
        )
    return None


def _unique_lines(lines: list[str]) -> list[str]:
    return list(dict.fromkeys(line.strip() for line in lines if line.strip()))


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
