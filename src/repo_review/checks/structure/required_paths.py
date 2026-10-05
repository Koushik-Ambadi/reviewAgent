# src/repo_review/checks/structure/required_paths.py

from ...contracts import (
    CaseResult,
    CaseStatus,
    CheckResult,
    CheckStatus,
    build_check_summary,
)

from .utils import (
    normalize,
    match_pattern,
)


def validate_required_paths(
    nodes,
    module_name,
    required_paths,
):

    cases = []

    files = [
        normalize(n.relative_path)
        for n in nodes
        if not n.is_dir
    ]

    dirs = {
        normalize(n.relative_path)
        for n in nodes
        if n.is_dir
    }

    for required in required_paths:

        req = normalize(
            required.replace(
                "{module}",
                module_name,
            )
        )

        if req.endswith("/"):

            req_dir = req.rstrip("/")

            if req_dir in dirs:

                cases.append(
                    CaseResult(
                        status=CaseStatus.SUCCESS,
                        name=req,
                        location=req,
                        reasons=[],
                    )
                )

            else:

                cases.append(
                    CaseResult(
                        status=CaseStatus.FAILED,
                        name=req,
                        location=req,
                        reasons=[
                            (
                                f"Required directory "
                                f"'{req}' is missing."
                            )
                        ],
                    )
                )

            continue

        found = any(
            match_pattern(
                file_path,
                req,
            )
            for file_path in files
        )

        if found:

            cases.append(
                CaseResult(
                    status=CaseStatus.SUCCESS,
                    name=req,
                    location=req,
                    reasons=[],
                )
            )

        else:

            cases.append(
                CaseResult(
                    status=CaseStatus.FAILED,
                    name=req,
                    location=req,
                    reasons=[
                        (
                            f"Required path "
                            f"'{req}' is missing."
                        )
                    ],
                )
            )

    return CheckResult(
        title="Required Paths",
        check_id="required_paths",
        status=CheckStatus.COMPLETED,
        summary=build_check_summary(
            cases
        ),
        cases=cases,
    )
