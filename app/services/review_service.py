from pathlib import Path
from uuid import uuid4

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
        "run_id": workspace_path.name,
        "module_name": module_name,
        "report": context.report,
    }