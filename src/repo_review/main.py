# src/repo_review/main.py
from __future__ import annotations

import argparse
import sys
from pathlib import Path


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from repo_review.pipeline import build_review_report
from repo_review.reporter import print_report, write_report


def parse_args():
    parser = argparse.ArgumentParser(description="Run the repository review pipeline.")
    parser.add_argument("--repo-url", required=True, help="Source repository URL.")
    parser.add_argument("--module-name", required=True, help="Module name used by naming checks.")
    parser.add_argument(
        "--source-path",
        default="soc",
        help="Local source path to scan.",
    )
    parser.add_argument(
        "--config",
        default="config/review_pipeline.yaml",
        help="Pipeline config file.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional report output path. Defaults to the config value.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    report = build_review_report(
        source_path=Path(args.source_path),
        module_name=args.module_name,
        repo_url=args.repo_url,
        pipeline_config_path=Path(args.config),
    )

    output_path = write_report(report, args.output or report["metadata"]["report_output_path"])
    print_report(report)
    print(f"\nReport written to: {output_path}")


if __name__ == "__main__":
    main()
