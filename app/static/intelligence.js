/* Guided, read-only exploration. All source-derived text is escaped. */
const intelligence = {catalog: null, selected: new Set(), modules: new Set(), runs: {}, visible: new Set(), result: null,
    epoch: 0, contextEpoch: 0, zoom: 1, controller: null};
const iq = id => document.getElementById(id);
const ie = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const relationWords = {calls:'calls', reads:'reads from', writes:'updates', includes:'includes',
    references:'refers to', resolves_to:'implemented by', control_flow:'can continue to',
    def_use:'supplies an operand to', memory_flow:'may supply a saved value to', contains:'contains', same_tokens:'has identical tokens to'};
const relationLabel = edge => edge.display_relation || relationWords[edge.kind] || edge.kind;
const edgeLabel = edge => edge.kind === 'control_flow' ?
    ({successor:'then',true:'if true',false:'if false'}[edge.attributes?.label] || edge.attributes?.label || relationLabel(edge)) :
    edge.attributes?.label || relationLabel(edge);

function flowTitle(node) {
    const a = node.attributes || {};
    if (node.kind === 'basic_block') return a.entry ? 'Start' : a.exit ? 'Exit' : `Step ${a.order + 1}: ${node.name}`;
    if (node.kind !== 'instruction') return node.name;
    const operations = {1:'Return',2:'Choose next step',3:'Choose a case',26:'Reserve local storage',27:'Read a value',28:'Save a value',
        29:'Locate a field or item',44:'Combine branch results',45:'Call an operation',8:'Add',10:'Subtract',12:'Multiply',
        30:'Narrow a number',31:'Extend a number',32:'Extend a signed number',34:'Convert to decimal',42:'Compare values',43:'Compare decimals'};
    return `${operations[a.opcode] || 'Transform a value'}${node.location?.line ? ` · line ${node.location.line}` : ''}`;
}

function layoutIntelligence(nodes, edges) {
    // Shortest levels from entries; disconnected/cyclic components remain finite.
    const byId = new Map(nodes.map(n => [n.id, n]));
    const outgoing = new Map(nodes.map(n => [n.id, new Set()]));
    const incoming = new Map(nodes.map(n => [n.id, 0]));
    edges.forEach(e => {if (byId.has(e.source) && byId.has(e.target) && e.source !== e.target && !outgoing.get(e.source).has(e.target)) {
        outgoing.get(e.source).add(e.target); incoming.set(e.target, incoming.get(e.target)+1);
    }});
    const levels = new Map();
    function visit(root) {
        if (levels.has(root)) return;
        levels.set(root, 0); const queue = [root];
        for (let i=0; i<queue.length; i++) for (const target of outgoing.get(queue[i])) if (!levels.has(target)) {
            levels.set(target, Math.min(8, levels.get(queue[i])+1)); queue.push(target);
        }
    }
    nodes.filter(n => incoming.get(n.id) === 0 || n.attributes?.entry).forEach(n => visit(n.id));
    nodes.forEach(n => visit(n.id));
    const rows = new Map();
    return nodes.map(n => {const level=levels.get(n.id), row=rows.get(level)||0; rows.set(level,row+1);
        return {...n,x:40+level*290,y:45+row*125};});
}

async function openIntelligence() {
    if (!iq('intelligenceWorkspace')) return;
    if (!intelligence.catalog) await refreshIntelligence();
}

async function openIntelligenceRun(module,runId) {
    await showGraphs();
    await refreshIntelligence({...intelligence.runs,[module]:runId},new Set([module]));
}

