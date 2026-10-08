from __future__ import annotations

from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from orchestrator.run_store import get_run_path, load_report


def generate_evidence_pack(run_id: str) -> Path:
    report = load_report(run_id)
    output_path = get_run_path(run_id) / "evidence-pack.html"
    output_path.write_text(render_evidence_pack(report), encoding="utf-8")
    return output_path


def render_evidence_pack(
    report: dict[str, Any],
    *,
    generated_at: str | None = None,
) -> str:
    generated_at = generated_at or datetime.now(UTC).isoformat()
    metadata = report.get("metadata") or {}
    profile = metadata.get("profile") or {}
    summary = report.get("summary") or {}
    build = report.get("build_result") or {}
    build_step = build.get("build_step") or {}
    format_step = build.get("format_step") or {}
    intelligence = build.get("intelligence_summary") or {}

    metadata_rows = [
        ("Run ID", report.get("run_id")),
        ("Module", metadata.get("module_name")),
        ("Profile", profile.get("name")),
        ("Domain", profile.get("domain")),
        ("Language", profile.get("language")),
        ("Review policy", profile.get("review_policy") or metadata.get("policy_name")),
        ("Policy version", report.get("policy_version")),
        ("Report version", report.get("report_version")),
        ("Formatter", profile.get("formatter")),
        ("Build adapter", profile.get("build_adapter")),
        ("Artifact types", ", ".join(profile.get("artifact_types") or [])),
        ("Review generated", metadata.get("generated_at")),
        ("Evidence generated", generated_at),
    ]
    build_status = build_step.get("status") or build.get("status") or "not run"
    format_status = format_step.get("status") or "not run"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review evidence pack — {_text(report.get('run_id'))}</title>
