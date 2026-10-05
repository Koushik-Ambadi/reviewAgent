

const stageLogs = [

    "Starting review...",

    "Preparing your upload...",

    "Reviewing repository contents...",

    "Applying selected review profile...",

    "Collecting review results...",

    "Preparing report sections...",

    "Checking report consistency...",

    "Reviewing repository organization...",

    "Checking required project items...",

    "Applying naming guidance...",

    "Reviewing source items...",

    "Checking project conventions...",

    "Reviewing declared values...",

    "Checking related project files...",

    "Organizing review findings...",

    "Preparing your report..."
];

let activeInterval = null;

/* ========================================================= */
/* PAGE NAV */
/* ========================================================= */

function showPage(id){

    document
        .querySelectorAll(".page")
        .forEach(page => {
            page.classList.remove("active");
        });

    requestAnimationFrame(() => {
        document
            .getElementById(id)
            .classList.add("active");
    });
}

function showIntro(){
    showPage("introPage");
}

function showSetup(){
    showPage("setupPage");
}

function showReport(){
    showPage("reportPage");
}

function showBuild(){
    showPage("buildPage");
}
/* ========================================================= */
/* LOGGING */
/* ========================================================= */

function setProgress(percent, text){

    document
        .getElementById("progressBar")
        .style.width = percent + "%";

    document
        .getElementById("progressText")
        .textContent = percent + "%";

    document
        .getElementById("statusText")
        .textContent = text;
}

function pushLog(text){

    const box = document.getElementById("logs");

    const row = document.createElement("div");

    row.className = "log";

    row.textContent = "→ " + text;

    box.appendChild(row);

    box.scrollTop = box.scrollHeight;
}

function clearLogs(){
    document.getElementById("logs").innerHTML = "";
}

async function startFakeProgress(){

    clearLogs();

    setProgress(3, "Initializing");

    const timings = [
        1200,
        1000,
        1300,
        1500,
        1200,
        2200,
        1800,
        1400,
        1600,
        1800,
        1500,
        1600,
        1400,
        1300,
        1600,
        1800
    ];

    for(let i = 0; i < stageLogs.length; i++){

        pushLog(stageLogs[i]);

        const progress =
            Math.min(
                92,
                8 + (i * 5.5)
            );

        setProgress(
            progress,
            stageLogs[i]
        );

        await new Promise(resolve =>
            setTimeout(
                resolve,
                timings[i] || 1200
            )
        );
    }
}

/* ========================================================= */
/* PIPELINE */
/* ========================================================= */

async function runPipeline(){

    const file =
        document
            .getElementById("zipFile")
            .files[0];

    if(!file){

        alert(
            "Please select a ZIP file."
        );

        return;
    }

    showSetup();

    startFakeProgress();

    try{

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );

        const response =
            await fetch(
                "/api/review",
                {
                    method:"POST",
                    body:formData
                }
            );

        if(!response.ok){

            throw new Error(
                await response.text()
            );
        }

        const responseData = await response.json();

        if(!responseData.run_id || !responseData.report){
            throw new Error("Invalid review response");
        }

window.currentRunId =
    responseData.run_id;

renderReport(
    responseData.report
);

showReport();

    }
    catch(error){

        setProgress(
            100,
            "Failed"
        );

        pushLog("The review could not be completed. Please try again.");
    }
}
/* ========================================================= */
/* REPORT */
/* ========================================================= */

window.currentReport = null;

function escapeHtml(value){
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
    })[character]);
}

function reportCases(report){
    return (report.stages || []).flatMap(stage =>
        (stage.checks || []).flatMap(check =>
            (check.cases || []).map(item => ({stage, check, item}))
        )
    );
}

function statusName(status){
    const normalized = String(status || "").toUpperCase();
    if(normalized === "SUCCESS" || normalized === "PASSED") return "success";
    if(normalized === "SKIPPED" || normalized === "EXCEPTION") return "skipped";
    return "failed";
}

function renderReport(report){
    window.currentReport = report;
    renderMetadata(report);
    renderSummary(report);
    populateReportFilters(report);
    renderStages(report);
}

function renderMetadata(report){
    const metadata = report.metadata || {};
    const values = [
        ["Run ID", report.run_id || "—"],
        ["Module", metadata.module_name || "—"],
        ["Policy", metadata.policy_name || "—"],
        ["Policy version", report.policy_version || "—"],
        ["Report version", report.report_version || "—"],
        ["Generated", metadata.generated_at || "—"]
    ];
    document.getElementById("reportMetadata").innerHTML = `
        <h2>Review Report</h2>
        <div class="meta-grid">${values.map(([label, value]) => `
            <div class="meta-value"><span class="meta-label">${escapeHtml(label)}</span>${escapeHtml(value)}</div>
        `).join("")}</div>`;
}

function renderSummary(report){
    const counts = {failed:0, skipped:0, success:0};
    reportCases(report).forEach(({item}) => counts[statusName(item.status)]++);
    const cards = [
        {label:"Failed", value:counts.failed, cls:"failed"},
        {label:"Skipped", value:counts.skipped, cls:"warning"},
        {label:"Passed", value:counts.success, cls:"success"},
        {label:"Total", value:counts.failed + counts.skipped + counts.success, cls:"total"}
    ];
    document.getElementById("summaryCards").innerHTML = cards.map(card => `
        <div class="metric ${card.cls}"><div class="value">${card.value}</div><div class="label">${card.label}</div></div>
    `).join("");
}

