window.managerPortfolio = null;
window.managerModule = null;
window.managerTab = "portfolio";
window.managerSelection = new Set();

async function showManager(tab = window.managerTab || "portfolio") {
    showPage("managerPage");
    switchManagerTab(tab, false);
    if (!window.managerPortfolio) await loadManagerPortfolio();
}

function switchManagerTab(tab, render = true) {
    window.managerTab = tab;
    document.getElementById("managerActionNotice").hidden = true;
    document.querySelectorAll("[data-manager-tab]").forEach(button => {
        const active = button.dataset.managerTab === tab;
        button.classList.toggle("active", active);
        button.setAttribute("aria-selected", String(active));
    });
    if (render && window.managerPortfolio) renderManagerTab();
}

async function loadManagerPortfolio() {
    const content = document.getElementById("managerContent");
    content.innerHTML = '<div class="manager-empty">Loading persisted module runs…</div>';
    try {
        const response = await fetch("/api/manager/portfolio");
        if (!response.ok) throw new Error(await response.text());
        window.managerPortfolio = await response.json();
        renderManagerTab();
    } catch (error) {
        content.innerHTML = '<div class="manager-empty">Manager data could not be loaded.<br>' + escapeHtml(String(error)) + "</div>";
        console.error(error);
    }
}

function renderManagerTab() {
    const renderers = {
        portfolio: renderManagerPortfolio,
        exceptions: renderManagerExceptions,
        ownership: renderManagerOwnership,
        audit: renderManagerAudit
    };
    (renderers[window.managerTab] || renderManagerPortfolio)();
}

function managerMetric(value, label, cls = "") {
    return '<article class="manager-metric ' + cls + '"><strong>' + escapeHtml(String(value ?? 0)) +
        "</strong><span>" + escapeHtml(label) + "</span></article>";
}

function managerBuildClass(status) {
    if (status === "passed") return "passed";
    if (status === "failed") return "failed";
    return "warning";
}

function renderManagerPortfolio() {
    const portfolio = window.managerPortfolio;
    const totals = portfolio.aggregates || {};
    const modules = portfolio.modules || [];
    const rows = modules.map(module => '<tr><td><strong>' + escapeHtml(module.module_name) +
        "</strong><small>" + escapeHtml(module.profile?.name || "Profile not recorded") + "</small></td><td>" +
        escapeHtml(module.run_id) + "<small>" + escapeHtml(formatDate(module.generated_at)) + "</small></td><td>" +
        '<span class="pill ' + (module.summary.failed ? "failed" : "passed") + '">' + (module.summary.failed || 0) +
        " failed</span><small>" + (module.summary.skipped || 0) + " skipped · " + (module.summary.passed || 0) +
        ' passed</small></td><td><span class="pill ' + managerBuildClass(module.build_status) + '">' +
        escapeHtml(module.build_status.replaceAll("_", " ")) + "</span></td><td>" + (module.artifact_count || 0) +
        "</td><td>" + module.run_count + ' runs</td><td><button class="inline-action" type="button" data-manager-module="' +
        escapeHtml(module.module_name) + '">Peek into module</button></td></tr>').join("");
    document.getElementById("managerContent").innerHTML =
        '<section class="manager-summary">' +
        managerMetric(totals.modules, "Modules") + managerMetric(totals.latest_failed, "Failed", "failed") +
        managerMetric(totals.latest_skipped, "Skipped", "warning") + managerMetric(totals.latest_passed, "Passed", "passed") +
        managerMetric(totals.builds_failed, "Builds failed", "failed") + managerMetric(totals.artifacts, "Artifacts") +
        '</section><section class="manager-panel"><div class="manager-panel-heading"><div><h2>Latest run by module</h2>' +
        "<p>Portfolio totals use only the newest persisted report for each unique module.</p></div>" +
        '<span class="pill passed">Read only</span></div>' +
        (rows ? '<div class="manager-table-wrap"><table class="manager-table"><thead><tr><th>Module</th><th>Latest run</th>' +
        "<th>Review</th><th>Build</th><th>Artifacts</th><th>History</th><th></th></tr></thead><tbody>" + rows +
        '</tbody></table></div>' : '<div class="manager-empty">No persisted reports are available.</div>') +
        "</section>" + (window.managerModule ? renderManagerModuleDetail(window.managerModule) : "") +
        renderManagerInsights(portfolio.insights || []);
}

