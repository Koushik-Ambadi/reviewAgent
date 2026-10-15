# LLM remediation input readiness audit

- Status: point-in-time audit
- Reviewed: 2026-10-15
- Scope: generated review reports, executable default policy, naming and
  repository-structure checks, and placeholder remediation
- Evidence: report versions 2.0 through 2.2 under `workspace/runs/`, with
  `20261013_160052_bd9a5d2b` used as the latest representative run
- Related: [`run-result.md`](../contracts/run-result.md),
  [`naming-policy-audit.md`](naming-policy-audit.md), and
  [`architecture.md`](../engineering/architecture.md)

## Question and decision standard

The proposed model input is one failed check at a time, containing its failed
cases, failure locations, failed rules, and the original policy for that check.
This audit distinguishes two outcomes:

1. **Exact candidate**: that bundle is sufficient to derive an unambiguous
   policy-compliant replacement or action.
2. **Safe patch**: that bundle is sufficient to edit the repository without
   guessing semantic intent, ownership, dependencies, or the true edit target.

A check is directly solvable only when both outcomes are true. A syntactically
valid suggestion is not a directly solvable patch when repository-wide rename
impact or the correct source location is unknown.

## Executive result

No currently generated failed-check bundle is sufficient for an unattended,
safe repository patch as-is. Some naming rules are sufficient for an exact
replacement candidate, but every symbol rename still needs declaration and
reference context, source ownership, and a real edit span.

The current placeholder remediation is a presentation template, not a policy
solver:

- `PlaceholderRemediationProvider` receives only the check and failed cases;
  it is not passed the executable policy despite the provider ID
  `policy-template-remediation-v2`.
- It repeats atomic reason strings and selects static actions by `check_id`.
- It neither proposes a replacement nor reads source, symbol references,
  generated-code ownership, build context, or API/linkage impact.
- `build_agent_detailed_report` further flattens failures into text, discarding
  stage/check/case structure and any possibility of a structured policy join.

The latest representative report has 131 failed cases: 3 required paths and
128 symbol-naming cases. The Analysis stage has inventory but no checks. Only
`required_paths` is currently executed from the repository-structure policy;
the other configured structure validators are imported but not run.

## Check-by-check classification

| Check | Latest failures | Exact candidate from proposed bundle? | Safe patch from proposed bundle? | Missing context |
|---|---:|---|---|---|
| `required_paths` | 3 | No. The bundle says what is missing, not what content or generation process creates it. | No | Path kind, required contents/template, generated-vs-source-owned status, build/bootstrap command, repository tree, and evidence that the policy requirement is applicable. `build/` and `node_modules/` especially look generated and should not be blindly created or committed. |
| `function_names` | 2 | **Mixed.** Prefix, letter-case, illegal-character, doubled/trailing-underscore rules can yield an exact candidate. Maximum length and missing/semantic description cannot. | No | Definition/declaration and all references, linkage/API/ABI status, owning module, generated-code status, source excerpt, exact token span, collision search, and compile/test verification. Length failures require a human-meaningful abbreviation. |
| `macro_names` | 0 latest; 8 in the persisted remediation example | **Usually yes** for uppercase, module prefix, illegal characters, and doubled/trailing underscores. Missing description is semantic. | No | Definition and uses, exact replacement span/value, collision search, public-header/generated-code ownership, conditional-compilation context, and whether the macro is object-like or function-like. |
| `type_names` | 16 | **Mixed.** Prefix/suffix and lexical cleanup can yield a candidate when existing semantic text can be preserved. A missing description cannot. | No | True declaration origin, typedef/enum/struct relationship, all uses, external/platform/generated ownership, public ABI/serialization impact, collision search, and exact token span. Current locations can identify a use in the translation unit rather than the declaration. |
| `enum_constant_names` | 60 | **Usually yes** for module prefix, uppercase, and lexical cleanup. Overlength or missing description is semantic. | No | True enum declaration origin, deduplicated symbol identity, all references, external/protocol value ownership, generated-code status, collision search, and exact token span. Current results repeat header constants across translation units. |
| `parameter_names` | 4 | No for the observed minimum-length failures: `p` does not reveal the parameter's purpose. An absent name also needs declaration/definition pairing. | No | Owning function, full signature, parameter type and position, function body or declaration/definition pair, nearby documentation, all same-scope names, and generated/public-header ownership. |
| `local_variable_names` | 0 latest; failures exist in earlier reports | **Mixed.** Pointer suffix and lexical cleanup can yield a candidate; short, long, or purpose-based names cannot. | No | Owning function and scope, declaration/type, uses, body excerpt, role classification for loop-counter/temporary exemptions, collision search, and exact token span. |
| `array_sizes` | 0 in reviewed runs | No for the policy's possible numeric/identifier failures. “Use a symbolic size” does not identify the symbol to use or define. | No | Full declaration and initializer, resolved constant-expression/type information, existing constants and visibility, intended dimension meaning, declarations shared across headers/sources, and compile context. |
| `global_variable_names` | 46 | No in general. The policy grammar gives allowed segments, but the report omits the variable type and semantic intent needed to choose type/size/unit/description segments. Some suffix-only failures could yield a partial candidate. | No | Declaration type/canonical type, storage/linkage, initializer, comments and uses, module/unit semantics, all references, generated/exported ownership, exact token span, collision search, and public ABI/calibration/tooling impact. |

## Rule classes that can produce deterministic candidates

These rules can be handled by a deterministic transformer or an LLM without
additional semantic context, provided the existing name contains a usable
description:

