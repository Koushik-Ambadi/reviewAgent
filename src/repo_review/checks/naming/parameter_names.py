# src/repo_review/checks/naming/parameter_names.py
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


def validate_parameter_names(
    symbols,
    naming_policy,
):
    cases = []

    min_length = naming_policy["min_length"]
    max_length = naming_policy["max_length"]
    allowed_characters_pattern = naming_policy[
        "allowed_characters_pattern"
    ]

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")

        for parameter in file_symbols.get(
            "parameters",
            [],
        ):
            name = parameter.get("name", "")
            line = parameter.get("line", "")

            location = (
                f"{file_path}:"
                f"{name}:"
                f"{line}"
            )

            reasons = []

            if not name:
                if not naming_policy["missing_name_allowed"]:
                    reasons.append(
                        "Parameter name is required"
                    )

            else:
                if not is_within_length(
                    name,
                    min_length=min_length,
                    max_length=max_length,
                ):
                    if len(name) < min_length:
                        reasons.append(
                            f"Parameter name must be at least "
                            f"{min_length} characters"
                        )

                    if len(name) > max_length:
                        reasons.append(
                            f"Parameter name must not exceed "
                            f"{max_length} characters"
                        )

                if not has_valid_characters(
                    name,
                    allowed_characters_pattern,
                ):
                    reasons.append(
                        "Parameter name contains invalid characters"
                    )

                if (
                    not naming_policy[
                        "leading_underscore_allowed"
                    ]
                    and has_leading_underscore(name)
                ):
                    reasons.append(
                        "Parameter name must not start with '_'"
                    )

                if (
                    not naming_policy[
                        "consecutive_underscores_allowed"
                    ]
                    and has_consecutive_underscores(name)
                ):
                    reasons.append(
                        "Parameter name must not contain "
                        "consecutive underscores"
                    )

                if (
                    not naming_policy[
                        "trailing_underscore_allowed"
                    ]
                    and has_trailing_underscore(name)
                ):
                    reasons.append(
                        "Parameter name must not end with '_'"
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
        title="Parameter Names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )