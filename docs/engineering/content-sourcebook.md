# Technical Content Sourcebook

- Status: living index of content candidates
- Owner: project maintainer
- Created: 2026-10-06
- Last reviewed: 2026-10-06
- Update trigger: reusable technical lesson, publication, or confidentiality review
- Source of truth for: provenance links and possible narrative angles
- Does not own: blog/social/portfolio drafts, publication status, or audience metrics

This file keeps story-ready facts close to engineering evidence without turning
the project record into marketing copy. Before publishing, remove organization-
specific standards, repository names, paths, input code, customer details, and
security-sensitive implementation specifics unless permission is explicit.

## Reuse rules

- Link every technical claim to a commit, artifact, or owning document.
- Say “recorded as working” when no reproducible test survives.
- Do not present failure-count changes as accuracy improvements without labeled
  ground truth.
- Distinguish the open-source/service code from proprietary or third-party
  embedded inputs.
- Preserve limitations; they often make the engineering story more credible.
- Create channel-specific drafts in a separate content project.

## Story candidates

### INSIGHT-001 — Why embedded C review needs the real build

- Topic: compiler-assisted static analysis
- Problem/stakes: include paths, defines, generated headers, target flags, and
  conditional compilation decide what the parser sees.
- First approach: direct libclang AST prototype.
- Evidence/turn: `9755213` added CMake/Ninja `compile_commands.json`; current
  extractor queries the compilation database per file.
- General lesson: for nontrivial C, parsing should begin from the build's view of
  the program, not just the source tree.
- Good format: deep technical blog or conference talk.
- Caveat: compilation database improves context but does not expose inactive
  conditional branches or final linked-binary behavior.
- Sources: history entries through 25 May, D001, architecture analysis section.
- Reuse status: candidate; confidentiality review required for input examples.

### INSIGHT-002 — AST structure plus surgical source recovery

- Topic: hybrid parsing design
- Problem: the AST located an array declaration, but the desired bracket spelling
  was not reliably available in prototype tokens.
- Change: `5fd77db` used the cursor location to recover suffixes from source text.
- Lesson: use a semantic parser for structure and a narrowly scoped lexical
  fallback for fidelity; document where the fallback fails.
- Good format: code walkthrough, short post, or “what I learned” thread.
- Caveat: do not generalize the single-line heuristic as a complete C parser.
- Sources: D002 and the 17 May history entries.
- Reuse status: candidate.

### INSIGHT-003 — The refactor that deleted abstractions

- Topic: architecture maturity
- Problem: the first modular split introduced generic stages and many context
  types before their variability was proven.
- Change: `f435aea` removed generic stage machinery and regrouped compile/AST
  responsibilities as `analysis`.
- Lesson: modularity is responsibility clarity, not maximum file/class count.
- Good format: engineering blog or interview portfolio story.
- Caveat: rationale is partly inferred from diffs; phrase it as retrospective
  interpretation rather than a documented contemporary motive.
- Sources: D005, 27–30 May history.
- Reuse status: candidate.

### INSIGHT-004 — One workspace, three owners

- Topic: orchestration boundaries
- Problem: review handled ingestion, workspace lifecycle, checks, reporting, and
  build, risking duplicate extraction and coupled source handling.
- Change: `4217116` separated `orchestrator`, `repo_review`, and `repo_build` but
  kept one run workspace.
- Lesson: split responsibility without duplicating state; a shared run identity
  can connect independent workflows.
- Good format: architecture case study or portfolio page.
- Strong evidence: the contemporary
  [archived daily log](../archive/daily_log.txt) states the reasoning.
- Caveat: current build lookup still uses report metadata instead of a dedicated
  manifest.
- Sources: D004, architecture diagram, 2 June history.
- Reuse status: candidate.

### INSIGHT-005 — A realistic fixture can damage the repository

- Topic: artifact governance
- Problem: early commits mixed application changes with millions of lines of
  firmware, build output, and reports.
- Change: run workspaces became ignored and a 655-file generated tree was removed
  in `62f1792`.
- Lesson: realism matters, but preserve small fixtures, manifests, hashes, and
  external artifact references—not entire regenerable environments in Git.
- Good format: cautionary post about test-data strategy.
- Caveat: commit statistics include third-party/generated content and are not an
  effort metric.
- Sources: P002 and May history.
- Reuse status: candidate; licensing/confidentiality review required.

### INSIGHT-006 — “Dockerized on Linux” did not mean every workflow was portable

- Topic: honest cross-platform claims
- Problem: analysis required Linux compiler/libclang fixes; build still called a
  Windows batch script.
- Change: `6947306` added container/toolchain resolution; current builder remains
  Windows-specific.
- Lesson: test and state portability per workflow, not per repository.
- Good format: short blog, retrospective, or deployment checklist.
- Sources: P004, Dockerfile, repo_build builder.
- Reuse status: candidate.

### INSIGHT-007 — A proof-of-concept MCP layer that was intentionally removed