async function openManagerModule(moduleName) {
    showManagerNotice("Loading " + moduleName + " run history…");
    try {
        const response = await fetch("/api/manager/modules/" + encodeURIComponent(moduleName));
        if (!response.ok) throw new Error(await response.text());
        window.managerModule = await response.json();
        document.getElementById("managerActionNotice").hidden = true;
        renderManagerPortfolio();
        document.querySelector(".manager-detail")?.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        showManagerNotice("Module history could not be loaded: " + String(error));
    }
}

function renderManagerModuleDetail(module) {
    const latest = module.latest_run;
    const defaults = module.comparison_defaults || {};
    const options = selected => (module.runs || []).map(run => '<option value="' + escapeHtml(run.run_id) + '"' +
        (run.run_id === selected ? " selected" : "") + ">" + escapeHtml(run.run_id) + " · " +
        escapeHtml(formatDate(run.generated_at)) + "</option>").join("");
    const compare = defaults.available ? '<div class="manager-compare-controls"><div class="manager-control">' +
        '<label for="managerBaseRun">Base run</label><select id="managerBaseRun">' + options(defaults.base_run_id) +
        '</select></div><div class="manager-control"><label for="managerTargetRun">Target run</label>' +
        '<select id="managerTargetRun">' + options(defaults.target_run_id) + '</select></div><button class="btn primary" ' +
        'type="button" data-manager-compare="' + escapeHtml(module.module_name) +
        '">Compare runs</button></div><div id="managerCompare" class="manager-compare-result"></div>' :
        '<p class="manager-notice">A second run is required before comparison is available.</p>';
    return '<section class="manager-panel manager-detail"><div class="manager-panel-heading"><div>' +
        '<span class="manager-kicker">Module drill-down</span><h2>' + escapeHtml(module.module_name) + "</h2><p>" +
        module.run_count + ' persisted runs. Compare any two without rerunning checks.</p></div><span class="pill ' +
        (latest.summary.failed ? "failed" : "passed") + '">' + (latest.summary.failed ? "Needs attention" : "Passed") +
        '</span></div><div class="manager-detail-grid"><div class="manager-detail-stat"><b>' +
        (latest.summary.failed || 0) + '</b><span>Failed</span></div><div class="manager-detail-stat"><b>' +
        (latest.summary.skipped || 0) + '</b><span>Skipped</span></div><div class="manager-detail-stat"><b>' +
        (latest.summary.passed || 0) + '</b><span>Passed</span></div><div class="manager-detail-stat"><b>' +
        escapeHtml(latest.build_status) + "</b><span>Build</span></div></div>" + compare + "</section>";
}

async function runManagerComparison(moduleName) {
    const base = document.getElementById("managerBaseRun")?.value;
    const target = document.getElementById("managerTargetRun")?.value;
    const output = document.getElementById("managerCompare");
    if (!base || !target || !output) return;
    if (base === target) {
        output.innerHTML = '<div class="manager-notice">Choose two different runs.</div>';
        return;
    }
    output.innerHTML = '<div class="manager-notice">Comparing persisted summaries…</div>';
    try {
        const query = new URLSearchParams({ base_run_id: base, target_run_id: target });
        const response = await fetch("/api/manager/modules/" + encodeURIComponent(moduleName) + "/compare?" + query);
        if (!response.ok) throw new Error(await response.text());
        output.innerHTML = renderManagerComparison(await response.json());
    } catch (error) {
        output.innerHTML = '<div class="manager-notice">Comparison failed: ' + escapeHtml(String(error)) + "</div>";
    }
}

function renderManagerComparison(comparison) {
    const delta = comparison.summary_delta || {};
    const failures = comparison.failures || {};
    const signed = value => (value > 0 ? "+" : "") + (value || 0);
    const cards = ["failed", "skipped", "passed", "total"].map(name => {
        const value = delta[name] || 0;
        const cls = name === "failed" ? (value > 0 ? "bad" : value < 0 ? "good" : "") : (value > 0 ? "good" : "");
        return '<div class="delta ' + cls + '"><b>' + signed(value) + "</b>" + escapeHtml(name) + "</div>";
    }).join("");
    return '<section class="insight-card"><header><strong>Target minus base</strong><span class="preview-label">' +
        escapeHtml(comparison.base.run_id) + " → " + escapeHtml(comparison.target.run_id) +
        '</span></header><div class="delta-grid">' + cards + "</div><p><strong>" + (failures.new || []).length +
        "</strong> new failures · <strong>" + (failures.resolved || []).length +
        "</strong> resolved · <strong>" + (failures.unchanged_count || 0) + "</strong> unchanged.</p><p>" +
        escapeHtml(comparison.interpretation) + "</p></section>";
}

