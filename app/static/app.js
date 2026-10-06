const stageLogs = [
    "Starting review...", "Preparing your upload...", "Reviewing repository contents...",
    "Applying selected review profile...", "Collecting review results...", "Preparing report sections...",
    "Checking report consistency...", "Reviewing repository organization...", "Checking required project items...",
    "Applying naming guidance...", "Reviewing source items...", "Checking project conventions...",
    "Reviewing declared values...", "Checking related project files...", "Organizing review findings...",
    "Preparing your report..."
];

window.currentRunId = null;
window.currentReport = null;

function showPage(id) {
    document.querySelectorAll(".page").forEach(page => page.classList.remove("active"));
    requestAnimationFrame(() => document.getElementById(id).classList.add("active"));
}
function showIntro() { showPage("introPage"); }
function showSetup() { showPage("setupPage"); }
function showReport() { showPage("reportPage"); }
function showBuild() { showPage("buildPage"); }

function setProgress(percent, text) {
    document.getElementById("progressBar").style.width = `${percent}%`;
    document.getElementById("progressText").textContent = `${percent}%`;
    document.getElementById("statusText").textContent = text;
}
function pushLog(text) {
    const row = document.createElement("div");
    row.className = "log";
    row.textContent = `→ ${text}`;
    const box = document.getElementById("logs");
    box.appendChild(row);
    box.scrollTop = box.scrollHeight;
}
function clearLogs() { document.getElementById("logs").innerHTML = ""; }
async function startFakeProgress() {
    clearLogs();
    setProgress(3, "Initializing");
    const timings = [1200, 1000, 1300, 1500, 1200, 2200, 1800, 1400, 1600, 1800, 1500, 1600, 1400, 1300, 1600, 1800];
    for (let index = 0; index < stageLogs.length; index += 1) {
        pushLog(stageLogs[index]);
        setProgress(Math.min(92, 8 + (index * 5.5)), stageLogs[index]);
        await new Promise(resolve => setTimeout(resolve, timings[index] || 1200));
    }
}

async function runPipeline() {
    const file = document.getElementById("zipFile").files[0];
    if (!file) {
        alert("Please select a ZIP file.");
        return;
    }
    showSetup();
    startFakeProgress();
    try {
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch("/api/review", { method: "POST", body: formData });
        if (!response.ok) throw new Error(await response.text());
        const payload = await response.json();
        if (!payload.run_id || !payload.report) throw new Error("Invalid review response");
        window.currentRunId = payload.run_id;
        renderReport(payload.report);
        showReport();
    } catch (error) {
        setProgress(100, "Failed");
        pushLog("The review could not be completed. Please try again.");
        console.error(error);
    }
}

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[character]);
}
function formatDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    return Number.isNaN(date.valueOf()) ? value : date.toLocaleString();
}
function formatBytes(value) {
    if (!Number.isFinite(value)) return "—";
    if (value < 1024) return `${value} B`;
    if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
    return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}
function reportCases(report) {
    return (report.stages || []).flatMap(stage =>
        (stage.checks || []).flatMap(check => (check.cases || []).map(item => ({ stage, check, item })))
    );
}
function statusName(status) {
    const normalized = String(status || "").toUpperCase();
    if (normalized === "SUCCESS" || normalized === "PASSED") return "success";
    if (normalized === "SKIPPED" || normalized === "EXCEPTION") return "skipped";
    return "failed";
}
function pillClass(status) {
    const normalized = String(status || "").toLowerCase();
    if (normalized === "success" || normalized === "passed") return "passed";
    if (normalized === "skipped" || normalized === "warning") return "warning";
    return "failed";
}

