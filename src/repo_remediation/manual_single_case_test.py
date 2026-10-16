"""Make one minimal Responses API call for a fixed failed naming case."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(REPOSITORY_ROOT))
sys.path.insert(0, str(SOURCE_ROOT))

from app.local_env import load_local_env  # noqa: E402
from repo_remediation.providers import (  # noqa: E402
    OpenAIResponsesClient,
    RemediationProviderError,
)


FAILED_CASE = {
    "name": "Shunt_msgcountercheck_Init",
    "location": "src/shunt_model.c:536",
    "failed_rule_id": "ABS-POLICY-FUNCTION-WORD-CASE",
}

ACTUAL_POLICY = {
    "id": "ABS-POLICY-FUNCTION-WORD-CASE",
    "validator": "lowercase_after_prefix",
    "value": "{module}_",
    "module_case": "title",
    "reason": "Letters after module prefix '{expected}' must be lowercase.",
}

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "current_name": {"type": "string"},
        "remediation": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["current_name", "remediation", "reason"],
}


def main() -> int:
    load_local_env()
    prompt = {
        "failed_case": FAILED_CASE,
        "actual_policy": ACTUAL_POLICY,
        "output_format": {
            "current_name": "original failed name",
            "remediation": "policy-compliant replacement name",
            "reason": "one short sentence",
        },
    }
    payload = {
        "model": "gpt-5-nano",
        "store": False,
        "reasoning": {"effort": "minimal"},
        "max_output_tokens": 200,
        "input": [
            {
                "role": "user",
                "content": json.dumps(prompt, separators=(",", ":")),
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "single_case_remediation",
                "strict": True,
                "schema": OUTPUT_SCHEMA,
            },
            "verbosity": "low",
        },
    }

    try:
        response = OpenAIResponsesClient().create(payload)
        output_text = _output_text(response)
        result = json.loads(output_text)
    except (RemediationProviderError, json.JSONDecodeError, ValueError) as error:
        print(f"Request failed: {error}", file=sys.stderr)
        return 1

    print("=== MODEL OUTPUT ===")
    print(output_text)
    print("\n\033[1;32m=== REMEDIATION ===")
    print(
        f"{result['current_name']}  ->  {result['remediation']}\033[0m"
    )
    print(f"Reason: {result['reason']}")
    return 0


def _output_text(response: dict[str, Any]) -> str:
    for output in response.get("output", []):
        if output.get("type") != "message":
            continue
        for content in output.get("content", []):
            if content.get("type") == "output_text":
                return str(content["text"])
    raise ValueError("The model response did not contain output text.")


if __name__ == "__main__":
    raise SystemExit(main())
