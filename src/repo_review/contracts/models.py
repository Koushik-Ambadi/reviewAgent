# src/repo_review/contracts/models.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .status import (
    CaseStatus,
    CheckStatus,
    RunStatus,
    StageStatus,
)


@dataclass
class CaseResult:
    status: CaseStatus
    name: str
    location: str
    case_id: str = ""
    reasons: list[str] = field(default_factory=list)


@dataclass
class CheckSummary:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0


@dataclass
class CheckResult:
    title: str
    status: CheckStatus
    summary: CheckSummary
    check_id: str = ""
    cases: list[CaseResult] = field(default_factory=list)


@dataclass
class StageSummary:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0


@dataclass
class StageResult:
    title: str
    status: StageStatus
    summary: StageSummary
    stage_id: str = ""
    checks: list[CheckResult] = field(default_factory=list)


@dataclass
class RunSummary:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total: int = 0


@dataclass
class RunResult:
    run_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    policy_version: str = ""
    report_version: str = ""
    status: RunStatus = RunStatus.COMPLETED
    summary: RunSummary = field(default_factory=RunSummary)
    stages: list[StageResult] = field(default_factory=list)
    remediation: list[dict[str, Any]] = field(default_factory=list)
    build_result: dict[str, Any] = field(default_factory=dict)
