from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_CONFIG_NAME = "review-build.json"


def load_formatter_configuration(repo_root: Path) -> dict[str, Any] | None:
    """Read an explicit repository-local formatter wrapper declaration.

    The optional file is deliberately narrow so a reviewed project controls its
    own formatter without accepting arbitrary commands from the browser:

    {"format": {"script": "tools/format.bat"}}
    """
    config_path = repo_root / _CONFIG_NAME
    if not config_path.is_file():
        return None

    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    format_config = config.get("format", {})
    script = format_config.get("script")
    if not isinstance(script, str) or not script.strip():
        return None
    return {"script": script.strip(), "config_path": _CONFIG_NAME}
