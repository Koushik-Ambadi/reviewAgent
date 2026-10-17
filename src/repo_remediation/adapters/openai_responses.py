"""OpenAI Responses API transport adapter."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

from repo_remediation.contracts import (
    RemediationProviderError,
    RemediationProviderUnavailableError,
)
from repo_remediation.observability import redact_sensitive


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
        request_snapshot = redact_sensitive(payload)
        attempts: list[dict[str, Any]] = []
        if not self.api_key:
            raise RemediationProviderUnavailableError(
                "OPENAI_API_KEY is not configured for model-backed remediation.",
                call_trace={
                    "request": request_snapshot,
                    "attempts": attempts,
                    "status": "configuration_error",
                },
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
                attempt_started = time.perf_counter()
                try:
                    response = client.post(self.endpoint, headers=headers, json=payload)
                except httpx.RequestError as error:
                    last_error = (
                        "OpenAI Responses API request failed: "
                        f"{error.__class__.__name__}."
                    )
                    attempts.append(
                        {
                            "attempt": attempt + 1,
                            "status": "network_error",
                            "error_type": error.__class__.__name__,
                            "elapsed_ms": _elapsed_ms(attempt_started),
                        }
                    )
                    if attempt == 0:
                        time.sleep(0.25)
                        continue
                    raise RemediationProviderUnavailableError(
                        last_error,
                        call_trace={
                            "request": request_snapshot,
                            "attempts": attempts,
                            "status": "failed",
                        },
                    ) from error

                response_body = _response_body(response)
                attempts.append(
                    {
                        "attempt": attempt + 1,
                        "status": "success" if response.is_success else "http_error",
                        "http_status": response.status_code,
                        "elapsed_ms": _elapsed_ms(attempt_started),
                        "response": redact_sensitive(response_body),
                    }
                )

                if response.is_success:
                    if not isinstance(response_body, dict):
                        raise RemediationProviderError(
                            "OpenAI Responses API returned a non-object response.",
                            call_trace={
                                "request": request_snapshot,
                                "attempts": attempts,
                                "status": "invalid_response",
                            },
                        )
                    result = dict(response_body)
                    result["_remediation_transport_trace"] = {
                        "request": request_snapshot,
                        "attempts": attempts,
                        "status": "completed",
                    }
                    return result

                last_error = _safe_openai_error(response)
                if response.status_code in retryable_statuses and attempt == 0:
                    time.sleep(0.25)
                    continue
                error_type = (
                    RemediationProviderUnavailableError
                    if response.status_code in retryable_statuses
                    else RemediationProviderError
                )
                raise error_type(
                    last_error,
                    call_trace={
                        "request": request_snapshot,
                        "attempts": attempts,
                        "status": "failed",
                    },
                )

        raise RemediationProviderUnavailableError(
            last_error,
            call_trace={
                "request": request_snapshot,
                "attempts": attempts,
                "status": "failed",
            },
        )


def _safe_openai_error(response: httpx.Response) -> str:
    message = f"OpenAI Responses API returned HTTP {response.status_code}."
    try:
        detail = response.json().get("error", {}).get("message")
    except (ValueError, AttributeError):
        detail = None
    if detail:
        message = f"{message} {str(detail)[:300]}"
    return message


def _elapsed_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 3)


def _response_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {"unparsed_text": response.text}
