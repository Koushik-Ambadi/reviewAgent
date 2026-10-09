# Agent Working Policy

## Required skill check

- At the start of every task, review the skills made available by the current
  Codex session and match their descriptions against the request before taking
  implementation actions.
- Also check repository-local skill locations when they exist (`skills/`,
  `.agents/skills/`, and `.codex/skills/`) with a targeted file search. Do not
  crawl unrelated directories or load unrelated skills.
- When a skill matches, read its complete `SKILL.md` before acting and follow its
  referenced instructions or resources as required. When no skill matches,
  continue with the normal repository workflow rather than forcing one.
- State the relevant skill being used and why in the first progress update. If
  the task is substantial and no skill applies, state that briefly as well.
- Re-evaluate skill relevance when the user materially changes the task; do not
  assume that a skill selected for an earlier turn still applies.

## Documentation is part of completion

- Treat documentation as part of the implementation, not as optional follow-up.
  Before editing code, identify which authoritative record has an update trigger
  for the requested change.
- Update documentation in the same increment as the behavior whenever practical:
  - API, serialized data, persistence, or identifiers: `docs/contracts/`.
  - Components, data flow, navigation, or runtime behavior:
    `docs/engineering/architecture.md`.
  - Material rationale, trade-offs, rejected alternatives, and fallbacks:
    `docs/engineering/decisions-and-lessons.md`.
  - Verification procedures, fixtures, or replay evidence:
    `docs/engineering/testing-and-replay.md`.
  - Deferred product capabilities and dependency gates:
    `docs/engineering/roadmap.md`.
  - User entry points or operating instructions: `README.md` or the closest
    scoped guide.
- Do not create documentation noise for a purely cosmetic edit. Do document a
  UI change when it alters navigation, workflow, state ownership, accessibility,
  operational behavior, or a deliberate product decision.
- Record explicit fallbacks and known limitations. Do not make implemented,
  planned, simulated, and unavailable behavior sound equivalent.
- In the final report, name the documentation updated. If no documentation was
  needed, state why.

## Incremental delivery and commits

- For implementation work, split the task into the smallest cohesive increments
  that remain independently understandable and safe to review.
- Complete each increment end to end: code, proportional verification,
  documentation triggered by that increment, focused diff review, then commit.
- Use narrow commit messages that describe one outcome. Do not combine unrelated
  cleanup, user-owned changes, or future work into the same commit.
- Before every commit, inspect the staged file list and staged diff. Stage exact
  paths, and never add an untracked or pre-existing user file unless the user
  explicitly authorized it.
- Preserve dirty-worktree changes. If requested work overlaps them, separate the
  staged result where practical or obtain explicit permission before including
  them.
- Documentation-only corrections may be their own increment. Do not create an
  empty or artificial commit merely to increase the commit count.

## Efficiency and context budget

- Before acting, estimate the task's complexity, risk, likely tool output, and context/token cost.
- Use the smallest effective investigation and verification scope. Do not collect broad logs, read unrelated files, or run redundant checks.
- Prefer targeted searches, narrow file reads, and concise tool output limits.
- Do not run a test merely because it is available. Match verification to the files and behavior changed:
  - CSS or presentation-only UI changes: inspect the focused diff and verify the affected UI behavior; do not start the application solely for this.
  - Startup, dependency, routing, or configuration changes: run an application-start smoke check.
  - Isolated logic changes: run the relevant unit tests.
  - Feature or integration changes: run the relevant functional tests.
  - Cross-cutting orchestration or pipeline changes: run the full pipeline when its value justifies its cost.
- Reuse reliable evidence already supplied by the user instead of reproducing it without a concrete reason.

## Agent versus user execution

- Choose between running a step directly and asking the user to run it based on total time, token/context cost, reliability, and convenience.
- Run steps directly when they are fast, automatable, non-interactive, and produce compact, decisive output.
- Ask the user to perform simple visual or interactive UI checks when that is more efficient than setting up automation and the user can readily access the running UI.
- When asking the user to verify something, provide short, exact steps and state the specific result to report, such as pass/fail plus any visible error text or screenshot.
- Do not offload work that is easier, faster, or more reliable for the agent to perform.
- If user verification is required, pause only at the point where its result affects the next action; continue all independent work first.

## Communication

- Keep progress updates and final reports concise and proportional to the task.
- Summarize tool results instead of pasting large outputs unless the raw details are needed for a decision.
- State when a check was intentionally omitted because it would be redundant or disproportionate.
- Report the incremental commits created and any remaining uncommitted files.