function renderReport(report) {
    window.currentReport = report;
    window.currentRunId = window.currentRunId || report.run_id;
    renderMetadata(report);
    renderSummary(report);
    populateReportFilters(report);
    renderStages(report);
}
function renderMetadata(report) {
    const metadata = report.metadata || {};
    const values = [
        ["Run ID", report.run_id || "—"], ["Module", metadata.module_name || "—"],
        ["Policy", metadata.policy_name || "—"], ["Policy version", report.policy_version || "—"],
        ["Report version", report.report_version || "—"], ["Generated", formatDate(metadata.generated_at)]
    ];
    document.getElementById("reportMetadata").innerHTML = `<div class="meta-grid">${values.map(([label, value]) =>
        `<div class="meta-value"><span class="meta-label">${escapeHtml(label)}</span>${escapeHtml(value)}</div>`
    ).join("")}</div>`;
}
function renderSummary(report) {
    const counts = { failed: 0, skipped: 0, success: 0 };
    reportCases(report).forEach(({ item }) => { counts[statusName(item.status)] += 1; });
    const cards = [
        { label: "Failed", value: counts.failed, cls: "failed" }, { label: "Skipped", value: counts.skipped, cls: "warning" },
        { label: "Passed", value: counts.success, cls: "success" }, { label: "Total", value: counts.failed + counts.skipped + counts.success, cls: "total" }
    ];
    document.getElementById("summaryCards").innerHTML = cards.map(card =>
        `<div class="metric ${card.cls}"><div class="value">${card.value}</div><div class="label">${card.label}</div></div>`
    ).join("");
}
function populateReportFilters(report) {
    const stageSelect = document.getElementById("stageFilter");
    stageSelect.innerHTML = '<option value="all">All stages</option>' + (report.stages || []).map(stage =>
        `<option value="${escapeHtml(stage.stage_id)}">${escapeHtml(stage.title)}</option>`
    ).join("");
    refreshCheckFilter(report);
}
function refreshCheckFilter(report) {
    const stageId = document.getElementById("stageFilter").value;
    const checks = (report.stages || []).filter(stage => stageId === "all" || stage.stage_id === stageId)
        .flatMap(stage => stage.checks || []);
    document.getElementById("checkFilter").innerHTML = '<option value="all">All checks</option>' + checks.map(check =>
        `<option value="${escapeHtml(check.check_id)}">${escapeHtml(check.title)}</option>`
    ).join("");
}
function renderStages(report) {
    const query = document.getElementById("caseSearch").value.trim().toLowerCase();
    const wantedStatus = document.getElementById("statusFilter").value;
    const wantedStage = document.getElementById("stageFilter").value;
    const wantedCheck = document.getElementById("checkFilter").value;
    const cards = (report.stages || []).filter(stage => wantedStage === "all" || stage.stage_id === wantedStage).map(stage => {
        const renderedChecks = (stage.checks || []).filter(check => wantedCheck === "all" || check.check_id === wantedCheck).map(check => {
            const cases = (check.cases || []).filter(item => {
                const haystack = [item.name, item.location, check.title, stage.title, ...(item.reasons || [])].join(" ").toLowerCase();
                return (wantedStatus === "all" || statusName(item.status) === wantedStatus) && (!query || haystack.includes(query));
            });
            if (!cases.length && (query || wantedStatus !== "all")) return "";
            const summary = check.summary || {};
            const hasFailures = (summary.failed || 0) > 0;
            return `<details class="check-card" data-check-id="${escapeHtml(check.check_id)}">
                <summary class="check-heading"><span><strong>${escapeHtml(check.title)}</strong><div class="section-sub">${summary.failed || 0} failed · ${summary.skipped || 0} skipped · ${summary.passed || 0} passed</div></span><span class="pill ${hasFailures ? "failed" : "passed"}">${hasFailures ? "Failed" : "Completed"}</span></summary>
                <div class="check-content"><div class="check-actions">${hasFailures ? `<button class="inline-action" type="button" data-remediation-scope="check" data-check-id="${escapeHtml(check.check_id)}">Suggest fixes for this check</button>` : ""}</div>${cases.length ? cases.map(item => renderCase(item, check.check_id)).join("") : '<div class="case-row success">No cases match the current filters.</div>'}</div>
            </details>`;
        }).filter(Boolean).join("");
        if (!renderedChecks && (query || wantedStatus !== "all")) return "";
        const summary = stage.summary || {};
        const hasFailures = (summary.failed || 0) > 0;
        return `<section class="stage-card" data-stage-id="${escapeHtml(stage.stage_id)}"><div class="stage-heading"><div><h2>${escapeHtml(stage.title)}</h2><div class="section-sub">${summary.failed || 0} failed · ${summary.skipped || 0} skipped · ${summary.passed || 0} passed</div></div><span class="pill ${hasFailures ? "failed" : "passed"}">${hasFailures ? "Failed" : "Completed"}</span></div><div class="check-list">${renderedChecks || '<div class="case-row success">No checks in this stage.</div>'}</div></section>`;
    }).filter(Boolean);
    document.getElementById("stages").innerHTML = cards.join("") || '<div class="empty-state">No results match the current filters.</div>';
}
function renderCase(item, checkId) {
    const status = statusName(item.status);
    const reasons = item.reasons || [];
    return `<article class="case-row ${status}" data-case-id="${escapeHtml(item.case_id)}">
        <div class="case-main"><div class="case-title"><strong>${escapeHtml(item.name || "Unnamed case")}</strong><span class="pill ${pillClass(status)}">${escapeHtml(item.status)}</span></div>
        <div class="case-location">${escapeHtml(item.location || "")}</div>
        ${reasons.length ? `<details class="case-reasons"><summary>${reasons.length} rule detail${reasons.length === 1 ? "" : "s"}</summary><ul>${reasons.map(reason => `<li>${escapeHtml(reason)}</li>`).join("")}</ul></details>` : ""}</div>
        ${status === "failed" ? `<button class="inline-action case-actions" type="button" data-remediation-scope="case" data-check-id="${escapeHtml(checkId)}" data-case-id="${escapeHtml(item.case_id)}">Suggest fix</button>` : ""}
    </article>`;
}
function applyReportFilters() { if (window.currentReport) renderStages(window.currentReport); }

