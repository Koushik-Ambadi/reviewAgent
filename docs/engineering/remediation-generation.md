# Remediation Generation Module

- Status: living
- Maturity: prototype
- Last verified: 2026-10-17
- Implementation: `src/repo_remediation/`
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
| `contracts.py` | Stable provider/error/transport protocols |
| `adapters/openai_responses.py` | OpenAI HTTP, timeout, retry, and transport evidence |
| `generation/model_selection.py` | Versioned model and inference profile |
| `generation/prompt_builder.py` | Check-specific compact prompt and private references |
| `generation/response_contract.py` | Strict output schema, parsing, and correlation |
| `generation/candidate_validation.py` | Full local policy rerun |
| `context.py` | Trusted developer-context gates and questions |
| `hierarchy.py` | Uniform per-case state, merge, legacy projection, derived views |
| `results.py` | Provider output to report-compatible suggestions/questions/limits |
| `observability/` | Redaction, immutable turns, and normalized model metrics |
| `providers.py` | OpenAI/offline workflow composition only |
| `app/services/remediation_service.py` | Run/check aggregation and artifact persistence |

The dependency direction is contracts/domain helpers → generation/adapters →
provider workflow → application service → API/UI. Model selection, prompt
profiles, output validation, and measurements can change independently without
changing the report checks or transport adapter.

No empty evaluation or experiment package is created. When a real comparison is
defined, authored benchmark definitions belong outside generated runs, and each
run must identify model profile, prompt profile, code revision, frozen cases,
metrics, and selection rule.

## Persisted hierarchy

```text
run
└── check remediation (one root per check)
    ├── case_results[] (one row per failed case)
    │   ├── not_requested + candidate_name: null
    │   ├── candidate_ready
    │   ├── input_required
    │   └── unsupported
    └── turns[]
        └── parent_turn_id → prior request/answer turn
```

A case request updates one child. A full-check request targets only
`not_requested` children. Context answers target their case IDs and append a new
turn to the same check root. Legacy plans without `case_results` are normalized
from their existing suggestions/questions/limitations before an update.

## Model input compiler

For each batch, `compile_remediation_prompt` selects a versioned check-specific
prompt profile, creates prompt-local references
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

## Context flow

The UI offers an optional context box for every case before the first call.
Blank values are omitted. Supplied values can prevent a parameter/global/semantic
question round trip. If context remains insufficient, either the local trusted
context gate or the model returns a specific question; the answer is passed in a
new child turn and does not create a second plan.

Function prompts permit conservative abbreviation for length failures but
forbid invented operations or domain meaning. Parameter/local/array/macro/type/
enum profiles ask for their specific semantic role when absent. Global prompts
forbid inventing module, data type, size, unit, or meaning segments.

## Measurement artifacts

- `remediation-calls.jsonl` owns redacted raw diagnostic evidence.
- `remediation-metrics.jsonl` owns normalized model/prompt IDs, response ID,
  token categories, attempt count, measured transport latency, cases, and turn
  outcome.
- `remediation.json` and `report.json.remediation` own the latest product view.

Latency/token metrics diagnose cost and performance; candidate pass rate and
context-question quality require a separate frozen evaluation corpus.

## Planned extension points

- Model selection: compare named `RemediationModelProfile` configurations on a
  frozen corpus before changing the default.
- Prompt tuning: version prompt compilers and compare them on a frozen corpus.
- Output validators: add semantic and cross-field checks after schema parsing.
- Candidate feedback: optionally make one bounded corrective call when local
  validation rejects a candidate; retain parent/child evidence and call cost.
- Evaluation: separate format validity, policy pass rate, unchanged-candidate
  rate, context-question quality, latency, and token cost.
- Context enrichment: add source-derived facts per check through typed inputs;
  do not restore broad report payloads to the prompt.
- Candidate conversation: add bounded per-case revision branches only after a
  typed message/history/budget contract exists.

No live call was made for this refactor. The next retained call is the evidence
gate for whether the compact prompt mitigates BUG-005.
