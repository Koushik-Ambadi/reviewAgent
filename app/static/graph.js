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
    payload: null,
    positionedNodes: [],
    scale: 1,
    offsetX: 0,
    offsetY: 0,
    dragging: false,
    dragX: 0,
    dragY: 0,
    selectedNodeId: null
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
    const nodes = graphState.payload?.nodes || [];
    if (!nodes.length) {
        graphState.positionedNodes = [];
        return;
    }
    if (graphState.scope === "file") {
        const groups = new Map();
        nodes.forEach(node => {
            const kind = node.kind || "other";
            if (!groups.has(kind)) groups.set(kind, []);
            groups.get(kind).push(node);
        });
        const kinds = [...groups.keys()].sort();
        const columnWidth = Math.max(150, (width - 80) / Math.max(1, kinds.length));
        graphState.positionedNodes = kinds.flatMap((kind, columnIndex) =>
            groups.get(kind).sort((a, b) => a.label.localeCompare(b.label)).map(
                (node, rowIndex) => ({
                    ...node,
                    x: 50 + columnIndex * columnWidth,
                    y: 50 + rowIndex * 62,
                    radius: node.kind === "file" ? 15 : 10
                })
            )
        );
    } else {
        const radius = Math.max(90, Math.min(width, height) * .34);
        graphState.positionedNodes = nodes.map((node, index) => {
            const angle = (Math.PI * 2 * index) / Math.max(1, nodes.length) - Math.PI / 2;
            return {
                ...node,
                x: width / 2 + Math.cos(angle) * radius,
                y: height / 2 + Math.sin(angle) * radius,
                radius: graphState.scope === "inter_module" ? 18 : 13
            };
        });
    }
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
    (graphState.payload?.edges || []).forEach(edge => {
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
    const angle = Math.atan2(target.y - source.y, target.x - source.x);
    const startX = source.x + Math.cos(angle) * source.radius;
    const startY = source.y + Math.sin(angle) * source.radius;
    const endX = target.x - Math.cos(angle) * (target.radius + 4);
    const endY = target.y - Math.sin(angle) * (target.radius + 4);
    context.beginPath();
    context.moveTo(startX, startY);
    context.lineTo(endX, endY);
    context.strokeStyle = color;
    context.globalAlpha = edge.kind.includes("of") || edge.kind === "contains" ? .25 : .48;
    context.lineWidth = Math.min(4, 1 + Math.log2(edge.count || 1));
    context.stroke();
    context.beginPath();
    context.moveTo(endX, endY);
    context.lineTo(
        endX - Math.cos(angle - .45) * 8,
        endY - Math.sin(angle - .45) * 8
    );
    context.lineTo(
        endX - Math.cos(angle + .45) * 8,
        endY - Math.sin(angle + .45) * 8
    );
    context.closePath();
    context.fillStyle = color;
    context.fill();
    context.globalAlpha = 1;
}

function drawGraphNode(context, node) {
    const selected = node.id === graphState.selectedNodeId;
    const external = node.external;
    context.beginPath();
    context.arc(node.x, node.y, node.radius + (selected ? 4 : 0), 0, Math.PI * 2);
    context.fillStyle = external ? "#f8fafc" : nodeColor(node.kind);
    context.fill();
    context.strokeStyle = selected ? "#0f172a" : (external ? "#94a3b8" : "#fff");
    context.lineWidth = selected ? 3 : 2;
    context.stroke();
    context.font = "600 11px Inter, sans-serif";
    context.fillStyle = "#334155";
    context.textAlign = "center";
    context.fillText(truncateGraphLabel(node.label, 24), node.x, node.y + node.radius + 15);
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
        Math.hypot(node.x - x, node.y - y) <= node.radius + 8
    );
}

function renderGraphInspector(node) {
    const inspector = document.getElementById("graphInspector");
    if (!node) {
        inspector.innerHTML = '<span class="eyebrow">Selection</span><h3>No node selected</h3><p>Select a node to inspect its path, metrics, incoming signals, and outgoing signals.</p>';
        return;
    }
    const edges = graphState.payload?.edges || [];
    const incoming = edges.filter(edge => edge.target === node.id);
    const outgoing = edges.filter(edge => edge.source === node.id);
    const metrics = Object.entries(node.metrics || {}).map(([key, value]) =>
        `<dt>${escapeHtml(key.replaceAll("_", " "))}</dt><dd>${escapeHtml(value)}</dd>`
    ).join("");
    const inputs = node.inputs || incoming.flatMap(edge => edge.signals || []);
    const outputs = node.outputs || outgoing.flatMap(edge => edge.signals || []);
    inspector.innerHTML = `<span class="eyebrow">${escapeHtml(node.kind)}</span>
        <h3>${escapeHtml(node.label)}</h3>
        <dl><dt>Path</dt><dd>${escapeHtml(node.path || "—")}</dd>
        <dt>Incoming</dt><dd>${incoming.length}</dd><dt>Outgoing</dt><dd>${outgoing.length}</dd>${metrics}</dl>
        ${graphSignalList("Inputs / reads", inputs)}
        ${graphSignalList("Outputs / writes", outputs)}`;
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
        graphState.selectedNodeId = node?.id || null;
        renderGraphInspector(node || null);
        drawGraph();
    });
    canvas.addEventListener("dblclick", async event => {
        const node = graphNodeAt(event.clientX, event.clientY);
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
