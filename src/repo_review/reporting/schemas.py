# src/repo_review/reporting/schemas.py

REPORT_VERSION = "1.0"

STATUS_FAILED = "failed"
STATUS_WARNING = "warning"
STATUS_PASSED = "passed"

SECTION_STRUCTURE = (
    "folder_and_file_structure"
)

SECTION_AST = (
    "ast_review_results"
)

SECTION_CODE_REVIEW = (
    "code_review_checks"
)

DEFAULT_BODY = {
    "failed": [],
    "exception": [],
    "passed": [],
}