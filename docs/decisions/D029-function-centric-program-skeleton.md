# D029 — Make the graph workspace a function-centric program skeleton

- Date: 2026-10-28
- Status: accepted; value-flow extension proposed
- Scope: visual hierarchy, selection behavior, and the evidence boundary for
  input/transformation/output explanations
- Context: promoting files, functions, parameters, locals, macros, and globals
  to equal canvas nodes produced crossing ownership edges and obscured the
  program flow. A parameter is a function-owned input binding while a local is
  function-owned storage; neither should normally compete with its function as
  a peer architectural node.
- Decision: file scope renders functions as the primary skeleton. Parameters and
  locals are nested in the selected function inspector and may be explicitly
  expanded; globals and macros are also optional detail nodes. Selecting a node
  centers it, preserves its incident relationships, and dims unrelated facts.
  Module edges remain aggregate file relationships but expose bounded concrete
  function/signal interactions when selected. Relationship visibility and node
  detail visibility are independent controls.
- Layout: use a deterministic dependency-ranked layout with stable alphabetical
  ordering inside ranks and curved relationship lanes. This reduces avoidable
  crossings but does not claim a globally minimal crossing layout.
- Evidence boundary: calls and conservative reads/writes can explain direct
  structural interaction. Argument origin, assignment transformation, returned
  value lineage, branch/path behavior, and pointer aliases require new evidence.
  Extend the AST contract conservatively with call-site argument-to-parameter,
  initializer/assignment, return-expression, and call-result relations before
  exposing value flow; add CFG/control-dependence and alias analysis separately.
- Rejected alternative: drawing ownership as ordinary edges leaves accurate
  facts technically present but makes the principal flow unreadable.
- Reconsideration trigger: a validated compound-node layout library or CPG/CFG
  engine can preserve hierarchy and path focus more accurately at scale.
- Implementation references: `app/static/graph.js`, `app/static/graph.css`,
  `app/services/graph_service.py`, and the graph workspace contract.
