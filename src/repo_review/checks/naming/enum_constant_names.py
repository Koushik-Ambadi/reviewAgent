# src/repo_review/checks/naming/enum_constant_names.py

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .common_identifier import evaluate_atomic_rules


def validate_enum_constant_names(
    symbols,
    module_name,
    naming_policy,
):
    cases = []

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

                reasons = evaluate_atomic_rules(
                    name,
                    naming_policy["rules"],
                    context={"module": module_name},
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
        check_id="enum_constant_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
