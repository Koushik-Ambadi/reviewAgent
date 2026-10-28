# D031 — Add an expandable trace playground beside overview graphs

- Date: 2026-10-28
- Status: accepted
- Scope: progressive graph disclosure and visual-instance identity
- Context: fixed file/module/function overview scopes remain useful for
  architecture, but they cannot support every investigation without rendering
  too many nodes and crossing edges at once.
- Decision: retain the existing overview graphs and add a separate expandable
  trace playground. A user chooses any canonical symbol in a run, expands its
  incoming, outgoing, or combined structural neighbors, and collapses any branch
  independently. The playground is not limited by the overview's current file.
- Visual identity: one canonical symbol may have multiple branch-local visual
  instances. This is allowed when it avoids long fan-out lines or crossings.
  Every instance retains `canonical_id`; no analysis fact or canonical node is
  duplicated. Expansion depth is bounded to 20 to prevent accidental unbounded
  cycling; a neighborhood does not silently truncate relationship groups.
- Layout: trace instances form a parent/child tree. Functions, variables, and
  macros retain distinct shapes. Expansion edges preserve their real direction,
  type, count, and source occurrences.
- Evidence boundary: the playground imitates structural movement through code,
  not runtime execution. Branch order, argument transformation, and path
  feasibility remain gated on value-flow and CFG evidence.
- Consequences: users can follow one question without globally expanding the
  program, while overview graphs continue to explain whole-file/module shape.
- Reconsideration trigger: validated CFG/value-flow evidence permits an ordered
  execution-oriented trace or server-side graph sessions are needed at scale.
- Implementation references: graph node/neighborhood API projections and
  `app/static/graph.js` trace-instance state.
