"""Model-facing contracts for naming remediation generation."""

from .candidate_validation import validate_candidate
from .model_settings import RemediationModelSettings
from .output import (
    REMEDIATION_RESPONSE_SCHEMA,
    parse_structured_response,
    restore_case_ids,
)
from .prompting import CompiledRemediationPrompt, compile_remediation_prompt

__all__ = [
    "CompiledRemediationPrompt",
    "REMEDIATION_RESPONSE_SCHEMA",
    "RemediationModelSettings",
    "compile_remediation_prompt",
    "parse_structured_response",
    "restore_case_ids",
    "validate_candidate",
]
