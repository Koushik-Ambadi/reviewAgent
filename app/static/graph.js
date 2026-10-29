const graphColors = {
    calls: "#2563eb",
    input: "#0891b2",
    output: "#dc2626",
    parameter_input: "#0e7490",
    reference: "#d97706",
    includes: "#7c3aed",
    reads: "#0891b2",
    writes: "#dc2626",
    references: "#d97706",
    contains: "#94a3b8",
    parameter_of: "#94a3b8",
    field_of: "#94a3b8",
    member_of: "#94a3b8"
};

const graphState = {
    catalog: [],
    runId: null,
    viewMode: "overview",
    scope: "module",
    file: null,
    modules: new Set(),
    layers: new Set(["calls", "includes", "reads", "writes"]),
    nodeDetails: new Set(),
    payload: null,
    overviewPayload: null,
    traceIndex: [],
    traceInstances: [],
    traceEdges: [],
    traceCounter: 0,
    positionedNodes: [],
    scale: 1,
    offsetX: 0,
    offsetY: 0,
    dragging: false,
    dragX: 0,
    dragY: 0,
    selectedNodeId: null,
    selectedEdgeId: null,
    lastSelectedNodeId: null,
    hoveredEdgeId: null
};

async function showGraphs() {
    showPage("graphsPage");
    updateWorkspaceChrome("graphs");
    if (typeof openIntelligence === "function") await openIntelligence();
    if (!graphState.catalog.length) await loadGraphCatalog();
    if (!graphState.payload) await loadGraphProjection();
    requestAnimationFrame(resizeGraphCanvas);
}

async function loadGraphCatalog() {
    const loading = document.getElementById("graphLoading");
    loading.hidden = false;
    loading.textContent = "Loading graph-bearing runs…";
    try {
        const response = await fetch("/api/graphs/catalog");
        if (!response.ok) throw new Error(await response.text());
        const payload = await response.json();
        graphState.catalog = payload.modules || [];
        const runIds = new Set(graphState.catalog.map(item => item.run_id));
        graphState.runId = runIds.has(window.currentRunId)
            ? window.currentRunId
            : (graphState.catalog[0]?.run_id || null);
        graphState.modules = new Set(
            graphState.catalog.map(item => item.module_name)
        );
        renderGraphRunOptions();
        renderGraphModuleOptions();
    } catch (error) {
        loading.textContent = `Graph catalog could not be loaded: ${String(error)}`;
    }
}

function renderGraphRunOptions() {
    const select = document.getElementById("graphRun");
    if (!graphState.catalog.length) {
        select.innerHTML = '<option value="">No graph artifacts</option>';
        select.disabled = true;
        return;
    }
    select.disabled = false;
    select.innerHTML = graphState.catalog.map(item =>
        `<option value="${escapeHtml(item.run_id)}" ${
            item.run_id === graphState.runId ? "selected" : ""
        }>${escapeHtml(item.module_name)} · ${item.nodes} nodes</option>`
    ).join("");
}

function renderGraphModuleOptions() {
    const container = document.getElementById("graphModules");
    container.innerHTML = graphState.catalog.map(item =>
        `<label class="graph-module-option"><input type="checkbox" value="${
            escapeHtml(item.module_name)
        }" ${graphState.modules.has(item.module_name) ? "checked" : ""}>
        <span>${escapeHtml(item.module_name)}<small>${item.nodes} nodes · ${
            item.edges
        } edges</small></span></label>`
    ).join("") || '<p class="empty-state">No module graphs are available.</p>';
}

async function loadGraphProjection() {
    const loading = document.getElementById("graphLoading");
    loading.hidden = false;
    loading.textContent = "Projecting selected graph layers…";
    graphState.scope = document.getElementById("graphScope").value;
    const params = new URLSearchParams();
    graphState.layers.forEach(layer => params.append("layers", layer));
    let endpoint;
    if (graphState.scope === "inter_module") {
        graphState.modules.forEach(module => params.append("modules", module));
        endpoint = `/api/graphs/inter-module?${params}`;
    } else {
        if (!graphState.runId) {
            loading.textContent = "No graph-bearing review run is available.";
            return;
        }
        params.set("scope", graphState.scope);
        if (graphState.scope === "file" && graphState.file) {
            params.set("file", graphState.file);
        }
        endpoint = `/api/runs/${encodeURIComponent(graphState.runId)}/graphs?${
            params
        }`;
    }
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(await response.text());
        graphState.payload = await response.json();
        graphState.overviewPayload = graphState.payload;
        graphState.file = graphState.payload.selected_file || graphState.file;
        graphState.selectedNodeId = null;
        graphState.selectedEdgeId = null;
        graphState.lastSelectedNodeId = null;
        renderGraphControls();
        renderGraphPayload();
        resetGraphView();
        loading.hidden = true;
    } catch (error) {
        graphState.payload = null;
        loading.textContent = `Graph projection could not be loaded: ${String(error)}`;
    }
}

function renderGraphControls() {
    const payload = graphState.payload || {};
    const fileField = document.getElementById("graphFileField");
    const moduleField = document.getElementById("graphModuleField");
    const traceField = document.getElementById("graphTraceField");
    const traceMode = graphState.viewMode === "trace";
    document.getElementById("graphViewMode").value = graphState.viewMode;
    document.getElementById("graphScope").disabled = traceMode;
    traceField.hidden = !traceMode;
    document.getElementById("graphRun").disabled =
        (!traceMode && graphState.scope === "inter_module") || !graphState.catalog.length;
    fileField.hidden = traceMode || graphState.scope !== "file";
    moduleField.hidden = traceMode || graphState.scope !== "inter_module";
    if (graphState.scope === "file") {
        const select = document.getElementById("graphFile");
        select.innerHTML = (payload.available_files || []).map(path =>
            `<option value="${escapeHtml(path)}" ${
                path === graphState.file ? "selected" : ""
            }>${escapeHtml(path)}</option>`
        ).join("");
    }
    document.getElementById("graphLayers").innerHTML = (payload.layers || []).map(
        layer => `<label class="graph-layer ${layer.available ? "" : "disabled"}">
            <input type="checkbox" value="${escapeHtml(layer.id)}" ${
                graphState.layers.has(layer.id) ? "checked" : ""
            } ${layer.available ? "" : "disabled"}>
            <span><strong>${escapeHtml(layer.label)}</strong><small>${
                escapeHtml(layer.description)
            }</small></span></label>`
    ).join("");
    document.querySelectorAll("#graphNodeDetails input").forEach(input => {
        input.checked = graphState.nodeDetails.has(input.value);
        input.disabled = traceMode || graphState.scope !== "file";
    });
}

