# review_mcp/client/review_client.py

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class ReviewClient:
    def __init__(
        self,
        base_url: str,
        timeout: int = 600,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def review_zip(
        self,
        zip_path: Path,
    ) -> dict[str, Any]:

        with zip_path.open("rb") as fp:

            files = {
                "file": (
                    zip_path.name,
                    fp,
                    "application/zip",
                )
            }

            response = requests.post(
                f"{self._base_url}/review",
                files=files,
                timeout=self._timeout,
            )

        response.raise_for_status()

        return response.json()