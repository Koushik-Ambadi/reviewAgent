# review_mcp/utils/config.py

from __future__ import annotations

import os

REVIEW_API_URL = os.getenv(
    "REVIEW_API_URL",
    "http://192.168.10.71:8001/api",
)