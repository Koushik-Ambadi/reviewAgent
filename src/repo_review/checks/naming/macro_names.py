from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)
from .common_identifier import evaluate_atomic_rules, find_applicability_exclusion


def validate_macro_names(symbols, module_name, naming_policy):
    cases = []
    value_type = naming_policy["macro_value_type"]

    for file_symbols in symbols:
        file_path = file_symbols.get("file", "")
        for macro in file_symbols.get("macros", []):
            name = macro.get("name", "")
            if macro.get("type", "") != value_type:
                continue

            location = f"{file_path}:{macro.get('line', '')}"
            exclusion = find_applicability_exclusion(
                name,
                naming_policy.get("applicability_exclusions", []),
                context={"module": module_name},
            )
            if exclusion:
                cases.append(
                    CaseResult(
                        status=CaseStatus.SKIPPED,
                        name=name,
                        location=location,
                        reasons=[f"[{exclusion['id']}] {exclusion['reason']}"],
                    )
                )
                continue

            reasons = evaluate_atomic_rules(
                name,
                naming_policy["rules"],
                context={"module": module_name},
            )
            cases.append(
                CaseResult(
                    status=CaseStatus.FAILED if reasons else CaseStatus.SUCCESS,
                    name=name,
                    location=location,
                    reasons=reasons,
                )
            )

    return CheckResult(
        title="Macro Names",
        check_id="macro_names",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(cases),
        cases=cases,
    )
