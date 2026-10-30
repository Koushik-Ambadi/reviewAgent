from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from code_intelligence.run_flow import generate_run_flow


def test_missing_toolchain_is_recorded_without_failing_review(tmp_path, monkeypatch):
    monkeypatch.setattr("code_intelligence.run_flow._toolchain", lambda policy: (None, None))
    analysis = tmp_path / "analysis"
    summary = generate_run_flow(repo_root=tmp_path, analysis_dir=analysis,
                                sources=["src/example.c"])
    assert summary["status"] == "unavailable"
    assert json.loads((analysis / "flow/summary.json").read_text()) == summary


def test_run_flow_projections_live_under_analysis_run(tmp_path):
    clang = shutil.which("clang")
    library = Path(os.environ.get("LLVM_C_LIBRARY", "C:/Program Files/LLVM/bin/LLVM-C.dll"))
    if not clang or not library.is_file():
        pytest.skip("matching clang and LLVM C library required")
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    source = repo / "src/flow.c"
    source.write_bytes((Path(__file__).parent / "fixtures/code_intelligence/flow.c").read_bytes())
    analysis = tmp_path / "run/analysis"
    build = analysis / "cmake_build"
    build.mkdir(parents=True)
    (build / "compile_commands.json").write_text(json.dumps([{
        "directory": str(repo), "file": str(source),
        "arguments": [clang, "-c", str(source), "-o", str(build / "flow.o")],
    }]))
    summary = generate_run_flow(repo_root=repo, analysis_dir=analysis,
                                sources=["src/flow.c"], policy={"flow": {"llvm_library": str(library)}})
    assert summary["status"] == "completed"
    bundle = analysis / summary["sources"][0]["bundle"]
    assert json.loads((bundle / "manifest.json").read_text())["status"] == "completed"
    assert json.loads((bundle / "control_flow.json").read_text())["edges"]
    assert json.loads((bundle / "data_flow.json").read_text())["edges"]
