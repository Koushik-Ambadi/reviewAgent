import traceback
from pathlib import Path
from pprint import pprint

from repo_review.pipeline.context import PipelineContext
from repo_review.pipeline.pipeline import run_pipeline

from repo_review.review import (
    run_review_from_zip,
)
repo_path=  r"C:\Users\koushik\Desktop\soc.zip"
repo_path = Path(repo_path).resolve()
context = run_review_from_zip(
    repo_path
)

print()
print("repo_root:", context.repo_root)
print("module_name:", context.module_name)
print("report_path:", context.report_path)
print()
print(context.report)