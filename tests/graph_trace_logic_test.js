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

console.log("trace cycle and centering assertions passed");
