from dataclasses import dataclass


@dataclass
class ValidationIssue:
    severity: str
    rule: str
    path: str
    message: str
    status: str = "FAILED"