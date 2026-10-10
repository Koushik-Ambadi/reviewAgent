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
class InventoryItem:
    inventory_id: str
    label: str
    identified: int


@dataclass
class InventoryArtifact:
    artifact_id: str
    name: str
    location: str
    evidence: list[str] = field(default_factory=list)
    audit_status: str = "not_audited"
    audit_reason: str | None = None


@dataclass
class InventoryGroup:
    group_id: str
    label: str
    artifacts: list[InventoryArtifact] = field(default_factory=list)


@dataclass
class InventoryAuditSummary:
    status: str = "inventory_initialized"
    audited: int = 0
    pending_approval: int = 0
    not_audited: int = 0


@dataclass
class InventorySummary:
    source_artifact: str = "analysis/symbols.json"
    parsed_files: int = 0
    skipped_files: int = 0
    items: list[InventoryItem] = field(default_factory=list)
    groups: list[InventoryGroup] = field(default_factory=list)
    audit: InventoryAuditSummary = field(default_factory=InventoryAuditSummary)


@dataclass
class StageResult:
    title: str
    status: StageStatus
    summary: StageSummary
    stage_id: str = ""
    checks: list[CheckResult] = field(default_factory=list)
    inventory: InventorySummary | None = None


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
