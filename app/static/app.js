const stageLogs = [
    "Starting review...", "Preparing your upload...", "Reviewing repository contents...",
    "Applying selected review profile...", "Collecting review results...", "Preparing report sections...",
    "Checking report consistency...", "Reviewing repository organization...", "Checking required project items...",
    "Applying naming guidance...", "Reviewing source items...", "Checking project conventions...",
    "Reviewing declared values...", "Checking related project files...", "Organizing review findings...",
    "Preparing your report..."
];
const DEFAULT_PROFILE = {
    name: "ABS Embedded C Default",
    domain: "Embedded / battery management",
    language: "C",
    review_policy: "ABS Default Policy v4",
    formatter: "repository configured",
    build_adapter: "cmake-build.bat",
    artifact_types: ["ELF", "HEX", "BIN", "MAP", "logs", "reports"]
};

window.currentRunId = null;
window.currentReport = null;
window.currentBuildState = "not-run";
window.currentProfile = { ...DEFAULT_PROFILE };

function showPage(id) {
    document.querySelectorAll(".page").forEach(page => {
        page.classList.toggle("active", page.id === id);
    });
}
function showIntro() { showPage("introPage"); }
function showSetup() { showPage("setupPage"); }
function showReport() { showPage("reportPage"); updateWorkspaceChrome("report"); }
function showBuild() {
    showPage("buildPage");
    if (window.currentReport?.build_result?.run_id) renderBuild(window.currentReport.build_result);
    else if (window.currentBuildState === "not-run") renderBuildNotRun();
    updateWorkspaceChrome("build");
}
function showRoadmap() { showPage("roadmapPage"); updateWorkspaceChrome("roadmap"); }

