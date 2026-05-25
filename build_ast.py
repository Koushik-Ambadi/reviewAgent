# build_ast.py
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from repo_review.ast_builder import build_ast_review_results  # noqa: E402
from repo_review.ingestion import load_yaml_config  # noqa: E402


def main():
    config = load_yaml_config(ROOT / "config" / "review_pipeline.yaml")
    result = build_ast_review_results(ROOT / config["runtime"]["source_path"], config)
    print(result.get("status", "unknown"))
    print(result.get("output_path", ""))


if __name__ == "__main__":
    main()
