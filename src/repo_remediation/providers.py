from __future__ import annotations

import json
import os
import re
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

import httpx

from repo_review.checks.naming.common_identifier import evaluate_atomic_rules


class RemediationProviderError(RuntimeError):
    """Base error for model-backed remediation failures."""


class RemediationProviderUnavailableError(RemediationProviderError):
    """Raised when the configured model provider cannot be used."""


class ResponsesClient(Protocol):
    def create(self, payload: dict[str, Any]) -> dict[str, Any]: ...


class OpenAIResponsesClient:
    """Small Responses API adapter that keeps credentials out of artifacts."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout_seconds: float | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.timeout_seconds = timeout_seconds or float(
            os.getenv("OPENAI_REMEDIATION_TIMEOUT_SECONDS", "30")
        )
        self.transport = transport

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise RemediationProviderUnavailableError(
                "OPENAI_API_KEY is not configured for model-backed remediation."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        retryable_statuses = {429, 500, 502, 503, 504}
        last_error = "OpenAI Responses API request failed."

        with httpx.Client(
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            for attempt in range(2):
                try:
                    response = client.post(self.endpoint, headers=headers, json=payload)
                except httpx.RequestError as error:
                    last_error = (
                        "OpenAI Responses API request failed: "
                        f"{error.__class__.__name__}."
                    )
                    if attempt == 0:
                        time.sleep(0.25)
                        continue
                    raise RemediationProviderUnavailableError(last_error) from error

                if response.is_success:
                    return response.json()

                last_error = _safe_openai_error(response)
                if response.status_code in retryable_statuses and attempt == 0:
                    time.sleep(0.25)
                    continue
                if response.status_code in retryable_statuses:
                    raise RemediationProviderUnavailableError(last_error)
                raise RemediationProviderError(last_error)

        raise RemediationProviderUnavailableError(last_error)


class RemediationProvider(ABC):
    """Produces remediation using one failed check and its policy snapshot."""

    provider_id: str

    @abstractmethod
    def suggest(
        self,
        *,
        run_id: str,
        module_name: str,
        check: dict[str, Any],
        check_policy: Any,
        cases: list[dict[str, Any]],
        scope: str,
        context_answers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


class OpenAIRemediationProvider(RemediationProvider):
    """Generates candidates or narrow context questions for one failed check."""

    provider_id = "openai-responses-remediation-v1"

    def __init__(
        self,
        *,
        client: ResponsesClient | None = None,
        model: str | None = None,
    ) -> None:
        self.client = client or OpenAIResponsesClient()
        self.model = model or os.getenv("OPENAI_REMEDIATION_MODEL", "gpt-5-nano")

    def suggest(
        self,
        *,
        run_id: str,
        module_name: str,
        check: dict[str, Any],
        check_policy: Any,
        cases: list[dict[str, Any]],
        scope: str,
        context_answers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        context_answers = {
            key: value.strip()
            for key, value in (context_answers or {}).items()
            if value and value.strip()
        }
        questions: list[dict[str, Any]] = []
        limitations: list[dict[str, Any]] = []
        eligible_cases: list[dict[str, Any]] = []

        for case in cases:
            disposition = _preflight_case(
                check["check_id"],
                case,
                module_name,
                context_answers,
            )
            if disposition["kind"] == "question":
                questions.append(disposition["question"])
            elif disposition["kind"] == "unsupported":
                limitations.append(disposition["limitation"])
            else:
                eligible_cases.append(
                    {
                        "case_id": case["case_id"],
                        "name": case.get("name", ""),
                        "location": case.get("location", ""),
                        "failed_rule_ids": _rule_ids(case.get("reasons", [])),
                        "developer_context": disposition.get(
                            "developer_context", ""
                        ),
                    }
                )

        suggestions: list[dict[str, Any]] = []
        model_evidence: dict[str, Any] | None = None
        if eligible_cases:
            payload = _responses_payload(
                model=self.model,
                module_name=module_name,
                check_id=check["check_id"],
                check_policy=_automatic_policy(check_policy),
                cases=eligible_cases,
            )
            response = self.client.create(payload)
            parsed = _parse_structured_response(response)
            suggestions, model_questions, model_limitations = _model_results(
                check_id=check["check_id"],
                module_name=module_name,
                check_policy=check_policy,
                requested_cases=eligible_cases,
                results=parsed["cases"],
            )
            questions.extend(model_questions)
            limitations.extend(model_limitations)
            model_evidence = _model_evidence(response, self.model)

        status = _result_status(suggestions, questions, limitations)
        now = datetime.now(UTC).isoformat()
        return {
            "remediation_id": uuid4().hex,
            "run_id": run_id,
            "provider": self.provider_id,
            "model": model_evidence,
            "scope": scope,
            "check_id": check["check_id"],
            "case_id": cases[0]["case_id"] if scope == "case" else None,
            "status": status,
            "generated_at": now,
            "updated_at": now,
            "title": f"Remediation plan: {check.get('title', 'Check')}",
            "summary": _result_summary(
                status, suggestions, questions, limitations
            ),
            "applicable_rules": _display_rules(check_policy),
            "affected_cases": [_affected_case(case) for case in cases],
            "suggestions": suggestions,
            "questions": questions,
            "limitations": limitations,
        }


class PlaceholderRemediationProvider(RemediationProvider):
    """Compatibility fallback retained for deterministic/offline callers."""

    provider_id = "policy-template-remediation-v2"

    def suggest(
        self,
        *,
        run_id: str,
        module_name: str = "",
        check: dict[str, Any],
        check_policy: Any = None,
        cases: list[dict[str, Any]],
        scope: str,
        context_answers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        affected_cases = [_affected_case(case) for case in cases]
        common_reasons = sorted(
            {reason for case in cases for reason in case.get("reasons", [])}
        )
        suggestions = [
            _case_suggestion(check["check_id"], case) for case in cases
        ]
        now = datetime.now(UTC).isoformat()
        return {
            "remediation_id": uuid4().hex,
            "run_id": run_id,
            "provider": self.provider_id,
            "model": None,
            "scope": scope,
            "check_id": check["check_id"],
            "case_id": cases[0]["case_id"] if scope == "case" else None,
            "status": "candidate_ready",
            "generated_at": now,
            "updated_at": now,
            "title": (
                f"Suggested fixes: {check.get('title', 'Check')}"
                if scope == "check"
                else f"Suggested fix: {cases[0].get('name') or 'Case'}"
            ),
            "summary": (
                f"Review the {len(cases)} failed case"
                f"{'s' if len(cases) != 1 else ''} against the configured "
                f"{check.get('title', 'check')} rules."
            ),
            "applicable_rules": _display_rules(check_policy),
            "common_failure_patterns": common_reasons,
            "affected_cases": affected_cases,
            "suggestions": suggestions,
            "questions": [],
            "limitations": [],
        }


class FutureOpenAIRemediationProvider(OpenAIRemediationProvider):
    """Compatibility alias for the formerly reserved provider name."""


_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "cases": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "case_id": {"type": "string"},
                    "disposition": {
                        "type": "string",
                        "enum": ["candidate", "context_required"],
                    },
                    "candidate": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                    "note": {"type": "string"},
                    "question": {"type": "string"},
                },
                "required": [
                    "case_id",
                    "disposition",
                    "candidate",
                    "confidence",
                    "note",
                    "question",
                ],
            },
        }
    },
    "required": ["cases"],
}

_GLOBAL_CATEGORICAL_RULES = {
    "ABS-POLICY-GLOBAL-DATA-TYPE",
    "ABS-POLICY-GLOBAL-DATA-SIZE",
    "ABS-POLICY-GLOBAL-MODULE",
    "ABS-POLICY-GLOBAL-UNIT",
    "ABS-SCS-17.g",
    "ABS-POLICY-GLOBAL-SEGMENTS",
}

_SEMANTIC_RULES = {
    "ABS-POLICY-FUNCTION-DESCRIPTION",
    "ABS-POLICY-MACRO-DESCRIPTION",
    "ABS-POLICY-TYPE-DESCRIPTION",
    "ABS-POLICY-ENUM-DESCRIPTION",
}


def _responses_payload(
    *,
    model: str,
    module_name: str,
    check_id: str,
    check_policy: Any,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    developer_prompt = (
        "Generate concise policy-compliant identifier candidates for the supplied "
        "failed cases. The check policy is supplied once; each case references only "
        "its failed rule IDs. Preserve the meaning visible in the current identifier "
        "and developer context. Abbreviate long names conservatively. Do not repeat "
        "rules or explanations. If meaning is insufficient, return context_required "
        "with one short, specific question. Never invent or change global variable "
        "type, size, module, or unit segments. Return every case exactly once."
    )
    remediation_input = {
        "module": module_name,
        "check_id": check_id,
        "policy": check_policy,
        "cases": cases,
    }
    return {
        "model": model,
        "store": False,
        "reasoning": {"effort": "minimal"},
        "max_output_tokens": max(400, min(1600, 160 + 120 * len(cases))),
        "input": [
            {"role": "developer", "content": developer_prompt},
            {
                "role": "user",
                "content": json.dumps(remediation_input, separators=(",", ":")),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "remediation_batch",
                "strict": True,
                "schema": _RESPONSE_SCHEMA,
            },
            "verbosity": "low",
        },
    }


def _preflight_case(
    check_id: str,
    case: dict[str, Any],
    module_name: str,
    context_answers: dict[str, str],
) -> dict[str, Any]:
    case_id = case["case_id"]
    rule_ids = set(_rule_ids(case.get("reasons", [])))
    case_context = "\n".join(
        answer
        for question_id, answer in context_answers.items()
        if question_id.startswith(f"{case_id}:")
    )

    if check_id == "required_paths":
        return {
            "kind": "unsupported",
            "limitation": _limitation(
                case,
                "Repository structure remediation needs artifact ownership, content, and generation context.",
            ),
        }

    if check_id == "global_variable_names" and rule_ids & _GLOBAL_CATEGORICAL_RULES:
        return {
            "kind": "unsupported",
            "limitation": _limitation(
                case,
                "Global type, size, module, unit, or segment repair is deferred until those categorical values are supplied from trusted context.",
            ),
        }

    question = _known_context_question(check_id, case, rule_ids, module_name)
    if question:
        answer = context_answers.get(question["question_id"], "")
        if not answer:
            return {"kind": "question", "question": question}
        return {"kind": "eligible", "developer_context": answer}

    return {"kind": "eligible", "developer_context": case_context}


def _known_context_question(
    check_id: str,
    case: dict[str, Any],
    rule_ids: set[str],
    module_name: str,
) -> dict[str, Any] | None:
    name = str(case.get("name", ""))
    prompt = ""
    field = "purpose"

    if check_id == "parameter_names" and (
        "ABS-SCS-17.e" in rule_ids or "ABS-SCS-16.2.e" in rule_ids
    ):
        prompt = f"What does parameter '{name or 'unnamed parameter'}' represent?"
        field = "parameter_purpose"
    elif check_id == "local_variable_names" and "ABS-SCS-17.e" in rule_ids:
        prompt = f"What does local variable '{name}' represent in its function?"
        field = "local_variable_purpose"
    elif check_id == "array_sizes":
        prompt = (
            f"What limit or dimension does array '{name}' represent, and what "
            "symbolic size name should express it?"
        )
        field = "array_dimension_meaning"
    elif rule_ids & _SEMANTIC_RULES and not _has_semantic_stem(
        check_id, name, module_name
    ):
        prompt = f"What purpose or domain concept should '{name}' describe?"
        field = "symbol_purpose"
    elif check_id == "global_variable_names" and any(
        rule_id.startswith("ABS-POLICY-GLOBAL-DESCRIPTION")
        for rule_id in rule_ids
    ) and not _global_description(name):
        prompt = f"What does global variable '{name}' represent?"
        field = "global_description"

    if not prompt:
        return None
    return {
        "question_id": f"{case['case_id']}:{field}",
        "case_ids": [case["case_id"]],
        "field": field,
        "prompt": prompt,
        "input_type": "text",
        "required": True,
    }


def _model_results(
    *,
    check_id: str,
    module_name: str,
    check_policy: Any,
    requested_cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    expected = {case["case_id"]: case for case in requested_cases}
    received: dict[str, dict[str, Any]] = {}
    for item in results:
        case_id = item.get("case_id")
        if case_id not in expected or case_id in received:
            raise RemediationProviderError(
                "Model remediation returned missing, duplicate, or unknown case IDs."
            )
        received[case_id] = item
    if received.keys() != expected.keys():
        raise RemediationProviderError(
            "Model remediation did not return every requested case."
        )

    suggestions: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    limitations: list[dict[str, Any]] = []
    for case_id, case in expected.items():
        item = received[case_id]
        if item["disposition"] == "context_required":
            question = item["question"].strip() or (
                f"What purpose should '{case['name']}' communicate?"
            )
            questions.append(
                {
                    "question_id": f"{case_id}:model_context",
                    "case_ids": [case_id],
                    "field": "model_context",
                    "prompt": question,
                    "input_type": "text",
                    "required": True,
                }
            )
            continue

        candidate = item["candidate"].strip()
        if not candidate or candidate == case["name"]:
            limitations.append(
                {
                    "case_id": case_id,
                    "name": case["name"],
                    "message": "The model did not produce a changed candidate.",
                }
            )
            continue
        validation_status, validation_reasons = _validate_candidate(
            check_id,
            candidate,
            module_name,
            check_policy,
        )
        if validation_status == "failed":
            limitations.append(
                {
                    "case_id": case_id,
                    "name": case["name"],
                    "message": (
                        "The generated candidate did not satisfy the configured policy."
                    ),
                    "details": validation_reasons,
                }
            )
            continue
        suggestions.append(
            {
                "case_id": case_id,
                "title": f"Rename {case['name']}",
                "current_name": case["name"],
                "candidate_name": candidate,
                "confidence": item["confidence"],
                "description": item["note"].strip(),
                "policy_validation": validation_status,
                "verification": (
                    "Re-run the naming check and compile affected targets after "
                    "an approved rename."
                ),
            }
        )
    return suggestions, questions, limitations


def _validate_candidate(
    check_id: str,
    candidate: str,
    module_name: str,
    check_policy: Any,
) -> tuple[str, list[str]]:
    if check_id == "global_variable_names":
        return "not_available_without_symbol_type", []
    if not isinstance(check_policy, dict) or "rules" not in check_policy:
        return "not_available", []
    reasons = evaluate_atomic_rules(
        candidate,
        check_policy["rules"],
        context={"module": module_name},
    )
    return ("failed", reasons) if reasons else ("passed", [])


def _parse_structured_response(response: dict[str, Any]) -> dict[str, Any]:
    for output in response.get("output", []):
        if output.get("type") != "message":
            continue
        for content in output.get("content", []):
            if content.get("type") == "refusal":
                raise RemediationProviderError(
                    "The model refused the remediation request."
                )
            if content.get("type") == "output_text":
                try:
                    parsed = json.loads(content["text"])
                except (KeyError, TypeError, json.JSONDecodeError) as error:
                    raise RemediationProviderError(
                        "Model remediation returned invalid structured output."
                    ) from error
                if not isinstance(parsed, dict) or not isinstance(
                    parsed.get("cases"), list
                ):
                    raise RemediationProviderError(
                        "Model remediation returned an unexpected structured output shape."
                    )
                return parsed
    raise RemediationProviderError("Model remediation returned no output text.")


def _model_evidence(response: dict[str, Any], model: str) -> dict[str, Any]:
    usage = response.get("usage") or {}
    output_details = usage.get("output_tokens_details") or {}
    return {
        "provider": "openai",
        "model": response.get("model") or model,
        "response_id": response.get("id"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "reasoning_tokens": output_details.get("reasoning_tokens"),
    }


def _safe_openai_error(response: httpx.Response) -> str:
    message = f"OpenAI Responses API returned HTTP {response.status_code}."
    try:
        detail = response.json().get("error", {}).get("message")
    except (ValueError, AttributeError):
        detail = None
    if detail:
        message = f"{message} {str(detail)[:300]}"
    return message


def _rule_ids(reasons: list[Any]) -> list[str]:
    ids: list[str] = []
    for reason in reasons:
        match = re.match(r"^\[([^\]]+)\]", str(reason))
        if match and match.group(1) not in ids:
            ids.append(match.group(1))
    return ids


def _automatic_policy(policy: Any) -> Any:
    if not isinstance(policy, dict):
        return policy
    result: dict[str, Any] = {}
    for key, value in policy.items():
        if key in {"source_rules", "source_exemptions"}:
            continue
        if key == "rules" and isinstance(value, list):
            result[key] = [
                item
                for item in value
                if not isinstance(item, dict)
                or item.get("mode", "automatic") == "automatic"
            ]
        else:
            result[key] = value
    return result


def _display_rules(policy: Any) -> list[dict[str, str]]:
    if not isinstance(policy, dict):
        return []
    candidates = policy.get("rules") or policy.get("automatic_rules") or []
    display: list[dict[str, str]] = []
    for rule in candidates:
        if not isinstance(rule, dict) or rule.get(
            "mode", "automatic"
        ) != "automatic":
            continue
        display.append(
            {
                "rule_id": str(rule.get("id", "")),
                "reason": str(
                    rule.get("reason") or rule.get("statement") or ""
                ),
            }
        )
    return display


def _has_semantic_stem(check_id: str, name: str, module_name: str) -> bool:
    module_title = module_name[:1].upper() + module_name[1:].lower()
    module_upper = module_name.upper()
    stem = name
    if check_id in {"function_names", "type_names"}:
        stem = re.sub(
            rf"^{re.escape(module_title)}_", "", stem, flags=re.IGNORECASE
        )
    elif check_id in {"macro_names", "enum_constant_names"}:
        stem = re.sub(
            rf"^{re.escape(module_upper)}_", "", stem, flags=re.IGNORECASE
        )
    if check_id == "type_names":
        stem = re.sub(r"_t$", "", stem, flags=re.IGNORECASE)
    return bool(stem.strip("_"))


def _global_description(name: str) -> str:
    parts = name.split("_")
    return "_".join(parts[2:]) if len(parts) >= 3 else ""


def _affected_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "name": case.get("name", "Unnamed case"),
        "location": case.get("location", ""),
        "reasons": case.get("reasons", []),
    }


def _limitation(case: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "name": case.get("name", "Unnamed case"),
        "message": message,
    }


def _result_status(
    suggestions: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> str:
    if suggestions and (questions or limitations):
        return "partial"
    if suggestions:
        return "candidate_ready"
    if questions:
        return "input_required"
    return "unsupported"


def _result_summary(
    status: str,
    suggestions: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
) -> str:
    if status == "candidate_ready":
        suffix = "s" if len(suggestions) != 1 else ""
        return f"Generated {len(suggestions)} rename candidate{suffix}."
    if status == "input_required":
        suffix = "s" if len(questions) != 1 else ""
        return f"Developer context is required for {len(questions)} case{suffix}."
    if status == "partial":
        return (
            f"Generated {len(suggestions)} candidate(s); "
            f"{len(questions)} question(s) and "
            f"{len(limitations)} limitation(s) remain."
        )
    return "No candidate was generated within the current prototype boundary."


_CHECK_TEMPLATES = {
    "required_paths": {
        "description": (
            "Restore the required repository path at the policy-defined location."
        ),
        "actions": [
            "Use the reported path exactly, including capitalization and module placeholders.",
            "Confirm whether the path is source-owned or generated before adding it.",
        ],
        "verification": (
            "Re-run the review and confirm the Required Paths case passes."
        ),
    },
    "array_sizes": {
        "description": (
            "Update the array declaration to use the size form required by policy."
        ),
        "actions": ["Use a domain-meaningful symbolic size identifier."],
        "verification": (
            "Re-run the naming stage and confirm the array-size case passes."
        ),
    },
}

_SYMBOL_TEMPLATE = {
    "description": "Rename the symbol to satisfy the active naming policy.",
    "actions": ["Update declarations, definitions, and references together."],
    "verification": "Re-run the naming stage and confirm this case passes.",
}


def _case_suggestion(check_id: str, case: dict[str, Any]) -> dict[str, Any]:
    template = _CHECK_TEMPLATES.get(check_id, _SYMBOL_TEMPLATE)
    return {
        "case_id": case["case_id"],
        "title": f"Update {case.get('name') or 'this item'}",
        "description": template["description"],
        "actions": template["actions"],
        "verification": template["verification"],
        "reasons": case.get("reasons", []),
    }
