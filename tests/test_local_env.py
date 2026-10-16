import os
import tempfile
from pathlib import Path

from app.local_env import PLACEHOLDER_VALUE, load_local_env


def test_local_env_loads_allowed_values_without_overriding_environment():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / ".env.local"
        path.write_text(
            "OPENAI_API_KEY=local-test-key\n"
            "OPENAI_REMEDIATION_MODEL=local-model\n",
            encoding="utf-8",
        )
        original_key = os.environ.get("OPENAI_API_KEY")
        original_model = os.environ.get("OPENAI_REMEDIATION_MODEL")
        os.environ["OPENAI_API_KEY"] = "existing-key"
        os.environ.pop("OPENAI_REMEDIATION_MODEL", None)
        try:
            loaded = load_local_env(path)
            assert os.environ["OPENAI_API_KEY"] == "existing-key"
            assert os.environ["OPENAI_REMEDIATION_MODEL"] == "local-model"
            assert loaded == {"OPENAI_REMEDIATION_MODEL"}
        finally:
            _restore("OPENAI_API_KEY", original_key)
            _restore("OPENAI_REMEDIATION_MODEL", original_model)


def test_local_env_ignores_placeholder_and_rejects_unknown_keys():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / ".env.local"
        path.write_text(
            f"OPENAI_API_KEY={PLACEHOLDER_VALUE}\n",
            encoding="utf-8",
        )
        original_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            assert load_local_env(path) == set()
            assert "OPENAI_API_KEY" not in os.environ

            path.write_text("UNEXPECTED_SECRET=value\n", encoding="utf-8")
            try:
                load_local_env(path)
            except ValueError as error:
                assert "Unsupported .env.local key" in str(error)
            else:
                raise AssertionError("Expected an unsupported-key error")
        finally:
            _restore("OPENAI_API_KEY", original_key)


def _restore(key: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