function startNewReview() {
    document.getElementById("zipFile").value = "";
    window.currentRunId = null;
    window.currentReport = null;
    window.currentBuildState = "not-run";
    showSetup();
}
function rerunReview() {
    if (!document.getElementById("zipFile").files[0]) {
        alert("The original ZIP is no longer available. Choose it again to re-run the review.");
        showSetup();
        return;
    }
    runPipeline();
}
function downloadEvidencePack() {
    if (!window.currentRunId) { alert("Run a review first."); return; }
    window.location.assign(`/api/runs/${encodeURIComponent(window.currentRunId)}/evidence-pack`);
}
function renderProfileSummary(profile = DEFAULT_PROFILE) {
    const values = [
        ["Profile", profile.name], ["Domain", profile.domain], ["Language", profile.language],
        ["Review policy", profile.review_policy], ["Formatter", profile.formatter],
        ["Build adapter", profile.build_adapter], ["Artifact types", (profile.artifact_types || []).join(", ")]
    ];
    document.getElementById("profileSummary").innerHTML = `<div class="meta-grid">${values.map(([label, value]) =>
        `<div class="meta-value"><span class="meta-label">${escapeHtml(label)}</span>${escapeHtml(value || "—")}</div>`
    ).join("")}</div>`;
}
async function loadReviewProfile() {
    try {
        const response = await fetch("/api/policies/default");
        if (!response.ok) throw new Error("Default policy profile is unavailable.");
        const payload = await response.json();
        window.currentProfile = { ...DEFAULT_PROFILE, ...(payload.template?.metadata?.profile || {}) };
    } catch (error) {
        window.currentProfile = { ...DEFAULT_PROFILE };
        console.warn(error);
    }
    renderProfileSummary(window.currentProfile);
}

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
        window.currentBuildState = payload.report.build_result?.run_id ? statusName(payload.report.build_result.status) : "not-run";
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
    return visibleStages(report).flatMap(stage =>
        (stage.checks || []).flatMap(check => (check.cases || []).map(item => ({ stage, check, item })))
    );
}
function visibleStages(report) {
    return (report.stages || []).filter(stage =>
        (stage.inventory?.items || []).length > 0 ||
        (stage.inventory?.groups || []).some(group => (group.artifacts || []).length > 0) ||
        (stage.checks || []).some(check => (check.cases || []).length > 0)
    );
}
function renderInventoryArtifact(artifact) {
    const evidence = artifact.evidence || [];
    const auditLabel = String(artifact.audit_status || "not_audited").replaceAll("_", " ");
    return `<article class="inventory-artifact" data-artifact-id="${escapeHtml(artifact.artifact_id)}">
        <div class="inventory-artifact-main"><div class="inventory-artifact-title"><strong>${escapeHtml(artifact.name || "Unnamed artifact")}</strong><span class="pill warning">${escapeHtml(auditLabel)}</span></div>
        <div class="case-location">${escapeHtml(artifact.location || "")}</div>
        ${evidence.length ? `<ul class="inventory-evidence">${evidence.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}</div>
        <p class="inventory-reason">${artifact.audit_reason ? `<strong>Audit rationale:</strong> ${escapeHtml(artifact.audit_reason)}` : "No audit rationale recorded."}</p>
    </article>`;
}
function renderInventoryGroup(group, index) {
    const artifacts = group.artifacts || [];
    const audited = artifacts.filter(item => item.audit_status === "audited").length;
    const pending = artifacts.filter(item => item.audit_status === "pending_approval").length;
    const notAudited = artifacts.length - audited - pending;
    return `<details class="inventory-group" ${index === 0 ? "open" : ""}>
        <summary><span><strong>${escapeHtml(group.label)}</strong><small>${artifacts.length} identified</small></span><span class="inventory-group-audit">${audited} audited · ${pending} pending · ${notAudited} not audited</span></summary>
        <div class="inventory-artifacts">${artifacts.map(renderInventoryArtifact).join("")}</div>
    </details>`;
}
function renderStageInventory(inventory, items, groups) {
    const audit = inventory.audit || {};
    const parsedFiles = inventory.parsed_files || 0;
    const skippedFiles = inventory.skipped_files || 0;
    const hasRegister = groups.some(group => (group.artifacts || []).length > 0);
    const auditContent = hasRegister
        ? `<div class="inventory-audit-values"><span><strong>${audit.audited ?? 0}</strong> audited</span><span><strong>${audit.pending_approval ?? 0}</strong> pending approval</span><span><strong>${audit.not_audited ?? 0}</strong> not audited</span></div><p class="inventory-audit-note"><strong>Audit register initialized.</strong> Every extracted record starts as not audited. Review decisions and approvals are not writable yet.</p>`
        : '<p class="inventory-audit-note"><strong>Detailed audit register is unavailable for this report.</strong> Re-run the review to generate individual artifact records.</p>';
    return `<div class="inventory-summary">
        <div class="inventory-coverage"><span><strong>${parsedFiles}</strong> ${parsedFiles === 1 ? "file" : "files"} parsed</span><span><strong>${skippedFiles}</strong> ${skippedFiles === 1 ? "file" : "files"} skipped</span><code>${escapeHtml(inventory.source_artifact || "analysis/symbols.json")}</code></div>
        <div class="inventory-summary-heading"><h3>Identified artifact summary</h3><p>Counts are derived from the generated symbol inventory.</p></div>
        <div class="inventory-grid">${items.map(item => `<article class="inventory-card"><strong>${item.identified || 0}</strong><span>${escapeHtml(item.label)}</span></article>`).join("")}</div>
        ${auditContent}
        ${hasRegister ? `<div class="inventory-register-heading"><h3>Artifact audit register</h3><p>Open a group to inspect every extracted record and its parser evidence.</p></div><div class="inventory-groups">${groups.filter(group => (group.artifacts || []).length).map(renderInventoryGroup).join("")}</div>` : ""}
    </div>`;
}
function renderAnalysisIntelligence(info, report) {
    if (!info || info.status !== 'available') return '';
    const top = info.top_functions || [];
    return `<div class="inventory-summary" aria-label="Code intelligence in this run">
        <div class="inventory-summary-heading"><h3>Code understanding and investigation priorities</h3><p>Static signals from this run. A high score is a review priority, not a defect.</p></div>
        <div class="inventory-coverage"><span><strong>${info.functions}</strong> functions</span><span><strong>${info.complexity_outliers}</strong> complexity outliers</span><span><strong>${info.shared_values}</strong> shared values</span><span><strong>${info.recursive_groups}</strong> recursive groups</span></div>
        <p>CFG/DFD: ${escapeHtml(info.flow_status)} · ${info.flow_completed_sources} source bundles completed · ${info.flow_failed_sources} failed · ${info.flow_skipped_sources} skipped.</p>
        <ol>${top.map(f=>`<li>${escapeHtml(f.name)} · complexity ${f.complexity??'unknown'} · ${f.callers} callers · ${f.callees} callees · review score ${f.review_score}</li>`).join('')}</ol>
        <button class="btn secondary" type="button" data-open-run-graphs="${escapeHtml(report.run_id)}" data-module="${escapeHtml(report.metadata?.module_name||'')}">Explore this run's graphs</button>
    </div>`;
}
function filterInventoryGroups(groups, query, stageMatchesQuery) {
    if (!query || stageMatchesQuery) return groups;
    return groups.map(group => {
        const groupMatches = [group.label, group.group_id].join(" ").toLowerCase().includes(query);
        const artifacts = groupMatches ? (group.artifacts || []) : (group.artifacts || []).filter(artifact =>
            [artifact.name, artifact.location, artifact.audit_status, artifact.audit_reason, ...(artifact.evidence || [])].join(" ").toLowerCase().includes(query)
        );
        return { ...group, artifacts };
    }).filter(group => group.artifacts.length);
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

function buildBadgeState() {
    if (window.currentBuildState === "queued" || window.currentBuildState === "running") return "running";
    if (window.currentBuildState === "success" || window.currentBuildState === "passed") return "passed";
    if (window.currentBuildState === "failed") return "failed";
    return "not run";
}
function updateWorkspaceChrome(activeTab) {
    const remediationCount = window.currentReport?.remediation?.length || 0;
    const buildState = buildBadgeState();
    document.querySelectorAll("[data-workspace-tab]").forEach(button => {
        const active = button.dataset.workspaceTab === activeTab;
        button.classList.toggle("active", active);
        button.setAttribute("aria-selected", String(active));
    });
    document.querySelectorAll("[data-remediation-count]").forEach(badge => {
        badge.textContent = `${remediationCount} ${remediationCount === 1 ? "plan" : "plans"}`;
    });
    document.querySelectorAll("[data-build-badge]").forEach(badge => {
        badge.textContent = buildState;
        badge.className = `tab-badge ${buildState.replace(" ", "-")}`;
    });
    document.querySelectorAll("[data-build-action]").forEach(button => {
        const running = buildState === "running";
        button.disabled = running;
        button.textContent = running ? "Build running…" : (buildState === "not run" ? "Run build" : "Re-run build");
    });
}

function renderReport(report) {
    window.currentReport = report;
    window.currentRunId = window.currentRunId || report.run_id;
    renderMetadata(report);
    renderSummary(report);
    populateReportFilters(report);
    renderStages(report);
    updateWorkspaceChrome("report");
}
function renderMetadata(report) {
    const metadata = report.metadata || {};
    const profile = { ...DEFAULT_PROFILE, ...window.currentProfile, ...(metadata.profile || {}) };
    const values = [
        ["Run ID", report.run_id || "—"], ["Module", metadata.module_name || "—"],
        ["Profile", profile.name], ["Domain", profile.domain],
        ["Language", profile.language], ["Review policy", profile.review_policy || metadata.policy_name || "—"],
        ["Policy version", report.policy_version || "—"], ["Formatter", profile.formatter],
        ["Build adapter", profile.build_adapter], ["Artifact types", profile.artifact_types.join(", ")],
        ["Report version", report.report_version || "—"], ["Generated", formatDate(metadata.generated_at)]
    ];
    document.getElementById("reportMetadata").innerHTML = `<div class="meta-grid">${values.map(([label, value]) =>
        `<div class="meta-value"><span class="meta-label">${escapeHtml(label)}</span>${escapeHtml(value)}</div>`
    ).join("")}</div>`;
    const summary = document.getElementById("reportMetadataSummary");
    if (summary) summary.textContent = `${profile.name} · ${metadata.module_name || "Uploaded repository"}`;
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
    document.getElementById("statusFilter").innerHTML = [
        ["failed", "Failed"], ["skipped", "Skipped"], ["success", "Passed"]
    ].map(([value, label]) => facetOption(value, label)).join("");
    document.getElementById("stageFilter").innerHTML = visibleStages(report).map(stage =>
        facetOption(stage.stage_id, stage.title)
    ).join("");
    refreshCheckFilter(report);
    updateFacetSummaries();
}
function refreshCheckFilter(report) {
    const selectedStages = selectedFacetValues("stageFilter");
    const selectedChecks = selectedFacetValues("checkFilter");
    const checks = visibleStages(report)
        .filter(stage => !selectedStages.size || selectedStages.has(stage.stage_id))
        .flatMap(stage => stage.checks || []);
    const uniqueChecks = [...new Map(checks.map(check => [check.check_id, check])).values()];
    document.getElementById("checkFilter").innerHTML = uniqueChecks.map(check =>
        facetOption(check.check_id, check.title, selectedChecks.has(check.check_id))
    ).join("");
    updateFacetSummary("checkFilter");
}
function facetOption(value, label, checked = false) {
    return `<label class="facet-option"><input type="checkbox" value="${escapeHtml(value)}" ${checked ? "checked" : ""}><span>${escapeHtml(label)}</span></label>`;
}
function selectedFacetValues(id) {
    return new Set([...document.querySelectorAll(`#${id} input:checked`)].map(input => input.value));
}
function updateFacetSummary(id) {
    const container = document.getElementById(id);
    const summary = document.querySelector(`[data-facet-summary="${id}"]`);
    if (!container || !summary) return;
    const selected = [...container.querySelectorAll("input:checked")];
    const allLabel = summary.dataset.allLabel;
    if (!selected.length) summary.textContent = allLabel;
    else if (selected.length === 1) summary.textContent = selected[0].nextElementSibling.textContent;
    else summary.textContent = `${selected.length} selected`;
}
function updateFacetSummaries() {
    ["statusFilter", "stageFilter", "checkFilter"].forEach(updateFacetSummary);
}
function renderStages(report) {
    const query = document.getElementById("caseSearch").value.trim().toLowerCase();
    const wantedStatuses = selectedFacetValues("statusFilter");
    const wantedStages = selectedFacetValues("stageFilter");
    const wantedChecks = selectedFacetValues("checkFilter");
    const cards = visibleStages(report).filter(stage => !wantedStages.size || wantedStages.has(stage.stage_id)).map(stage => {
        const inventory = stage.inventory || {};
        const inventoryItems = inventory.items || [];
        const inventoryGroups = inventory.groups || [];
        const stageMatchesQuery = !query || [stage.title, stage.stage_id].join(" ").toLowerCase().includes(query);
        const matchingInventory = stageMatchesQuery
            ? inventoryItems
            : inventoryItems.filter(item => [item.label, item.inventory_id].join(" ").toLowerCase().includes(query));
        const matchingGroups = filterInventoryGroups(inventoryGroups, query, stageMatchesQuery);
        const showInventory = (matchingInventory.length > 0 || matchingGroups.length > 0) && !wantedStatuses.size && !wantedChecks.size;
        const renderedChecks = (stage.checks || []).filter(check => !wantedChecks.size || wantedChecks.has(check.check_id)).map(check => {
            const cases = (check.cases || []).filter(item => {
                const haystack = [item.name, item.location, check.title, stage.title, ...(item.reasons || [])].join(" ").toLowerCase();
                return (!wantedStatuses.size || wantedStatuses.has(statusName(item.status))) && (!query || haystack.includes(query));
            });
            if (!cases.length && (query || wantedStatuses.size || wantedChecks.size)) return "";
            const summary = check.summary || {};
            const hasFailures = (summary.failed || 0) > 0;
            return `<details class="check-card" data-check-id="${escapeHtml(check.check_id)}">
                <summary class="check-heading"><span><strong>${escapeHtml(check.title)}</strong><div class="section-sub">${summary.failed || 0} failed · ${summary.skipped || 0} skipped · ${summary.passed || 0} passed</div></span><span class="pill ${hasFailures ? "failed" : "passed"}">${hasFailures ? "Failed" : "Completed"}</span></summary>
                <div class="check-content"><div class="check-actions">${hasFailures ? `<button class="inline-action" type="button" data-remediation-scope="check" data-check-id="${escapeHtml(check.check_id)}">${remediationForCheck(check.check_id) ? "Generate missing remediations" : "Suggest fixes for this check"}</button>` : ""}</div>${cases.length ? cases.map(item => renderCase(item, check.check_id)).join("") : '<div class="case-row success">No cases match the current filters.</div>'}</div>
            </details>`;
        }).filter(Boolean).join("");
        if (!renderedChecks && !showInventory && (query || wantedStatuses.size || wantedChecks.size)) return "";
        const summary = stage.summary || {};
        const hasFailures = (summary.failed || 0) > 0;
        const identified = inventoryItems.reduce((total, item) => total + (item.identified || 0), 0);
        const hasInventory = inventoryItems.length || inventoryGroups.length;
        const stageDetail = hasInventory
            ? `${identified} extracted records · ${inventory.parsed_files || 0} parsed files · ${inventory.skipped_files || 0} skipped files`
            : `${summary.failed || 0} failed · ${summary.skipped || 0} skipped · ${summary.passed || 0} passed`;
        const insightContent = stage.stage_id === 'analysis' && !query && !wantedStatuses.size && !wantedChecks.size ? renderAnalysisIntelligence(report.analysis_intelligence, report) : '';
        const content = (showInventory ? renderStageInventory(inventory, matchingInventory, matchingGroups) : "") + insightContent + renderedChecks;
        if (!content) return "";
        return `<section class="stage-card" data-stage-id="${escapeHtml(stage.stage_id)}"><div class="stage-heading"><div><h2>${escapeHtml(stage.title)}</h2><div class="section-sub">${stageDetail}</div></div><span class="pill ${hasFailures ? "failed" : "passed"}">${hasFailures ? "Failed" : (hasInventory ? "Inventory ready" : "Completed")}</span></div><div class="check-list">${content}</div></section>`;
    }).filter(Boolean);
    document.getElementById("stages").innerHTML = cards.join("") || '<div class="empty-state">No results match the current filters.</div>';
}
function renderCase(item, checkId) {
    const status = statusName(item.status);
    const reasons = item.reasons || [];
    const remediationCase = remediationCaseFor(checkId, item.case_id);
    const remediationStatus = remediationCase?.status || "not_requested";
    const remediationDetail = remediationStatus === "candidate_ready"
        ? `Candidate: ${escapeHtml(remediationCase.candidate_name || "")}`
        : remediationStatus === "input_required"
            ? "Developer context required"
            : remediationStatus === "unsupported"
                ? "Current limitation recorded"
                : "No remediation generated";
    const actionLabel = remediationStatus === "not_requested" ? "Generate remediation" : "View remediation";
    return `<article class="case-row ${status}" data-case-id="${escapeHtml(item.case_id)}">
        <div class="case-main"><div class="case-title"><strong>${escapeHtml(item.name || "Unnamed case")}</strong><span class="pill ${pillClass(status)}">${escapeHtml(item.status)}</span></div>
        <div class="case-location">${escapeHtml(item.location || "")}</div>
        ${status === "failed" ? `<div class="case-remediation-state ${escapeHtml(remediationStatus)}">${remediationDetail}</div>` : ""}
        ${reasons.length ? `<details class="case-reasons"><summary>${reasons.length} rule detail${reasons.length === 1 ? "" : "s"}</summary><ul>${reasons.map(reason => `<li>${escapeHtml(reason)}</li>`).join("")}</ul></details>` : ""}</div>
        ${status === "failed" ? `<button class="inline-action case-actions" type="button" data-remediation-scope="case" data-check-id="${escapeHtml(checkId)}" data-case-id="${escapeHtml(item.case_id)}">${actionLabel}</button>` : ""}
    </article>`;
}
function applyReportFilters() { if (window.currentReport) renderStages(window.currentReport); }

