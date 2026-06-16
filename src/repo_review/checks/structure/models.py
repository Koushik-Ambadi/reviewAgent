# src/repo_review/checks/structure/models.py

from pydantic import BaseModel


class FileNode(BaseModel):
    relative_path: str
    is_dir: bool
    size: int
    extension: str
    depth: int
    name: str


class ValidationIssue(BaseModel):
    severity: str
    rule: str
    path: str
    message: str
    status: str = "FAILED"