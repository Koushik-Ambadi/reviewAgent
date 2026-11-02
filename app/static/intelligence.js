/* Guided, read-only exploration. All source-derived text is escaped. */
const intelligence = {catalog: null, selected: new Set(), modules: new Set(), runs: {}, visible: new Set(), result: null,
    baseResult: null, expandedFlows: new Map(),
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
    if (node.kind === 'basic_block') return a.entry ? 'Start / first decision' : a.exit ? 'Function ends' :
        node.flow_summary?.condition ? 'Decide next outcome' : node.flow_summary?.effects?.length ? 'Result on this path' : `Compiler step ${a.order + 1}`;
    if (node.kind !== 'instruction') return node.name;
    const operations = {1:'Return',2:'Choose next step',3:'Choose a case',26:'Reserve local storage',27:'Read a value',28:'Save a value',
        29:'Locate a field or item',44:'Combine branch results',45:'Call an operation',8:'Add',10:'Subtract',12:'Multiply',
        30:'Narrow a number',31:'Extend a number',32:'Extend a signed number',34:'Convert to decimal',42:'Compare values',43:'Compare decimals'};
    return `${operations[a.opcode] || 'Transform a value'}${node.location?.line ? ` · line ${node.location.line}` : ''}`;
}

function flowRelationName(node) {
    if(!node)return 'Unknown item';
    const summary=node.flow_summary;
    if(summary?.condition)return `If ${summary.condition}`;
    if(summary?.effects?.some(effect=>effect.source))return summary.effects.find(effect=>effect.source).source;
    return node.kind==='basic_block'?flowTitle(node):node.name;
}

function layoutIntelligence(nodes, edges) {
    const base = nodes.filter(n => !n.inline_owner);
    const internals = nodes.filter(n => n.inline_owner);
    // Shortest levels from entries; disconnected/cyclic components remain finite.
    const byId = new Map(base.map(n => [n.id, n]));
    const outgoing = new Map(base.map(n => [n.id, new Set()]));
    const incoming = new Map(base.map(n => [n.id, 0]));
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
    base.filter(n => incoming.get(n.id) === 0 || n.attributes?.entry).forEach(n => visit(n.id));
    base.forEach(n => visit(n.id));
    const rows = new Map();
    const positioned = base.map(n => {const level=levels.get(n.id), row=rows.get(level)||0; rows.set(level,row+1);
        return {...n,x:40+level*290,y:45+row*125};});
    const groups = new Map();
    internals.forEach(n => {const key=`${n.inline_owner}:${n.inline_mode}`;
        if(!groups.has(key))groups.set(key,[]);groups.get(key).push(n);});
    const right=Math.max(40,...positioned.map(n=>n.x))+320;
    let top=95;
    positioned.containers=[];
    for(const group of groups.values()) {
        const mode=group[0].inline_mode, owner=group[0].inline_owner;
        const groupIds=new Set(group.map(n=>n.id));
        const children=new Map(group.map(n=>[n.id,[]]));
        edges.filter(e=>e.kind==='control_flow'&&groupIds.has(e.source)&&groupIds.has(e.target))
            .forEach(e=>children.get(e.source).push(e));
        for(const values of children.values())values.sort((a,b)=>
            ({true:0,false:1,successor:2}[a.attributes?.label]??3)-({true:0,false:1,successor:2}[b.attributes?.label]??3));
        const local=new Map(), visited=new Set();let leaf=0;
        function place(id,depth) {
            if(visited.has(id))return local.get(id)?.x ?? leaf++;
            visited.add(id);
            const next=(children.get(id)||[]).map(e=>e.target).filter(target=>!visited.has(target));
            const xs=next.map(target=>place(target,depth+1));
            const x=xs.length?(Math.min(...xs)+Math.max(...xs))/2:leaf++;
            local.set(id,{x,depth});return x;
        }
        if(mode==='cfg') {
            group.filter(n=>n.attributes?.entry).forEach(n=>place(n.id,0));
            group.forEach(n=>{if(!visited.has(n.id))place(n.id,0);});
        } else group.forEach((n,row)=>local.set(n.id,{x:0,depth:row}));
        const maxX=Math.max(0,...[...local.values()].map(p=>p.x));
        const maxDepth=Math.max(0,...[...local.values()].map(p=>p.depth));
        const width=(maxX+1)*350+50,height=(maxDepth+1)*220+80;
        positioned.containers.push({x:right-20,y:top-55,width,height,owner,mode});
        group.forEach(n=>{const p=local.get(n.id);positioned.push({...n,x:right+20+p.x*350,y:top+p.depth*220});});
        top+=height+35;
    }
    return positioned;
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
    ++intelligence.epoch;
    iq('iqStatus').textContent = 'Reading available module evidence…';
    try {
        const response = await fetch('/api/intelligence/catalog',runs ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({runs})} : {});
        if (!response.ok) throw new Error(`Could not load evidence (${response.status})`);
        intelligence.catalog = await response.json();
        intelligence.modules = preserveModules || new Set(intelligence.catalog.modules.map(m => m.module_name));
        intelligence.runs = Object.fromEntries(intelligence.catalog.modules.map(m=>[m.module_name,m.run_id]));
        intelligence.result=null;
        intelligence.baseResult=null; intelligence.expandedFlows.clear();
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
        intelligence.baseResult=result; intelligence.expandedFlows.clear();
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
    renderIntelligenceRelationships();
    renderIntelligenceMap();
    iq('iqInspector').innerHTML=(r.structures||[]).map(contextHtml).join('') || '<p>Inspect a map item to see its source, inputs, outputs and compiler evidence. Use “Add to selection” to combine it with other items.</p>';
}

