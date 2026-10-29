from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from code_intelligence.flow import generate_flow
from code_intelligence.extraction.llvm_api import LLVM
from code_intelligence.graph import KnowledgeGraph
from code_intelligence.views import control_flow_graph, data_flow_graph


ROOT = Path(__file__).resolve().parents[1]
CLANG = shutil.which("clang")
LIBRARY = Path(os.environ.get("LLVM_C_LIBRARY", "C:/Program Files/LLVM/bin/LLVM-C.dll"))


@pytest.fixture(scope="module")
def evidence(tmp_path_factory):
    if not CLANG or not LIBRARY.is_file():
        pytest.skip("Matching clang and LLVM C library required for real compiler test")
    output = tmp_path_factory.mktemp("flow") / "evidence"
    manifest = generate_flow(source=ROOT / "tests/fixtures/code_intelligence/flow.c",
        repo_root=ROOT, output=output, clang=Path(CLANG), llvm_library=LIBRARY, args=[])
    return output, manifest, json.loads((output / "code-intelligence.json").read_text())


def _function(graph, name):
    fn = next(n for n in graph["nodes"] if n["kind"] == "function" and n["name"] == name)
    return {n["id"]: n for n in graph["nodes"] if n["attributes"].get("function") == fn["id"]}


def test_real_branch_merge_memory_and_ssa(evidence):
    _, manifest, graph = evidence
    assert manifest["status"] == "completed"
    assert graph["schema_version"] == "1.2"
    nodes = _function(graph, "branch_merge")
    cfg = [e for e in graph["edges"] if e["kind"] == "control_flow" and e["source"] in nodes]
    assert len(cfg) == 4
    assert {e["attributes"]["label"] for e in cfg} == {"true", "false", "successor"}
    load = next(n for n in nodes.values() if n["kind"] == "instruction"
                and "load i32, ptr %value" in n["attributes"]["ir"])
    reaching = [e for e in graph["edges"] if e["kind"] == "memory_flow" and e["target"] == load["id"]]
    assert {nodes[e["source"]]["location"]["line"] for e in reaching} == {7, 9}
    ret = next(n for n in nodes.values() if n["attributes"].get("opcode") == 1)
    assert any(e["kind"] == "def_use" and e["source"] == load["id"]
               and e["target"] == ret["id"] for e in graph["edges"])


def test_loop_switch_short_circuit_and_pointer_boundary(evidence):
    _, _, graph = evidence
    nodes = _function(graph, "loop_switch")
    cfg = [e for e in graph["edges"] if e["kind"] == "control_flow" and e["source"] in nodes]
    assert any(nodes[e["source"]]["attributes"]["order"] > nodes[e["target"]]["attributes"]["order"] for e in cfg)
    assert {"default", "i32 0", "i32 1"} <= {e["attributes"]["label"] for e in cfg}
    sum_loads = {n["id"] for n in nodes.values() if "load i32, ptr %sum" in n["attributes"].get("ir", "")}
    assert any(e["kind"] == "memory_flow" and e["target"] in sum_loads
               and nodes[e["source"]]["location"]["line"] == 19 for e in graph["edges"])
    short = _function(graph, "short_circuit")
    assert sum(e["kind"] == "control_flow" and e["source"] in short
               and e["attributes"].get("label") == "true" for e in graph["edges"]) == 2
    pointer = _function(graph, "pointer_boundary")
    load = next(n for n in pointer.values() if "load i32, ptr %value" in n["attributes"].get("ir", ""))
    assert load["attributes"]["memory_boundary"] == "unresolved_memory_or_call_effect"
    assert not any(e["kind"] == "memory_flow" and e["target"] == load["id"] for e in graph["edges"])


def test_projections_are_exact_subsets_and_source_locations_exist(evidence):
    output, _, graph = evidence
    node_ids = {n["id"] for n in graph["nodes"]}
    edges = {e["id"]: e for e in graph["edges"]}
    for kind in ("control_flow", "data_flow"):
        projection = json.loads((output / (kind + ".json")).read_text())
        assert all(n["id"] in node_ids for n in projection["nodes"])
        assert all(e == edges[e["id"]] for e in projection["edges"])
        ids = {n["id"] for n in projection["nodes"]}
        assert all(e["source"] in ids and e["target"] in ids for e in projection["edges"])
    for node in graph["nodes"]:
        loc = node["location"]
        if node["kind"] == "instruction" and loc:
            assert 1 <= loc["line"] <= len((ROOT / loc["path"]).read_text().splitlines())


def test_preserve_existing_output_and_old_graph(evidence):
    output, _, _ = evidence
    before = (output / "code-intelligence.json").read_bytes()
    with pytest.raises(ValueError, match="new directory"):
        generate_flow(source=ROOT / "tests/fixtures/code_intelligence/flow.c", repo_root=ROOT,
            output=output, clang=Path(CLANG), llvm_library=LIBRARY, args=[])
    assert before == (output / "code-intelligence.json").read_bytes()
    graph = KnowledgeGraph()
    assert graph.to_dict()["schema_version"] == "1.1"
    assert not control_flow_graph(graph).metadata["available"]
    assert not data_flow_graph(graph).metadata["available"]


def test_malformed_ir_fails_closed(evidence):
    with pytest.raises(ValueError):
        with LLVM(LIBRARY).parse(b"not valid llvm IR"):
            pass


def test_phi_preserves_predecessors(evidence):
    _, _, graph = evidence
    nodes = _function(graph, "select_value")
    phi = next(n for n in nodes.values() if n["attributes"].get("opcode") == 44)
    inputs = [e for e in graph["edges"] if e["kind"] == "def_use" and e["target"] == phi["id"]]
    assert len(inputs) == 2
    assert len({e["attributes"]["incoming_block"] for e in inputs}) == 2
    assert all(nodes[e["attributes"]["incoming_block"]]["kind"] == "basic_block" for e in inputs)


def test_repeat_is_deterministic_and_invalid_source_retains_failure(evidence, tmp_path):
    _, _, graph = evidence
    output = tmp_path / "repeat"
    generate_flow(source=ROOT / "tests/fixtures/code_intelligence/flow.c", repo_root=ROOT,
        output=output, clang=Path(CLANG), llvm_library=LIBRARY, args=[])
    repeated = json.loads((output / "code-intelligence.json").read_text())
    assert repeated["nodes"] == graph["nodes"]
    assert repeated["edges"] == graph["edges"]
    source = tmp_path / "invalid.c"
    source.write_text("int broken( {", encoding="utf-8")
    output = tmp_path / "failed"
    with pytest.raises(ValueError, match="IR compilation failed"):
        generate_flow(source=source, repo_root=tmp_path, output=output,
            clang=Path(CLANG), llvm_library=LIBRARY, args=[])
    assert json.loads((output / "manifest.json").read_text())["status"] == "failed"
    assert not (output / "code-intelligence.json").exists()


def test_retained_evidence_auditor_rejects_projection_drift(evidence, tmp_path):
    from scripts.verify_flow_evidence import verify_flow_evidence

    output, _, _ = evidence
    result = verify_flow_evidence(output, ROOT, LIBRARY)
    assert result["consistent"]
    assert result["verified_successors"] > 0
    assert result["verified_instruction_operands"] > 0
    copied = tmp_path / "tampered"
    shutil.copytree(output, copied)
    path = copied / "control_flow.json"
    projection = json.loads(path.read_text())
    projection["edges"].pop()
    path.write_text(json.dumps(projection), encoding="utf-8")
    with pytest.raises(ValueError, match="Edge projection drift"):
        verify_flow_evidence(copied, ROOT, LIBRARY)