function populateReportFilters(report){
    const stageSelect = document.getElementById("stageFilter");
    const checkSelect = document.getElementById("checkFilter");
    stageSelect.innerHTML = '<option value="all">All stages</option>' +
        (report.stages || []).map(stage => `<option value="${escapeHtml(stage.stage_id)}">${escapeHtml(stage.title)}</option>`).join("");
    refreshCheckFilter(report);
}

function refreshCheckFilter(report){
    const stageId = document.getElementById("stageFilter").value;
    const checks = (report.stages || [])
        .filter(stage => stageId === "all" || stage.stage_id === stageId)
        .flatMap(stage => stage.checks || []);
    document.getElementById("checkFilter").innerHTML = '<option value="all">All checks</option>' +
        checks.map(check => `<option value="${escapeHtml(check.check_id)}">${escapeHtml(check.title)}</option>`).join("");
}

function renderStages(report){
    const query = document.getElementById("caseSearch").value.trim().toLowerCase();
    const wantedStatus = document.getElementById("statusFilter").value;
    const wantedStage = document.getElementById("stageFilter").value;
    const wantedCheck = document.getElementById("checkFilter").value;
    const stages = (report.stages || []).filter(stage => wantedStage === "all" || stage.stage_id === wantedStage);
    const cards = stages.map(stage => {
        const checks = (stage.checks || []).filter(check => wantedCheck === "all" || check.check_id === wantedCheck);
        const renderedChecks = checks.map(check => {
            const cases = (check.cases || []).filter(item => {
                const status = statusName(item.status);
                const haystack = [item.name, item.location, check.title, stage.title, ...(item.reasons || [])].join(" ").toLowerCase();
                return (wantedStatus === "all" || status === wantedStatus) && (!query || haystack.includes(query));
            });
            if(!cases.length && (query || wantedStatus !== "all")) return "";
            const summary = check.summary || {};
            return `<details class="check-card" data-check-id="${escapeHtml(check.check_id)}" open>
                <summary class="check-heading"><span><strong>${escapeHtml(check.title)}</strong><div class="section-sub">${summary.failed || 0} failed · ${summary.skipped || 0} skipped · ${summary.passed || 0} passed</div></span><span class="pill ${summary.failed ? "failed" : "passed"}">${summary.failed ? "Failed" : "Completed"}</span></summary>
                <div class="check-content">${cases.length ? cases.map(renderCase).join("") : '<div class="case-row success">No cases match the current filters.</div>'}</div>
            </details>`;
        }).filter(Boolean).join("");
        if(!renderedChecks && (query || wantedStatus !== "all")) return "";
        const summary = stage.summary || {};
        return `<section class="stage-card" data-stage-id="${escapeHtml(stage.stage_id)}"><div class="stage-heading"><div><h2>${escapeHtml(stage.title)}</h2><div class="section-sub">${summary.failed || 0} failed · ${summary.skipped || 0} skipped · ${summary.passed || 0} passed</div></div><span class="pill ${summary.failed ? "failed" : "passed"}">${summary.failed ? "Failed" : "Completed"}</span></div><div class="check-list">${renderedChecks || '<div class="case-row success">No checks in this stage.</div>'}</div></section>`;
    }).filter(Boolean);
    document.getElementById("stages").innerHTML = cards.join("") || '<div class="empty-state">No results match the current filters.</div>';
}

function renderCase(item){
    const status = statusName(item.status);
    const reasons = item.reasons || [];
    return `<article class="case-row ${status}" data-case-id="${escapeHtml(item.case_id)}">
        <strong>${escapeHtml(item.name || "Unnamed case")}</strong><span class="pill ${status === "success" ? "passed" : status === "skipped" ? "warning" : "failed"}">${escapeHtml(item.status)}</span>
        <div class="case-location">${escapeHtml(item.location || "")}</div>
        ${reasons.length ? `<ul class="case-reasons">${reasons.map(reason => `<li>${escapeHtml(reason)}</li>`).join("")}</ul>` : ""}
    </article>`;
}

function applyReportFilters(){
    if(window.currentReport) renderStages(window.currentReport);
}

document.getElementById("caseSearch").addEventListener("input", applyReportFilters);
document.getElementById("statusFilter").addEventListener("change", applyReportFilters);
document.getElementById("checkFilter").addEventListener("change", applyReportFilters);
document.getElementById("stageFilter").addEventListener("change", () => {
    if(window.currentReport){
        refreshCheckFilter(window.currentReport);
        renderStages(window.currentReport);
    }
});
async function triggerBuild(){

    if(!window.currentRunId){

        alert(
            "Run review first."
        );

        return;
    }

    showBuild();

    document
        .getElementById(
            "buildStatus"
        )
        .textContent =
            "Build Running...";

    document
        .getElementById(
            "buildOutput"
        )
        .innerHTML =
            "Starting build...\n";

    try{

        const response =
            await fetch(
                `/api/runs/${window.currentRunId}/build`,
                {
                    method:"POST"
                }
            );

        const result =
            await response.json();

        const stdout =
            result.stdout || [];

        const stderr =
            result.stderr || [];

        const output = [

            "RETURN CODE: "
            + result.return_code,

            "",

            ...stdout,

            "",

            "================",

            "STDERR",

            "================",

            "",

            ...stderr

        ].join("\n");

        document
            .getElementById(
                "buildOutput"
            )
            .textContent =
                output;

        document
            .getElementById(
                "buildStatus"
            )
            .textContent =
                result.return_code === 0
                ? "Build Success"
                : "Build Failed";

    }
    catch(error){

        document
            .getElementById(
                "buildStatus"
            )
            .textContent =
                "Build Failed";

        document
            .getElementById(
                "buildOutput"
            )
            .textContent =
                String(error);

        console.error(error);
    }
}
