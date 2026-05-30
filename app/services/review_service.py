from pathlib import Path
from uuid import uuid4

from repo_review.review import (
    run_review_from_zip,
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

    context = (
        run_review_from_zip(
            zip_path
        )
    )

    try:
        zip_path.unlink()
    except OSError:
        pass

    return context.report