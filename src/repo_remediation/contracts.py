"""Stable provider and transport contracts for remediation workflows."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class RemediationProviderError(RuntimeError):
    """Base error for model-backed remediation failures."""

    def __init__(
        self,
        message: str,
        *,
        call_trace: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.call_trace = call_trace


class RemediationProviderUnavailableError(RemediationProviderError):
    """Raised when the configured model provider cannot be used."""


class ResponsesClient(Protocol):
    def create(self, payload: dict[str, Any]) -> dict[str, Any]: ...


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
