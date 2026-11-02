const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{value:'',innerHTML:'',textContent:'',hidden:false,disabled:false,addEventListener(){},setAttribute(){}});return elements.get(id);}
const context={console,document:{getElementById:element,addEventListener(){}},AbortController,fetch:async()=>{throw Error('unexpected network')},URL,Blob};
vm.createContext(context);vm.runInContext(fs.readFileSync('app/static/intelligence.js','utf8'),context);
vm.runInContext(`
const nodes=[{id:'a',name:'<img src=x onerror=alert(1)>',kind:'function',module:'A',attributes:{}},{id:'b',name:'B',kind:'function',module:'B',attributes:{}},{id:'c',name:'C',kind:'function',module:'A',attributes:{}}];
const edges=[{id:'ab',source:'a',target:'b',kind:'calls'},{id:'ba',source:'b',target:'a',kind:'calls'},{id:'cc',source:'c',target:'c',kind:'calls'}];
const first=layoutIntelligence(nodes,edges),second=layoutIntelligence(nodes,edges);
if(JSON.stringify(first)!==JSON.stringify(second))throw Error('Non-deterministic layout');
if(new Set(first.map(n=>n.x+':'+n.y)).size!==3)throw Error('Overlapping cards');
if(first.some(n=>!Number.isFinite(n.x)||!Number.isFinite(n.y)))throw Error('Unbounded cycle layout');
intelligence.catalog={symbols:nodes};intelligence.modules=new Set(['A','B']);
iq('iqKind').value='';renderIntelligencePicker();
if(iq('iqPicker').innerHTML.includes('<img'))throw Error('Unescaped source name');
toggleIntelligenceSelection('a',true);toggleIntelligenceSelection('b',true);
if(intelligence.selected.size!==2)throw Error('Multi-selection failed');
toggleIntelligenceSelection('a',false);if(intelligence.selected.has('a'))throw Error('Removal failed');
intelligence.result={nodes,edges,title:'Connections'};intelligence.visible=new Set(nodes.map(n=>n.id));renderIntelligenceMap();
if(!iq('iqMap').innerHTML.includes('tabindex="0"'))throw Error('Missing keyboard controls');
if(iq('iqMap').innerHTML.includes('<img'))throw Error('Unescaped graph text');
const denseEdges=Array.from({length:21},(_,i)=>({id:'d'+i,source:'a',target:'b',kind:'def_use'}));
intelligence.result={nodes,edges:denseEdges,title:'Values'};renderIntelligenceMap();
if(!iq('iqMapHelp').textContent.includes('Repeated arrow labels') || iq('iqMap').innerHTML.includes('iq-edge-label'))throw Error('Dense edge labels obscure map');
if(edgeLabel({kind:'control_flow',attributes:{label:'true'}})!=='if true')throw Error('Branch label unclear');
intelligence.visible=new Set(['a']);renderIntelligenceMap();
if(!iq('iqMapHelp').textContent.includes('1 of 3')||iq('iqMap').innerHTML.includes('Inspect B'))throw Error('Node focus did not reduce map');
if(!neighborControls('a').includes('data-show-node="b"'))throw Error('Connected item cannot be chosen');
intelligence.visible.add('b');renderIntelligenceMap();
intelligence.baseResult={nodes,edges,title:'Calls',mode:'calls',coverage:{displayed:3,complete_within_scope:true}};
intelligence.expandedFlows.set('a',new Map([['cfg',{nodes:[
    {id:'step',name:'entry',kind:'basic_block',module:'A',attributes:{order:0}}],edges:[],coverage:{displayed:1,omitted:2}}]]));
intelligence.expandedFlows.set('b',new Map([['dfd',{nodes:[
    {id:'value',name:'input',kind:'ir_value',module:'B',attributes:{}}],edges:[],coverage:{displayed:1,omitted:0}}]]));
composeInlineFlow();
if(!intelligence.result.edges.some(e=>e.kind==='contains'&&e.source==='a'&&e.target==='step'))throw Error('Inline CFG not connected to call graph');
if(!iq('iqMap').innerHTML.includes('CFG inside'))throw Error('Inline CFG card missing');
if(!contextHtml({node:nodes[0],notes:[],relationships:[],regions:[]}).includes('Expand DFD'))throw Error('Function expansion controls missing');
if(!intelligence.result.edges.some(e=>e.kind==='contains'&&e.source==='b'&&e.target==='value'))throw Error('Second function flow missing');
const branchNodes=[
 {id:'root',name:'entry',kind:'basic_block',attributes:{entry:true},flow_summary:{condition:'input > 0',condition_line:6,effects:[],structural_join:false}},
 {id:'yes',name:'if.then',kind:'basic_block',attributes:{order:1},flow_summary:{condition:null,effects:[{source:'value = input + 1',line:7}],structural_join:false}},
 {id:'no',name:'if.else',kind:'basic_block',attributes:{order:2},flow_summary:{condition:null,effects:[{source:'value = input - 1',line:9}],structural_join:false}},
 {id:'join',name:'if.end',kind:'basic_block',attributes:{order:3},flow_summary:{condition:null,effects:[],structural_join:true}}];
const branchEdges=[{id:'true',source:'root',target:'yes',kind:'control_flow',attributes:{label:'true'}},
 {id:'false',source:'root',target:'no',kind:'control_flow',attributes:{label:'false'}},
 {id:'merge',source:'yes',target:'join',kind:'control_flow',attributes:{label:'successor'}}];
intelligence.expandedFlows.set('a',new Map([['cfg',{nodes:branchNodes,edges:branchEdges,coverage:{displayed:3,omitted:0}}]]));
composeInlineFlow();
if(intelligence.visible.has('join')||!intelligence.result.nodes.some(n=>n.id==='join'))throw Error('Compiler-only join should be retained but initially hidden');
const placed=layoutIntelligence(intelligence.result.nodes,intelligence.result.edges);
const byId=new Map(placed.map(n=>[n.id,n]));
if(byId.get('yes').y!==byId.get('no').y||byId.get('yes').x===byId.get('no').x||byId.get('root').y>=byId.get('yes').y)throw Error('True and false are not sibling paths');
if(!iq('iqMap').innerHTML.includes('If input &gt; 0')||!iq('iqMap').innerHTML.includes('value = input + 1')||!iq('iqMap').innerHTML.includes('>Yes</text>')||!iq('iqMap').innerHTML.includes('iq-flow-box'))throw Error('CFG conditions, effects or containment missing');
intelligence.expandedFlows.delete('a');composeInlineFlow();
if(intelligence.result.nodes.some(n=>n.id==='step')||!intelligence.result.nodes.some(n=>n.id==='value'))throw Error('Hiding one flow removed another');
intelligence.expandedFlows.clear();composeInlineFlow();
const html=contextHtml({node:nodes[0],notes:[],source:{text:'<script>bad()</script>',path:'a.c',match:'verified'},relationships:[],regions:[]});
if(html.includes('<script>'))throw Error('Unescaped source excerpt');
`,context);
assert(context.document.getElementById('iqMap').innerHTML.includes('marker-end'));
console.log('Intelligence multi-select, cyclic layout, keyboard and escaping checks passed');
