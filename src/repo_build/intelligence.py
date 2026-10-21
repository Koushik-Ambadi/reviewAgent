from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from repo_remediation.adapters import OpenAIResponsesClient
from repo_remediation.contracts import RemediationProviderError
from repo_remediation.observability import build_model_metrics, redact_sensitive


class BuildRemediationProvider(ABC):
    """Optional model-backed explanation for a failed build."""

    provider_id: str

    @abstractmethod
    def remediate(
        self,
        *,
        build_result: dict[str, Any],
        deterministic_summary: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        raise NotImplementedError


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


class OpenAIBuildRemediationProvider(BuildRemediationProvider):
    """Generate one structured, failure-only build remediation result."""

    provider_id = "openai-responses-build-remediation-v1"
    model = "gpt-5-nano"
    profile_id = "openai-build-remediation-v1"
    prompt_profile_id = "build-failure-remediation-v1"

    def __init__(self, *, client: Any | None = None, model: str | None = None):
        self.client = client or OpenAIResponsesClient()
        self.model = model or os.getenv(
            "OPENAI_BUILD_REMEDIATION_MODEL",
            os.getenv("OPENAI_REMEDIATION_MODEL", self.model),
        )

    def remediate(
        self,
        *,
        build_result: dict[str, Any],
        deterministic_summary: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        payload = _build_remediation_payload(
            self.model,
            build_result=build_result,
            deterministic_summary=deterministic_summary,
        )
        trace: dict[str, Any] = {
            "provider": self.provider_id,
            "model": self.model,
            "model_profile_id": self.profile_id,
            "prompt_profile_id": self.prompt_profile_id,
            "request": payload,
        }
        try:
            response = self.client.create(payload)
        except RemediationProviderError as error:
            trace["status"] = "provider_error"
            trace["error"] = str(error)
            trace["provider_trace"] = error.call_trace
            return _unavailable_build_remediation(str(error)), trace

        trace["status"] = "completed"
        trace["response"] = redact_sensitive(response)
        transport_trace = response.get("_remediation_transport_trace") or {}
        try:
            parsed = _parse_build_remediation(response)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            trace["status"] = "invalid_output"
            trace["error"] = str(error)
            return _unavailable_build_remediation(
                "The model response could not be validated."
            ), trace
        parsed["provider"] = self.provider_id
        parsed["model"] = self.model
        parsed["model_profile_id"] = self.profile_id
        parsed["prompt_profile_id"] = self.prompt_profile_id
        parsed["status"] = "candidate_ready"
        parsed["metrics"] = build_model_metrics(
            response,
            model=self.model,
            model_profile_id=self.profile_id,
            prompt_profile_id=self.prompt_profile_id,
            transport_trace=transport_trace,
        )
        trace["metrics"] = parsed["metrics"]
        return parsed, trace


_BUILD_REMEDIATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "root_cause": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "string"}},
        "verification": {"type": "string"},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
    },
    "required": ["summary", "root_cause", "actions", "verification", "confidence"],
}


def _build_remediation_payload(
    model: str,
    *,
    build_result: dict[str, Any],
    deterministic_summary: dict[str, Any],
) -> dict[str, Any]:
    evidence = _bounded_build_strings(build_result)
    user_input = {
        "build_status": build_result.get("status"),
        "return_code": build_result.get("return_code"),
        "build_step": build_result.get("build_step") or {},
        "deterministic_classification": {
            "issue_code": deterministic_summary.get("issue_code"),
            "primary_issue": deterministic_summary.get("primary_issue"),
            "evidence": deterministic_summary.get("evidence") or [],
        },
        "captured_output": evidence,
    }
    return {
        "model": model,
        "store": False,
        "reasoning": {"effort": "minimal"},
        "max_output_tokens": 700,
        "input": [
            {
                "role": "developer",
                "content": (
                    "You are a conservative build-failure remediation assistant. "
                    "Use the deterministic classification and captured strings as "
                    "evidence. Do not invent source changes, tool versions, paths, "
                    "credentials, or network facts. Return JSON matching the schema. "
                    "Give concrete next actions and a verification step."
                ),
            },
            {"role": "user", "content": json.dumps(user_input, separators=(",", ":"))},
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "build_remediation",
                "strict": True,
                "schema": _BUILD_REMEDIATION_SCHEMA,
            },
            "verbosity": "low",
        },
    }


def _bounded_build_strings(build_result: dict[str, Any]) -> dict[str, list[str]]:
    """Keep the full strings in build.json, but bound model prompt size."""
    return {
        "important_diagnostics": list(build_result.get("important_diagnostics") or [])[:20],
        "stderr_tail": list(build_result.get("stderr") or [])[-40:],
        "stdout_tail": list(build_result.get("stdout") or [])[-40:],
    }


def _parse_build_remediation(response: dict[str, Any]) -> dict[str, Any]:
    for output in response.get("output", []):
        if output.get("type") != "message":
            continue
        for content in output.get("content", []):
            if content.get("type") == "refusal":
                raise ValueError("The model refused build remediation.")
            if content.get("type") == "output_text":
                parsed = json.loads(content["text"])
                if not isinstance(parsed, dict):
                    raise ValueError("Build remediation output was not an object.")
                for key in ("summary", "root_cause", "verification", "confidence"):
                    if not isinstance(parsed.get(key), str) or not parsed[key].strip():
                        raise ValueError(f"Build remediation field is invalid: {key}")
                if not isinstance(parsed.get("actions"), list) or not all(
                    isinstance(item, str) and item.strip() for item in parsed["actions"]
                ):
                    raise ValueError("Build remediation actions are invalid.")
                return parsed
    raise ValueError("Build remediation returned no structured output.")


def _unavailable_build_remediation(message: str) -> dict[str, Any]:
    return {
        "status": "unsupported",
        "provider": "openai-responses-build-remediation-v1",
        "summary": "Model build remediation is unavailable.",
        "root_cause": "",
        "actions": [],
        "verification": "Review the deterministic build classification and captured output.",
        "confidence": "low",
        "limitation": message,
    }


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
