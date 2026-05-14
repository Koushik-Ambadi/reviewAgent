# src\repo_review\reporter.py

from rich.console import Console

console = Console()


def print_report(issues):
    if not issues:
        console.print("[green]No issues found[/green]")
        return

    for issue in issues:
        console.print(
            f"[red]{issue.severity}[/red] "
            f"{issue.rule} "
            f"{issue.path} "
            f"{issue.message}"
        )