async function refreshIntelligence(runs=null, preserveModules=null) {
    iq('iqStatus').textContent = 'Reading available module evidence…';
    try {
        const response = await fetch('/api/intelligence/catalog',runs ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({runs})} : {});
        if (!response.ok) throw new Error(`Could not load evidence (${response.status})`);
        intelligence.catalog = await response.json();
        intelligence.modules = preserveModules || new Set(intelligence.catalog.modules.map(m => m.module_name));
        intelligence.runs = Object.fromEntries(intelligence.catalog.modules.map(m=>[m.module_name,m.run_id]));
        intelligence.result=null;
        intelligence.selected.clear();
        iq('iqMode').innerHTML = intelligence.catalog.modes.map(m => `<option value="${ie(m.id)}">${ie(m.label)}</option>`).join('');
        iq('iqModules').innerHTML = intelligence.catalog.modules.map(m => `<label><input type="checkbox" ${intelligence.modules.has(m.module_name)?'checked':''} value="${ie(m.module_name)}"> ${ie(m.module_name)}<select data-run="${ie(m.module_name)}" aria-label="Run for ${ie(m.module_name)}">${(intelligence.catalog.run_choices[m.module_name]||[]).map(c=>`<option value="${ie(c.run_id)}" ${c.run_id===m.run_id?'selected':''}>${c.latest?'Latest · ':''}${ie(c.run_id)}</option>`).join('')}</select></label>`).join('') || '<p>No modules with analysis yet.</p>';
        iq('iqGates').innerHTML = intelligence.catalog.gates.map(g => `<li><strong>${ie(g.feature)}</strong> — ${ie(g.requires)} <small>(${ie(g.status.replaceAll('_',' '))})</small></li>`).join('');
        renderIntelligencePicker(); await queryIntelligence();
    } catch (e) { iq('iqStatus').textContent = e.message; }
}

function renderIntelligencePicker() {
    const catalog = intelligence.catalog; if (!catalog) return;
    const search = iq('iqSearch').value.toLowerCase();
    const kind = iq('iqKind').value;
    const eligible = catalog.symbols.filter(n => intelligence.modules.has(n.module) && (!kind || n.kind===kind) &&
        `${n.name} ${n.module} ${n.location?.path || ''}`.toLowerCase().includes(search));
    const shown = eligible.slice(0,100);
    iq('iqPickerCount').textContent = `${eligible.length} matches${eligible.length>100 ? ' · showing first 100; narrow your search' : ''}`;
    iq('iqPicker').innerHTML = shown.map(n => `<label><input type="checkbox" data-symbol="${ie(n.id)}" ${intelligence.selected.has(n.id)?'checked':''}><span>${ie(n.name)}<small>${ie(n.module)} · ${ie(n.kind.replaceAll('_',' '))} · ${ie(n.location?.path || 'external')}</small></span></label>`).join('') || '<p>No matching symbols.</p>';
    iq('iqSelections').innerHTML = [...intelligence.selected].map(id => {
        const n = catalog.symbols.find(n=>n.id===id) || intelligence.result?.nodes.find(n=>n.id===id);
        return `<button type="button" data-remove="${ie(id)}" title="Remove selection">${ie(n?.name || id)} ×</button>`;
    }).join('') || '<span>Select items here or in the map.</span>';
    iq('iqSelectionCount').textContent = `${intelligence.selected.size}/20 selected`;
}

function toggleIntelligenceSelection(id, checked) {
    if (checked && intelligence.selected.size >= 20 && !intelligence.selected.has(id)) {
        iq('iqStatus').textContent = 'Choose up to 20 items at a time.'; renderIntelligencePicker(); return;
    }
    if (checked) intelligence.selected.add(id); else intelligence.selected.delete(id);
    renderIntelligencePicker();
}

