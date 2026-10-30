import hashlib
import json
from pathlib import Path

import pytest
from code_intelligence.exploration import Explorer, MODES, components
from app.services.intelligence_service import Workspace, inside


def node(key, kind="function", **kw):
    return {"id":key,"name":key,"kind":kind,"module":"A","attributes":{},"is_definition":True, **kw}


def edge(key, kind, source, target):
    return {"id":key,"kind":kind,"source":source,"target":target,"attributes":{}}


def fixture():
    return Explorer({"nodes":[node("root"),node("work"),node("leaf"),node("other"),node("value","global_variable")],
        "edges":[edge("a","calls","root","work"),edge("b","calls","work","leaf"),
                 edge("c","calls","leaf","work"),edge("d","writes","work","value"),
                 edge("e","reads","other","value")]})


def test_connected_selection_and_influence_have_distinct_semantics():
    explorer = fixture()
    r = explorer.query(selected=["root","other"],depth=4)
    assert r["paths"][0]["status"] == "association_path"
    assert {n["id"] for n in r["nodes"]} == {"root","work","value","other"}
    downstream = explorer.query(mode="downstream",selected=["value"])
    assert {n["id"] for n in downstream["nodes"]} == {"value","other"}
    assert downstream["edges"][0]["display_relation"] == "may affect a reader"
    signals = explorer.query(mode="signals", selected=["value"])
    assert next(e for e in signals["edges"] if e["kind"] == "reads")["display_relation"] == "is read by"
    upstream = explorer.query(mode="upstream",selected=["value"])
    assert {n["id"] for n in upstream["nodes"]} == {"value","work","leaf"}


def test_truncation_is_not_negative_proof_and_keeps_roots():
    r = fixture().query(selected=["root","other"],depth=1,limit=2)
    assert not r["coverage"]["complete_within_scope"]
    assert r["paths"][0]["status"] == "not_found_within_scope_and_budget"
    assert len(r["nodes"]) == 2
    with pytest.raises(ValueError): fixture().query(selected=["missing"])
    with pytest.raises(ValueError): fixture().query(selected=["root","other"],limit=1)
    with pytest.raises(ValueError): fixture().query(mode="reachability",selected=["value"])


def test_cycles_call_depth_and_long_chains_do_not_recurse():
    metrics = fixture().analytics()
    assert metrics["recursive_groups"] == [["leaf","work"]]
    assert next(r for r in metrics["functions"] if r["id"]=="root")["call_depth_scc_edges"] == 1
    ids = [str(i) for i in range(4000)]
    assert len(components(ids,{str(i):{str(i+1)} for i in range(3999)})) == 4000


def test_all_modes_deterministic_and_valid_endpoints():
    for mode in MODES:
        r = fixture().query(mode=mode)
        assert r == fixture().query(mode=mode)
        ids = {n["id"] for n in r["nodes"]}
        assert all(e["source"] in ids and e["target"] in ids for e in r["edges"])
    r = fixture().query(mode="cfg",selected=["root"])
    assert not r["nodes"] and "No compiler flow" in r["notes"][0]


def write_run(root, module, nodes, edges):
    run = root / (module+"_run"); (run/"analysis").mkdir(parents=True)
    (run/module).mkdir()
    (run/"report.json").write_text(json.dumps({"metadata":{"module_name":module,"generated_at":"2026-10-29T00:00:00+00:00"}}))
    (run/"analysis/code-intelligence.json").write_text(json.dumps({"nodes":nodes,"edges":edges}))
    return run/module


def test_modules_are_namespaced_and_exact_resolution_crosses_boundaries(tmp_path):
    public = "c:@F@work"
    write_run(tmp_path,"A",[node("root"),node("decl",usr=public,is_definition=False),node("local",usr="c:a.c@F@same")], [edge("call","calls","root","decl")])
    write_run(tmp_path,"B",[node("work",usr=public),node("local",usr="c:b.c@F@same")], [])
    w = Workspace(root=tmp_path)
    assert len(w.graph["nodes"]) == 5
    r = w.query(mode="calls",selected=["A_run::root"])
    assert {n["id"] for n in r["nodes"]} == {"A_run::root","B_run::work"}
    assert r["edges"][0]["declaration_target"] == "A_run::decl"
    assert w.query(mode="modules",rules=[{"from":"A","to":"B"}])["analytics"]["architecture"]["findings"]
    write_run(tmp_path,"C",[node("ambiguous",usr=public)],[])
    w = Workspace(root=tmp_path)
    assert not any(e["kind"] == "resolves_to" for e in w.graph["edges"])


