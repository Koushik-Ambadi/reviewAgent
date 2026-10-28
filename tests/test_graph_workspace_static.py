from pathlib import Path


def test_graph_workspace_shell_exposes_scopes_layers_and_accessible_fallback():
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/graph.js").read_text(encoding="utf-8")

    for identity in (
        'id="graphsPage"',
        'id="graphRun"',
        'id="graphScope"',
        'id="graphFile"',
        'id="graphModules"',
        'id="graphLayers"',
        'id="graphCanvas"',
        'id="graphRelationships"',
    ):
        assert identity in html
    assert html.count('data-workspace-tab="graphs"') == 4
    assert '<script src="/graph.js" defer></script>' in html
    assert '<link href="/graph.css" rel="stylesheet">' in html
    assert 'option value="file"' in html
    assert 'option value="module"' in html
    assert 'option value="inter_module"' in html
    assert "control_flow" not in html
    assert "Control flow and definition-use data flow stay disabled" in html
    assert 'canvas.addEventListener("dblclick"' in script
    assert 'fetch("/api/graphs/catalog")' in script
