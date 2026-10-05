# src/repo_review/checks/naming/type_names.py
import re

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .common_identifier import (
    has_consecutive_underscores,
    has_leading_underscore,
    has_trailing_underscore,
    has_valid_characters,
    is_within_length,
)


def validate_type_names(
    symbols,
    module_name,
    naming_policy,
):
    cases = []

    max_length = naming_policy["max_length"]
    allowed_characters_pattern = naming_policy[
        "allowed_characters_pattern"
    ]

    module_prefix = naming_policy[
        "module_prefix"
    ].format(
        module=module_name
    )

    suffix = naming_policy["suffix"]

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")

        for typedef in file_symbols.get(
            "typedefs",
            [],
        ):
            name = typedef.get("name", "")
            line = typedef.get("line", "")

            location = (
                f"{file_path}:"
                f"{name}:"
                f"{line}"
            )

            reasons = []

            # Maximum length
            if not is_within_length(
                name,
                max_length=max_length,
            ):
                reasons.append(
                    f"Type name must not exceed "
                    f"{max_length} characters"
                )

            # Allowed characters
            if not has_valid_characters(
                name,
                allowed_characters_pattern,
            ):
                reasons.append(
                    "Type name contains invalid characters"
                )

            # Leading underscore
            if (
                not naming_policy[
                    "leading_underscore_allowed"
                ]
                and has_leading_underscore(name)
            ):
                reasons.append(
                    "Type name must not start with '_'"
                )

            # Consecutive underscores
            if (
                not naming_policy[
                    "consecutive_underscores_allowed"
                ]
                and has_consecutive_underscores(name)
            ):
                reasons.append(
                    "Type name must not contain consecutive underscores"
                )

            # Trailing underscore
            if (
                not naming_policy[
                    "trailing_underscore_allowed"
                ]
                and has_trailing_underscore(name)
            ):
                reasons.append(
                    "Type name must not end with '_'"
                )

            # Module prefix
            if not name.startswith(module_prefix):
                reasons.append(
                    f"Type name must start with "
                    f"'{module_prefix}'"
                )

            # Suffix
            if not name.endswith(suffix):
                reasons.append(
                    f"Type name must end with "
                    f"'{suffix}'"
                )

            # Description
            if (
                naming_policy["description_required"]
                and name.startswith(module_prefix)
                and name.endswith(suffix)
            ):
                description = name[
                    len(module_prefix):
                    -len(suffix)
                ]

                if not description:
                    reasons.append(
                        "Type name must contain a description "
                        "between module prefix and suffix"
                    )

            cases.append(
                CaseResult(
                    status=(
                        CaseStatus.FAILED
                        if reasons
                        else CaseStatus.SUCCESS
                    ),
                    name=name,
                    location=location,
                    reasons=reasons,
                )
            )

    return CheckResult(
        title="Type Names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )