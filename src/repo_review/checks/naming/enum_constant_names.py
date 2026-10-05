# src/repo_review/checks/naming/enum_constant_names.py

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


def validate_enum_constant_names(
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

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")

        for enum in file_symbols.get(
            "enums",
            [],
        ):
            enum_name = enum.get("name", "")
            enum_line = enum.get("line", "")

            for constant in enum.get(
                "constants",
                [],
            ):
                name = constant.get("name", "")
                line = constant.get("line", "")

                location = (
                    f"{file_path}:"
                    f"{enum_name}:"
                    f"{name}:"
                    f"{line}"
                )

                reasons = []

                if not is_within_length(
                    name,
                    max_length=max_length,
                ):
                    reasons.append(
                        f"Enum constant name must not exceed "
                        f"{max_length} characters"
                    )

                if not has_valid_characters(
                    name,
                    allowed_characters_pattern,
                ):
                    reasons.append(
                        "Enum constant name contains invalid characters"
                    )

                if (
                    not naming_policy[
                        "leading_underscore_allowed"
                    ]
                    and has_leading_underscore(name)
                ):
                    reasons.append(
                        "Enum constant name must not start with '_'"
                    )

                if (
                    not naming_policy[
                        "consecutive_underscores_allowed"
                    ]
                    and has_consecutive_underscores(name)
                ):
                    reasons.append(
                        "Enum constant name must not contain "
                        "consecutive underscores"
                    )

                if (
                    not naming_policy[
                        "trailing_underscore_allowed"
                    ]
                    and has_trailing_underscore(name)
                ):
                    reasons.append(
                        "Enum constant name must not end with '_'"
                    )

                if not name.startswith(module_prefix):
                    reasons.append(
                        f"Enum constant name must start with "
                        f"'{module_prefix}'"
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
        title="Enum Constant Names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )