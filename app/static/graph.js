const graphColors = {
    calls: "#2563eb",
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
    scope: "module",
    file: null,
    modules: new Set(),
    layers: new Set(["calls", "includes", "reads", "writes"]),
    nodeDetails: new Set(),
    payload: null,
    positionedNodes: [],
    scale: 1,
    offsetX: 0,
    offsetY: 0,
    dragging: false,
    dragX: 0,
    dragY: 0,
    selectedNodeId: null,
    selectedEdgeId: null,
    lastSelectedNodeId: null
};

async function showGraphs() {
    showPage("graphsPage");
    updateWorkspaceChrome("graphs");
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
    document.getElementById("graphRun").disabled =
        graphState.scope === "inter_module" || !graphState.catalog.length;
    fileField.hidden = graphState.scope !== "file";
    moduleField.hidden = graphState.scope !== "inter_module";
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
        input.disabled = graphState.scope !== "file";
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
        `<span style="--legend-color:${graphColors[kind] || "#64748b"}">${
            escapeHtml(kind.replaceAll("_", " "))
        }</span>`
    ).join("");
    const limitations = payload.limitations || [];
    document.getElementById("graphLimitations").innerHTML = limitations.length
        ? `<ul>${limitations.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
        : "";
    renderGraphRelationshipList();
    renderGraphInspector(null);
    document.getElementById("graphScopeHelp").textContent = graphState.scope === "file"
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
        const signals = edge.signals?.length
            ? ` · ${edge.signals.slice(0, 8).join(", ")}`
            : "";
        return `<div><strong>${escapeHtml(names.get(edge.source) || edge.source)}</strong>
            → ${escapeHtml(edge.kind)} →
            <strong>${escapeHtml(names.get(edge.target) || edge.target)}</strong>
            · ${edge.count || 1} occurrence${(edge.count || 1) === 1 ? "" : "s"}${
                escapeHtml(signals)
            }</div>`;
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
    const columnGap = Math.max(190, (width - 100) / Math.max(1, orderedRanks.length));
    graphState.positionedNodes = orderedRanks.flatMap((rank, columnIndex) => {
        const group = groups.get(rank).sort((a, b) => a.label.localeCompare(b.label));
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

function visibleGraphNodes() {
    const nodes = graphState.payload?.nodes || [];
    if (graphState.scope !== "file") return nodes;
    const primary = new Set(["function"]);
    return nodes.filter(node => primary.has(node.kind) || graphState.nodeDetails.has(node.kind));
}

function visibleGraphEdges(nodeIds = new Set(visibleGraphNodes().map(node => node.id))) {
    return (graphState.payload?.edges || []).filter(edge =>
        !["contains", "parameter_of", "field_of", "member_of"].includes(edge.kind) &&
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
    visibleGraphEdges(new Set(positions.keys())).forEach(edge => {
        const source = positions.get(edge.source);
        const target = positions.get(edge.target);
        if (!source || !target) return;
        drawGraphEdge(context, source, target, edge);
    });
    graphState.positionedNodes.forEach(node => drawGraphNode(context, node));
    context.restore();
}

function drawGraphEdge(context, source, target, edge) {
    const color = graphColors[edge.kind] || "#64748b";
    const focused = !graphState.selectedNodeId || edge.source === graphState.selectedNodeId || edge.target === graphState.selectedNodeId;
    const selected = edge.id === graphState.selectedEdgeId;
    const angle = Math.atan2(target.y - source.y, target.x - source.x);
    const startX = source.x + Math.cos(angle) * Math.min(source.width / 2, 46);
    const startY = source.y + Math.sin(angle) * source.radius;
    const endX = target.x - Math.cos(angle) * Math.min(target.width / 2 + 5, 52);
    const endY = target.y - Math.sin(angle) * (target.radius + 4);
    const curve = Math.min(52, Math.abs(target.x - source.x) * .16) * (edge.kind === "writes" ? -1 : 1);
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2 + curve;
    context.beginPath();
    context.moveTo(startX, startY);
    context.quadraticCurveTo(midX, midY, endX, endY);
    context.strokeStyle = color;
    context.globalAlpha = focused ? (selected ? 1 : .82) : .08;
    context.lineWidth = selected ? 4 : Math.min(3.5, 1.6 + Math.log2(edge.count || 1));
    context.stroke();
    const tangent = Math.atan2(endY - midY, endX - midX);
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

function drawGraphNode(context, node) {
    const selected = node.id === graphState.selectedNodeId;
    const external = node.external;
    const connected = !graphState.selectedNodeId || selected || visibleGraphEdges().some(edge =>
        (edge.source === graphState.selectedNodeId && edge.target === node.id) ||
        (edge.target === graphState.selectedNodeId && edge.source === node.id)
    );
    context.globalAlpha = connected ? 1 : .18;
    context.beginPath();
    context.roundRect(node.x - node.width / 2, node.y - node.height / 2,
        node.width, node.height, 10);
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
    context.fillText(node.kind.replaceAll("_", " "), node.x, node.y + 11);
    context.globalAlpha = 1;
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
    const positions = new Map(graphState.positionedNodes.map(node => [node.id, node]));
    return visibleGraphEdges(new Set(positions.keys())).find(edge => {
        const source = positions.get(edge.source);
        const target = positions.get(edge.target);
        if (!source || !target) return false;
        const curve = Math.min(52, Math.abs(target.x - source.x) * .16) * (edge.kind === "writes" ? -1 : 1);
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2 + curve;
        for (let step = 0; step <= 20; step += 1) {
            const t = step / 20;
            const px = (1 - t) ** 2 * source.x + 2 * (1 - t) * t * midX + t ** 2 * target.x;
            const py = (1 - t) ** 2 * source.y + 2 * (1 - t) * t * midY + t ** 2 * target.y;
            if (Math.hypot(px - x, py - y) < 8) return true;
        }
        return false;
    });
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
    const callers = incoming.filter(edge => edge.kind === "calls").map(edge => nodes.get(edge.source)?.label);
    const callees = outgoing.filter(edge => edge.kind === "calls").map(edge => nodes.get(edge.target)?.label);
    const reads = outgoing.filter(edge => edge.kind === "reads").map(edge => nodes.get(edge.target)?.label);
    const writes = outgoing.filter(edge => edge.kind === "writes").map(edge => nodes.get(edge.target)?.label);
    const inputs = node.inputs || reads;
    const outputs = node.outputs || writes;
    const owner = node.owner_id ? nodes.get(node.owner_id) : null;
    const parameters = children.filter(child => child.kind === "parameter").map(formatGraphDeclaration);
    const locals = children.filter(child => child.kind === "local_variable").map(formatGraphDeclaration);
    inspector.innerHTML = `<span class="eyebrow">${escapeHtml(node.kind)}</span>
        <h3>${escapeHtml(node.label)}</h3>
        <dl><dt>Path</dt><dd>${escapeHtml(node.path || "—")}${node.line ? `:${escapeHtml(node.line)}` : ""}</dd>
        ${node.type ? `<dt>Type</dt><dd>${escapeHtml(node.type)}</dd>` : ""}
        ${node.return_type ? `<dt>Returns</dt><dd>${escapeHtml(node.return_type)}</dd>` : ""}
        ${owner ? `<dt>Owned by</dt><dd>${escapeHtml(owner.label)}</dd>` : ""}
        <dt>Incoming relations</dt><dd>${incoming.length}</dd><dt>Outgoing relations</dt><dd>${outgoing.length}</dd>${metrics}</dl>
        ${graphSignalList("Parameters (owned)", parameters)}
        ${graphSignalList("Local storage (owned)", locals)}
        ${graphSignalList("Called by", callers)}
        ${graphSignalList("Calls", callees)}
        ${graphSignalList(node.kind === "module" ? "Inputs" : "Reads", inputs)}
        ${graphSignalList(node.kind === "module" ? "Outputs" : "Writes", outputs)}
        ${node.kind === "function" ? '<p class="graph-evidence-note">Argument origins, return-expression dependencies, and transformations are not claimed yet; they require value-flow evidence.</p>' : ""}`;
}

function formatGraphDeclaration(node) {
    return `${node.type ? `${node.type} ` : ""}${node.label}${node.line ? ` · line ${node.line}` : ""}`;
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
    inspector.innerHTML = `<span class="eyebrow">${escapeHtml(edge.kind)}</span>
        <h3>${escapeHtml(source)} → ${escapeHtml(target)}</h3>
        <dl><dt>Occurrences</dt><dd>${escapeHtml(edge.count || 1)}</dd>
        <dt>Direction</dt><dd>Source → target</dd>
        <dt>Resolution</dt><dd>${escapeHtml(edge.resolution || "—")}</dd></dl>
        ${graphSignalList("Named signals", edge.signals || [])}
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

function initializeGraphWorkspace() {
    const scope = document.getElementById("graphScope");
    if (!scope) return;
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
        await loadGraphProjection();
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
        if (graphState.scope === "module" && node.kind === "file" && node.path) {
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

document.addEventListener("DOMContentLoaded", initializeGraphWorkspace);
