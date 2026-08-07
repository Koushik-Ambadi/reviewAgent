from .models import (
    CaseResult,
    CheckResult,
    CheckSummary,
    StageResult,
    StageSummary,
    RunSummary,
)
from .status import (
    CaseStatus,
)


def build_check_summary(
    cases: list[CaseResult],
) -> CheckSummary:

    return CheckSummary(
        passed=sum(
            case.status == CaseStatus.SUCCESS
            for case in cases
        ),
        failed=sum(
            case.status == CaseStatus.FAILED
            for case in cases
        ),
        skipped=sum(
            case.status == CaseStatus.SKIPPED
            for case in cases
        ),
        total=len(cases),
    )


def build_stage_summary(
    checks: list[CheckResult],
) -> StageSummary:

    summary = StageSummary()

    for check in checks:
        summary.passed += check.summary.passed
        summary.failed += check.summary.failed
        summary.skipped += check.summary.skipped
        summary.total += check.summary.total

    return summary


def build_run_summary(
    stages: list[StageResult],
) -> RunSummary:

    summary = RunSummary()

    for stage in stages:
        summary.passed += stage.summary.passed
        summary.failed += stage.summary.failed
        summary.skipped += stage.summary.skipped
        summary.total += stage.summary.total

    return summary