function renderGraphPayload() {
    const payload = graphState.payload;
    if (!payload) return;
    const summary = payload.summary || {};
    document.getElementById("graphSummary").innerHTML = [
        [summary.nodes ?? summary.modules ?? 0, graphState.scope === "inter_module" ? "modules" : "nodes"],
        [summary.relationships || 0, "relationships"],
        [summary.signal_names || 0, "named signals"],
        [summary.unresolved || 0, "unresolved"]
    ].map(([value, label]) => `<span>${value} ${label}</span>`).join("");
    const visibleKinds = [...new Set((payload.edges || []).map(edge => edge.kind))];
    document.getElementById("graphLegend").innerHTML = visibleKinds.map(kind =>
        `<span data-kind="${escapeHtml(kind)}" style="--legend-color:${graphColors[kind] || "#64748b"}">${
            escapeHtml(kind.replaceAll("_", " "))
        }</span>`
    ).join("");
    const limitations = payload.limitations || [];
    document.getElementById("graphLimitations").innerHTML = limitations.length
        ? `<ul>${limitations.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
        : "";
    renderGraphRelationshipList();
    renderGraphInspector(null);
    document.getElementById("graphScopeHelp").textContent = graphState.viewMode === "trace"
        ? "Double-click to expand/collapse. Repeated symbols may appear per branch for readability."
        : graphState.scope === "file"
        ? "Functions are primary; owned declarations stay in the inspector."
        : graphState.scope === "module"
            ? "Each arrow aggregates concrete cross-file interactions; select it for evidence."
            : "Each arrow is a recorded cross-module dependency, not computed runtime behavior.";
}

function renderGraphRelationshipList() {
    const payload = graphState.payload || { nodes: [], edges: [] };
    const names = new Map((payload.nodes || []).map(node => [node.id, node.label]));
    const edges = payload.edges || [];
    const visible = edges.slice(0, 250).map(edge => {
        const targetName = names.get(edge.target) || edge.target;
        const distinctSignals = (edge.signals || []).filter(signal => signal !== targetName);
        const signals = distinctSignals.length
            ? ` · signals: ${distinctSignals.slice(0, 8).join(", ")}`
            : "";
        const locations = (edge.occurrences || []).slice(0, 6).map(item =>
            `${item.path || "unknown"}${item.line ? `:${item.line}` : ""}`
        );
        const locationText = locations.length ? ` · at ${locations.join(", ")}` : "";
        return `<div><strong>${escapeHtml(names.get(edge.source) || edge.source)}</strong>
            → ${escapeHtml(edge.kind)} →
            <strong>${escapeHtml(targetName)}</strong>
            · ${edge.count || 1} occurrence${(edge.count || 1) === 1 ? "" : "s"}${
                escapeHtml(signals)
            }${escapeHtml(locationText)}</div>`;
    }).join("");
    const remainder = edges.length > 250
        ? `<p class="empty-state">${edges.length - 250} more relationships remain in the projection.</p>`
        : "";
    document.getElementById("graphRelationships").innerHTML =
        `<div class="graph-relationship-list">${visible}</div>${remainder}`;
}

function resizeGraphCanvas() {
    const canvas = document.getElementById("graphCanvas");
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.round(rect.width * ratio));
    canvas.height = Math.max(1, Math.round(rect.height * ratio));
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    positionGraphNodes(rect.width, rect.height);
    drawGraph();
}

function positionGraphNodes(width, height) {
    const nodes = visibleGraphNodes();
    if (!nodes.length) {
        graphState.positionedNodes = [];
        return;
    }
    if (graphState.viewMode === "trace") {
        positionTraceNodes(nodes);
        return;
    }
    const edges = visibleGraphEdges(new Set(nodes.map(node => node.id)));
    const incoming = new Map(nodes.map(node => [node.id, 0]));
    const outgoing = new Map(nodes.map(node => [node.id, []]));
    edges.filter(edge => edge.kind === "calls" || edge.kind === "includes").forEach(edge => {
        incoming.set(edge.target, (incoming.get(edge.target) || 0) + 1);
        outgoing.get(edge.source)?.push(edge.target);
    });
    const ranks = new Map(nodes.map(node => [node.id, 0]));
    const queue = nodes.filter(node => !incoming.get(node.id)).map(node => node.id);
    const remaining = new Map(incoming);
    while (queue.length) {
        const source = queue.shift();
        (outgoing.get(source) || []).forEach(target => {
            ranks.set(target, Math.max(ranks.get(target) || 0, (ranks.get(source) || 0) + 1));
            remaining.set(target, remaining.get(target) - 1);
            if (!remaining.get(target)) queue.push(target);
        });
    }
    const groups = new Map();
    nodes.forEach(node => {
        const rank = ranks.get(node.id) || 0;
        if (!groups.has(rank)) groups.set(rank, []);
        groups.get(rank).push(node);
    });
    const orderedRanks = [...groups.keys()].sort((a, b) => a - b);
    groups.forEach(group => group.sort((a, b) => a.label.localeCompare(b.label)));
    const adjacency = new Map(nodes.map(node => [node.id, []]));
    edges.forEach(edge => {
        adjacency.get(edge.source)?.push(edge.target);
        adjacency.get(edge.target)?.push(edge.source);
    });
    for (let sweep = 0; sweep < 3; sweep += 1) {
        const order = new Map();
        orderedRanks.forEach(rank => groups.get(rank).forEach(
            (node, index) => order.set(node.id, index)
        ));
        orderedRanks.slice(1).forEach(rank => groups.get(rank).sort(
            (a, b) => graphBarycenter(a, adjacency, order) - graphBarycenter(b, adjacency, order)
        ));
        orderedRanks.slice(0, -1).reverse().forEach(rank => groups.get(rank).sort(
            (a, b) => graphBarycenter(a, adjacency, order) - graphBarycenter(b, adjacency, order)
        ));
    }
    const columnGap = Math.max(190, (width - 100) / Math.max(1, orderedRanks.length));
    graphState.positionedNodes = orderedRanks.flatMap((rank, columnIndex) => {
        const group = groups.get(rank);
        const rowGap = Math.max(72, Math.min(112, (height - 90) / Math.max(1, group.length)));
        return group.map((node, rowIndex) => ({
            ...node,
            x: 70 + columnIndex * columnGap,
            y: 52 + rowIndex * rowGap,
            radius: node.kind === "module" ? 24 : 18,
            width: node.kind === "function" ? 148 : 132,
            height: node.kind === "function" ? 44 : 40
        }));
    });
}

function positionTraceNodes(nodes) {
    const children = new Map(nodes.map(node => [node.id, []]));
    nodes.forEach(node => {
        if (node.parent_instance_id && children.has(node.parent_instance_id)) {
            children.get(node.parent_instance_id).push(node);
        }
    });
    children.forEach(group => group.sort((a, b) =>
        (a.trace_column || 0) - (b.trace_column || 0) ||
        `${a.trace_role || ""}:${a.kind}:${a.label}`.localeCompare(
            `${b.trace_role || ""}:${b.kind}:${b.label}`
        )
    ));
    const roots = nodes.filter(node => !node.parent_instance_id);
    let leafY = 70;
    const positions = new Map();
    const visit = node => {
        const descendants = children.get(node.id) || [];
        if (!descendants.length) {
            positions.set(node.id, leafY);
            leafY += 82;
            return;
        }
        descendants.forEach(visit);
        const childYs = descendants.map(child => positions.get(child.id));
        positions.set(node.id, (Math.min(...childYs) + Math.max(...childYs)) / 2);
    };
    roots.forEach(visit);
    const minimumColumn = Math.min(...nodes.map(node => node.trace_column || 0));
    const originX = 100 + Math.abs(minimumColumn) * 220;
    graphState.positionedNodes = nodes.map(node => {
        const compact = node.kind === "parameter";
        return {
            ...node,
            x: originX + (node.trace_column || 0) * 220,
            y: positions.get(node.id),
            radius: compact ? 14 : 18,
            width: compact ? 112 : (node.kind === "function" ? 160 : 138),
            height: compact ? 30 : (node.kind === "function" ? 48 : 40)
        };
    });
}

function graphBarycenter(node, adjacency, order) {
    const positions = (adjacency.get(node.id) || [])
        .map(identity => order.get(identity)).filter(value => value !== undefined);
    if (!positions.length) return order.get(node.id) || 0;
    return positions.reduce((total, value) => total + value, 0) / positions.length;
}

function visibleGraphNodes() {
    const nodes = graphState.payload?.nodes || [];
    if (graphState.scope !== "file") return nodes;
    const primary = new Set(["function"]);
    return nodes.filter(node => primary.has(node.kind) || graphState.nodeDetails.has(node.kind));
}

function visibleGraphEdges(nodeIds = new Set(visibleGraphNodes().map(node => node.id))) {
    return (graphState.payload?.edges || []).filter(edge =>
        (graphState.viewMode === "trace" ||
            !["contains", "parameter_of", "field_of", "member_of"].includes(edge.kind)) &&
        nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );
}

function drawGraph() {
    const canvas = document.getElementById("graphCanvas");
    const context = canvas?.getContext("2d");
    if (!context) return;
    const ratio = window.devicePixelRatio || 1;
    const width = canvas.width / ratio;
    const height = canvas.height / ratio;
    context.clearRect(0, 0, width, height);
    context.save();
    context.translate(graphState.offsetX, graphState.offsetY);
    context.scale(graphState.scale, graphState.scale);
    const positions = new Map(
        graphState.positionedNodes.map(node => [node.id, node])
    );
    graphEdgeRoutes(positions).forEach(route => drawGraphEdge(context, route));
    graphState.positionedNodes.forEach(node => drawGraphNode(context, node));
    context.restore();
}

function graphEdgeRoutes(positions = new Map(
    graphState.positionedNodes.map(node => [node.id, node])
)) {
    const edges = visibleGraphEdges(new Set(positions.keys()));
    const groups = new Map();
    edges.forEach(edge => {
        const key = [edge.source, edge.target].sort().join("::");
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(edge);
    });
    return [...groups.values()].flatMap(group =>
        group.sort((a, b) => `${a.kind}:${a.id}`.localeCompare(`${b.kind}:${b.id}`))
            .map((edge, index) => {
                const source = positions.get(edge.source);
                const target = positions.get(edge.target);
                if (!source || !target) return null;
                const lane = index - (group.length - 1) / 2;
                const canonical = [source, target].sort((a, b) => a.id.localeCompare(b.id));
                const canonicalDx = canonical[1].x - canonical[0].x;
                const canonicalDy = canonical[1].y - canonical[0].y;
                const canonicalDistance = Math.max(1, Math.hypot(canonicalDx, canonicalDy));
                const offsetX = -canonicalDy / canonicalDistance * lane * 26;
                const offsetY = canonicalDx / canonicalDistance * lane * 26;
                return { edge, source, target,
                    ...edgeGeometry(
                        source, target, lane, offsetX, offsetY,
                        [...positions.values()].filter(node =>
                            node.id !== source.id && node.id !== target.id
                        ), edge.id
                    ) };
            }).filter(Boolean)
    );
}

function edgeGeometry(source, target, lane, offsetX, offsetY, obstacles = [], edgeId = "") {
    if (source.id === target.id) {
        const spread = 58 + Math.abs(lane) * 18;
        const controlX = source.x + (lane >= 0 ? spread : -spread);
        const controlY = source.y - 72 - Math.abs(lane) * 12;
        const start = rectangleBoundary(source, controlX, controlY);
        const end = rectangleBoundary(target, controlX, controlY + 28);
        return { startX: start.x, startY: start.y, endX: end.x, endY: end.y,
            controlX, controlY };
    }
    const midpointX = (source.x + target.x) / 2;
    const midpointY = (source.y + target.y) / 2;
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const distance = Math.max(1, Math.hypot(dx, dy));
    const baseBend = 24 + Math.min(54, distance * .08);
    const sign = stableGraphSign(edgeId);
    const candidates = lane
        ? [0]
        : [sign * baseBend, -sign * baseBend, sign * baseBend * 2];
    let best = null;
    candidates.forEach(bend => {
        const controlX = midpointX + offsetX - dy / distance * bend;
        const controlY = midpointY + offsetY + dx / distance * bend;
        const start = rectangleBoundary(source, controlX, controlY);
        const end = rectangleBoundary(target, controlX, controlY);
        const collisions = edgeObstacleCount(
            start, end, { x: controlX, y: controlY }, obstacles
        );
        if (!best || collisions < best.collisions) {
            best = { start, end, controlX, controlY, collisions };
        }
    });
    const { start, end, controlX, controlY } = best;
    return { startX: start.x, startY: start.y, endX: end.x, endY: end.y,
        controlX, controlY };
}

function stableGraphSign(value) {
    let hash = 0;
    for (const character of String(value || "edge")) {
        hash = ((hash << 5) - hash + character.charCodeAt(0)) | 0;
    }
    return hash % 2 ? 1 : -1;
}

function edgeObstacleCount(start, end, control, obstacles) {
    let collisions = 0;
    obstacles.forEach(node => {
        for (let step = 2; step < 19; step += 1) {
            const t = step / 20;
            const x = (1 - t) ** 2 * start.x +
                2 * (1 - t) * t * control.x + t ** 2 * end.x;
            const y = (1 - t) ** 2 * start.y +
                2 * (1 - t) * t * control.y + t ** 2 * end.y;
            if (Math.abs(node.x - x) < node.width / 2 + 8 &&
                Math.abs(node.y - y) < node.height / 2 + 8) {
                collisions += 1;
                break;
            }
        }
    });
    return collisions;
}

function rectangleBoundary(node, towardX, towardY) {
    const dx = towardX - node.x;
    const dy = towardY - node.y;
    if (!dx && !dy) return { x: node.x, y: node.y };
    const halfWidth = node.width / 2 + 3;
    const halfHeight = node.height / 2 + 3;
    const scale = Math.min(
        dx ? halfWidth / Math.abs(dx) : Number.POSITIVE_INFINITY,
        dy ? halfHeight / Math.abs(dy) : Number.POSITIVE_INFINITY
    );
    return { x: node.x + dx * scale, y: node.y + dy * scale };
}

function drawGraphEdge(context, route) {
    const { edge, startX, startY, endX, endY, controlX, controlY } = route;
    const color = graphColors[edge.kind] || "#64748b";
    const focused = !graphState.selectedNodeId || edge.source === graphState.selectedNodeId || edge.target === graphState.selectedNodeId;
    const selected = edge.id === graphState.selectedEdgeId;
    const hovered = edge.id === graphState.hoveredEdgeId;
    context.beginPath();
    context.moveTo(startX, startY);
    context.quadraticCurveTo(controlX, controlY, endX, endY);
    context.strokeStyle = color;
    context.globalAlpha = focused ? (selected || hovered ? 1 : .78) : .06;
    context.lineWidth = selected || hovered ? 4.5 : Math.min(3.5, 1.6 + Math.log2(edge.count || 1));
    context.setLineDash(edgeLineDash(edge.kind));
    context.stroke();
    context.setLineDash([]);
    const tangent = Math.atan2(endY - controlY, endX - controlX);
    context.beginPath();
    context.moveTo(endX, endY);
    context.lineTo(
        endX - Math.cos(tangent - .5) * 11,
        endY - Math.sin(tangent - .5) * 11
    );
    context.lineTo(
        endX - Math.cos(tangent + .5) * 11,
        endY - Math.sin(tangent + .5) * 11
    );
    context.closePath();
    context.fillStyle = color;
    context.fill();
    context.globalAlpha = 1;
}

function edgeLineDash(kind) {
    if (kind === "includes") return [9, 5];
    if (kind === "reads" || kind === "input" || kind === "parameter_input") return [2, 5];
    if (kind === "references") return [10, 4, 2, 4];
    return [];
}

function drawGraphNode(context, node) {
    const selected = node.id === graphState.selectedNodeId;
    const external = node.external;
    const connected = !graphState.selectedNodeId || selected || visibleGraphEdges().some(edge =>
        (edge.source === graphState.selectedNodeId && edge.target === node.id) ||
        (edge.target === graphState.selectedNodeId && edge.source === node.id)
    );
    context.globalAlpha = connected ? 1 : .18;
    context.beginPath();
    traceGraphNodeShape(context, node);
    context.fillStyle = external ? "#f8fafc" : nodeColor(node.kind);
    context.fill();
    context.strokeStyle = selected ? "#020617" : (external ? "#64748b" : "#fff");
    context.lineWidth = selected ? 4 : 2;
    context.stroke();
    context.font = "700 11px Inter, sans-serif";
    context.fillStyle = external ? "#334155" : "#fff";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(truncateGraphLabel(node.label, 21), node.x, node.y - 4);
    context.font = "600 9px Inter, sans-serif";
    context.fillStyle = external ? "#64748b" : "rgba(255,255,255,.78)";
    const callPosition = node.call_position;
    const callPositionLabel = callPosition
        ? `${callPosition.entry_candidate ? "start · " : ""}${callPosition.functions_before}← ${callPosition.functions_after}→${callPosition.exit_candidate ? " · end" : ""}`
        : null;
    const subtitle = graphState.viewMode === "trace"
        ? (node.kind === "parameter"
            ? `parameter input · ${node.expanded ? "open" : "closed"}`
            : `${node.trace_role || node.kind.replaceAll("_", " ")} · ${callPositionLabel || (node.expanded ? "expanded" : "collapsed")}`)
        : node.kind.replaceAll("_", " ");
    context.fillText(truncateGraphLabel(subtitle, 25), node.x, node.y + 11);
    context.globalAlpha = 1;
}

function traceGraphNodeShape(context, node) {
    if (["global_variable", "local_variable", "parameter"].includes(node.kind)) {
        context.ellipse(node.x, node.y, node.width / 2, node.height / 2, 0, 0, Math.PI * 2);
        return;
    }
    if (node.kind === "macro") {
        context.moveTo(node.x, node.y - node.height / 2);
        context.lineTo(node.x + node.width / 2, node.y);
        context.lineTo(node.x, node.y + node.height / 2);
        context.lineTo(node.x - node.width / 2, node.y);
        context.closePath();
        return;
    }
    context.roundRect(node.x - node.width / 2, node.y - node.height / 2,
        node.width, node.height, node.kind === "function" ? 10 : 4);
}

function nodeColor(kind) {
    const colors = {
        module: "#2563eb",
        file: "#7c3aed",
        function: "#0f766e",
        global_variable: "#dc2626",
        local_variable: "#ea580c",
        parameter: "#0891b2",
        struct: "#4f46e5",
        enum: "#9333ea",
        macro: "#64748b"
    };
    return colors[kind] || "#475569";
}

function truncateGraphLabel(value, size) {
    const text = String(value || "");
    return text.length > size ? `${text.slice(0, size - 1)}…` : text;
}

function resetGraphView() {
    graphState.scale = 1;
    graphState.offsetX = 0;
    graphState.offsetY = 0;
    resizeGraphCanvas();
}

function graphNodeAt(clientX, clientY) {
    const canvas = document.getElementById("graphCanvas");
    const rect = canvas.getBoundingClientRect();
    const x = (clientX - rect.left - graphState.offsetX) / graphState.scale;
    const y = (clientY - rect.top - graphState.offsetY) / graphState.scale;
    return graphState.positionedNodes.find(node =>
        Math.abs(node.x - x) <= node.width / 2 + 6 &&
        Math.abs(node.y - y) <= node.height / 2 + 6
    );
}

function graphEdgeAt(clientX, clientY) {
    const canvas = document.getElementById("graphCanvas");
    const rect = canvas.getBoundingClientRect();
    const x = (clientX - rect.left - graphState.offsetX) / graphState.scale;
    const y = (clientY - rect.top - graphState.offsetY) / graphState.scale;
    const route = graphEdgeRoutes().find(candidate => {
        for (let step = 0; step <= 20; step += 1) {
            const t = step / 20;
            const px = (1 - t) ** 2 * candidate.startX +
                2 * (1 - t) * t * candidate.controlX + t ** 2 * candidate.endX;
            const py = (1 - t) ** 2 * candidate.startY +
                2 * (1 - t) * t * candidate.controlY + t ** 2 * candidate.endY;
            if (Math.hypot(px - x, py - y) < 9) return true;
        }
        return false;
    });
    return route?.edge || null;
}

function focusGraphNode(node) {
    const rect = document.getElementById("graphCanvas").getBoundingClientRect();
    graphState.offsetX = rect.width / 2 - node.x * graphState.scale;
    graphState.offsetY = rect.height / 2 - node.y * graphState.scale;
}

function renderGraphInspector(node) {
    const inspector = document.getElementById("graphInspector");
    if (!node) {
        inspector.innerHTML = '<span class="eyebrow">Selection</span><h3>No node selected</h3><p>Select a node to isolate and center its direct neighborhood. Owned parameters and locals stay nested here by default.</p>';
        return;
    }
    const edges = graphState.payload?.edges || [];
    const incoming = edges.filter(edge => edge.target === node.id);
    const outgoing = edges.filter(edge => edge.source === node.id);
    const nodes = new Map((graphState.payload?.nodes || []).map(item => [item.id, item]));
    const children = edges.filter(edge => edge.source === node.id &&
        ["contains", "parameter_of", "field_of", "member_of"].includes(edge.kind))
        .map(edge => nodes.get(edge.target)).filter(Boolean);
    const metrics = Object.entries(node.metrics || {}).map(([key, value]) =>
        `<dt>${escapeHtml(key.replaceAll("_", " "))}</dt><dd>${escapeHtml(value)}</dd>`
    ).join("");
    const callers = node.incoming_interactions
        ? node.incoming_interactions.filter(item => item.kind === "calls").map(item => item.source_label)
        : incoming.filter(edge => edge.kind === "calls").map(edge => nodes.get(edge.source)?.label);
    const callees = node.outgoing_interactions
        ? node.outgoing_interactions.filter(item => item.kind === "calls").map(item => item.target_label)
        : outgoing.filter(edge => edge.kind === "calls").map(edge => nodes.get(edge.target)?.label);
    const reads = node.outgoing_interactions
        ? node.outgoing_interactions.filter(item => item.kind === "reads").map(item => item.target_label)
        : outgoing.filter(edge => edge.kind === "reads").map(edge => nodes.get(edge.target)?.label);
    const writes = node.outgoing_interactions
        ? node.outgoing_interactions.filter(item => item.kind === "writes").map(item => item.target_label)
        : outgoing.filter(edge => edge.kind === "writes").map(edge => nodes.get(edge.target)?.label);
    const inputs = node.interface?.inputs || node.inputs || reads;
    const outputs = node.interface?.outputs || node.outputs || writes;
    const owner = node.owner_id ? nodes.get(node.owner_id) : null;
    const parameters = node.interface?.parameters ||
        children.filter(child => child.kind === "parameter").map(formatGraphDeclaration);
    const locals = children.filter(child => child.kind === "local_variable").map(formatGraphDeclaration);
    const parameterBytes = graphOwnedObjectBytes(children, "parameter");
    const localBytes = graphOwnedObjectBytes(children, "local_variable");
    const declarations = (node.declarations || []).map(formatGraphOccurrence);
    const definitions = (node.definitions || []).map(formatGraphOccurrence);
    const incomingEvidence = (node.incoming_interactions || []).map(
        interaction => formatGraphInteraction(interaction, "incoming")
    );
    const outgoingEvidence = (node.outgoing_interactions || []).map(
        interaction => formatGraphInteraction(interaction, "outgoing")
    );
    const observedInputs = (node.outgoing_interactions || [])
        .filter(interaction => ["reads", "references"].includes(interaction.kind))
        .map(interaction => formatGraphInteraction(interaction, "outgoing"));
    const observedOutputs = (node.outgoing_interactions || [])
        .filter(interaction => interaction.kind === "writes")
        .map(interaction => formatGraphInteraction(interaction, "outgoing"));
    const callPosition = node.call_position;
    inspector.innerHTML = `<span class="eyebrow">${escapeHtml(node.kind)}</span>
        <h3>${escapeHtml(node.label)}</h3>
        <dl><dt>Path</dt><dd>${escapeHtml(node.path || "—")}${node.line ? `:${escapeHtml(node.line)}` : ""}</dd>
        ${node.type ? `<dt>Type</dt><dd>${escapeHtml(node.type)}</dd>` : ""}
        ${node.return_type ? `<dt>Returns</dt><dd>${escapeHtml(node.return_type)}</dd>` : ""}
        ${owner ? `<dt>Owned by</dt><dd>${escapeHtml(owner.label)}</dd>` : ""}
        ${callPosition ? `<dt>Call position</dt><dd>${callPosition.entry_candidate ? "Beginning candidate · " : ""}${callPosition.functions_before} functions before · ${callPosition.functions_after} after${callPosition.exit_candidate ? " · ending candidate" : ""}${callPosition.recursive ? " · recursive" : ""}</dd><dt>Direct callers / callees</dt><dd>${callPosition.direct_callers} / ${callPosition.direct_callees}</dd>` : ""}
        ${graphState.viewMode === "trace" && node.suppressed_cycles ? `<dt>Cycle links hidden</dt><dd>${node.suppressed_cycles} already traversed on this branch</dd>` : ""}
        ${node.kind === "function" ? `<dt>Parameter object sizes</dt><dd>${parameterBytes} bytes observed</dd><dt>Local object sizes</dt><dd>${localBytes} bytes observed</dd>` : ""}
        <dt>Incoming relationship groups</dt><dd>${incoming.length}</dd><dt>Outgoing relationship groups</dt><dd>${outgoing.length}</dd>${metrics}</dl>
        ${graphSignalList("Declared at", declarations)}
        ${graphSignalList("Defined at", definitions)}
        ${graphSignalList("Parameters (owned)", parameters)}
        ${graphSignalList("Local storage (owned)", locals)}
        ${graphSignalList("Called by", callers)}
        ${graphSignalList("Calls", callees)}
        ${graphSignalList(node.kind === "function" ? "Interface inputs" : (node.kind === "module" ? "Inputs" : "Reads"), node.interface ? inputs : (node.kind === "function" ? observedInputs : inputs))}
        ${graphSignalList(node.kind === "function" ? "Side-effect outputs" : (node.kind === "module" ? "Outputs" : "Writes"), node.interface ? outputs : (node.kind === "function" ? observedOutputs : outputs))}
        ${node.kind !== "function" && node.kind !== "module" ? graphSignalList("Interacted with by", incomingEvidence) : ""}
        ${node.kind !== "function" && node.kind !== "module" ? graphSignalList("Interacts with", outgoingEvidence) : ""}
        ${node.kind === "function" ? '<p class="graph-evidence-note">Inputs and outputs are structural: parameters and read variables flow in; written variables flow out. Return-value lineage and argument-to-parameter binding remain unavailable until value/control-flow extraction exists. Object-size totals are type-size sums, not code size or an exact stack frame.</p>' : node.kind === "parameter" ? '<p class="graph-evidence-note">This compact parameter port can be expanded to its owner. Its concrete constant, macro, global, return value, or expression origin is not yet extracted, so no binding is invented.</p>' : '<p class="graph-evidence-note">Interactions are source occurrences, not execution order. Control-flow evidence is required before ordering them.</p>'}`;
}

function formatGraphDeclaration(node) {
    const size = node.metrics?.size_bytes !== undefined
        ? ` · ${node.metrics.size_bytes} bytes`
        : "";
    return `${node.type ? `${node.type} ` : ""}${node.label}${size}${node.line ? ` · line ${node.line}` : ""}`;
}

function graphOwnedObjectBytes(children, kind) {
    const sizes = new Map();
    children.filter(child => child.kind === kind).forEach(child => {
        const key = `${child.label}:${child.type || ""}`;
        sizes.set(key, Math.max(sizes.get(key) || 0, Number(child.metrics?.size_bytes || 0)));
    });
    return [...sizes.values()].reduce((total, size) => total + size, 0);
}

function formatGraphOccurrence(occurrence) {
    const location = occurrence.path || occurrence.owner_label || "unknown source";
    return `${location}${occurrence.line ? `:${occurrence.line}` : ""}`;
}

function formatGraphInteraction(interaction, direction) {
    const location = interaction.path
        ? ` · ${interaction.path}${interaction.line ? `:${interaction.line}` : ""}`
        : "";
    if (direction === "incoming") {
        return `${interaction.source_label} (${interaction.source_kind}) → ${interaction.kind}${location}`;
    }
    return `${interaction.kind} → ${interaction.target_label} (${interaction.target_kind})${location}`;
}

function renderGraphEdgeInspector(edge) {
    const inspector = document.getElementById("graphInspector");
    const nodes = new Map((graphState.payload?.nodes || []).map(node => [node.id, node]));
    const source = nodes.get(edge.source)?.label || edge.source;
    const target = nodes.get(edge.target)?.label || edge.target;
    const interactions = edge.interactions || [];
    const evidence = interactions.map(item =>
        `${item.source_label} → ${item.target_label}${item.path ? ` · ${item.path}${item.line ? `:${item.line}` : ""}` : ""}`
    );
    const occurrences = (edge.occurrences || []).map(formatGraphOccurrence);
    inspector.innerHTML = `<span class="eyebrow">${escapeHtml(edge.kind)}</span>
        <h3>${escapeHtml(source)} → ${escapeHtml(target)}</h3>
        <dl><dt>Occurrences</dt><dd>${escapeHtml(edge.count || 1)}</dd>
        <dt>Direction</dt><dd>Displayed flow: source → target</dd>
        ${edge.canonical_kind && edge.canonical_kind !== edge.kind ? `<dt>Canonical evidence</dt><dd>${escapeHtml(edge.canonical_kind)}</dd>` : ""}
        <dt>Resolution</dt><dd>${escapeHtml(edge.resolution || "—")}</dd></dl>
        ${graphSignalList("Named signals", edge.signals || [])}
        ${graphSignalList("Source occurrences", occurrences)}
        ${graphSignalList("Underlying interactions", evidence)}
        ${interactions.length < (edge.count || 1) ? '<p class="graph-evidence-note">The evidence list is bounded; the occurrence count is authoritative.</p>' : ""}`;
}

function graphSignalList(label, values) {
    const unique = [...new Set(values)].filter(Boolean).slice(0, 20);
    if (!unique.length) return "";
    return `<h4>${escapeHtml(label)}</h4><ul>${unique.map(value =>
        `<li>${escapeHtml(value)}</li>`
    ).join("")}</ul>`;
}

async function loadTraceIndex() {
    if (!graphState.runId) return;
    const response = await fetch(
        `/api/runs/${encodeURIComponent(graphState.runId)}/graphs/nodes`
    );
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    graphState.traceIndex = payload.nodes || [];
    renderTraceRootOptions();
}

function renderTraceRootOptions() {
    const select = document.getElementById("graphTraceRoot");
    const mode = document.getElementById("graphTraceRootMode").value;
    const current = select.value;
    const candidates = graphState.traceIndex.filter(node => {
        if (mode === "entry") return node.kind === "function" && node.call_position?.entry_candidate;
        if (mode === "exit") return node.kind === "function" && node.call_position?.exit_candidate;
        return true;
    });
    select.innerHTML = candidates.map(node => {
        const position = node.call_position;
        const marker = position
            ? `${position.entry_candidate ? "START · " : ""}${position.exit_candidate ? "END · " : ""}${position.functions_before} before / ${position.functions_after} after · `
            : "";
        return `<option value="${escapeHtml(node.id)}">${escapeHtml(marker)}${escapeHtml(node.kind)} · ${escapeHtml(node.label)}${node.path ? ` · ${escapeHtml(node.path)}` : ""}</option>`;
    }
    ).join("");
    const defaultRoot = candidates.find(node => node.id === current) ||
        candidates.find(node => node.kind === "function") || candidates[0];
    if (defaultRoot) select.value = defaultRoot.id;
}

async function startGraphTrace() {
    const canonicalId = document.getElementById("graphTraceRoot").value;
    const root = graphState.traceIndex.find(node => node.id === canonicalId);
    if (!root) return;
    graphState.traceCounter = 1;
    graphState.traceInstances = [{
        ...root,
        id: "trace:1",
        canonical_id: root.id,
        parent_instance_id: null,
        trace_depth: 0,
        trace_column: 0,
        trace_role: "root",
        trace_relation_path: [],
        trace_canonical_path: [root.id],
        suppressed_cycles: 0,
        expanded: false
    }];
    graphState.traceEdges = [];
    syncTracePayload("trace:1");
}

async function toggleTraceNode(positionedNode) {
    const node = graphState.traceInstances.find(item => item.id === positionedNode.id);
    if (!node) return;
    if (node.expanded) {
        collapseTraceNode(node.id);
        node.expanded = false;
        syncTracePayload(node.id);
        return;
    }
    if ((node.trace_depth || 0) >= 20) return;
    const params = new URLSearchParams({
        node_id: node.canonical_id,
        direction: document.getElementById("graphTraceDirection").value
    });
    graphState.layers.forEach(layer => params.append("layers", layer));
    const response = await fetch(
        `/api/runs/${encodeURIComponent(graphState.runId)}/graphs/neighborhood?${params}`
    );
    if (!response.ok) throw new Error(await response.text());
    const neighborhood = await response.json();
    const canonicalNodes = new Map(neighborhood.nodes.map(item => [item.id, item]));
    const center = canonicalNodes.get(node.canonical_id);
    if (center) {
        const identity = {
            id: node.id,
            canonical_id: node.canonical_id,
            parent_instance_id: node.parent_instance_id,
            trace_depth: node.trace_depth,
        };
        Object.assign(node, center, identity);
        node.interface = neighborhood.interface;
    }
    let suppressedCycles = 0;
    (neighborhood.edges || []).forEach(edge => {
        const neighborId = edge.source === node.canonical_id ? edge.target : edge.source;
        const neighbor = canonicalNodes.get(neighborId);
        if (!neighbor) return;
        if (!traceBranchAllows(node, edge.id, neighborId)) {
            suppressedCycles += 1;
            return;
        }
        graphState.traceCounter += 1;
        const childId = `trace:${graphState.traceCounter}`;
        const flowSource = edge.flow_source || edge.source;
        const flowTarget = edge.flow_target || edge.target;
        const neighborIsSource = flowSource === neighborId;
        const traceColumn = (node.trace_column || 0) + (neighborIsSource ? -1 : 1);
        const traceRole = neighborIsSource ? edge.source_role : edge.target_role;
        graphState.traceInstances.push({
            ...neighbor,
            id: childId,
            canonical_id: neighbor.id,
            parent_instance_id: node.id,
            trace_depth: (node.trace_depth || 0) + 1,
            trace_column: traceColumn,
            trace_role: traceRole,
            trace_relation_path: [...(node.trace_relation_path || []), edge.id],
            trace_canonical_path: [...(node.trace_canonical_path || []), neighbor.id],
            suppressed_cycles: 0,
            expanded: false
        });
        const visualSource = flowSource === node.canonical_id ? node.id : childId;
        const visualTarget = flowTarget === node.canonical_id ? node.id : childId;
        graphState.traceEdges.push({
            ...edge,
            id: `${node.id}:${childId}:${edge.kind}`,
            kind: edge.flow_kind || edge.kind,
            source: visualSource,
            target: visualTarget
        });
    });
    node.suppressed_cycles = suppressedCycles;
    node.expanded = true;
    syncTracePayload(node.id);
}

function traceBranchAllows(node, relationshipId, neighborCanonicalId) {
    return !(node.trace_relation_path || []).includes(relationshipId) &&
        !(node.trace_canonical_path || []).includes(neighborCanonicalId);
}

function collapseTraceNode(parentId) {
    const descendants = new Set();
    let changed = true;
    while (changed) {
        changed = false;
        graphState.traceInstances.forEach(node => {
            if (node.parent_instance_id === parentId || descendants.has(node.parent_instance_id)) {
                if (!descendants.has(node.id)) {
                    descendants.add(node.id);
                    changed = true;
                }
            }
        });
    }
    graphState.traceInstances = graphState.traceInstances.filter(
        node => !descendants.has(node.id)
    );
    graphState.traceEdges = graphState.traceEdges.filter(
        edge => !descendants.has(edge.source) && !descendants.has(edge.target)
    );
}

function syncTracePayload(focusId = null) {
    graphState.payload = {
        scope: "trace",
        nodes: graphState.traceInstances,
        edges: graphState.traceEdges,
        layers: graphState.overviewPayload?.layers || [],
        summary: {
            nodes: graphState.traceInstances.length,
            relationships: graphState.traceEdges.length,
            unresolved: graphState.traceEdges.filter(
                edge => edge.resolution === "unresolved"
            ).length
        },
        limitations: [
            "Trace instances may duplicate one canonical symbol to keep branches readable.",
            "A canonical symbol may repeat on separate branches, but a branch never revisits a symbol or relationship already in its ancestry.",
            "Expansion follows structural evidence; it is not runtime execution order.",
            ...(graphState.overviewPayload?.limitations || [])
        ]
    };
    graphState.selectedNodeId = null;
    graphState.selectedEdgeId = null;
    renderGraphControls();
    renderGraphPayload();
    resetGraphView();
    if (focusId) {
        const focused = graphState.positionedNodes.find(node => node.id === focusId);
        if (focused) {
            graphState.selectedNodeId = focusId;
            graphState.lastSelectedNodeId = focusId;
            focusGraphNode(focused);
            renderGraphInspector(focused);
            drawGraph();
        }
    }
}

function initializeGraphWorkspace() {
    const scope = document.getElementById("graphScope");
    if (!scope) return;
    document.getElementById("graphViewMode").addEventListener("change", async event => {
        graphState.viewMode = event.target.value;
        if (graphState.viewMode === "trace") {
            try {
                await loadTraceIndex();
                renderGraphControls();
                await startGraphTrace();
            } catch (error) {
                document.getElementById("graphLoading").hidden = false;
                document.getElementById("graphLoading").textContent =
                    `Trace playground could not be loaded: ${String(error)}`;
            }
        } else {
            graphState.payload = graphState.overviewPayload;
            renderGraphControls();
            renderGraphPayload();
            resetGraphView();
        }
    });
    scope.addEventListener("change", async () => {
        graphState.scope = scope.value;
        document.getElementById("graphFileField").hidden = scope.value !== "file";
        document.getElementById("graphModuleField").hidden = scope.value !== "inter_module";
        await loadGraphProjection();
    });
    document.getElementById("graphRun").addEventListener("change", async event => {
        graphState.runId = event.target.value;
        graphState.file = null;
        await loadGraphProjection();
        if (graphState.viewMode === "trace") {
            await loadTraceIndex();
            await startGraphTrace();
        }
    });
    document.getElementById("graphFile").addEventListener("change", async event => {
        graphState.file = event.target.value;
        await loadGraphProjection();
    });
    document.getElementById("graphLayers").addEventListener("change", async event => {
        if (!event.target.matches('input[type="checkbox"]')) return;
        if (!event.target.checked && graphState.layers.size === 1) {
            event.target.checked = true;
            return;
        }
        if (event.target.checked) graphState.layers.add(event.target.value);
        else graphState.layers.delete(event.target.value);
        if (graphState.viewMode === "trace") await startGraphTrace();
        else await loadGraphProjection();
    });
    document.getElementById("graphNodeDetails").addEventListener("change", event => {
        if (!event.target.matches('input[type="checkbox"]')) return;
        if (event.target.checked) graphState.nodeDetails.add(event.target.value);
        else graphState.nodeDetails.delete(event.target.value);
        graphState.selectedNodeId = null;
        graphState.selectedEdgeId = null;
        graphState.lastSelectedNodeId = null;
        resetGraphView();
        renderGraphInspector(null);
    });
    document.getElementById("graphModules").addEventListener("change", async event => {
        if (!event.target.matches('input[type="checkbox"]')) return;
        if (event.target.checked) graphState.modules.add(event.target.value);
        else graphState.modules.delete(event.target.value);
        await loadGraphProjection();
    });
    document.getElementById("graphReset").addEventListener("click", resetGraphView);
    document.getElementById("graphTraceRootMode").addEventListener("change", async () => {
        renderTraceRootOptions();
        await startGraphTrace();
    });
    document.getElementById("graphTraceStart").addEventListener("click", startGraphTrace);
    const canvas = document.getElementById("graphCanvas");
    canvas.addEventListener("click", event => {
        const node = graphNodeAt(event.clientX, event.clientY);
        const edge = node ? null : graphEdgeAt(event.clientX, event.clientY);
        graphState.selectedNodeId = node?.id || null;
        graphState.selectedEdgeId = edge?.id || null;
        if (node) {
            graphState.lastSelectedNodeId = node.id;
            focusGraphNode(node);
            renderGraphInspector(node);
        } else if (edge) {
            renderGraphEdgeInspector(edge);
        } else {
            renderGraphInspector(null);
        }
        drawGraph();
    });
    canvas.addEventListener("dblclick", async event => {
        const node = graphNodeAt(event.clientX, event.clientY) ||
            graphState.positionedNodes.find(item => item.id === graphState.lastSelectedNodeId);
        if (!node) return;
        if (graphState.viewMode === "trace") {
            await toggleTraceNode(node);
        } else if (graphState.scope === "module" && node.kind === "file" && node.path) {
            graphState.scope = "file";
            graphState.file = node.path;
            document.getElementById("graphScope").value = "file";
            await loadGraphProjection();
        } else if (graphState.scope === "inter_module" && node.kind === "module") {
            const record = graphState.catalog.find(item => item.module_name === node.id);
            if (!record) return;
            graphState.scope = "module";
            graphState.runId = record.run_id;
            document.getElementById("graphScope").value = "module";
            renderGraphRunOptions();
            await loadGraphProjection();
        }
    });
    canvas.addEventListener("mousemove", event => {
        if (graphState.dragging) return;
        const edge = graphNodeAt(event.clientX, event.clientY)
            ? null
            : graphEdgeAt(event.clientX, event.clientY);
        const nextId = edge?.id || null;
        if (graphState.hoveredEdgeId !== nextId) {
            graphState.hoveredEdgeId = nextId;
            drawGraph();
        }
        renderGraphEdgeTooltip(edge, event.clientX, event.clientY);
    });
    canvas.addEventListener("mouseleave", () => {
        graphState.hoveredEdgeId = null;
        document.getElementById("graphEdgeTooltip").hidden = true;
        drawGraph();
    });
    canvas.addEventListener("mousedown", event => {
        graphState.dragging = true;
        graphState.dragX = event.clientX - graphState.offsetX;
        graphState.dragY = event.clientY - graphState.offsetY;
    });
    window.addEventListener("mouseup", () => { graphState.dragging = false; });
    window.addEventListener("mousemove", event => {
        if (!graphState.dragging) return;
        graphState.offsetX = event.clientX - graphState.dragX;
        graphState.offsetY = event.clientY - graphState.dragY;
        drawGraph();
    });
    canvas.addEventListener("wheel", event => {
        event.preventDefault();
        graphState.scale = Math.min(3, Math.max(.35,
            graphState.scale * (event.deltaY < 0 ? 1.1 : .9)));
        drawGraph();
    }, { passive: false });
    window.addEventListener("resize", () => {
        if (document.getElementById("graphsPage").classList.contains("active")) {
            resizeGraphCanvas();
        }
    });
}

function renderGraphEdgeTooltip(edge, clientX, clientY) {
    const tooltip = document.getElementById("graphEdgeTooltip");
    if (!edge) {
        tooltip.hidden = true;
        return;
    }
    const nodes = new Map((graphState.payload?.nodes || []).map(node => [node.id, node]));
    const source = nodes.get(edge.source)?.label || edge.source;
    const target = nodes.get(edge.target)?.label || edge.target;
    tooltip.innerHTML = `<strong>${escapeHtml(edge.kind.replaceAll("_", " "))}</strong><br>${escapeHtml(source)} → ${escapeHtml(target)} · ${escapeHtml(edge.count || 1)} occurrence${(edge.count || 1) === 1 ? "" : "s"}`;
    const rect = document.getElementById("graphCanvasWrap").getBoundingClientRect();
    tooltip.style.left = `${Math.max(8, Math.min(rect.width - 330, clientX - rect.left + 14))}px`;
    tooltip.style.top = `${Math.max(8, clientY - rect.top + 14)}px`;
    tooltip.hidden = false;
}

document.addEventListener("DOMContentLoaded", initializeGraphWorkspace);
