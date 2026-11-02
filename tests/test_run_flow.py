from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from code_intelligence.run_flow import generate_run_flow
from app.services.intelligence_service import Workspace
from app.services.graph_service import get_run_function_flow
from app.services.function_flow_presentation import describe_cfg
from repo_review.analysis.runner import run_analysis
from repo_review.contracts import StageStatus


def test_cfg_display_does_not_bind_other_file_debug_line(tmp_path):
    source = tmp_path / "flow.c"
    source.write_text("if (value > 0)\n    result = 1;\n")
    block = {"id": "block", "kind": "basic_block", "name": "entry",
             "attributes": {"entry": True, "exit": False}}
    graph = {"nodes": [
        {"id": "branch", "kind": "instruction", "location": {"path": "other.c", "line": 1},
         "attributes": {"block": "block", "order": 0, "ir": "br i1 %cmp, label %a, label %b"}},
        {"id": "store", "kind": "instruction", "location": {"path": "other.c", "line": 2},
         "attributes": {"block": "block", "order": 1, "ir": "store i32 1, ptr %result"}},
    ]}
    summary = describe_cfg([block], graph, source, "flow.c")[0]["flow_summary"]
    assert summary["condition"] is None
    assert summary["effects"][0]["source"] is None


def test_cfg_display_traces_condition_to_declared_initializer(tmp_path):
    source = tmp_path / "flow.c"
    source.write_text("static int threshold = 2;\nif (value > threshold)\n    result = 1;\n")
    block = {"id": "block", "kind": "basic_block", "name": "entry",
             "attributes": {"entry": True, "exit": False}}
    graph = {"nodes": [
        {"id": "threshold", "kind": "global_variable", "name": "threshold",
         "location": {"path": "flow.c", "line": 1}, "attributes": {}},
        {"id": "branch", "kind": "instruction", "location": {"path": "flow.c", "line": 2},
         "attributes": {"block": "block", "order": 0, "ir": "br i1 %cmp, label %a, label %b"}},
    ]}
    summary = describe_cfg([block], graph, source, "flow.c")[0]["flow_summary"]
    assert summary["condition"] == "value > threshold"
    assert summary["condition_inputs"] == [{"name": "threshold",
                                            "declaration": "static int threshold = 2", "line": 1}]


def test_missing_toolchain_is_recorded_without_failing_review(tmp_path, monkeypatch):
    monkeypatch.setattr("code_intelligence.run_flow._toolchain", lambda policy: (None, None))
    analysis = tmp_path / "analysis"
    summary = generate_run_flow(repo_root=tmp_path, analysis_dir=analysis,
                                sources=["src/example.c"])
    assert summary["status"] == "unavailable"
    assert json.loads((analysis / "flow/summary.json").read_text()) == summary


def test_unexpected_flow_error_keeps_analysis_stage_completed(tmp_path, monkeypatch):
    monkeypatch.setattr("repo_review.analysis.runner.build_source_index",
                        lambda **kwargs: {"status": "success"})
    monkeypatch.setattr("repo_review.analysis.runner.build_symbol_inventory",
                        lambda **kwargs: {"status": "success", "results": []})

    def fail_flow(**kwargs):
        raise RuntimeError("compiler unavailable")

    monkeypatch.setattr("code_intelligence.run_flow.generate_run_flow", fail_flow)
    stage = run_analysis(tmp_path, tmp_path / "run", {})
    summary = json.loads((tmp_path / "run/analysis/flow/summary.json").read_text())
    assert stage.status == StageStatus.COMPLETED
    assert summary["status"] == "failed" and summary["reason"] == "compiler unavailable"


def test_run_flow_projections_live_under_analysis_run(tmp_path, monkeypatch):
    clang = shutil.which("clang")
    library = Path(os.environ.get("LLVM_C_LIBRARY", "C:/Program Files/LLVM/bin/LLVM-C.dll"))
    if not clang or not library.is_file():
        pytest.skip("matching clang and LLVM C library required")
    run = tmp_path / "runs/run1"
    repo = run / "A"
    (repo / "src").mkdir(parents=True)
    source = repo / "src/flow.c"
    source.write_bytes((Path(__file__).parent / "fixtures/code_intelligence/flow.c").read_bytes())
    analysis = run / "analysis"
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
    (run / "report.json").write_text(json.dumps({"metadata": {
        "module_name": "A", "generated_at": "2026-10-30T00:00:00+00:00"}}))
    (analysis / "code-intelligence.json").write_text((bundle / "code-intelligence.json").read_text())
    workspace = Workspace(root=tmp_path / "runs")
    assert len(workspace.evidence) == 1 and not workspace.warnings
    assert workspace.query(mode="cfg")["edges"]
    function = next(n for n in workspace.catalog()["symbols"]
                    if n["kind"] == "function" and n["location"]["path"] == "src/flow.c")
    monkeypatch.setattr("orchestrator.run_store.WORKSPACE_ROOT", tmp_path / "runs")
    for mode in ("cfg", "dfd"):
        inline = get_run_function_flow("run1", function["canonical_id"], mode=mode, limit=24)
        assert inline["edges"] and inline["evidence"]
        identities = {n["id"] for n in inline["nodes"]}
        assert all(e["source"] in identities and e["target"] in identities
                   for e in inline["edges"])
        if mode == "cfg":
            conditions = [n["flow_summary"]["condition"] for n in inline["nodes"]
                          if n.get("flow_summary", {}).get("condition")]
            assert "input > 0" in conditions
            effects = [effect["source"] for n in inline["nodes"]
                       for effect in n.get("flow_summary", {}).get("effects", [])]
            assert any(effect and "value = input + 1" in effect for effect in effects)
