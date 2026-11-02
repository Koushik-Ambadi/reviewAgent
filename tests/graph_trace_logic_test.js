const fs = require("fs");
const vm = require("vm");

const context = {
    document: { addEventListener: () => {} },
    window: {}
};
vm.createContext(context);
vm.runInContext(fs.readFileSync("app/static/graph.js", "utf8"), context);

const repeatedRelationAllowed = vm.runInContext(
    `traceBranchAllows(
        {trace_relation_path: ["call:a:b"], trace_canonical_path: ["fn:a", "fn:b"]},
        "call:a:b", "fn:a"
    )`,
    context
);
if (repeatedRelationAllowed) throw new Error("A traversed relation was allowed");

const separateBranchAllowed = vm.runInContext(
    `traceBranchAllows(
        {trace_relation_path: [], trace_canonical_path: ["fn:c"]},
        "call:a:b", "fn:a"
    )`,
    context
);
if (!separateBranchAllowed) throw new Error("An independent branch was blocked");

vm.runInContext(
    `positionTraceNodes([
        {id: "root", label: "root", kind: "function", trace_column: 0},
        {id: "left", label: "left", kind: "function",
            parent_instance_id: "root", trace_column: -1},
        {id: "right1", label: "right1", kind: "function",
            parent_instance_id: "root", trace_column: 1},
        {id: "right2", label: "right2", kind: "function",
            parent_instance_id: "root", trace_column: 1}
    ]);
    const root = graphState.positionedNodes.find(node => node.id === "root");
    const children = graphState.positionedNodes.filter(
        node => node.parent_instance_id === "root"
    );
    const expected = (Math.min(...children.map(node => node.y)) +
        Math.max(...children.map(node => node.y))) / 2;
    if (root.y !== expected) throw new Error("Parent is not centered");`,
    context
);

vm.runInContext(`
    const parent={id:'trace:1',canonical_id:'run::function',kind:'function',trace_depth:0,trace_column:0,
        trace_relation_path:[],trace_canonical_path:['run::function']};
    graphState.traceInstances=[parent];graphState.traceEdges=[];graphState.traceCounter=1;
    appendTraceFunctionFlow(parent,{mode:'cfg',nodes:[
        {id:'run::b0',kind:'basic_block',name:'entry',attributes:{order:0}},
        {id:'run::b1',kind:'basic_block',name:'exit',attributes:{order:1}}],
        edges:[{id:'run::next',kind:'control_flow',source:'run::b0',target:'run::b1'}]});
    appendTraceFunctionFlow(parent,{mode:'dfd',nodes:[
        {id:'run::v0',kind:'instruction',name:'load',attributes:{ir:'%0 = load i32'}}],edges:[]});
    if(graphState.traceInstances.length!==4 ||
       !graphState.traceEdges.some(e=>e.kind==='control_flow') ||
       !graphState.traceEdges.some(e=>e.kind==='contains'))throw Error('Inline flow missing from trace');
    if(!graphState.traceInstances.some(n=>n.flow_view==='dfd'&&n.flow_ir))throw Error('DFD operation missing');
    collapseTraceNode(parent.id);
    if(graphState.traceInstances.length!==1 || graphState.traceEdges.length)throw Error('Collapse left flow internals');
`,context);

console.log("trace cycle, centering and inline flow assertions passed");
