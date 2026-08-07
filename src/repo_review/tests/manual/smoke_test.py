from orchestrator.runner import prepare_review_run
from repo_review.review import run_review

workspace_path, repo_root, module_name = prepare_review_run(
    source_path=r"D:/BMS_related_testing_data/bmsAlgo/soe.zip",
    source_type="zip",   # or whatever your ingestion layer expects
)

context = run_review(
    repo_root=repo_root,
    workspace_path=workspace_path,
    module_name=module_name,
)