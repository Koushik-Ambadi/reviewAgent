# src/repo_review/contracts/status.py

from enum import StrEnum


class CaseStatus(StrEnum):
    # one item checked
    # example: one function name
    SUCCESS = "SUCCESS"   # rule passed
    FAILED = "FAILED"     # rule failed
    SKIPPED = "SKIPPED"   # rule not applied


class CheckStatus(StrEnum):
    # one check finished
    # example: all function names checked
    COMPLETED = "COMPLETED"  # check finished
    ERROR = "ERROR"          # check crashed
    SKIPPED = "SKIPPED"      # check disabled/not run


class StageStatus(StrEnum):
    # group of checks finished
    # example: structure stage, checks stage
    COMPLETED = "COMPLETED"  # stage finished
    ERROR = "ERROR"          # stage crashed


class RunStatus(StrEnum):
    # full review finished
    COMPLETED = "COMPLETED"  # everything passed
    PARTIAL = "PARTIAL"      # some stages failed/skipped
    ERROR = "ERROR"          # run crashed