from code_intelligence.models import EdgeKind, NodeKind
from .projections import GraphProjection


def control_flow_graph(graph):
    """A lossless block/edge projection; never reinterpret source access order."""
    graph.validate()
    nodes = tuple(n for n in graph.nodes if n.kind == NodeKind.BASIC_BLOCK)
    return GraphProjection("control_flow", nodes,
        tuple(e for e in graph.edges if e.kind == EdgeKind.CONTROL_FLOW),
        {"available": bool(nodes), "representation": "lowered_llvm_ir"})


def data_flow_graph(graph):
    graph.validate()
    nodes = tuple(n for n in graph.nodes if n.kind in {NodeKind.INSTRUCTION, NodeKind.IR_VALUE})
    return GraphProjection("data_flow", nodes,
        tuple(e for e in graph.edges if e.kind in {EdgeKind.DEF_USE, EdgeKind.MEMORY_FLOW}),
        {"available": bool(nodes), "ssa_operands": "exact",
         "memory": "may_reach_non_escaping_direct_allocas",
         "interprocedural_alias_analysis": False})
