from pathlib import Path


def test_graph_workspace_shell_exposes_scopes_layers_and_accessible_fallback():
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/graph.js").read_text(encoding="utf-8")

    for identity in (
        'id="graphsPage"',
        'id="graphRun"',
        'id="graphViewMode"',
        'id="graphTraceRootMode"',
        'id="graphTraceRoot"',
        'id="graphTraceStart"',
        'id="graphScope"',
        'id="graphFile"',
        'id="graphModules"',
        'id="graphLayers"',
        'id="graphNodeDetails"',
        'id="graphCanvas"',
        'id="graphEdgeTooltip"',
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
    assert "focusGraphNode(node)" in script
    assert "renderGraphEdgeInspector(edge)" in script
    assert '["contains", "parameter_of", "field_of", "member_of"]' in script
    assert "function graphEdgeRoutes" in script
    assert "function rectangleBoundary" in script
    assert "renderGraphEdgeTooltip(edge" in script
    assert "incoming_interactions" in script
    assert (
        "Return-value lineage and argument-to-parameter binding remain unavailable"
        in script
    )
    assert "/graphs/nodes" in script
    assert "/graphs/neighborhood" in script
    assert "function toggleTraceNode" in script
    assert "function collapseTraceNode" in script
    assert "trace_relation_path" in script
    assert "trace_canonical_path" in script
    assert "function renderTraceRootOptions" in script
    assert "function traceBranchAllows" in script
    assert "function edgeObstacleCount" in script
    assert "parameter input" in script
