# Remediation Generation Module

- Status: living
- Maturity: prototype
- Last verified: 2026-10-16
- Implementation: `src/repo_remediation/`, especially `llm/`
- Update trigger: model input/output, model settings, candidate validation,
  retry/evaluation policy, or remediation orchestration changes

## Responsibility and boundary

The module converts failed review findings into rename candidates or targeted
context questions. It does not edit source, approve a rename, search references,
or prove repository-wide rename safety.

The report policy and generated finding are authoritative application data. The
model receives a compiled prompt projection, not the report serialization or
executable validator configuration. The returned candidate is untrusted until
the application reruns the complete executable check policy.

## Current module structure

| Path | Responsibility |
|---|---|
| `llm/model_settings.py` | Model identity and inference/output settings |
| `llm/prompting.py` | Compact prompt compilation and private case-reference mapping |
| `llm/output.py` | Strict output schema, parsing, and case-reference restoration |
| `llm/candidate_validation.py` | Full local policy rerun for returned candidates |
| `providers.py` | Current orchestration, preflight/context decisions, transport, trace formation, and compatibility provider |
| `app/services/remediation_service.py` | Run lookup, persistence, call log, and turn lineage |

`providers.py` remains a compatibility/orchestration concentration, not the
target home for future model selection, prompt variants, output validators, or
evaluation logic. Those concerns now have explicit `llm/` extension points and
can move independently without changing the API/UI remediation contract.

## Model input compiler

For each batch, `compile_remediation_prompt` creates prompt-local references
(`C1`, `R1`) and keeps their mapping to persistent case IDs outside model input.
The model sees only:

- each current symbol name;
- optional developer context when supplied;
- one resolved, human-readable line for each atomic rule that actually failed.

It does not receive source locations, persistent IDs, rule IDs, validator names,
validator operands, report modes, passing rules, or applicability exclusions.
Those fields remain available to application logging, reporting, and local
validation. Applicability exclusions belong before finding creation; a retained
failed case has already passed that gate.

For the retained `Shunt_msgcountercheck_Init` example, this reduces developer
plus user message content from 3,103 characters to 424 characters. This is a
message-character comparison, not a complete token or cost measurement because
the strict output schema and API framing also consume input tokens.

## Output and validation flow

1. Structured Outputs require one result per prompt-local case reference.
2. `output.py` parses JSON and rejects missing, duplicate, or unknown references.
3. Private application case IDs are restored after parsing.
4. An unchanged/empty candidate remains a limitation.
5. `candidate_validation.py` reruns the complete check policy, including rules
   omitted from the prompt, and rejects a candidate that creates another failure.
6. The service retains the observable request, raw response, parsed output,
   validation result, and turn lineage.

The strict schema guarantees shape, not naming correctness. Official OpenAI
guidance likewise distinguishes schema adherence from model mistakes and
recommends clearer instructions, examples, simpler subtasks, and evals when
content is wrong.

## Planned extension points

- Model selection: introduce named, evaluated profiles through
  `RemediationModelSettings`; do not scatter model names across workflows.
- Prompt tuning: version prompt compilers and compare them on a frozen corpus.
- Output validators: add semantic and cross-field checks after schema parsing.
- Candidate feedback: optionally make one bounded corrective call when local
  validation rejects a candidate; retain parent/child evidence and call cost.
- Evaluation: separate format validity, policy pass rate, unchanged-candidate
  rate, context-question quality, latency, and token cost.
- Context enrichment: add source-derived facts per check through typed inputs;
  do not restore broad report payloads to the prompt.

No live call was made for this refactor. The next retained call is the evidence
gate for whether the compact prompt mitigates BUG-005.
