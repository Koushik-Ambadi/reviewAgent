# src/repo_review/checks/naming/macro_names.py

import re

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .utils import is_excluded_macro


def validate_macro_names(
    symbols,
    module_name,
    naming_policy,
):

    cases = []

    allowed_characters_pattern = re.compile(
        naming_policy["allowed_characters_pattern"]
    )

    value_type = naming_policy[
        "macro_value_type"
    ]

    module_prefix = naming_policy["module_prefix"].format(
        module=module_name.upper()
    )

    for file_symbols in symbols:

        file_path = file_symbols.get(
            "file",
            "",
        )

        macros = file_symbols.get(
            "macros",
            [],
        )

        for macro in macros:

            name = macro.get(
                "name",
                "",
            )

            macro_type = macro.get(
                "type",
                "",
            )

            line = macro.get(
                "line",
                "",
            )

            location = (
                f"{file_path}:{line}"
            )

            #
            # Only validate configured macro type
            #

            if macro_type != value_type:
                continue

            #
            # Excluded macros
            #

            if is_excluded_macro(
                name,
                naming_policy["applicability_exclusions"],
                module_name,
            ):

                cases.append(
                    CaseResult(
                        status=CaseStatus.SKIPPED,
                        name=name,
                        location=location,
                        reasons=[
                            (
                                "Macro excluded by "
                                "applicability policy."
                            )
                        ],
                    )
                )

                continue

            #
            # Naming validation
            #

            reasons = []

            if not allowed_characters_pattern.fullmatch(name):
                reasons.append(
                    "Macro name may contain only letters, digits, and underscores."
                )

            if naming_policy.get("uppercase_only", True) and any(
                character.isalpha() and not character.isupper()
                for character in name
            ):
                reasons.append("Macro name must use uppercase letters.")

            if not name.startswith(module_prefix):
                if name.startswith(module_name.upper()):
                    reasons.append(
                        f"Module prefix must be followed by an underscore ('{module_prefix}')."
                    )
                else:
                    reasons.append(
                        f"Macro name must start with module prefix '{module_prefix}'."
                    )

            if (
                not naming_policy.get("consecutive_underscores_allowed", False)
                and "__" in name
            ):
                reasons.append("Macro name must not contain consecutive underscores.")

            if (
                not naming_policy.get("trailing_underscore_allowed", False)
                and name.endswith("_")
            ):
                reasons.append("Macro name must not end with an underscore.")

            if name.startswith(module_prefix) and not name[
                len(module_prefix):
            ].strip("_"):
                reasons.append("Macro name must include a description after the module prefix.")

            #
            # Final result
            #

            if reasons:

                cases.append(
                    CaseResult(
                        status=CaseStatus.FAILED,
                        name=name,
                        location=location,
                        reasons=reasons,
                    )
                )

            else:

                cases.append(
                    CaseResult(
                        status=CaseStatus.SUCCESS,
                        name=name,
                        location=location,
                        reasons=[],
                    )
                )

    return CheckResult(
        title="Macro Names",
        check_id="macro_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
