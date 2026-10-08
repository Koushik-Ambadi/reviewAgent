# Agent Working Policy

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
