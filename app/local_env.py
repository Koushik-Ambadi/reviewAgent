from __future__ import annotations

import os
from pathlib import Path


LOCAL_ENV_PATH = Path(__file__).resolve().parents[1] / ".env.local"
PLACEHOLDER_VALUE = "replace_with_your_openai_api_key"
ALLOWED_LOCAL_KEYS = {
    "OPENAI_API_KEY",
    "OPENAI_REMEDIATION_MODEL",
    "OPENAI_BUILD_REMEDIATION_MODEL",
    "OPENAI_REMEDIATION_TIMEOUT_SECONDS",
}


def load_local_env(path: Path = LOCAL_ENV_PATH) -> set[str]:
    """Load the small, allow-listed local configuration without overriding env."""
    if not path.is_file():
        return set()

    loaded: set[str] = set()
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid .env.local entry on line {line_number}.")

        key, value = (part.strip() for part in line.split("=", 1))
        if key not in ALLOWED_LOCAL_KEYS:
            raise ValueError(
                f"Unsupported .env.local key on line {line_number}: {key}"
            )
        value = _strip_matching_quotes(value)
        if not value or value == PLACEHOLDER_VALUE or key in os.environ:
            continue
        os.environ[key] = value
        loaded.add(key)
    return loaded


def _strip_matching_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value
