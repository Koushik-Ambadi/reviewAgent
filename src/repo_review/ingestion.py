# src/repo_review/ingestion.py

from pathlib import Path
from typing import Any

try:
    from .config_loader import load_policy
except ImportError:  # pragma: no cover
    from config_loader import load_policy


def load_yaml_config(path: Path | str) -> dict[str, Any]:
    return load_policy(Path(path))


def ingest_local_source(source_path: Path | str, config: dict[str, Any]) -> dict[str, Any]:
    source_root = Path(source_path).resolve()
    runtime = config.get("runtime", {})
    ast_config = config.get("ast", {})

    policy_path = Path(runtime.get("policy_path", "policies/default.yaml"))
    if not policy_path.is_absolute():
        policy_path = (Path.cwd() / policy_path).resolve()

    return {
        "source_kind": "local_directory",
        "source_path": source_root,
        "policy_path": policy_path,
        "review_results_path": source_root / runtime.get("review_results_filename", "review_results.json"),
        "report_output_path": Path.cwd() / runtime.get("output_report_filename", "review_report.json"),
        "compile_db_dir": source_root / ast_config.get("compile_db_dir", "build"),
        "target_folders": [
            source_root / folder
            for folder in ast_config.get("target_folders", ["src"])
        ],
    }
