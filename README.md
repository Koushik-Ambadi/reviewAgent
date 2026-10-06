# Review Agent

Review Agent is a policy-driven repository review service for embedded C
projects. It accepts a repository ZIP, creates an isolated run workspace,
generates a CMake compilation database, extracts C symbols with libclang,
applies repository-structure and naming checks, persists a versioned JSON
report, and renders the result in a FastAPI-hosted web UI. A separate endpoint
can invoke the uploaded firmware repository's `cmake-build.bat`.

The current checkout documents 31 linear commits from 14 May through
5 October 2026. The engineering record was reconstructed on 6 October 2026
from Git history, current code, retained run artifacts, manual tests, and the
existing project notes. Claims that cannot be proved are explicitly marked as
recorded, inferred, or unknown.

## Start here

- [Documentation index](docs/README.md)
- [Engineering evidence index](docs/engineering/evidence-index.md)
- [Project history and daily log](docs/engineering/project-history.md)
- [Current architecture and module guide](docs/engineering/architecture.md)
- [Decisions, problems, and lessons](docs/engineering/decisions-and-lessons.md)
- [Testing, retained runs, and replay](docs/engineering/testing-and-replay.md)
- [Current limitations and roadmap](docs/engineering/roadmap-and-gaps.md)
- [Developer skills evidence](docs/engineering/developer-skills-evidence.md)
- [Content sourcebook](docs/engineering/content-sourcebook.md)

Existing domain references remain authoritative for their narrower subjects:

- [Review check catalog](docs/standards/review-check-catalog.md)
- [Naming policy audit](docs/standards/naming-policy-audit.md)
- [RunResult contract](docs/contracts/run-result.md)
- [Coding-standard rulebook](docs/standards/coding-standard-rulebook.md)

## Current execution path

```text
POST /api/review (ZIP)
  -> app service
  -> orchestrator workspace and ingestion
  -> repo_review structure -> analysis -> naming -> reporting
  -> workspace/runs/<run_id>/report.json
  -> browser or agent-oriented response
```

The supported development launcher is `run.bat`, which activates `venv313`,
sets `PYTHONPATH=src`, and starts Uvicorn with reload. Reproduction constraints,
safer historical replay commands, and known platform mismatches are documented
in [Testing, retained runs, and replay](docs/engineering/testing-and-replay.md).