function openRemediationDrawer() {
    document.getElementById("drawerBackdrop").hidden = false;
    document.getElementById("remediationDrawer").classList.add("open");
    document.getElementById("remediationDrawer").setAttribute("aria-hidden", "false");
}
function closeRemediationDrawer() {
    document.getElementById("drawerBackdrop").hidden = true;
    document.getElementById("remediationDrawer").classList.remove("open");
    document.getElementById("remediationDrawer").setAttribute("aria-hidden", "true");
}
function renderRemediation(remediation) {
    const affected = remediation.affected_cases || [];
    const suggestions = remediation.suggestions || [];
    document.getElementById("remediationContent").innerHTML = `<article class="remediation-result">
        <span class="pill ${remediation.scope === "case" ? "warning" : "passed"}">${escapeHtml(remediation.scope)} scope</span>
        <h3>${escapeHtml(remediation.title || "Suggested fixes")}</h3>
        <p>${escapeHtml(remediation.summary || "")}</p>
        ${remediation.common_failure_patterns?.length ? `<section><h4>Patterns</h4><ul>${remediation.common_failure_patterns.map(pattern => `<li>${escapeHtml(pattern)}</li>`).join("")}</ul></section>` : ""}
        ${suggestions.length ? `<section><h4>Suggestions</h4>${suggestions.map(suggestion => `<div class="suggestion"><strong>${escapeHtml(suggestion.title)}</strong><p>${escapeHtml(suggestion.description)}</p></div>`).join("")}</section>` : ""}
        ${affected.length ? `<section><h4>Affected cases</h4><ul>${affected.map(item => `<li><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(item.location || "")}</span></li>`).join("")}</ul></section>` : ""}
    </article>`;
}
async function requestRemediation(button) {
    if (!window.currentRunId) return;
    const payload = { scope: button.dataset.remediationScope, check_id: button.dataset.checkId };
    if (payload.scope === "case") payload.case_id = button.dataset.caseId;
    openRemediationDrawer();
    document.getElementById("remediationContent").innerHTML = '<p class="empty-state">Preparing remediation suggestion…</p>';
    button.disabled = true;
    try {
        const response = await fetch(`/api/runs/${encodeURIComponent(window.currentRunId)}/remediations`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(await response.text());
        const result = await response.json();
        const items = window.currentReport.remediation || [];
        window.currentReport.remediation = [...items, result.remediation];
        renderRemediation(result.remediation);
    } catch (error) {
        document.getElementById("remediationContent").innerHTML = `<p class="empty-state">${escapeHtml(String(error))}</p>`;
        console.error(error);
    } finally {
        button.disabled = false;
    }
}
function showPlannedNotice() { alert("Pull request creation is not available in this prototype."); }

function renderBuildLoading(status = {}) {
    const output = [...(status.stdout || []), ...(status.stderr || [])].join("\n");
    document.getElementById("buildResult").innerHTML = `<div class="build-grid"><section class="glass panel build-live"><div class="build-live-header"><h3>Build in progress</h3><span id="buildState" class="pill warning">${escapeHtml(String(status.state || "queued").toUpperCase())}</span></div><p id="buildStateMessage">${escapeHtml(status.state === "queued" ? "Waiting for a build worker." : "The build is running. New output appears below as it is captured.")}</p><pre id="liveBuildOutput">${escapeHtml(output || "No output captured yet.")}</pre></section><section class="glass panel"><h3>Build settings</h3><p>Formatting: ${status.run_format ? "requested" : "disabled"}</p><p class="section-sub">A formatter runs only when the uploaded project includes a repository-local <code>review-build.json</code> wrapper declaration.</p></section></div>`;
}
function updateLiveBuild(status) {
    const output = [...(status.stdout || []), ...(status.stderr || [])].join("\n");
    const state = document.getElementById("buildState");
    const message = document.getElementById("buildStateMessage");
    const outputElement = document.getElementById("liveBuildOutput");
    if (!state || !message || !outputElement) {
        renderBuildLoading(status);
        return;
    }
    state.textContent = String(status.state || "running").toUpperCase();
    message.textContent = status.state === "queued" ? "Waiting for a build worker." : "The build is running. New output appears below as it is captured.";
    outputElement.textContent = output || "No output captured yet.";
    outputElement.scrollTop = outputElement.scrollHeight;
}
function renderBuild(result) {
    const formatStep = result.format_step || { status: "skipped", message: "Formatting is not configured for this uploaded repository." };
    const buildStep = result.build_step || { status: result.status || "failed", message: "Build did not return a step result." };
    const diagnostics = result.important_diagnostics || [];
    const artifacts = result.artifact_manifest || [];
    const intelligence = result.intelligence_summary || {};
    const output = [...(result.stdout || []), ...(result.stderr || [])].join("\n");
    document.getElementById("buildResult").innerHTML = `
        <div class="build-config"><span><strong>Formatting:</strong> ${escapeHtml(formatStep.command || "not configured")}</span><span><strong>Build:</strong> ${escapeHtml(result.build_script || "cmake-build.bat")}</span></div>
        <div class="summary build-summary"><div class="metric ${pillClass(buildStep.status)}"><div class="value">${escapeHtml(String(buildStep.status || result.status || "unknown").toUpperCase())}</div><div class="label">Build</div></div><div class="metric ${pillClass(formatStep.status)}"><div class="value">${escapeHtml(String(formatStep.status || "skipped").toUpperCase())}</div><div class="label">Formatting</div></div><div class="metric total"><div class="value">${escapeHtml(String(result.return_code ?? "—"))}</div><div class="label">Return code</div></div></div>
        <div class="build-grid">
            <section class="glass panel"><h3>Build intelligence</h3><p>${escapeHtml(intelligence.summary || buildStep.message || "Build result is available.")}</p><p class="section-sub">Next action: ${escapeHtml(intelligence.next_action || "Review the build output.")}</p>${intelligence.suggestions?.length ? `<ul>${intelligence.suggestions.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}</section>
            <section class="glass panel"><h3>Important diagnostics</h3>${diagnostics.length ? `<ul class="diagnostic-list">${diagnostics.map(line => `<li>${escapeHtml(line)}</li>`).join("")}</ul>` : '<p class="section-sub">No important diagnostics were selected.</p>'}</section>
            <section class="glass panel build-artifacts"><h3>Available artifacts</h3>${artifacts.length ? `<ul>${artifacts.map(artifact => `<li><strong>${escapeHtml(artifact.relative_path)}</strong><span>${escapeHtml(artifact.type)} · ${formatBytes(artifact.size_bytes)} · ${escapeHtml(formatDate(artifact.modified_at))}</span></li>`).join("")}</ul>` : '<p class="section-sub">No build artifacts were discovered.</p>'}</section>
            <section class="glass panel build-output"><h3>Raw output</h3><pre>${escapeHtml(output || "No output was captured.")}</pre></section>
        </div>`;
}
async function triggerBuild() {
    if (!window.currentRunId) { alert("Run review first."); return; }
    const runFormat = document.getElementById("runFormatter")?.checked || false;
    showBuild();
    renderBuildLoading({ state: "queued", run_format: runFormat });
    await new Promise(resolve => requestAnimationFrame(resolve));
    try {
        const query = new URLSearchParams({ background: "true", run_format: String(runFormat) });
        const response = await fetch(`/api/runs/${encodeURIComponent(window.currentRunId)}/build?${query}`, { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        await pollBuildStatus();
    } catch (error) {
        document.getElementById("buildResult").innerHTML = `<div class="glass panel"><span class="pill failed">Failed</span><h3>Build could not be started</h3><p>${escapeHtml(String(error))}</p></div>`;
        console.error(error);
    }
}
async function pollBuildStatus() {
    const endpoint = `/api/runs/${encodeURIComponent(window.currentRunId)}/build/status`;
    while (true) {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(await response.text());
        const status = await response.json();
        if (status.state === "completed" && status.result) {
            if (window.currentReport) window.currentReport.build_result = status.result;
            renderBuild(status.result);
            return;
        }
        if (status.state === "failed") {
            throw new Error(status.error || "Build worker failed before producing a result.");
        }
        updateLiveBuild(status);
        await new Promise(resolve => setTimeout(resolve, 750));
    }
}

document.getElementById("caseSearch").addEventListener("input", applyReportFilters);
document.getElementById("statusFilter").addEventListener("change", applyReportFilters);
document.getElementById("checkFilter").addEventListener("change", applyReportFilters);
document.getElementById("stageFilter").addEventListener("change", () => {
    if (window.currentReport) { refreshCheckFilter(window.currentReport); renderStages(window.currentReport); }
});
document.getElementById("stages").addEventListener("click", event => {
    const button = event.target.closest("[data-remediation-scope]");
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();
    requestRemediation(button);
});
document.getElementById("drawerBackdrop").addEventListener("click", closeRemediationDrawer);
