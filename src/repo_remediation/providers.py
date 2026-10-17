from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from repo_remediation.adapters import OpenAIResponsesClient
from repo_remediation.context import preflight_case as _preflight_case
from repo_remediation.contracts import (
    RemediationProvider,
    RemediationProviderError,
    RemediationProviderUnavailableError,
    ResponsesClient,
)
from repo_remediation.generation import (
    RemediationModelProfile,
    compile_remediation_prompt,
    parse_structured_response,
    restore_case_ids,
)
from repo_remediation.hierarchy import project_case_results
from repo_remediation.observability import (
    build_model_metrics,
    completed_turn as _completed_turn,
    failed_turn as _failed_turn,
    redact_sensitive,
)
from repo_remediation.results import (
    affected_case as _affected_case,
    case_suggestion as _case_suggestion,
    display_rules as _display_rules,
    failed_rules as _failed_rules,
    map_model_results as _model_results,
    result_status as _result_status,
    result_summary as _result_summary,
)


_redact_sensitive = redact_sensitive


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
        self.profile = RemediationModelProfile.from_environment(model=model)
        self.model = self.profile.model

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
        turn_id = uuid4().hex
        turn_started_at = datetime.now(UTC).isoformat()
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
                        "failed_rules": _failed_rules(case.get("reasons", [])),
                        "developer_context": disposition.get(
                            "developer_context", ""
                        ),
                    }
                )

        suggestions: list[dict[str, Any]] = []
        model_evidence: dict[str, Any] | None = None
        provider_call: dict[str, Any] | None = None
        if eligible_cases:
            compiled_prompt = compile_remediation_prompt(
                profile=self.profile,
                check_id=check["check_id"],
                cases=eligible_cases,
            )
            payload = compiled_prompt.payload
            try:
                response_with_trace = self.client.create(payload)
            except RemediationProviderError as error:
                error.call_trace = _failed_turn(
                    turn_id=turn_id,
                    started_at=turn_started_at,
                    scope=scope,
                    check_id=check["check_id"],
                    cases=cases,
                    context_answers=context_answers,
                    eligible_cases=eligible_cases,
                    questions=questions,
                    limitations=limitations,
                    provider_trace=error.call_trace,
                    message=str(error),
                )
                raise
            response = dict(response_with_trace)
            transport_trace = response.pop("_remediation_transport_trace", None)
            if transport_trace is None:
                transport_trace = {
                    "request": _redact_sensitive(payload),
                    "attempts": [
                        {
                            "attempt": 1,
                            "status": "completed_by_client",
                            "http_status": None,
                        }
                    ],
                    "status": "completed",
                }
            provider_call = {
                **transport_trace,
                "response": _redact_sensitive(response),
            }
            try:
                parsed = parse_structured_response(response)
                restored_results = restore_case_ids(
                    parsed["cases"],
                    compiled_prompt.case_ref_to_id,
                )
                suggestions, model_questions, model_limitations = _model_results(
                    check_id=check["check_id"],
                    module_name=module_name,
                    check_policy=check_policy,
                    requested_cases=eligible_cases,
                    results=restored_results,
                )
            except (RemediationProviderError, ValueError) as caught_error:
                error = RemediationProviderError(str(caught_error))
                error.call_trace = _failed_turn(
                    turn_id=turn_id,
                    started_at=turn_started_at,
                    scope=scope,
                    check_id=check["check_id"],
                    cases=cases,
                    context_answers=context_answers,
                    eligible_cases=eligible_cases,
                    questions=questions,
                    limitations=limitations,
                    provider_trace=provider_call,
                    message=str(error),
                )
                raise error from caught_error
            questions.extend(model_questions)
            limitations.extend(model_limitations)
            model_evidence = build_model_metrics(
                response,
                model=self.model,
                model_profile_id=self.profile.profile_id,
                prompt_profile_id=compiled_prompt.prompt_profile_id,
                transport_trace=transport_trace,
            )
            provider_call["parsed_output"] = _redact_sensitive(parsed)
            provider_call["metrics"] = _redact_sensitive(model_evidence)

        status = _result_status(suggestions, questions, limitations)
        case_results = project_case_results(
            cases,
            suggestions=suggestions,
            questions=questions,
            limitations=limitations,
        )
        now = datetime.now(UTC).isoformat()
        turn = _completed_turn(
            turn_id=turn_id,
            started_at=turn_started_at,
            scope=scope,
            check_id=check["check_id"],
            cases=cases,
            context_answers=context_answers,
            eligible_cases=eligible_cases,
            provider_call=provider_call,
            status=status,
            suggestions=suggestions,
            questions=questions,
            limitations=limitations,
        )
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
            "case_results": case_results,
            "latest_turn_id": turn_id,
            "turns": [turn],
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
        case_results = project_case_results(
            cases,
            suggestions=suggestions,
            questions=[],
            limitations=[],
        )
        now = datetime.now(UTC).isoformat()
        turn_id = uuid4().hex
        turn = _completed_turn(
            turn_id=turn_id,
            started_at=now,
            scope=scope,
            check_id=check["check_id"],
            cases=cases,
            context_answers=context_answers or {},
            eligible_cases=[],
            provider_call=None,
            status="candidate_ready",
            suggestions=suggestions,
            questions=[],
            limitations=[],
        )
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
            "case_results": case_results,
            "latest_turn_id": turn_id,
            "turns": [turn],
        }


class FutureOpenAIRemediationProvider(OpenAIRemediationProvider):
    """Compatibility alias for the formerly reserved provider name."""