<style>
:root{{--ink:#172033;--muted:#5e6b7f;--line:#dce3ec;--soft:#f5f7fa;--accent:#1d4ed8;--bad:#b91c1c;--warn:#92400e;--good:#047857}}
*{{box-sizing:border-box}}body{{margin:0;background:#eef2f7;color:var(--ink);font:14px/1.5 Arial,sans-serif}}
main{{max-width:1120px;margin:32px auto;padding:0 24px 48px}}header,section{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px;margin:16px 0}}
h1{{font-size:28px;margin:0 0 6px}}h2{{font-size:19px;margin:0 0 14px}}h3{{font-size:15px;margin:20px 0 8px}}p{{margin:6px 0}}.muted{{color:var(--muted)}}
.meta{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}}.meta div{{background:var(--soft);padding:10px;border-radius:8px}}
.meta b{{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}
.summary{{display:flex;gap:10px;flex-wrap:wrap}}.summary span,.badge{{padding:6px 9px;border-radius:999px;background:var(--soft);font-weight:700}}
.failed{{color:var(--bad)}}.skipped{{color:var(--warn)}}.passed{{color:var(--good)}}
table{{width:100%;border-collapse:collapse}}th,td{{border-bottom:1px solid var(--line);padding:9px;text-align:left;vertical-align:top}}th{{font-size:11px;text-transform:uppercase;color:var(--muted)}}
ul,ol{{margin:7px 0;padding-left:22px}}code{{font:12px Consolas,monospace;overflow-wrap:anywhere}}.card{{border:1px solid var(--line);border-radius:9px;padding:13px;margin:10px 0}}@media print{{body{{background:#fff}}main{{margin:0;max-width:none}}header,section{{break-inside:avoid;box-shadow:none}}}}
</style>
</head>
<body><main>
<header><p class="muted">Developer Workspace</p><h1>Review evidence pack</h1><p>Persisted review, remediation, build, and artifact evidence for one run.</p></header>
<section><h2>Run metadata</h2><div class="meta">{_metadata(metadata_rows)}</div></section>
<section><h2>Review findings</h2><div class="summary">
<span class="failed">{_text(summary.get('failed', 0))} failed</span><span class="skipped">{_text(summary.get('skipped', 0))} skipped</span><span class="passed">{_text(summary.get('passed', 0))} passed</span><span>{_text(summary.get('total', 0))} total</span>
</div>{_review_findings(report.get('stages') or [])}</section>
<section><h2>Requested remediation</h2>{_remediations(report.get('remediation') or [])}</section>
<section><h2>Build and format status</h2><p><b>Build:</b> {_text(build_status)} &nbsp; <b>Formatting:</b> {_text(format_status)}</p>
<p><b>Primary issue:</b> {_text(intelligence.get('primary_issue') or intelligence.get('summary') or 'No build intelligence available.')}</p>
{_named_list('Evidence', intelligence.get('evidence') or [])}{_named_list('Next actions', intelligence.get('next_actions') or intelligence.get('suggestions') or [], ordered=True)}</section>
<section><h2>Important diagnostics</h2>{_plain_list(build.get('important_diagnostics') or [], code=True, empty='No important diagnostics were recorded.')}</section>
<section><h2>Artifact manifest</h2>{_artifacts(build.get('artifact_manifest') or [])}</section>
</main></body></html>"""


def _text(value: Any) -> str:
    if value in (None, ""):
        return "—"
    return escape(str(value))


def _metadata(rows: list[tuple[str, Any]]) -> str:
    return "".join(
        f"<div><b>{_text(label)}</b>{_text(value)}</div>" for label, value in rows
    )


def _review_findings(stages: list[dict[str, Any]]) -> str:
    content: list[str] = []
    for stage in stages:
        checks = stage.get("checks") or []
        if not any(check.get("cases") for check in checks):
            continue
        content.append(f"<h3>{_text(stage.get('title'))}</h3>")
        for check in checks:
            cases = check.get("cases") or []
            if not cases:
                continue
            rows = "".join(
                "<tr>"
                f"<td>{_text(case.get('status'))}</td>"
                f"<td>{_text(case.get('name'))}<br><code>{_text(case.get('location'))}</code></td>"
                f"<td>{_plain_list(case.get('reasons') or [], empty='No atomic reason recorded.')}</td>"
                "</tr>"
                for case in cases
            )
            content.append(
                f"<div class='card'><b>{_text(check.get('title'))}</b>"
                f"<table><thead><tr><th>Status</th><th>Finding</th><th>Atomic reasons</th></tr></thead><tbody>{rows}</tbody></table></div>"
            )
    return "".join(content) or "<p class='muted'>No review findings were recorded.</p>"


def _remediations(remediations: list[dict[str, Any]]) -> str:
    if not remediations:
        return "<p class='muted'>No remediation has been requested for this run.</p>"
    content: list[str] = []
    for remediation in remediations:
        suggestions = remediation.get("suggestions") or []
        suggestion_html = "".join(
            f"<div class='card'><b>{_text(item.get('title'))}</b>"
            f"<p>{_text(item.get('description'))}</p>"
            f"{_named_list('Policy reasons', item.get('reasons') or [])}"
            f"{_named_list('Actions', item.get('actions') or [], ordered=True)}"
            f"<p><b>Verification:</b> {_text(item.get('verification'))}</p></div>"
            for item in suggestions
        )
        content.append(
            f"<h3>{_text(remediation.get('title'))}</h3>"
            f"<p>{_text(remediation.get('summary'))}</p>{suggestion_html}"
        )
    return "".join(content)


def _named_list(name: str, items: list[Any], *, ordered: bool = False) -> str:
    if not items:
        return ""
    return f"<h3>{_text(name)}</h3>{_plain_list(items, ordered=ordered)}"


def _plain_list(
    items: list[Any],
    *,
    ordered: bool = False,
    code: bool = False,
    empty: str = "",
) -> str:
    if not items:
        return f"<p class='muted'>{_text(empty)}</p>" if empty else ""
    tag = "ol" if ordered else "ul"
    values = "".join(
        f"<li>{'<code>' if code else ''}{_text(item)}{'</code>' if code else ''}</li>"
        for item in items
    )
    return f"<{tag}>{values}</{tag}>"


def _artifacts(artifacts: list[dict[str, Any]]) -> str:
    if not artifacts:
        return "<p class='muted'>No build artifacts were recorded.</p>"
    rows = "".join(
        "<tr>"
        f"<td><code>{_text(item.get('relative_path'))}</code></td>"
        f"<td>{_text(item.get('type'))}</td>"
        f"<td>{_text(item.get('size_bytes'))}</td>"
        f"<td>{_text(item.get('modified_at'))}</td>"
        "</tr>"
        for item in artifacts
    )
    return (
        "<table><thead><tr><th>Path</th><th>Type</th><th>Bytes</th>"
        f"<th>Modified</th></tr></thead><tbody>{rows}</tbody></table>"
    )