function renderManagerInsights(insights) {
    if (!insights.length) return "";
    const cards = insights.map(insight => '<article class="insight-card"><header><strong>' +
        escapeHtml(insight.title) + '</strong><span class="preview-label">' + escapeHtml(insight.status) +
        "</span></header><p>" + escapeHtml(insight.summary) + "</p>" +
        (insight.actions?.length ? "<p><strong>Possible next step:</strong> " +
        escapeHtml(insight.actions.join(" · ")) + "</p>" : "") + "</article>").join("");
    return '<section class="manager-panel"><div class="manager-panel-heading"><div><h2>Insights</h2>' +
        "<p>One wrapper for deterministic remediation and future governed assisted analysis.</p></div>" +
        '<span class="preview-label">Placeholder source</span></div><div class="insight-grid">' + cards + "</div></section>";
}

function managerFailureKey(item) {
    return [item.run_id, item.case_id || item.case_index, item.check_id].join(":");
}

function renderManagerExceptions() {
    const queue = window.managerPortfolio.exception_queue || { groups: [], items: [] };
    const items = (queue.items || []).slice(0, 120);
    const groups = (queue.groups || []).map(group => '<label class="exception-group"><input type="checkbox" ' +
        'data-manager-group-select="' + escapeHtml(group.group_id) + '"><span>' + escapeHtml(group.module_name) +
        " · " + escapeHtml(group.check_title) + " (" + group.failed + ")</span></label>").join("");
    const cases = items.map(item => {
        const key = managerFailureKey(item);
        const group = [item.module_name, item.stage_id, item.check_id].join(":");
        return '<label class="exception-item"><input type="checkbox" data-manager-case-select="' + escapeHtml(key) +
            '" data-exception-group="' + escapeHtml(group) + '"' + (window.managerSelection.has(key) ? " checked" : "") +
            '><span><strong>' + escapeHtml(item.name || "Unnamed failure") + "</strong><code>" +
            escapeHtml(item.module_name) + " · " + escapeHtml(item.check_title) + " · " +
            escapeHtml(item.location || "") + "</code><p>" + escapeHtml((item.reasons || []).join(" ")) +
            '</p></span><span class="pill failed">Failed</span></label>';
    }).join("");
    document.getElementById("managerContent").innerHTML = '<section class="manager-panel">' +
        '<div class="manager-panel-heading"><div><span class="manager-kicker">Workflow preview</span>' +
        "<h2>Exception queue</h2><p>Select failed cases individually or by check group, choose an owner, and preview " +
        'ticket creation. Nothing is persisted.</p></div><span class="preview-label">No workflow writes</span></div>' +
        '<div class="exception-toolbar"><div class="manager-control"><label for="managerOwner">Owner</label>' +
        '<select id="managerOwner"><option>Unassigned</option><option>Firmware team</option><option>Module owner</option>' +
        '<option>Quality lead</option></select></div><button class="btn" type="button" data-manager-preview-action="assignment">' +
        'Preview assignment</button><button class="btn primary" type="button" data-manager-preview-action="ticket">' +
        'Create ticket (preview)</button></div><div class="exception-groups">' + groups +
        '</div><div class="exception-list">' + (cases || '<div class="manager-empty">No failed cases in the latest module runs.</div>') +
        "</div>" + (queue.total_failed_cases > items.length ? '<p class="section-sub">Showing the first ' + items.length +
        " of " + queue.total_failed_cases + " failed cases. Group totals include the complete latest-run portfolio.</p>" : "") +
        "</section>";
}

function renderManagerOwnership() {
    const rows = (window.managerPortfolio.ownership_preview || []).map(row => "<tr><td><strong>" +
        escapeHtml(row.module_name) + "</strong></td><td>" + escapeHtml(row.owner) +
        '</td><td><span class="preview-label">' + escapeHtml(row.status) +
        '</span></td><td><button class="btn manager-placeholder-button" type="button" data-manager-preview-action="owner">' +
        'Assign owner (preview)</button> <button class="btn manager-placeholder-button" type="button" ' +
        'data-manager-preview-action="ticket">Create ticket (preview)</button></td></tr>').join("");
    document.getElementById("managerContent").innerHTML = '<section class="manager-panel">' +
        '<div class="manager-panel-heading"><div><span class="manager-kicker">Workflow preview</span>' +
        "<h2>Tickets and ownership</h2><p>Static module-owner rows show the intended workflow without claiming a ticket " +
        'or directory integration.</p></div><span class="preview-label">Not persisted</span></div>' +
        '<div class="manager-table-wrap"><table class="manager-table"><thead><tr><th>Module</th><th>Owner</th>' +
        "<th>Status</th><th>Actions</th></tr></thead><tbody>" + rows + "</tbody></table></div></section>" +
        renderManagerInsights(window.managerPortfolio.insights || []);
}