def test_source_path_boundary(tmp_path):
    with pytest.raises(ValueError): inside(tmp_path,"../outside")
    repo=write_run(tmp_path,"A",[node("escape",location={"path":"../../secret","line":1})],[])
    assert Workspace(root=tmp_path).context("A_run::escape")["source"] is None


def test_stale_flow_never_attached(tmp_path):
    repo=write_run(tmp_path,"A",[node("f")],[])
    src=repo/"a.c";src.write_text("int f(void) { return 1; }")
    bundle=tmp_path/"flows"/"one"; bundle.mkdir(parents=True)
    manifest={"status":"completed","flow":{"functions":1},"source":"a.c", "source_sha256":"wrong",
              "input_hashes":{str(src.resolve()):"wrong"}}
    (bundle/"manifest.json").write_text(json.dumps(manifest))
    w=Workspace(root=tmp_path)
    assert not w.evidence and "source changed" in w.warnings[0]["reason"]


def test_flow_projection_retains_branches_and_store_load_identity():
    nodes=[node("f"),node("b0","basic_block",attributes={"function":"f","order":0}),
           node("b1","basic_block",attributes={"function":"f","order":1}),
           node("store","instruction",attributes={"function":"f","order":0}),
           node("load","instruction",attributes={"function":"f","order":1})]
    edges=[edge("branch","control_flow","b0","b1"),edge("memory","memory_flow","store","load")]
    edges[0]["attributes"]={"branch":"true"}
    e=Explorer({"nodes":nodes,"edges":edges})
    assert e.query(mode="cfg",selected=["f"])["edges"]==[edges[0]]
    assert e.query(mode="dfd",selected=["f"])["edges"]==[edges[1]]


def test_run_selection_preserves_latest_default_and_namespaces_old_snapshot(tmp_path):
    write_run(tmp_path, "A", [node("old")], [])
    old_run = tmp_path / "A_run"
    new_run = tmp_path / "A_new"
    (new_run / "analysis").mkdir(parents=True)
    (new_run / "A").mkdir()
    (new_run / "report.json").write_text(json.dumps({"metadata": {
        "module_name": "A", "generated_at": "2026-10-30T00:00:00+00:00"}}))
    (new_run / "analysis/code-intelligence.json").write_text(json.dumps({
        "nodes": [node("new")], "edges": []}))
    latest = Workspace(root=tmp_path)
    assert latest.records["A"]["run_id"] == "A_new"
    assert {n["id"] for n in latest.graph["nodes"]} == {"A_new::new"}
    previous = Workspace(runs={"A": old_run.name}, root=tmp_path)
    assert {n["id"] for n in previous.graph["nodes"]} == {"A_run::old"}
    assert {c["run_id"] for c in previous.catalog()["run_choices"]["A"]} == {"A_run", "A_new"}
    with pytest.raises(ValueError): Workspace(runs={"A": "../other"}, root=tmp_path)


def test_run_selection_api_catalog_query_and_context(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    write_run(tmp_path, "A", [node("old")], [])
    monkeypatch.setattr("app.api.intelligence.Workspace",
        lambda modules=None, runs=None: Workspace(modules, runs, root=tmp_path))
    client = TestClient(app)
    assert client.get("/api/intelligence/catalog").json()["run_choices"]["A"][0]["run_id"] == "A_run"
    request = {"modules": ["A"], "runs": {"A": "A_run"}, "selected": ["A_run::old"]}
    assert client.post("/api/intelligence/catalog", json=request).status_code == 200
    assert client.post("/api/intelligence/query", json=request).json()["selected"] == ["A_run::old"]
    assert client.post("/api/intelligence/context", json={"node_id":"A_run::old","runs":request["runs"]}).status_code == 200
    assert client.post("/api/intelligence/query", json={**request,"runs":{"A":"../invalid"}}).status_code == 400
