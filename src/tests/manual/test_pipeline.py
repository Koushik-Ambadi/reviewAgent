# src/tests/manual/test_pipeline.py

import traceback
from pathlib import Path
from pprint import pprint

from repo_review.pipeline.context import PipelineContext
from repo_review.pipeline.pipeline import run_pipeline


def main():

    repo_path = r"C:\Users\koushik\Desktop\review\soc"
    repo_path = Path(repo_path).resolve()

    try:

        # -----------------------------
        # CREATE CONTEXT (FIXED)
        # -----------------------------
        context = PipelineContext(
            source_path=str(repo_path),
            module_name=repo_path.name,          # "soc"
            repo_url="local-test-repo",         # dummy value
            pipeline_config_path=r"C:\Users\koushik\Desktop\review\config\review_pipeline.yaml"  # adjust if needed
        )

        print("\nINITIAL CONTEXT")
        pprint(context.__dict__)

        # -----------------------------
        # RUN PIPELINE
        # -----------------------------
        result = run_pipeline(context)

        print("\n==============================")
        print("PIPELINE EXECUTION SUCCESS")
        print("==============================")

        print("Module Name:", getattr(result, "module_name", None))
        print("Source Path:", getattr(result, "source_path", None))
        print("Repo URL:", getattr(result, "repo_url", None))
        print("Config Path:", getattr(result, "pipeline_config_path", None))

        print("\nValidation Issues:")
        for issue in getattr(result, "validation_issues", []):
            print(issue)

    except Exception as e:

        print("\n==============================")
        print("PIPELINE EXECUTION FAILED")
        print("==============================")

        print(f"Error: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()