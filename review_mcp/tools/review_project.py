# review_mcp/tools/review_project.py

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from review_mcp.client.review_client import ReviewClient
from review_mcp.utils.config import REVIEW_API_URL


def review_project(
    repository_path: str,
) -> dict:

    repo = Path(repository_path).resolve()

    if not repo.exists():
        raise FileNotFoundError(repo)

    with tempfile.NamedTemporaryFile(
        suffix=".zip",
        delete=False,
    ) as tmp:

        zip_path = Path(tmp.name)

    try:

        with zipfile.ZipFile(
            zip_path,
            "w",
            zipfile.ZIP_DEFLATED,
        ) as archive:

            for file in repo.rglob("*"):

                if file.is_file():

                    archive.write(
                        file,
                        Path(repo.name) / file.relative_to(repo),
                    )

        client = ReviewClient(REVIEW_API_URL)

        return client.review_zip(zip_path)

    finally:

        if zip_path.exists():
            zip_path.unlink()