function remediationForCheck(checkId) {
    return [...(window.currentReport?.remediation || [])].reverse().find(item => item.check_id === checkId) || null;
}
function remediationCaseFor(checkId, caseId) {
    return (remediationForCheck(checkId)?.case_results || []).find(item => item.case_id === caseId) || null;
}
function failedCasesForCheck(checkId) {
    for (const stage of window.currentReport?.stages || []) {
        const check = (stage.checks || []).find(item => item.check_id === checkId);
        if (check) return (check.cases || []).filter(item => statusName(item.status) === "failed");
    }
    return [];
}

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
    const questions = remediation.questions || [];
    const limitations = remediation.limitations || [];
    const rules = remediation.applicable_rules || [];
    const model = remediation.model || {};
    const caseResults = remediation.case_results || [];
    const statusClass = remediation.status === "candidate_ready" ? "passed" : remediation.status === "unsupported" ? "failed" : "warning";
    document.getElementById("remediationContent").innerHTML = `<article class="remediation-result">
        <span class="pill ${statusClass}">${escapeHtml((remediation.status || "plan").replaceAll("_", " "))}</span>
        <h3>${escapeHtml(remediation.title || "Suggested fixes")}</h3>
        <p>${escapeHtml(remediation.summary || "")}</p>
        ${model.model ? `<p class="remediation-model">${escapeHtml(model.model)} · ${escapeHtml(String(model.input_tokens ?? "?"))} input / ${escapeHtml(String(model.output_tokens ?? "?"))} output tokens</p>` : ""}
        ${caseResults.length ? `<section><h4>Case coverage</h4><div class="remediation-case-grid">${caseResults.map(item => `<div class="remediation-case-result ${escapeHtml(item.status || "not_requested")}"><strong>${escapeHtml(item.name || "Case")}</strong><span>${escapeHtml((item.status || "not_requested").replaceAll("_", " "))}</span><p>${item.candidate_name ? `Candidate: ${escapeHtml(item.candidate_name)}` : item.question ? escapeHtml(item.question.prompt || "Developer context required") : item.limitation ? escapeHtml(item.limitation.message || "Current limitation") : "Candidate not generated yet."}</p>${item.status === "not_requested" ? `<button class="inline-action" type="button" data-remediation-scope="case" data-check-id="${escapeHtml(remediation.check_id)}" data-case-id="${escapeHtml(item.case_id)}">Generate remediation</button>` : ""}</div>`).join("")}</div></section>` : ""}
        ${suggestions.length ? `<section><h4>Candidates</h4>${suggestions.map(suggestion => `<div class="suggestion"><strong>${escapeHtml(suggestion.current_name || suggestion.title)} → ${escapeHtml(suggestion.candidate_name || "")}</strong><p>${escapeHtml(suggestion.description || "")}</p><p><strong>Confidence:</strong> ${escapeHtml(suggestion.confidence || "not recorded")} · <strong>Policy:</strong> ${escapeHtml((suggestion.policy_validation || "not checked").replaceAll("_", " "))}</p>${suggestion.actions?.length ? `<ol>${suggestion.actions.map(action => `<li>${escapeHtml(action)}</li>`).join("")}</ol>` : ""}${suggestion.verification ? `<p><strong>Verify:</strong> ${escapeHtml(suggestion.verification)}</p>` : ""}</div>`).join("")}</section>` : ""}
        ${questions.length ? `<form class="remediation-questions" onsubmit="submitRemediationContext(event)"><h4>Developer context required</h4>${questions.map(question => `<label class="remediation-question"><span>${escapeHtml(question.prompt)}</span><textarea name="${escapeHtml(question.question_id)}" rows="3" required placeholder="Add only the meaning or context needed to name this item."></textarea></label>`).join("")}<button class="btn primary" type="submit">Generate candidates</button></form>` : ""}
        ${limitations.length ? `<section><h4>Current limitations</h4><ul>${limitations.map(item => `<li><strong>${escapeHtml(item.name || "Case")}</strong> — ${escapeHtml(item.message || "Not supported in this prototype.")}</li>`).join("")}</ul></section>` : ""}
        ${rules.length ? `<details class="remediation-rules"><summary>Applicable policy rules (${rules.length})</summary><ul>${rules.map(rule => `<li><strong>${escapeHtml(rule.rule_id)}</strong> ${escapeHtml(rule.reason)}</li>`).join("")}</ul></details>` : ""}
        ${affected.length ? `<section><h4>Affected cases</h4><ul>${affected.map(item => `<li><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(item.location || "")}</span></li>`).join("")}</ul></section>` : ""}
    </article>`;
}
function upsertCurrentRemediation(remediation) {
    const items = window.currentReport.remediation || [];
    const index = items.findIndex(item => item.remediation_id === remediation.remediation_id);
    window.currentReport.remediation = index >= 0
        ? items.map((item, itemIndex) => itemIndex === index ? remediation : item)
        : [...items, remediation];
}
async function sendRemediation(payload, button = null) {
    document.getElementById("remediationContent").innerHTML = '<p class="empty-state">Preparing remediation plan…</p>';
    if (button) button.disabled = true;
    try {
        const response = await fetch(`/api/runs/${encodeURIComponent(window.currentRunId)}/remediations`, {
            method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(await response.text());
        const result = await response.json();
        window.currentRemediationRequest = {
            scope: payload.scope,
            check_id: payload.check_id,
            case_id: payload.case_id,
            remediation_id: result.remediation.remediation_id
        };
        upsertCurrentRemediation(result.remediation);
        renderRemediation(result.remediation);
        updateWorkspaceChrome(document.getElementById("buildPage").classList.contains("active") ? "build" : "report");
    } catch (error) {
        document.getElementById("remediationContent").innerHTML = `<p class="empty-state">${escapeHtml(String(error))}</p>`;
        console.error(error);
    } finally {
        if (button) button.disabled = false;
    }
}
async function requestRemediation(button) {
    if (!window.currentRunId) return;
    const payload = { scope: button.dataset.remediationScope, check_id: button.dataset.checkId };
    if (payload.scope === "case") payload.case_id = button.dataset.caseId;
    openRemediationDrawer();
    const existing = remediationForCheck(payload.check_id);
    const failedCases = failedCasesForCheck(payload.check_id);
    const selectedCases = payload.scope === "case"
        ? failedCases.filter(item => item.case_id === payload.case_id)
        : failedCases.filter(item => (remediationCaseFor(payload.check_id, item.case_id)?.status || "not_requested") === "not_requested");
    const selectedExisting = payload.scope === "case" ? remediationCaseFor(payload.check_id, payload.case_id) : null;
    if ((selectedExisting && selectedExisting.status !== "not_requested") || (!selectedCases.length && existing)) {
        window.currentRemediationRequest = { ...payload, remediation_id: existing.remediation_id };
        renderRemediation(existing);
        return;
    }
    renderRemediationRequestForm(payload, selectedCases, button);
}
function renderRemediationRequestForm(payload, cases, sourceButton) {
    window.currentRemediationRequest = payload;
    document.getElementById("remediationContent").innerHTML = `<form class="remediation-context-form" onsubmit="submitInitialRemediation(event)">
        <h3>${payload.scope === "check" ? "Generate missing remediations" : "Generate remediation"}</h3>
        <p>Add any context you already know. Leave a box empty when the current symbol contains enough meaning; the model can request a specific missing fact.</p>
        ${cases.map(item => `<label class="remediation-question"><span>${escapeHtml(item.name || "Case")}</span><small>${escapeHtml(item.location || "")}</small><textarea name="${escapeHtml(item.case_id)}" rows="3" placeholder="Purpose, usage, module, data type, size, unit, or other naming context (optional)."></textarea></label>`).join("")}
        <button class="btn primary" type="submit">Generate candidates</button>
    </form>`;
    window.currentRemediationSourceButton = sourceButton;
}
async function submitInitialRemediation(event) {
    event.preventDefault();
    if (!window.currentRemediationRequest) return;
    const form = event.currentTarget;
    const developerContext = Object.fromEntries(
        [...new FormData(form).entries()].filter(([, value]) => String(value).trim())
    );
    await sendRemediation({
        ...window.currentRemediationRequest,
        developer_context: developerContext
    }, form.querySelector('button[type="submit"]'));
    window.currentRemediationSourceButton = null;
}
async function submitRemediationContext(event) {
    event.preventDefault();
    if (!window.currentRemediationRequest) return;
    const form = event.currentTarget;
    const contextAnswers = Object.fromEntries(new FormData(form).entries());
    const button = form.querySelector('button[type="submit"]');
    await sendRemediation({
        ...window.currentRemediationRequest,
        context_answers: contextAnswers
    }, button);
}
function renderBuildLoading(status = {}) {
    window.currentBuildState = status.state || "queued";
    const output = [...(status.stdout || []), ...(status.stderr || [])].join("\n");
    document.getElementById("buildResult").innerHTML = `<div class="build-grid"><section class="glass panel build-live"><div class="build-live-status"><span id="buildState" class="pill warning">${escapeHtml(String(status.state || "queued").toUpperCase())}</span></div><h3>Build in progress</h3><p id="buildStateMessage">${escapeHtml(status.state === "queued" ? "Waiting for a build worker." : "The build is running. New output appears below as it is captured.")}</p><pre id="liveBuildOutput">${escapeHtml(output || "No output captured yet.")}</pre></section><section class="glass panel"><h3>Build settings</h3><p>Formatting: ${status.run_format ? "requested" : "disabled"}</p><p class="section-sub">Formatting is included with the build when the uploaded project provides <code>.clang-format</code> or a repository-local <code>review-build.json</code> wrapper.</p></section></div>`;
    updateWorkspaceChrome("build");
}
function updateLiveBuild(status) {
    window.currentBuildState = status.state || "running";
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
    updateWorkspaceChrome("build");
}
function renderBuildNotRun() {
    document.getElementById("buildResult").innerHTML = '<div class="glass panel build-empty"><span class="pill warning">NOT RUN</span><h3>No build result yet</h3><p>Run the repository build to attach output, diagnostics, and artifacts to this review run.</p><button class="btn success" type="button" onclick="triggerBuild()">Run build</button></div>';
}
function renderBuild(result) {
    const formatStep = result.format_step || { status: "skipped", message: "Formatting is not configured for this uploaded repository." };
    const buildStep = result.build_step || { status: result.status || "failed", message: "Build did not return a step result." };
    const diagnostics = result.important_diagnostics || [];
    const artifacts = result.artifact_manifest || [];
    const artifactReferences = result.artifact_references || [];
    const intelligence = result.intelligence_summary || {};
    const remediation = intelligence.remediation || {};
    window.currentBuildState = statusName(result.status || buildStep.status);
    const output = [...(result.stdout || []), ...(result.stderr || [])].join("\n");
    document.getElementById("buildResult").innerHTML = `
        <div class="build-config"><span><strong>Formatting:</strong> ${escapeHtml(formatStep.command || "not configured")}</span><span><strong>Build:</strong> ${escapeHtml(result.build_script || "cmake-build.bat")}</span></div>
        <div class="summary build-summary"><div class="metric ${pillClass(buildStep.status)}"><div class="value">${escapeHtml(String(buildStep.status || result.status || "unknown").toUpperCase())}</div><div class="label">Build</div></div><div class="metric ${pillClass(formatStep.status)}"><div class="value">${escapeHtml(String(formatStep.status || "skipped").toUpperCase())}</div><div class="label">Formatting</div></div><div class="metric total"><div class="value">${escapeHtml(String(result.return_code ?? "—"))}</div><div class="label">Return code</div></div></div>
        <div class="build-grid">
            <section class="glass panel"><h3>Build intelligence</h3><p><strong>Primary issue:</strong> ${escapeHtml(intelligence.primary_issue || intelligence.summary || buildStep.message || "Build result is available.")}</p>${intelligence.evidence?.length ? `<h4>Evidence</h4><ul>${intelligence.evidence.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}${(intelligence.next_actions || intelligence.suggestions)?.length ? `<h4>Next actions</h4><ol>${(intelligence.next_actions || intelligence.suggestions).map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ol>` : `<p class="section-sub">Next action: ${escapeHtml(intelligence.next_action || "Review the build output.")}</p>`}${remediation.summary ? `<h4>Model remediation</h4><p><strong>${escapeHtml(remediation.summary)}</strong></p>${remediation.root_cause ? `<p>${escapeHtml(remediation.root_cause)}</p>` : ""}${remediation.actions?.length ? `<ol>${remediation.actions.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ol>` : ""}${remediation.verification ? `<p class="section-sub"><strong>Verify:</strong> ${escapeHtml(remediation.verification)}</p>` : ""}${remediation.limitation ? `<p class="section-sub">${escapeHtml(remediation.limitation)}</p>` : ""}` : ""}</section>
            <section class="glass panel"><h3>Important diagnostics</h3>${diagnostics.length ? `<ul class="diagnostic-list">${diagnostics.map(line => `<li>${escapeHtml(line)}</li>`).join("")}</ul>` : '<p class="section-sub">No important diagnostics were selected.</p>'}</section>
            <section class="glass panel build-artifacts"><h3>Available artifacts</h3>${artifacts.length ? `<ul>${artifacts.map(artifact => `<li><strong>${escapeHtml(artifact.relative_path)}</strong><span>${escapeHtml(artifact.type)} · ${formatBytes(artifact.size_bytes)} · ${escapeHtml(formatDate(artifact.modified_at))}</span></li>`).join("")}</ul>` : '<p class="section-sub">No artifacts were produced by this build.</p>'}${artifactReferences.length ? `<h4>Reference artifacts from successful run ${escapeHtml(artifactReferences[0].source_run_id || "")}</h4><ul>${artifactReferences.map(artifact => `<li><strong>${escapeHtml(artifact.relative_path)}</strong><span>${escapeHtml(artifact.type)} · ${formatBytes(artifact.size_bytes)} · retained reference only</span></li>`).join("")}</ul>` : ""}</section>
            <section class="glass panel build-output"><h3>Raw output</h3><pre>${escapeHtml(output || "No output was captured.")}</pre></section>
        </div>`;
    updateWorkspaceChrome("build");
}
async function triggerBuild() {
    if (!window.currentRunId) { alert("Run review first."); return; }
    const runFormat = true;
    showBuild();
    renderBuildLoading({ state: "queued", run_format: runFormat });
    await new Promise(resolve => requestAnimationFrame(resolve));
    try {
        const query = new URLSearchParams({ background: "true", run_format: String(runFormat) });
        const response = await fetch(`/api/runs/${encodeURIComponent(window.currentRunId)}/build?${query}`, { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        await pollBuildStatus();
    } catch (error) {
        window.currentBuildState = "failed";
        document.getElementById("buildResult").innerHTML = `<div class="glass panel"><span class="pill failed">Failed</span><h3>Build could not be started</h3><p>${escapeHtml(String(error))}</p></div>`;
        updateWorkspaceChrome("build");
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
            renderBuildWorkerFailure(status);
            return;
        }
        updateLiveBuild(status);
        await new Promise(resolve => setTimeout(resolve, 750));
    }
}
function renderBuildWorkerFailure(status) {
    const output = [...(status.stdout || []), ...(status.stderr || [])].join("\n");
    const result = {
        status: "failed",
        return_code: status.return_code ?? 1,
        build_step: { status: "failed", message: status.error || "Build worker failed before producing a result." },
        important_diagnostics: status.stderr || [],
        stdout: status.stdout || [],
        stderr: status.stderr || [],
        intelligence_summary: { primary_issue: status.error || "Build worker failed before producing a result.", remediation: { status: "unsupported", summary: "Model build remediation was not reached.", limitation: "The worker failed before a normalized build result was produced." } }
    };
    if (window.currentReport) window.currentReport.build_result = result;
    renderBuild(result);
    if (!output) console.error(status.error || "Build worker failed before producing a result.");
}

document.getElementById("caseSearch").addEventListener("input", applyReportFilters);
document.getElementById("statusFilter").addEventListener("change", () => { updateFacetSummary("statusFilter"); applyReportFilters(); });
document.getElementById("checkFilter").addEventListener("change", () => { updateFacetSummary("checkFilter"); applyReportFilters(); });
document.getElementById("stageFilter").addEventListener("change", () => {
    updateFacetSummary("stageFilter");
    if (window.currentReport) { refreshCheckFilter(window.currentReport); renderStages(window.currentReport); }
});
document.getElementById("stages").addEventListener("click", event => {
    const graphs = event.target.closest('[data-open-run-graphs]');
    if (graphs) { if (typeof openIntelligenceRun === 'function') openIntelligenceRun(graphs.dataset.module,graphs.dataset.openRunGraphs); return; }
    const button = event.target.closest("[data-remediation-scope]");
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();
    requestRemediation(button);
});
document.getElementById("drawerBackdrop").addEventListener("click", closeRemediationDrawer);
document.addEventListener("click", event => {
    document.querySelectorAll(".facet-dropdown[open]").forEach(dropdown => {
        if (!dropdown.contains(event.target)) dropdown.removeAttribute("open");
    });
});
loadReviewProfile();
