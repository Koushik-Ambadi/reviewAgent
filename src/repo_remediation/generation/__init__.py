"""Model-facing generation contracts for naming remediation."""

from .candidate_validation import validate_candidate
from .model_selection import RemediationModelProfile
from .prompt_builder import CompiledRemediationPrompt, compile_remediation_prompt
from .response_contract import (
    REMEDIATION_RESPONSE_SCHEMA,
    parse_structured_response,
    restore_case_ids,
)

__all__ = [
    "CompiledRemediationPrompt",
    "REMEDIATION_RESPONSE_SCHEMA",
    "RemediationModelProfile",
    "compile_remediation_prompt",
    "parse_structured_response",
    "restore_case_ids",
    "validate_candidate",
]