async function queryIntelligence() {
    const epoch=++intelligence.epoch;
    intelligence.controller?.abort(); intelligence.controller=new AbortController();
    iq('iqRun').disabled=true; iq('iqStatus').textContent='Connecting evidence…';
    const rules=iq('iqRules').value.trim();
    try {
        const payload={modules:[...intelligence.modules],runs:intelligence.runs,selected:[...intelligence.selected], mode:iq('iqMode').value,
            depth:Number(iq('iqDepth').value),limit:Number(iq('iqLimit').value), rules:rules?JSON.parse(rules):[]};
        const response=await fetch('/api/intelligence/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:intelligence.controller.signal});
        if (!response.ok) {const error=await response.json();throw new Error(typeof error.detail==='string'?error.detail:'Check the selection and query settings.');}
        const result=await response.json(); if (epoch!==intelligence.epoch) return;
        intelligence.result=result; renderIntelligenceResult();
    } catch(e) {if(e.name!=='AbortError' && epoch===intelligence.epoch) iq('iqStatus').textContent=e.message;}
    finally {if(epoch===intelligence.epoch) iq('iqRun').disabled=false;}
}

function renderIntelligenceResult() {
    const r=intelligence.result, c=r.coverage, a=r.analytics;
    intelligence.visible=new Set([...intelligence.selected,...r.nodes.slice(0,12).map(n=>n.id)]);
    iq('iqTitle').textContent=r.title;
    iq('iqStatus').textContent=`${c.displayed} items · ${r.edges.length} connections · ${c.omitted} hidden · ${c.frontier.length} beyond search boundary`;
    iq('iqCoverage').textContent=c.complete_within_scope?'All eligible results in this query are shown. Source analysis may still be partial.':'Partial view: increase depth or item limit, or narrow your selection. Missing paths are not proof that items are unrelated.';
    iq('iqNotes').innerHTML=r.notes.map(n=>`<p>${ie(n)}</p>`).join('');
    const names=new Map([...intelligence.catalog.symbols,...r.nodes].map(n=>[n.id,n.name]));
    iq('iqPaths').innerHTML=r.paths.map(p=>`<li>${p.nodes.length ? p.nodes.map(id=>ie(names.get(id)||id)).join(' ↔ ') : `${ie(names.get(p.from))} ↔ ${ie(names.get(p.to))}: no path found within this scope and budget`}</li>`).join('');
    iq('iqEvidence').textContent=`${r.snapshots.length} module snapshots · ${r.evidence.length} source-matched compiler flow bundles · ${r.warnings.length} attachment warnings. ${r.warnings.map(w=>w.reason).join('; ')}`;
    iq('iqMetrics').innerHTML=`<div class="iq-stats"><span><b>${a.functions.length}</b> functions</span><span><b>${a.recursive_groups.length}</b> recursive groups</span><span><b>${a.clone_groups.length}</b> exact clone groups</span><span><b>${a.complexity_outliers.length}</b> complexity outliers</span><span><b>${a.file_cycles.length}</b> file cycles</span><span><b>${a.storage_estimate_bytes}</b> bytes of symbol types</span></div>
        <p>${ie(a.score_formula)}</p><p>${ie(a.storage_boundary)}; ${a.storage_unknown_symbols} unknown sizes.</p><p>${ie(a.call_depth_boundary)}</p>
        <div class="iq-table-scroll"><table><caption>Investigation order in the selected modules</caption><thead><tr><th>Function</th><th>Complexity</th><th>Callers</th><th>Callees</th><th>Chain depth</th><th>Globals written</th><th>Review score</th></tr></thead><tbody>${a.functions.map(f=>`<tr><td><button data-inspect="${ie(f.id)}">${ie(f.name)}</button><small>${ie(f.module)}</small></td><td>${f.complexity??'Unknown'}</td><td>${f.callers}</td><td>${f.callees}</td><td>${f.call_depth_scc_edges}</td><td>${f.shared_writes}</td><td>${f.review_score}</td></tr>`).join('')}</tbody></table></div>
        <details><summary>Shared values, cycles, clones and explicit rules</summary>
        <h4>Shared values</h4><ul>${a.shared_state.map(v=>`<li>${ie(names.get(v.variable)||v.variable)}: ${v.writers.length} writers, ${v.readers.length} readers${v.multiple_writers?' · investigate coordination; not a proven race':''}</li>`).join('')||'<li>None observed.</li>'}</ul>
        <h4>Recursive groups</h4>${groupsHtml(a.recursive_groups,names)}<h4>Identical implementations</h4>${groupsHtml(a.clone_groups,names)}
        <h4>File cycles</h4>${groupsHtml(a.file_cycles,new Map(a.file_nodes.map(n=>[n.id,n.name])))}
        <p>Architecture rules: ${ie(a.architecture.status)} · ${a.architecture.findings.length} matching forbidden dependencies.</p>
        <pre>${ie(JSON.stringify(a.architecture.findings,null,2))}</pre></details>`;
    iq('iqRelationships').innerHTML=r.edges.map(e=>`<li><button data-inspect="${ie(e.source)}">${ie(names.get(e.source))}</button> ${ie(edgeLabel(e))} <button data-inspect="${ie(e.target)}">${ie(names.get(e.target))}</button>${e.source_order?` · source call #${e.source_order}`:''}${e.count?` (${e.count} observations)`:''}</li>`).join('')||'<li>No relationships in this view.</li>';
    renderIntelligenceMap();
    iq('iqInspector').innerHTML=(r.structures||[]).map(contextHtml).join('') || '<p>Inspect a map item to see its source, inputs, outputs and compiler evidence. Use “Add to selection” to combine it with other items.</p>';
}

function groupsHtml(groups,names) {return `<ul>${groups.map(g=>`<li>${g.map(id=>ie(names.get(id)||id)).join(' ↔ ')}</li>`).join('')||'<li>None observed.</li>'}</ul>`;}

function renderIntelligenceMap() {
    const r=intelligence.result; if(!r)return;
    const shown=r.nodes.filter(n=>intelligence.visible.has(n.id));
    const shownIds=new Set(shown.map(n=>n.id));
    const shownEdges=r.edges.filter(e=>shownIds.has(e.source)&&shownIds.has(e.target));
    const dense=shownEdges.length>20;
    iq('iqMapHelp').textContent=`Showing ${shown.length} of ${r.nodes.length} returned map items. Inspect a card to choose which connected items to pursue; Show all restores this view. ` +
        (dense?'Repeated arrow labels are hidden for readability. Branch labels remain; inspect an arrow or open the relationship list for details.':'');
    const nodes=layoutIntelligence(shown,shownEdges), byId=new Map(nodes.map(n=>[n.id,n]));
    const width=Math.max(800,...nodes.map(n=>n.x+270)),height=Math.max(350,...nodes.map(n=>n.y+110));
    const edges=shownEdges.map((e,index)=>{const s=byId.get(e.source),t=byId.get(e.target);if(!s||!t)return '';
        const x=s.x+230,y=s.y+40,tx=t.x,ty=t.y+40;
        const curve=s.id===t.id?`M ${x-30} ${y-40} C ${x+70} ${y-110}, ${x+100} ${y+80}, ${x} ${y+20}`:
            `M ${x} ${y} C ${x+55} ${y+(tx<=x?65:0)}, ${tx-55} ${ty+(tx<=x?65:0)}, ${tx} ${ty}`;
        const label=edgeLabel(e), showLabel=!dense || (e.kind==='control_flow' && (label==='if true'||label==='if false'));
        return `<g><path d="${curve}" class="iq-edge ${e.kind==='memory_flow'?'iq-memory':''}" marker-end="url(#iqArrow)"><title>${ie(s.name)} ${ie(label)} ${ie(t.name)}</title></path>${showLabel?`<text x="${(x+tx)/2}" y="${(y+ty)/2-8-(index%2)*12}" class="iq-edge-label">${ie(label)}</text>`:''}</g>`;}).join('');
    const cards=nodes.map(n=>`<g class="iq-node ${intelligence.selected.has(n.id)?'selected':''}" data-inspect="${ie(n.id)}" role="button" tabindex="0" aria-label="Inspect ${ie(flowTitle(n))}" transform="translate(${n.x},${n.y})"><rect width="230" height="85" rx="12"/><text x="12" y="23">${ie(flowTitle(n).slice(0,29))}</text><text x="12" y="44" class="iq-node-kind">${ie(n.kind.replaceAll('_',' '))} · ${ie(n.module||'')}</text><text x="12" y="66" class="iq-node-kind">${ie((n.location?.path||n.attributes?.ir||'Inspect for details').slice(0,34))}</text><title>${ie(n.name)}</title></g>`).join('');
    iq('iqMap').innerHTML=nodes.length?`<svg width="${width*intelligence.zoom}" height="${height*intelligence.zoom}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${ie(r.title)}"><defs><marker id="iqArrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#6b829f"/></marker></defs>${edges}${cards}</svg>`:'<p class="iq-empty">No graph evidence for this selection. Select a function with a verified flow bundle for decisions and values.</p>';
}

function contextHtml(c) {
    const n=c.node,a=n.attributes||{};
    return `<article class="iq-context"><h3>${ie(flowTitle(n))}</h3><p>${ie(n.name)} · ${ie(n.kind)} · ${ie(n.module)}</p>
      <button data-add="${ie(n.id)}">Add to selection</button>
      ${neighborControls(n.id)}
      <p>${(c.notes||[]).map(ie).join(' ')}</p>
      ${a.memory_boundary?`<p>Memory evidence: ${ie(a.memory_boundary.replaceAll('_',' '))}</p>`:''}
      ${c.source?`<p>${ie(c.source.path)} · ${ie(c.source.match)}${c.source.truncated?' · excerpt shortened':''}</p><pre>${ie(c.source.text)}</pre>`:'<p>No source excerpt available.</p>'}
      ${a.ir?`<details><summary>Compiler operation</summary><pre>${ie(a.ir)}</pre></details>`:''}
      ${(c.explanation||[]).length?`<h4>Relationships in plain language</h4><ul>${c.explanation.map(e=>`<li>${ie(e.source)} ${ie(relationWords[e.kind]||e.kind)} ${ie(e.target)}${e.label?` · ${ie(e.label)}`:''}${e.location?.line?` (line ${e.location.line})`:''}</li>`).join('')}</ul>`:''}
      ${(c.call_sites||[]).length?`<h4>Calls in source order</h4><p>This is reading order in the C file, not guaranteed runtime order across branches or loops.</p><ol>${c.call_sites.map(site=>`<li><button data-inspect="${ie(site.callee_id)}">${ie(site.callee)}</button>${site.location?.line?` · line ${site.location.line}${site.location.column?`, column ${site.location.column}`:''}`:''}${site.ordinal?` · position ${site.ordinal}`:' · position unknown'}</li>`).join('')}</ol>`:''}
      ${(c.operations||[]).length?`<h4>Operations in this step</h4><ol>${c.operations.map(op=>`<li><button data-inspect="${ie(op.id)}">${ie(flowTitle(op))}</button><details><summary>Compiler evidence</summary><pre>${ie(op.attributes.ir)}</pre></details></li>`).join('')}</ol>`:''}
      ${(c.regions||[]).length?`<h4>Inside this function</h4><p>Nested structure, not execution order.${c.regions_truncated?' Some regions omitted.':''}</p><ol>${c.regions.map(region=>`<li style="margin-left:${Math.min(region.guard_context.length,6)*12}px"><details><summary>${ie(region.name)} · lines ${region.line}–${region.end_line}</summary><pre>${ie(region.text)}</pre></details></li>`).join('')}</ol>`:''}
      ${(c.boundary_test_ideas||[]).length?`<details><summary>Boundary test ideas — not executed</summary><ul>${c.boundary_test_ideas.map(t=>`<li><code>${ie(t.expression)}</code><p>${ie(t.suggestion)}</p></li>`).join('')}</ul></details>`:''}
      <details><summary>${c.relationships?.length||0} source relationships</summary><pre>${ie(JSON.stringify(c.relationships||[],null,2))}</pre></details></article>`;
}

function neighborControls(id) {
    const r=intelligence.result;
    if(!r)return '';
    const names=new Map(r.nodes.map(n=>[n.id,n.name]));
    const neighbors=[...new Set(r.edges.filter(e=>e.source===id||e.target===id)
        .map(e=>e.source===id?e.target:e.source).filter(other=>other!==id&&names.has(other)))].sort();
    return `<details open><summary>Choose connected items to pursue (${neighbors.length})</summary>
        <button type="button" data-focus="${ie(id)}">Focus on this item</button>
        <div class="iq-neighbors">${neighbors.slice(0,50).map(other=>`<label><input type="checkbox" data-show-node="${ie(other)}" ${intelligence.visible.has(other)?'checked':''}>${ie(names.get(other))}</label>`).join('')||'<p>No direct connection in this returned view.</p>'}</div>
        ${neighbors.length>50?'<p>Showing the first 50 connections; narrow the question to see more.</p>':''}</details>`;
}

async function inspectIntelligence(id) {
    const epoch=++intelligence.contextEpoch;
    const n=intelligence.result?.nodes.find(n=>n.id===id);
    if(n?.members) {iq('iqInspector').innerHTML=`<h3>${ie(n.name)}</h3><p>${n.members.length} owned symbols. Select individual symbols to explore connections.</p>`;return;}
    iq('iqInspector').textContent='Loading source and structure…';
    try {const response=await fetch('/api/intelligence/context',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({node_id:id,runs:intelligence.runs})});
        if(!response.ok)throw new Error('Source context unavailable. Refresh the catalog if the snapshot changed.');
        const c=await response.json(); if(epoch===intelligence.contextEpoch)iq('iqInspector').innerHTML=contextHtml(c);
    }catch(e){if(epoch===intelligence.contextEpoch)iq('iqInspector').textContent=e.message;}
}

function exportIntelligence() {
    if(!intelligence.result)return;
    const blob=new Blob([JSON.stringify(intelligence.result,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='code-exploration.json';link.click();URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded',()=>{
    if(!iq('intelligenceWorkspace'))return;
    iq('iqRun').addEventListener('click',queryIntelligence);
    iq('iqRefresh').addEventListener('click',()=>refreshIntelligence());
    iq('iqSearch').addEventListener('input',renderIntelligencePicker);
    iq('iqKind').addEventListener('change',renderIntelligencePicker);
    iq('iqModules').addEventListener('change',e=>{if(e.target.dataset.run){
        const runs={...intelligence.runs,[e.target.dataset.run]:e.target.value};
        refreshIntelligence(runs,new Set(intelligence.modules));return;
    } if(e.target.type!=='checkbox')return;
        if(e.target.checked)intelligence.modules.add(e.target.value);else intelligence.modules.delete(e.target.value);
        const valid=new Set(intelligence.catalog.symbols.filter(n=>intelligence.modules.has(n.module)).map(n=>n.id));
        intelligence.selected=new Set([...intelligence.selected].filter(id=>valid.has(id)));renderIntelligencePicker();});
    iq('iqPicker').addEventListener('change',e=>{if(e.target.dataset.symbol)toggleIntelligenceSelection(e.target.dataset.symbol,e.target.checked);});
    iq('iqClear').addEventListener('click',()=>{intelligence.selected.clear();renderIntelligencePicker();});
    iq('iqExport').addEventListener('click',exportIntelligence);
    iq('iqShowAll').addEventListener('click',()=>{intelligence.visible=new Set(intelligence.result?.nodes.map(n=>n.id)||[]);renderIntelligenceMap();});
    iq('iqZoom').addEventListener('input',e=>{intelligence.zoom=Number(e.target.value);renderIntelligenceMap();});
    iq('iqLegacy').addEventListener('click',()=>{const old=iq('legacyGraphWorkspace');old.hidden=!old.hidden;iq('iqLegacy').setAttribute('aria-expanded',String(!old.hidden));if(!old.hidden)requestAnimationFrame(resizeGraphCanvas);});
    iq('intelligenceWorkspace').addEventListener('click',e=>{const target=e.target.closest('[data-inspect],[data-add],[data-remove],[data-focus]');if(!target)return;
        if(target.dataset.inspect)inspectIntelligence(target.dataset.inspect);
        if(target.dataset.add)toggleIntelligenceSelection(target.dataset.add,true);
        if(target.dataset.remove)toggleIntelligenceSelection(target.dataset.remove,false);
        if(target.dataset.focus){intelligence.visible=new Set([target.dataset.focus]);renderIntelligenceMap();
            iq('iqInspector').querySelectorAll('[data-show-node]').forEach(box=>box.checked=false);}});
    iq('iqInspector').addEventListener('change',e=>{if(!e.target.dataset.showNode)return;
        if(e.target.checked)intelligence.visible.add(e.target.dataset.showNode);else intelligence.visible.delete(e.target.dataset.showNode);
        renderIntelligenceMap();});
    iq('iqMap').addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.dataset.inspect){e.preventDefault();inspectIntelligence(e.target.dataset.inspect);}});
});
