"""Secret-safe snapshots for remediation evidence."""

from __future__ import annotations

from typing import Any


_SENSITIVE_TRACE_KEYS = {
    "authorization",
    "api-key",
    "api_key",
    "openai_api_key",
    "x-api-key",
}


def redact_sensitive(value: Any) -> Any:
    """Return a JSON-safe trace snapshot without credentials or secret fields."""
    if isinstance(value, dict):
        return {
            str(key): (
                "[REDACTED]"
                if str(key).casefold() in _SENSITIVE_TRACE_KEYS
                else redact_sensitive(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_sensitive(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)