function renderIntelligenceRelationships() {
    const r=intelligence.result, names=new Map([...intelligence.catalog.symbols,...r.nodes].map(n=>[n.id,flowRelationName(n)]));
    iq('iqRelationships').innerHTML=r.edges.map(e=>`<li><button data-inspect="${ie(e.source)}">${ie(names.get(e.source))}</button> ${ie(edgeLabel(e))} <button data-inspect="${ie(e.target)}">${ie(names.get(e.target))}</button>${e.source_order?` · source call #${e.source_order}`:''}${e.count?` (${e.count} observations)`:''}</li>`).join('')||'<li>No relationships in this view.</li>';
}

function composeInlineFlow() {
    const base=intelligence.baseResult;
    const nodes=new Map(base.nodes.map(n=>[n.id,n]));
    const edges=new Map(base.edges.map(e=>[e.id,e]));
    for(const [owner, modes] of intelligence.expandedFlows)for(const [mode, flow] of modes) {
        flow.nodes.forEach(n=>nodes.set(n.id,{...n,inline_owner:owner,inline_mode:mode}));
        flow.edges.forEach(e=>edges.set(e.id,e));
        if(flow.nodes.length)edges.set(`inline:${owner}:${mode}`,{
            id:`inline:${owner}:${mode}`,kind:'contains',source:owner,target:flow.nodes[0].id,
            display_relation:`has ${mode.toUpperCase()} internals`,resolution:'verified_compiler_flow'});
    }
    intelligence.result={...base,nodes:[...nodes.values()],edges:[...edges.values()],
        inline_flow:[...intelligence.expandedFlows].flatMap(([owner,modes])=>[...modes].map(([mode,flow])=>({owner,mode,coverage:flow.coverage})))};
    const flows=intelligence.result.inline_flow;
    const internalCount=flows.reduce((total,item)=>total+item.coverage.displayed,0);
    iq('iqStatus').textContent=`${base.coverage.displayed} call-graph items · ${internalCount} internal flow items · ${intelligence.result.edges.length} connections.`;
    iq('iqCoverage').textContent=flows.length
        ? `Call view and ${flows.length} expanded flow${flows.length===1?'':'s'} are bounded. ${flows.reduce((total,item)=>total+item.coverage.omitted,0)} internal items remain beyond the selected limits; missing paths are not proof of absence.`
        : base.coverage.complete_within_scope?'All eligible results in this query are shown. Source analysis may still be partial.':'Partial view: increase depth or item limit, or narrow your selection.';
    intelligence.visible=new Set([...intelligence.visible].filter(id=>nodes.has(id)));
    for(const modes of intelligence.expandedFlows.values())for(const [mode,flow] of modes)
        flow.nodes.filter(n=>mode!=='cfg'||(!n.flow_summary?.structural_join&&!n.attributes?.exit))
            .slice(0,mode==='cfg'?16:8).forEach(n=>intelligence.visible.add(n.id));
    renderIntelligenceRelationships(); renderIntelligenceMap();
}

async function toggleInlineFlow(id,mode) {
    if(intelligence.result?.mode!=='calls')return;
    const node=intelligence.baseResult.nodes.find(n=>n.id===id);
    if(node?.kind!=='function')return;
    const modes=intelligence.expandedFlows.get(id)||new Map();
    if(modes.has(mode)){modes.delete(mode);if(!modes.size)intelligence.expandedFlows.delete(id);
        composeInlineFlow(); inspectIntelligence(id);return;}
    const epoch=intelligence.epoch;
    iq('iqStatus').textContent=`Loading ${mode.toUpperCase()} inside ${node.name}…`;
    try {
        const params=new URLSearchParams({node_id:node.canonical_id,mode,limit:'48'});
        const response=await fetch(`/api/runs/${encodeURIComponent(node.run_id)}/graphs/function-flow?${params}`);
        if(!response.ok)throw new Error('Verified compiler flow is unavailable for this function.');
        const flow=await response.json();if(epoch!==intelligence.epoch)return;
        if(!flow.nodes.length)throw new Error(`No ${mode.toUpperCase()} internals matched this function.`);
        modes.set(mode,flow);intelligence.expandedFlows.set(id,modes);composeInlineFlow();
        inspectIntelligence(id);
    }catch(error){if(epoch===intelligence.epoch)iq('iqStatus').textContent=error.message;}
}

function groupsHtml(groups,names) {return `<ul>${groups.map(g=>`<li>${g.map(id=>ie(names.get(id)||id)).join(' ↔ ')}</li>`).join('')||'<li>None observed.</li>'}</ul>`;}

function renderIntelligenceMap() {
    const r=intelligence.result; if(!r)return;
    const shown=r.nodes.filter(n=>intelligence.visible.has(n.id));
    const shownIds=new Set(shown.map(n=>n.id));
    const shownEdges=r.edges.filter(e=>shownIds.has(e.source)&&shownIds.has(e.target));
    const dense=shownEdges.length>20;
    iq('iqMapHelp').textContent=`Showing ${shown.length} of ${r.nodes.length} returned map items. Inspect a card to choose which connected items to pursue; Show all restores this view. ` +
        (r.inline_flow?.some(flow=>flow.mode==='cfg')?'Decision cards show verified source conditions; Yes and No lead to sibling paths. Compiler-only join steps start hidden and remain in the relationship list and JSON. ':'') +
        (dense?'Repeated arrow labels are hidden for readability; inspect an arrow or open the relationship list for details.':'');
    const nodes=layoutIntelligence(shown,shownEdges), byId=new Map(nodes.map(n=>[n.id,n]));
    const containers=nodes.containers||[];
    const width=Math.max(800,...nodes.map(n=>n.x+(n.inline_owner?340:270)),...containers.map(c=>c.x+c.width+20));
    const height=Math.max(350,...nodes.map(n=>n.y+(n.inline_owner?190:110)),...containers.map(c=>c.y+c.height+20));
    const boxes=containers.map(c=>`<g class="iq-flow-box"><rect x="${c.x}" y="${c.y}" width="${c.width}" height="${c.height}" rx="18"/><text x="${c.x+18}" y="${c.y+29}">${ie(c.mode.toUpperCase())} inside ${ie(r.nodes.find(n=>n.id===c.owner)?.name||'function')}</text></g>`).join('');
    const edges=shownEdges.map((e,index)=>{const s=byId.get(e.source),t=byId.get(e.target);if(!s||!t)return '';
        const branch=e.kind==='control_flow'&&s.inline_mode==='cfg'&&t.inline_mode==='cfg';
        const x=s.x+(s.inline_owner?157:230),y=s.y+(branch?175:40),tx=t.x+(branch?157:0),ty=t.y+(branch?0:40);
        const curve=branch?`M ${x} ${y} L ${x} ${y+20} L ${tx} ${y+20} L ${tx} ${ty-5}`:
            s.id===t.id?`M ${x-30} ${y-40} C ${x+70} ${y-110}, ${x+100} ${y+80}, ${x} ${y+20}`:
            `M ${x} ${y} C ${x+55} ${y+(tx<=x?65:0)}, ${tx-55} ${ty+(tx<=x?65:0)}, ${tx} ${ty}`;
        const label=branch?({true:'Yes',false:'No',successor:'Next'}[e.attributes?.label]||edgeLabel(e)):edgeLabel(e);
        const showLabel=branch?(e.attributes?.label==='true'||e.attributes?.label==='false'):
            (!dense||e.id.startsWith('inline:'));
        return `<g><path d="${curve}" class="iq-edge ${e.kind==='memory_flow'?'iq-memory':''} ${branch?'iq-branch':''}" marker-end="url(#iqArrow)"><title>${ie(s.name)} ${ie(label)} ${ie(t.name)}</title></path>${showLabel?`<text x="${branch?tx+8:(x+tx)/2}" y="${branch?ty-12:(y+ty)/2-8-(index%2)*12}" class="iq-edge-label">${ie(label)}</text>`:''}</g>`;}).join('');
    const cards=nodes.map(n=>{
        const summary=n.flow_summary, internal=Boolean(n.inline_owner);
        const details=summary?[summary.condition?`If ${summary.condition}`:null,
            ...(summary.condition_inputs||[]).filter(input=>input.declaration)
                .map(input=>`${input.name} initializer: ${input.declaration.split('=').slice(1).join('=').trim()}`),
            ...summary.effects.filter(effect=>effect.source).map(effect=>effect.source)].filter(Boolean):[];
        const allLines=details.flatMap(detail=>wrapFlowText(detail,46));
        const detailLines=allLines.length>6?[...allLines.slice(0,5),'… inspect for full expression']:allLines;
        const content=internal?`<text x="12" y="27">${ie(flowTitle(n))}</text><text x="12" y="48" class="iq-node-kind">${ie(summary?.condition_line?'Decision · source line '+summary.condition_line:summary?.effects?.[0]?.line?'Change · source line '+summary.effects[0].line:n.kind.replaceAll('_',' '))}</text>${detailLines.map((line,i)=>`<text x="12" y="${72+i*17}" class="iq-node-detail">${ie(line)}</text>`).join('')}${!detailLines.length?`<text x="12" y="77" class="iq-node-kind">Inspect compiler step</text>`:''}`:
            `<text x="12" y="23">${ie(flowTitle(n).slice(0,29))}</text><text x="12" y="44" class="iq-node-kind">${ie(n.kind.replaceAll('_',' ')+' · '+(n.module||''))}</text><text x="12" y="66" class="iq-node-kind">${ie((n.location?.path||n.attributes?.ir||'Inspect for details').slice(0,34))}</text>`;
        return `<g class="iq-node ${intelligence.selected.has(n.id)?'selected':''} ${n.inline_mode?'inline-'+n.inline_mode:''}" data-inspect="${ie(n.id)}" role="button" tabindex="0" aria-label="Inspect ${ie(flowTitle(n))}" transform="translate(${n.x},${n.y})"><rect width="${internal?315:230}" height="${internal?175:85}" rx="12"/>${content}<title>${ie([n.name,...details].join(' · '))}</title></g>`;
    }).join('');
    iq('iqMap').innerHTML=nodes.length?`<svg width="${width*intelligence.zoom}" height="${height*intelligence.zoom}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${ie(r.title)}"><defs><marker id="iqArrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#6b829f"/></marker></defs>${boxes}${edges}${cards}</svg>`:'<p class="iq-empty">No graph evidence for this selection. Select a function with a verified flow bundle for decisions and values.</p>';
}

function wrapFlowText(value,max) {
    const text=String(value).replace(/\s+/g,' ').trim();
    const lines=[];let rest=text;
    while(rest.length>max&&lines.length<3){let cut=rest.lastIndexOf(' ',max);if(cut<max/2)cut=max;
        lines.push(rest.slice(0,cut));rest=rest.slice(cut).trim();}
    if(rest)lines.push(rest.length>max?rest.slice(0,max-1)+'…':rest);
    return lines;
}

function contextHtml(c) {
    const n=c.node,a=n.attributes||{};
    const summary=n.flow_summary;
    const inline=intelligence.result?.mode==='calls'&&n.kind==='function';
    const active=intelligence.expandedFlows.get(n.id)||new Map();
    return `<article class="iq-context"><h3>${ie(flowTitle(n))}</h3><p>${ie(n.name)} · ${ie(n.kind)} · ${ie(n.module)}</p>
      <button data-add="${ie(n.id)}">Add to selection</button>
      ${inline?`<div class="iq-inline-controls"><strong>Show this function's internals in the call graph</strong>
        <button type="button" data-inline-flow="cfg" data-function="${ie(n.id)}" aria-pressed="${active.has('cfg')}">${active.has('cfg')?'Hide':'Expand'} CFG</button>
        <button type="button" data-inline-flow="dfd" data-function="${ie(n.id)}" aria-pressed="${active.has('dfd')}">${active.has('dfd')?'Hide':'Expand'} DFD</button>
        ${[...active].map(([mode,flow])=>`<small>${mode.toUpperCase()}: ${flow.nodes.length} shown; ${flow.coverage.omitted} beyond the bound.</small>`).join('')}
        <small>Compiler-derived static flow; call order remains source position, not a runtime trace.</small></div>`:''}
      ${neighborControls(n.id)}
      ${summary?`<section class="iq-flow-summary"><h4>What this step does</h4>
        ${summary.condition?`<p><strong>Condition:</strong> <code>${ie(summary.condition)}</code>${summary.condition_line?` · line ${summary.condition_line}`:''}</p>`:''}
        ${(summary.condition_inputs||[]).length?`<h5>Compared values</h5><ul>${summary.condition_inputs.map(input=>`<li><code>${ie(input.name)}</code>${input.declaration?` · declared as <code>${ie(input.declaration)}</code>`:''} · line ${input.line}${input.declaration?' (initializer, not a proven runtime value)':''}</li>`).join('')}</ul>`:''}
        ${summary.effects.length?`<ul>${summary.effects.map(effect=>`<li>${effect.source?`<code>${ie(effect.source)}</code>`:'Compiler store; inspect operation below'}${effect.line?` · line ${effect.line}`:''}</li>`).join('')}</ul>`:''}
        ${!summary.condition&&!summary.effects.length?'<p>Compiler routing step; no source change is mapped to this block.</p>':''}</section>`:''}
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
        const c=await response.json(); if(epoch===intelligence.contextEpoch){c.node={...c.node,flow_summary:n.flow_summary};iq('iqInspector').innerHTML=contextHtml(c);}
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
    iq('intelligenceWorkspace').addEventListener('click',e=>{const target=e.target.closest('[data-inspect],[data-add],[data-remove],[data-focus],[data-inline-flow]');if(!target)return;
        if(target.dataset.inspect)inspectIntelligence(target.dataset.inspect);
        if(target.dataset.inlineFlow){toggleInlineFlow(target.dataset.function,target.dataset.inlineFlow);return;}
        if(target.dataset.add)toggleIntelligenceSelection(target.dataset.add,true);
        if(target.dataset.remove)toggleIntelligenceSelection(target.dataset.remove,false);
        if(target.dataset.focus){intelligence.visible=new Set([target.dataset.focus]);renderIntelligenceMap();
            iq('iqInspector').querySelectorAll('[data-show-node]').forEach(box=>box.checked=false);}});
    iq('iqInspector').addEventListener('change',e=>{if(!e.target.dataset.showNode)return;
        if(e.target.checked)intelligence.visible.add(e.target.dataset.showNode);else intelligence.visible.delete(e.target.dataset.showNode);
        renderIntelligenceMap();});
    iq('iqMap').addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.dataset.inspect){e.preventDefault();inspectIntelligence(e.target.dataset.inspect);}});
});