- Topic: agent architecture and reversible experiments
- Problem: agents needed a tool-friendly interface.
- Attempt: local MCP client/server/tool and role skills in `196e282`/`b69bfda`.
- Decision: delete local MCP in `f0d40b9` and keep remote MCP separate; later add
  agent-focused HTTP summaries.
- Lesson: deleting a successful prototype can be an architectural outcome when
  the deployment boundary changes.
- Good format: agent-system architecture story.
- Caveat: original remote-boundary rationale and remote deployment proof are not
  retained; do not invent cost/security claims.
- Sources: D007, July history.
- Reuse status: candidate.

### INSIGHT-008 — Contract first, consumers second, compatibility last

- Topic: schema migration
- Problem: ad hoc issue dictionaries constrained adding checks and serving UI/
  agent consumers.
- Change: `095ae1a` created Run/Stage/Check/Case; `46e6e21` finished internal
  propagation; `97084dd` and `0269843` migrated agents/UI.
- Lesson: make the core contract explicit, name deferred consumers, and use a
  bounded compatibility adapter.
- Good format: multipart engineering series or system-design portfolio item.
- Caveat: compatibility removal is still unresolved, which is part of the story.
- Sources: D008, August/October history.
- Reuse status: candidate.

### INSIGHT-009 — Configuration-driven is not policy-driven until logic moves

- Topic: compliance architecture
- Problem: checkers read configuration but still hid regexes, combined failures,
  and reason text.
- Change: `b6792eb` moved atomic criteria into YAML; `c603a69` documented source
  coverage and manual blockers.
- Lesson: true policy ownership includes applicability, criterion, reason,
  source identity, and explicit non-automation—not only constants.
- Good format: technical article on policy-as-data or compliance tooling.
- Strong evidence: implementation diff plus policy audit.
- Sources: D009 and the
  [`naming-policy-audit.md`](../standards/naming-policy-audit.md).
- Reuse status: candidate; standard text may have licensing restrictions.

### INSIGHT-010 — Same symbols, different policy, different outcomes

- Topic: controlled change analysis
- Observation: three October reports share the exact `symbols.json` SHA-256 and
  367-case population while policy versions 2, 3, and 4 report 196, 168, and 161
  failures respectively.
- Useful lesson: freezing an intermediate representation helps isolate policy/
  checker behavior from extraction changes.
- What cannot be claimed: fewer failures do not prove higher accuracy; there is
  no labeled expected-result set or recorded Git revision.
- Good format: experiment-method post showing how to make a careful claim.
- Sources: retained-run table/hashes in
  [`testing-and-replay.md`](testing-and-replay.md).
- Reuse status: candidate; sanitize module/result details.

### INSIGHT-011 — A failed test is valuable project evidence

- Topic: test-contract drift
- Observation: the current naming manual script fails with `KeyError: 'rules'`
  after atomic policy migration.
- Lesson: a checked-in test file is not evidence of coverage; execute it, require
  nonzero failures, and make fixtures load the owned contract.
- Good format: brief retrospective or testing checklist.
- Sources: P006 and current verification table.
- Reuse status: candidate.

### INSIGHT-012 — The missing manifest limited an otherwise strong audit trail

- Topic: reproducibility
- Problem: retained reports contain useful versions/timestamps and repeated
  outputs, but not code revision, command, input checksum, or environment.
- Contemporary clue: the June daily log proposed ORCH-002 metadata persistence.
- Lesson: capture provenance at run creation; it cannot be reconstructed later
  with the same confidence.
- Good format: “what I would design next” section in a portfolio case study.
- Sources: P007, G02, run inventory.
- Reuse status: candidate.

## Portfolio-ready project outline

Use this only as a source map, not final copy:

1. Problem: review embedded C repository structure and naming against an
   organization-specific coding standard.
2. Constraints: real build context, compiler/preprocessor visibility, large
   firmware repositories, cross-platform native tooling, human and agent users.
3. Initial prototype: libclang extraction and structure validation.
4. First product slice: policy checks, report, web UI, build trigger.
5. Architectural evolution: isolated run workspace; orchestration/review/build
   split; analysis/check/report packages.
6. Contract evolution: ad hoc issues to typed RunResult hierarchy.
7. Policy evolution: hard-coded/combined checks to source-linked atomic YAML.
8. Evidence: commit timeline, retained artifacts and hashes, rulebook/catalog,
   policy audit.
9. Honest limitations: stale tests, missing provenance, security/operations
   boundary, partial compliance coverage.
10. Next step: security + manifest + automated baseline before broader rules.

## Short-form idea bank

- “A compilation database is an API between your build and your analyzer.”
- “Why an AST tool sometimes still needs the original source line.”
- “The refactor where I removed my own framework.”
- “One run workspace can serve review, UI, agents, and builds.”
- “Configuration values are not the same as policy ownership.”
- “Fewer static-analysis failures do not automatically mean better accuracy.”
- “A local agent integration taught me where the service boundary belonged.”
- “Generated artifacts made my Git history huge—here is the retention model I
  would use now.”
- “The test existed, but the contract had moved: what execution revealed.”
- “The metadata I wish every long-running engineering job captured.”

Each statement should be expanded only after checking its cited source and
applying organizational disclosure policy.
