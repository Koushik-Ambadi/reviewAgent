# review/app/services/review_service.py
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
import json

import re
from collections import defaultdict
from collections import Counter
from typing import Any

from orchestrator.runner import (
    prepare_review_run,
)

from repo_review.review import (
    run_review,
)

UPLOAD_DIR = (
    Path("app")
    / "temp"
    / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

RUNS_DIR = (
    Path("workspace")
    / "runs"
)


def review_uploaded_zip(
    upload_file,
):

    file_id = uuid4().hex

    zip_path = (
        UPLOAD_DIR
        / f"{file_id}.zip"
    )

    with open(zip_path, "wb") as f:
        f.write(
            upload_file.file.read()
        )

    (
        workspace_path,
        repo_root,
        module_name,
    ) = prepare_review_run(
        source_path=zip_path,
        source_type="zip",
    )

    context = run_review(
        repo_root=repo_root,
        workspace_path=workspace_path,
        module_name=module_name,
    )

    try:
        zip_path.unlink()
    except OSError:
        pass

    return {
        "report": context.report,
    }


###################################
##### Review Summary Builders #####
###################################

def build_agent_review_summary(
    review_report: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a compact agent-readable review summary.

    Rules:
    - Ignore passed checks completely.
    - Treat failed checks as actionable.
    - Treat exceptions as skipped/excluded checks.
    - Group code-review failures dynamically by rule.
    """
    metadata = review_report.get("metadata") or {}
    report_summary = review_report.get("summary") or {}
    sections = review_report.get("sections") or []

    run_id = metadata.get("run_id")
    module_name = metadata.get("module_name")
    policy_name = metadata.get("policy_name")

    summary_lines: list[str] = []
    total_exceptions = 0

    for section in sections:
        section_name = section.get("name")
        issues = section.get("issues") or []

        if section_name == "structure":
            summary_lines.extend(
                summarize_structure_section(
                    issues
                )
            )

        elif section_name == "code_review":
            code_summary, exception_count = (
                summarize_code_review_section(
                    issues,
                    run_id=run_id,
                )
            )

            summary_lines.extend(code_summary)
            total_exceptions += exception_count

    failed_count = int(
        report_summary.get("failed", 0)
    )

    exception_count = int(
        report_summary.get(
            "exception",
            total_exceptions,
        )
    )

    if exception_count:
        summary_lines.append(
            f"{exception_count} check"
            f"{'s were' if exception_count != 1 else ' was'} "
            "skipped or excluded."
        )

    return {
        "run_id": run_id,
        "module": module_name,
        "policy_name": policy_name,
        "status": (
            "failed"
            if failed_count > 0
            else "passed"
        ),
        "result": build_result_sentence(
            failed_count,
            exception_count,
        ),
        "summary": summary_lines,
        "details_available": bool(run_id),
    }


def summarize_structure_section(
    issues: list[dict[str, Any]],
) -> list[str]:
    """
    Summarize the fixed structure section.

    Passed checks are ignored.
    """
    missing_paths: list[str] = []
    other_failures: Counter[str] = Counter()

    for issue in issues:
        status = normalize_status(
            issue.get("status")
        )

        if status != "FAILED":
            continue

        rule = str(
            issue.get("rule") or "unknown"
        )

        if rule == "required_paths":
            path = issue.get("path")

            if path:
                missing_paths.append(str(path))
        else:
            other_failures[rule] += 1

    lines: list[str] = []

    if missing_paths:
        unique_paths = list(
            dict.fromkeys(missing_paths)
        )

        lines.append(
            f"{len(unique_paths)} required project "
            f"path{'s are' if len(unique_paths) != 1 else ' is'} "
            f"missing: {', '.join(unique_paths)}."
        )

    # Defensive handling in case another structure rule
    # unexpectedly appears later.
    for rule, count in other_failures.items():
        readable_rule = humanize_rule(rule)

        lines.append(
            f"{count} {readable_rule} "
            f"violation{'s' if count != 1 else ''} found."
        )

    return lines



def summarize_code_review_section(
    issues: list[dict[str, Any]],
    *,
    run_id: str | None,
) -> tuple[list[str], int]:
    """
    Group every failed code-review issue dynamically by rule.

    New rule types are included automatically.
    """
    failures_by_rule: Counter[str] = Counter()
    files_by_rule: dict[str, set[str]] = {}
    exceptions = 0

    for issue in issues:
        status = normalize_status(
            issue.get("status")
        )

        if status == "PASSED":
            continue

        if status == "EXCEPTION":
            exceptions += 1
            continue

        if status != "FAILED":
            continue

        rule = str(
            issue.get("rule") or "unknown"
        )

        failures_by_rule[rule] += 1

        path = clean_report_path(
            issue.get("file")
            or issue.get("path"),
            run_id=run_id,
        )

        if path:
            files_by_rule.setdefault(
                rule,
                set(),
            ).add(path)

    lines: list[str] = []

    for rule, count in failures_by_rule.most_common():
        readable_rule = humanize_rule(rule)
        files = sorted(
            files_by_rule.get(rule, set())
        )

        line = (
            f"{count} {readable_rule} "
            f"violation{'s' if count != 1 else ''} found"
        )

        if files:
            line += (
                f", mainly in "
                f"{format_items(files, limit=3)}"
            )

        lines.append(line + ".")

    return lines, exceptions


def humanize_rule(
    rule: str,
) -> str:
    """
    Convert rule identifiers into readable labels.

    Examples:
        global_variable_names -> global variable names
        array_sizes -> array sizes
    """
    return rule.replace("_", " ").strip()


def format_items(
    items: list[str],
    *,
    limit: int,
) -> str:
    visible_items = items[:limit]
    remaining = len(items) - len(visible_items)

    result = ", ".join(visible_items)

    if remaining > 0:
        result += (
            f", and {remaining} other "
            f"file{'s' if remaining != 1 else ''}"
        )

    return result


def clean_report_path(
    value: Any,
    *,
    run_id: str | None,
) -> str | None:
    if not value:
        return None

    path = str(value).replace("\\", "/")

    if run_id:
        marker = f"/runs/{run_id}/"

        if marker in path:
            path = path.split(
                marker,
                1,
            )[1]

    return path.removeprefix("./")


def normalize_status(
    value: Any,
) -> str:
    return str(value or "").strip().upper()


def build_result_sentence(
    failed_count: int,
    exception_count: int,
) -> str:
    if failed_count == 0 and exception_count == 0:
        return "The review passed with no issues."

    parts: list[str] = []

    if failed_count:
        parts.append(
            f"{failed_count} failure"
            f"{'s' if failed_count != 1 else ''}"
        )

    if exception_count:
        parts.append(
            f"{exception_count} exception"
            f"{'s' if exception_count != 1 else ''}"
        )

    verb = "was" if sum(
        [failed_count, exception_count]
    ) == 1 else "were"

    return f"{' and '.join(parts)} {verb} found."



###################################
##### Review Report Builders ######
###################################

def load_agent_review(
    run_id: str,
) -> dict[str, Any]:
    """
    Load the full report and return a compact,
    agent-readable detailed report.
    """
    report_path = (
        RUNS_DIR
        / run_id
        / "report.json"
    )

    if not report_path.exists():
        raise FileNotFoundError(
            f"Review report not found: {run_id}"
        )

    with report_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        review_report = json.load(file)

    return build_agent_detailed_report(
        review_report
    )


def build_agent_detailed_report(
    review_report: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a complete review report into a compact
    remediation input for an agent.

    The function:
    - expects metadata, summary, and sections directly;
    - removes passed checks;
    - reports structure failures without suggestions;
    - groups code-review failures by rule;
    - keeps code-review exceptions separate;
    - returns facts only.
    """
    validate_review_report(review_report)

    metadata = review_report["metadata"]
    summary = review_report["summary"]
    sections = review_report["sections"]

    run_id = str(
        metadata.get("run_id") or ""
    )


    structure_section = find_section(
        sections,
        "structure",
    )

    code_review_section = find_section(
        sections,
        "code_review",
    )

    report_text = build_agent_report_text(
        structure_section=structure_section,
        code_review_section=code_review_section,
        run_id=run_id,
    )

    return {
        "run_id": run_id,
        "module": metadata.get("module_name"),
        "policy_name": metadata.get("policy_name"),
        "status": str(
            summary.get(
                "overall_status",
                "unknown",
            )
        ).lower(),
        "failure_count": int(
            summary.get("failed", 0)
        ),
        "exception_count": int(
            summary.get("exception", 0)
        ),
        "report": report_text,
    }


def build_agent_report_text(
    *,
    structure_section: dict[str, Any],
    code_review_section: dict[str, Any],
    run_id: str,
) -> str:
    blocks: list[str] = []

    structure_block = format_structure_section(
        structure_section
    )

    if structure_block:
        blocks.append(structure_block)

    code_review_block = format_code_review_section(
        code_review_section,
        run_id=run_id,
    )

    if code_review_block:
        blocks.append(code_review_block)

    if not blocks:
        return "No failed or exceptional checks were found."

    return "\n\n".join(blocks)    

def format_structure_section(
    section: dict[str, Any],
) -> str:
    failed_issues = [
        issue
        for issue in section.get("issues", [])
        if normalize_status(
            issue.get("status")
        ) == "FAILED"
    ]

    if not failed_issues:
        return ""

    lines = [
        (
            "STRUCTURE"
            f" — {len(failed_issues)} "
            f"{pluralize('failure', len(failed_issues))}"
        ),
        "Path | Reason",
        "--- | ---",
    ]

    for issue in failed_issues:
        path = sanitize_table_cell(
            issue.get("path")
        )

        reason = clean_structure_message(
            issue.get("message")
        )

        lines.append(
            f"{path} | {reason}"
        )

    return "\n".join(lines)

def format_code_review_section(
    section: dict[str, Any],
    *,
    run_id: str,
) -> str:
    failures_by_rule: dict[
        str,
        list[dict[str, str]],
    ] = defaultdict(list)

    exceptions_by_rule: dict[
        str,
        list[dict[str, str]],
    ] = defaultdict(list)

    for issue in section.get("issues", []):
        status = normalize_status(
            issue.get("status")
        )

        # Passed cases are removed completely.
        if status == "PASSED":
            continue

        rule = str(
            issue.get("rule") or "unknown"
        )

        normalized = normalize_code_issue(
            issue,
            run_id=run_id,
        )

        if status == "FAILED":
            failures_by_rule[rule].append(
                normalized
            )

        elif status == "EXCEPTION":
            exceptions_by_rule[rule].append(
                normalized
            )

    failure_count = sum(
        len(cases)
        for cases in failures_by_rule.values()
    )

    exception_count = sum(
        len(cases)
        for cases in exceptions_by_rule.values()
    )

    if failure_count == 0 and exception_count == 0:
        return ""

    header = (
        "CODE REVIEW"
        f" — {failure_count} "
        f"{pluralize('failure', failure_count)}"
    )

    if exception_count:
        header += (
            f", {exception_count} "
            f"{pluralize('exception', exception_count)}"
        )

    blocks = [header]

    sorted_failure_groups = sorted(
        failures_by_rule.items(),
        key=lambda item: (
            -len(item[1]),
            item[0],
        ),
    )

    for rule, cases in sorted_failure_groups:
        blocks.append(
            format_code_rule_group(
                rule=rule,
                cases=cases,
                status_label="failures",
            )
        )

    if exceptions_by_rule:
        blocks.append(
            format_exception_groups(
                exceptions_by_rule
            )
        )

    return "\n\n".join(blocks)

def normalize_code_issue(
    issue: dict[str, Any],
    *,
    run_id: str,
) -> dict[str, str]:
    message = str(
        issue.get("message") or ""
    )

    return {
        "file": clean_report_path(
            issue.get("file"),
            run_id=run_id,
        ),
        "current": extract_subject(
            message
        ),
        "reason": extract_reason(
            message
        ),
    }


def format_code_rule_group(
    *,
    rule: str,
    cases: list[dict[str, str]],
    status_label: str,
) -> str:
    title = humanize_rule(rule)

    lines = [
        (
            f"{title} — {len(cases)} "
            f"{status_label}"
        ),
        "File | Current | Reason",
        "--- | --- | ---",
    ]

    for case in cases:
        file_path = sanitize_table_cell(
            case.get("file")
        )

        current = sanitize_table_cell(
            case.get("current")
        )

        reason = sanitize_table_cell(
            case.get("reason")
        )

        lines.append(
            f"{file_path} | {current} | {reason}"
        )

    return "\n".join(lines)

def format_exception_groups(
    exceptions_by_rule: dict[
        str,
        list[dict[str, str]],
    ],
) -> str:
    total = sum(
        len(cases)
        for cases in exceptions_by_rule.values()
    )

    blocks = [
        (
            f"EXCEPTIONS — {total} "
            f"{pluralize('check', total)}"
        )
    ]

    for rule, cases in sorted(
        exceptions_by_rule.items(),
        key=lambda item: (
            -len(item[1]),
            item[0],
        ),
    ):
        blocks.append(
            format_code_rule_group(
                rule=rule,
                cases=cases,
                status_label="exceptions",
            )
        )

    return "\n\n".join(blocks)

def extract_subject(
    message: str,
) -> str:
    """
    Extract the symbol or array name from known validator
    message formats.

    Examples:
        -> Soc_test failed validation
        -> Invalid function name: Soc_test
        -> someArray uses symbolic array size [...]
        -> look2_iflf_binlca skipped (...)
    """
    patterns = [
        (
            r"Invalid function name:\s*"
            r"([A-Za-z_][A-Za-z0-9_]*)"
        ),
        (
            r"->\s*"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s+failed validation"
        ),
        (
            r"->\s*"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s+skipped"
        ),
        (
            r"->\s*"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s+uses\b"
        ),
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            message,
        )

        if match:
            return match.group(1)

    return "-"

def extract_reason(
    message: str,
) -> str:
    """
    Remove file paths and validator prefixes while keeping
    the factual failure explanation.
    """
    normalized = " ".join(
        message.split()
    )

    lower_message = normalized.lower()

    if "failed validation:" in lower_message:
        marker_index = lower_message.index(
            "failed validation:"
        )

        reason = normalized[
            marker_index
            + len("failed validation:"):
        ].strip()

        return clean_reason(reason)

    invalid_function_marker = (
        "invalid function name:"
    )

    if invalid_function_marker in lower_message:
        return "Function name failed validation"

    if "skipped" in lower_message:
        opening_parenthesis = normalized.rfind("(")
        closing_parenthesis = normalized.rfind(")")

        if (
            opening_parenthesis >= 0
            and closing_parenthesis
            > opening_parenthesis
        ):
            reason = normalized[
                opening_parenthesis + 1:
                closing_parenthesis
            ]

            return clean_reason(reason)

        return "Check was skipped"

    if "uses symbolic array size" in lower_message:
        marker = "uses symbolic array size"
        marker_index = lower_message.index(marker)

        return clean_reason(
            normalized[marker_index:]
        )

    if "->" in normalized:
        return clean_reason(
            normalized.split("->", 1)[1]
        )

    return clean_reason(normalized)

def clean_reason(
    reason: str,
) -> str:
    reason = reason.strip()

    replacements = {
        "description missing":
            "description is missing",
        "exceeds max length (31)":
            "name exceeds maximum length 31",
        "description length must be >= 14":
            "description length must be at least 14",
        "description length must be <= 22":
            "description length must be at most 22",
        "description must start with lowercase letter":
            "description must start with a lowercase letter",
        "excluded pattern":
            "matched an excluded pattern",
    }

    parts = [
        part.strip()
        for part in reason.split(";")
        if part.strip()
    ]

    cleaned_parts = [
        replacements.get(
            part.lower(),
            part,
        )
        for part in parts
    ]

    return "; ".join(cleaned_parts)

def clean_report_path(
    value: Any,
    *,
    run_id: str,
) -> str:
    if not value:
        return "-"

    path = str(value).replace(
        "\\",
        "/",
    )

    if run_id:
        marker = f"/runs/{run_id}/"

        if marker in path:
            path = path.split(
                marker,
                1,
            )[1]

    return path.removeprefix("./")

def clean_structure_message(
    value: Any,
) -> str:
    message = " ".join(
        str(value or "").split()
    )

    if ":" in message:
        reason, _ = message.split(
            ":",
            1,
        )

        return reason.strip()

    return message or "Structure validation failed"


def sanitize_table_cell(
    value: Any,
) -> str:
    if value is None:
        return "-"

    text = " ".join(
        str(value).split()
    )

    # Prevent values from breaking pipe tables.
    text = text.replace("|", "/")

    return text or "-"


def humanize_rule(
    rule: str,
) -> str:
    return rule.replace(
        "_",
        " ",
    ).strip().title()


def normalize_status(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip().upper()


def pluralize(
    word: str,
    count: int,
) -> str:
    return word if count == 1 else f"{word}s"


def find_section(
    sections: list[dict[str, Any]],
    name: str,
) -> dict[str, Any]:
    for section in sections:
        if section.get("name") == name:
            return section

    return {
        "name": name,
        "status": "passed",
        "summary": {
            "failed": 0,
            "exception": 0,
            "passed": 0,
            "total": 0,
        },
        "issues": [],
    }


def validate_review_report(
    review_report: Any,
) -> None:
    if not isinstance(review_report, dict):
        raise ValueError(
            "Review report must be an object"
        )

    required_keys = {
        "metadata",
        "summary",
        "sections",
    }

    missing_keys = (
        required_keys
        - review_report.keys()
    )

    if missing_keys:
        raise ValueError(
            "Invalid review report. Missing: "
            + ", ".join(
                sorted(missing_keys)
            )
        )

    if not isinstance(
        review_report["sections"],
        list,
    ):
        raise ValueError(
            "Review report sections must be a list"
        )




