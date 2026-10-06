# Naming policy rule audit

- Status: living
- Owner: project maintainer
- Last reviewed: 2026-10-06 at revision `c603a69`
- Update trigger: naming policy, checker, source rule, or applicability change
- Related: [`review-check-catalog.md`](review-check-catalog.md),
  [`decisions-and-lessons.md`](../engineering/decisions-and-lessons.md)

## Purpose and scope

This audit records how the active symbol-naming checks derive their behavior
from `src/repo_review/policies/default.yaml` and compares those checks with
the naming requirements in
[`sources/software-coding-standard.docx`](sources/software-coding-standard.docx).
The machine-readable rulebook at
[`coding-standard-rulebook.yaml`](coding-standard-rulebook.yaml)
provides stable rule IDs and source page references. This audit covers the
existing naming checks; it does not claim that every rule in the full coding
standard is automated.

## Changes made

- Function checks now read individual rules from policy. The module prefix is
  explicitly declared as `{module}_` with title-case expansion, matching the
  standard's `Battsm_get_state()` example. The maximum length, leading
  underscore prohibition, and word format are separate rule outcomes.
- Macro checks now read character, uppercase, module-prefix, underscore, and
  description rules from policy. Macro prefixes expand the module placeholder
  to uppercase. Applicability exclusions carry their reason in policy.
- Type, enum-constant, local-variable, and parameter checks now evaluate
  policy-declared atomic rules instead of applying a hidden combined pattern.
  Enum constants now enforce the configured uppercase module prefix and
  description requirement.
- Pointer and pointer-to-pointer suffix requirements are now enforced for
  locals and globals using their extracted C type, with the suffix values
  declared in policy. Parameter rules follow the source's three-character
  minimum and named-parameter requirement; parameters are not incorrectly
  subjected to the full local-variable rule set.
- Array-size literal forms and symbolic-identifier recognition are configured
  in policy. Failures identify the policy rule and tell the developer to use a
  named size.
- Global-variable diagnostics now identify the corresponding source or local
  policy rule. Segment positions and separators are explicit policy settings.
- Automatic naming failures include a rule ID and a corrective explanation.
  Rules that need external symbol lists or semantic judgment are recorded as
  `manual` and are not silently run by the checker.

## Source coverage and current limits

| Check | Automatic policy coverage | Recorded manual items |
|---|---|---|
| Function names | `ABS-SCS-16.1.c`, `.d`, `.e`, `.g` | `.a` keyword collision, `.b` C library collision, `.h` meaningful purpose, `.i` set/get recommendation, `16.4.a` thread/task/process suffix, `16.5.b` ISR suffix |
| Macro names | `ABS-SCS-15.6.a`, `.b`, `ABS-SCS-16.1.f`, and explicit project-format rules | `ABS-SCS-11.1.d`, `ABS-SCS-15.6.c`, and `ABS-SCS-16.3.a` through `.b.iv` for function-like macro safety |
| Type names | `ABS-SCS-15.1.a` and configured length/identifier rules | `ABS-SCS-15.1.b` typedef declaration requirement; `ABS-SCS-15.5.c` structure-member naming |
| Enum constants | `ABS-SCS-15.6.b` plus the project's explicit uppercase/length rules | The source wording under 15.6 is ambiguous; the rulebook resolves it for macro and enum-constant prefixes |
| Local variables | `ABS-SCS-17.c` through `.e`, `.g`, `.i`, `.j` | `.a`, `.b`, `.f`, `.h`, and `.k` role-based exemptions |
| Parameters | `ABS-SCS-16.2.e` name presence and `ABS-SCS-17.e` minimum length | Semantic meaning in 16.2.e; `.k` exemption is documented |
| Globals | `ABS-SCS-17.c` through `.e`, `.g`, `.i`, `.j`, plus configured ABS project schema | `.a`, `.b`, `.f`, `.h` need keyword/library inventories or semantic review |
| Array dimensions | Project policy's symbolic-size extension | Name resolution, visibility, integral-constant evaluation, and broader C declaration cases |

## Findings resolved

1. **Function module prefix existed only in checker code.** It was not an
   explicit function rule in policy. Policy now declares `ABS-SCS-16.1.e`, and
   the checker no longer computes an independent expected prefix.
2. **Function regex collapsed distinct failures.** It has been split into
   source-linked rules for leading underscore, 31-character maximum, module
   prefix, and procedure word format.
3. **Macro checks had policy fields but their failures were embedded in code.**
   The criteria and messages now live alongside atomic policy rules, including
   the uppercase module prefix and description requirement.
4. **Enum description policy was unused.** The check now enforces it as a
   separate rule.
5. **Pointer suffixes were present in some policy blocks but not enforced.**
   The local and global checks now apply configured suffixes based on pointer
   depth.
6. **Policy did not describe array literal recognition.** Integer, floating,
   hexadecimal floating, and identifier patterns are now policy values.
7. **Global pointer names conflicted with the global schema parser.** The
   validator now checks and removes the configured pointer suffix before
   validating the remaining data-type, module, unit, and description segments.

## Remaining blockers

- The source standard requires avoiding C/C++ keywords and C Standard Library
  name collisions. The project does not yet provide versioned keyword and
  library-name inventories for the configured language/compiler profile.
- The source's generated/third-party function-name length exemptions require
  provenance. A name regex is not sufficient evidence, so those cases remain
  manual until provenance is available to a run.
- Thread/task/process and ISR function roles are not yet classified in symbol
  metadata. Their required suffix rules are listed as manual policy rules.
- Meaningful function/variable names and the numeric-value rule require
  semantic review; lexical checks cannot establish intent.
- `ABS-SCS-17.k` exemptions depend on identifying loop counters and local
  temporaries. The current symbol inventory does not reliably classify those
  roles, so that exemption is documented but not applied by guessing from a
  name.
- Function-like macro safety rules are recorded under the macro policy but are
  not yet implemented as AST/preprocessor checks.
- Array checks do not yet resolve each identifier to a visible integral
  constant declaration.

The checks intentionally do not report these unresolved items as passes. The
next implementation phase can add the required inventories and AST evidence
without changing the stable rule IDs or policy ownership model.