function renderManagerAudit() {
    const workflow = window.managerPortfolio.workflow_preview || {};
    const approvals = workflow.approvals || {};
    const delivery = workflow.delivery || {};
    const modules = (window.managerPortfolio.modules || []).map(module => "<tr><td><strong>" +
        escapeHtml(module.module_name) + "</strong></td><td>" + escapeHtml(module.run_id) + "</td><td>" +
        escapeHtml(module.build_status) + "</td><td>" + module.remediation_count + "</td><td>" +
        module.artifact_count + "</td></tr>").join("");
    document.getElementById("managerContent").innerHTML = '<section class="manager-summary">' +
        managerMetric(approvals.pending, "Pending approvals", "warning") +
        managerMetric(approvals.historical, "Historical approvals") +
        managerMetric((window.managerPortfolio.aggregates || {}).remediations, "Remediations") +
        managerMetric((window.managerPortfolio.aggregates || {}).artifacts, "Artifacts") +
        '</section><div class="manager-grid"><section class="manager-panel"><div class="manager-panel-heading">' +
        "<div><h2>Audit and delivery</h2><p>Run metadata and delivery evidence come from each persisted report.</p></div>" +
        '<span class="pill passed">Derived</span></div><div class="manager-table-wrap"><table class="manager-table">' +
        "<thead><tr><th>Module</th><th>Run</th><th>Build</th><th>Remediation</th><th>Artifacts</th></tr></thead><tbody>" +
        modules + '</tbody></table></div></section><section class="manager-panel"><div class="manager-panel-heading">' +
        "<div><h2>Future delivery status</h2><p>These values are placeholders, not connected system states.</p></div>" +
        '<span class="preview-label">Workflow preview</span></div><div class="manager-detail-grid">' +
        '<div class="manager-detail-stat"><b>' + escapeHtml(delivery.pull_request || "not connected") +
        '</b><span>Pull request</span></div><div class="manager-detail-stat"><b>' +
        escapeHtml(delivery.continuous_integration || "not connected") +
        "</b><span>CI</span></div></div><p>" + escapeHtml(approvals.label || "") + "</p><p>" +
        escapeHtml(delivery.label || "") + "</p></section></div>";
}

function showManagerNotice(message) {
    const notice = document.getElementById("managerActionNotice");
    notice.textContent = message;
    notice.hidden = false;
}

function previewManagerAction(action) {
    const owner = document.getElementById("managerOwner")?.value || "Unassigned";
    const selected = window.managerSelection.size;
    if (action === "ticket") {
        showManagerNotice("Preview only: a ticket would be prepared for " + selected + " selected failure" +
            (selected === 1 ? "" : "s") + " and assigned to " + owner + ". No ticket was created.");
    } else if (action === "assignment") {
        showManagerNotice("Preview only: " + selected + " selected failure" + (selected === 1 ? "" : "s") +
            " would be assigned to " + owner + ". No owner was persisted.");
    } else {
        showManagerNotice("Preview only: owner changes are not persisted or sent to another system.");
    }
}

document.getElementById("managerContent").addEventListener("click", event => {
    const moduleButton = event.target.closest("[data-manager-module]");
    const compareButton = event.target.closest("[data-manager-compare]");
    const previewButton = event.target.closest("[data-manager-preview-action]");
    if (moduleButton) openManagerModule(moduleButton.dataset.managerModule);
    else if (compareButton) runManagerComparison(compareButton.dataset.managerCompare);
    else if (previewButton) previewManagerAction(previewButton.dataset.managerPreviewAction);
});

document.getElementById("managerContent").addEventListener("change", event => {
    if (event.target.matches("[data-manager-case-select]")) {
        if (event.target.checked) window.managerSelection.add(event.target.dataset.managerCaseSelect);
        else window.managerSelection.delete(event.target.dataset.managerCaseSelect);
    }
    if (event.target.matches("[data-manager-group-select]")) {
        const groupId = event.target.dataset.managerGroupSelect;
        document.querySelectorAll("[data-exception-group]").forEach(input => {
            if (input.dataset.exceptionGroup !== groupId) return;
            input.checked = event.target.checked;
            if (input.checked) window.managerSelection.add(input.dataset.managerCaseSelect);
            else window.managerSelection.delete(input.dataset.managerCaseSelect);
        });
    }
});