- add or correct a known module prefix;
- convert letters to required case;
- add a fixed suffix such as `_t`, `_ptr`, or `_ptr_ptr` when symbol type is
  supplied;
- remove a leading, trailing, or repeated underscore;
- replace characters outside a fixed identifier alphabet.

Even for these rules, applying the rename requires source ownership, a correct
declaration location, complete references, collision checking, and verification.
The exact-candidate class should therefore return a proposed rename and
confidence, not silently edit code.

The following rule classes are not directly solvable from a failed case plus
policy:

- maximum/minimum length when a meaningful expansion or abbreviation must be
  chosen;
- missing or insufficient semantic description;
- parameter/local names whose purpose depends on the enclosing function;
- global naming grammar whose segments depend on actual type, engineering unit,
  linkage, calibration role, or domain meaning;
- symbolic array dimensions;
- missing repository paths whose content or generation lifecycle is unknown;
- source-policy rules marked `manual`, such as purpose, keyword/library
  collision, ISR/task suffix applicability, and macro behavioral safety.

## Problems in the present report/remediation contract

1. **Policy is referenced, not captured.** Reports contain policy name/version,
   but not the exact effective rule objects or a policy hash. Loading today's
   `default.yaml` can give a different policy from the one that produced an old
   report.
2. **Reasons are prose.** Rule IDs are embedded in strings; `required_paths`
   reasons have no rule ID. There are no structured `actual`, `expected`,
   validator, or applicability fields.
3. **Locations are not edit targets.** Function/macro findings use useful file
   lines, while type/enum/parameter/local locations are colon-composed display
   strings. Some extracted header declarations are attributed to each parsed
   `.c` translation unit.
4. **Duplicate symbols are not normalized.** Included typedefs and enum
   constants can produce repeated cases, inflating the 60 enum failures and
   inviting duplicate edits.
5. **Source facts are dropped.** `analysis/symbols.json` often has type,
   storage, raw declaration, function bounds, enum value, and macro replacement
   facts, but naming cases and remediation input do not carry or join them.
6. **No ownership boundary exists.** Generated, third-party, platform, public
   API, model-generated, and locally owned symbols are indistinguishable.
7. **No rename impact exists.** The bundle has no declaration/reference set,
   collision result, ABI impact, or build/test plan.
8. **Grouping is too coarse for reasoning.** The placeholder groups by check.
   Large checks should preserve all reasons per case but partition work by
   `check_id + rule_id set + ownership class`, after duplicate symbol cases are
   collapsed.

## Minimum model input contract

Each remediation request should use the immutable policy snapshot from the run,
with module placeholders already resolved, rather than reloading the current
policy file.

```json
{
  "run": {
    "run_id": "...",
    "module": "shunt",
    "policy_name": "ABS Default Policy",
    "policy_version": "4",
    "policy_hash": "...",
    "source_revision": "..."
  },
  "group": {
    "stage_id": "symbol_naming",
    "check_id": "function_names",
    "rules": [
      {
        "rule_id": "ABS-SCS-16.1.e",
        "mode": "automatic",
        "validator": "starts_with",
        "resolved_expected": "Shunt_",
        "reason_template": "..."
      }
    ]
  },
  "cases": [
    {
      "case_id": "...",
      "symbol_id": "stable identity",
      "name": "shunt_getcurrent_ibatt_ma",
      "finding": {
        "rule_id": "ABS-SCS-16.1.e",
        "actual": "shunt_",
        "expected": "Shunt_",
        "message": "..."
      },
      "location": {
        "file": "src/shunt.c",
        "start_line": 210,
        "start_column": 1,
        "end_line": 210,
        "end_column": 27,
        "origin_file": "src/shunt.c"
      },
      "symbol": {
        "kind": "function",
        "type": "status_t (...) ",
        "scope": "global",
        "linkage": "external",
        "generated": false,
        "owned": true
      },
      "source": {
        "declaration": "...",
        "context": "small relevant excerpt"
      },
      "references": ["structured locations"],
      "collision_check": "clear"
    }
  ],
  "verification": {
    "required": ["rerun affected check", "compile affected targets"],
    "available_commands": ["repository-approved commands"]
  }
}
```

Check-specific additions are still required:

- `required_paths`: expected path kind/content, template or producer, lifecycle,
  and whether it belongs in source control;
- parameters/locals/functions: enclosing function signature/body and comments;
- globals: canonical type, initializer, engineering unit evidence, storage,
  linkage, and calibration/export metadata;
- types/enums: true declaration/definition origin and ABI/protocol ownership;
- arrays: complete declaration/initializer and constant-expression resolution;
- macros: replacement body, macro kind, conditions, and call/use sites.

## Recommended operating policy

Use three remediation dispositions:

- `AUTO_CANDIDATE`: return a deterministic proposed replacement for lexical
  rules, but apply only after ownership/reference/collision gates pass.
- `CONTEXT_REQUIRED`: request the check-specific context listed above, then ask
  the model for a candidate and rationale.
- `HUMAN_DECISION_REQUIRED`: use when policy applicability, domain semantics,
  generated-source ownership, public compatibility, or required artifact
  lifecycle cannot be established mechanically.

The model response should remain a proposal containing replacement, affected
files, assumptions, confidence, and verification steps. Patch application
should be a separate governed action followed by the affected check and a
compile/test gate. This preserves the useful current grouping and response
wrapper without treating placeholder guidance as an implemented fix.
