# Review Check Catalog and Implementation Backlog

## Purpose

This file is the implementation map for converting the ABS Software Coding
Standard into small, independently actionable review checks. It is not an
implementation and does not change the standard.

Primary source:

- `ABS_Software_Coding_Standard_Rulebook.yaml` (`schema_version: 2.0.0`, 211 rules)

Supporting sources:

- `Software Coding Standard 1.docx` (document 0151, revision 2.4)
- `Software Configuration Management Plan.docx` (document 0179)

The YAML rule IDs below preserve traceability to the original document,
including its section and page metadata. Before implementing a check, copy its
exact applicability, exceptions, verification method, and source reference from
the YAML into the check policy or check documentation.

## Status and Automation Legend

- `[EXISTING]`: a check runner exists now.
- `[PARTIAL]`: some deterministic cases are supported, but the standard is not
  fully represented.
- `[PLANNED]`: suitable for deterministic implementation but not present yet.
- `[CONFIG]`: deterministic only after project-specific policy is supplied.
- `[REPO]`: requires cross-file or repository-wide analysis.
- `[SEMANTIC]`: requires program meaning, data-flow, or intent analysis.
- `[MANUAL]`: requires human evidence or judgment; do not report an automatic
  PASS without evidence.
- `[INACTIVE]`: explicitly inactive in the current standard phase.
- `[DECISION]`: the source standard is ambiguous or contradictory; resolve the
  policy decision before implementation.

Each leaf below should eventually become either one `CheckResult` or one clearly
identified `CaseResult`. A regex may implement a leaf, but a regex mismatch must
never be the user-facing reason.

## Recommended Pipeline Ownership

```text
Review Run
├── Repository Structure
├── Analysis
│   ├── Source/compile inventory
│   ├── AST and symbol inventory
│   ├── Token and comment inventory
│   ├── Include/dependency graph
│   ├── Control-flow and call graph
│   └── Static-analysis imports
├── File and Module Organization
├── Naming
├── Lexical Formatting
├── Declarations and Types
├── Functions and Interfaces
├── Expressions and Control Flow
├── Comments and Documentation
├── Concurrency, ISR, and Hardware
├── Metrics and Static Analysis
├── Process and Governance Evidence
└── Reporting
```

`Analysis` and `Reporting` are operational stages, not fake collections of
checks. Their `summary` may be absent. Analysis publishes artifacts and
diagnostics; Reporting publishes the report path and serialization diagnostics.

---

## 1. Repository Structure

### 1.1 Generic policy-driven repository checks

```text
Repository Structure
├── Required path exists                         [EXISTING]
├── Required path has expected kind              [EXISTING]
│   ├── File
│   └── Directory
├── Required path contains expected file pattern [EXISTING]
├── Forbidden path does not exist                [EXISTING]
├── Allowed extension by path                    [EXISTING]
├── Forbidden extension by path                  [EXISTING]
├── Required file type by path                   [EXISTING]
├── File size                                    [EXISTING]
│   ├── Global maximum
│   ├── Extension-specific maximum
│   ├── Path-specific maximum
│   └── Empty/minimum-size file
└── Directory tree limits                        [EXISTING]
    ├── Maximum depth
    ├── Maximum file count
    └── Maximum directory count
```

These are platform capabilities rather than direct ABS rule IDs. Their actual
requirements must come from project policy; an empty configuration means “not
checked,” not “passed.”

### 1.2 Project and toolchain artifacts

```text
Project Artifacts
├── Version-control repository/evidence exists             [CONFIG][REPO]
├── Defect-tracking reference/evidence exists              [CONFIG][MANUAL]
├── Architecture/design review evidence exists             [MANUAL]
├── Peer-review evidence exists                            [MANUAL]
├── Automated-scan configuration/results exist             [CONFIG][REPO]
├── Project rule subset/customization exists               [CONFIG][REPO]
├── Deviation register exists when deviations are present  [REPO][MANUAL]
├── Abbreviation table exists and is version controlled    [CONFIG][REPO]
├── Project source/header templates exist                  [CONFIG][REPO]
├── Documentation-generation target/artifact exists        [CONFIG][REPO]
└── Diagram source is version controlled when referenced   [REPO][MANUAL]
```

Rule references: `ABS-SCS-1.MIN_PROCESS`, `ABS-SCS-7.1`, `ABS-SCS-7.2`,
`ABS-SCS-7.3`, `ABS-SCS-7.4`, `ABS-SCS-7.5`, `ABS-SCS-7.6`, `ABS-SCS-8.1`,
`ABS-SCS-8.2`, `ABS-SCS-8.3`, `ABS-SCS-8.4`, `ABS-SCS-9.1`,
`ABS-SCS-11.5.b`, `ABS-SCS-12.2.f`, `ABS-SCS-12.2.REBUILD_DOCS`,
`ABS-SCS-14.4.a`.

### 1.3 Source/header location, pairing, and file identity

```text
Module File Structure
├── Source and header use an allowed configured directory     [CONFIG]
├── Source file has exactly one same-root public header       [REPO][CONFIG]
├── Header has its expected source counterpart                [REPO][CONFIG]
├── Source includes its matching header                       [REPO]
├── Header and source share the configured module root        [REPO][CONFIG]
├── Module-root prefix is unique across repository            [REPO]
├── Header filename does not collide with standard headers    [REPO]
├── Module containing main includes `main` in filename        [REPO]
├── Public header does not include a private header            [REPO][CONFIG]
├── Header does not allocate variable storage                 [REPO]
├── Source file is not included as a header                   [REPO]
├── Include path is relative, never absolute                  [PLANNED]
├── Include is used                                           [REPO][SEMANTIC]
└── Source file has one coherent responsibility               [MANUAL][SEMANTIC]
```

Rule references: `ABS-SCS-14.1.a`, `ABS-SCS-14.1.b`, `ABS-SCS-14.1.c`,
`ABS-SCS-14.1.d`, `ABS-SCS-14.2.a`, `ABS-SCS-14.2.b`, `ABS-SCS-14.2.c`,
`ABS-SCS-14.2.c.i`, `ABS-SCS-14.2.c.ii`, `ABS-SCS-14.2.d`,
`ABS-SCS-14.3.a`, `ABS-SCS-14.3.c`, `ABS-SCS-14.3.d`,
`ABS-SCS-14.3.e`, `ABS-SCS-14.3.f`.

### 1.4 Source-file section order

```text
Source File Order                                           [PLANNED]
├── File comment/header appears first
├── Include section precedes declarations
├── Types/constants/macros precede data definitions
├── Static data precedes function bodies
├── Private prototypes precede public function bodies
├── Public function bodies precede private function bodies
└── Unexpected or duplicate section is reported precisely
```

Rule reference: `ABS-SCS-14.3.b`.

---

## 2. Analysis Artifacts and Prerequisites

These are stage outputs, not standard violations by themselves.

```text
Analysis
├── Compile database
│   ├── Generated successfully
│   ├── Compiler and flags recorded
│   └── Translation-unit coverage recorded
├── AST/symbol inventory
│   ├── Functions and declarations
│   ├── Globals, locals, parameters, and members
│   ├── Typedefs, structs, unions, and enums
│   ├── Object-like and function-like macros
│   ├── Arrays and dimension expressions
│   ├── Storage class, linkage, qualifiers, and attributes
│   └── Source location and generated/third-party provenance
├── Lexical inventory
│   ├── Tokens and operators
│   ├── Whitespace, line endings, and line width
│   ├── Comments and comment-to-node association
│   └── Preprocessor regions
├── Repository graphs
│   ├── Include graph
│   ├── Call graph
│   └── Recursion cycles
├── Function analysis
│   ├── Control-flow graph
│   ├── Data flow and initialization
│   └── Metrics
└── Imported evidence
    ├── MISRA/HIS results
    ├── Compiler diagnostics
    └── Build/documentation results
```

If a prerequisite fails, dependent checks are `SKIPPED` with the dependency
reason. They must not be reported as PASS or as naming failures.

---

## 3. Naming

### 3.1 Common identifier checks

Apply only to symbol kinds for which the referenced rule is applicable.

```text
Identifier Common Rules
├── Is not a C/C++ keyword                         [PLANNED]
├── Does not use a reserved leading underscore    [PLANNED]
├── Does not collide with reserved library name   [REPO][CONFIG]
├── Uses only allowed characters                  [PARTIAL]
├── Does not contain consecutive underscores      [PLANNED]
├── Does not end with underscore                   [PLANNED]
├── Does not exceed 31 characters                  [PARTIAL]
├── Meets minimum length where applicable         [PLANNED]
├── Uses configured module prefix                  [PARTIAL][CONFIG]
├── Uses unambiguous words/abbreviations           [CONFIG][SEMANTIC]
└── Describes purpose rather than representation   [SEMANTIC][MANUAL]
```

Rule references: `ABS-SCS-11.5.a`, `ABS-SCS-11.5.b`, `ABS-SCS-16.1.a`,
`ABS-SCS-16.1.b`, `ABS-SCS-16.1.c`, `ABS-SCS-16.1.d`,
`ABS-SCS-17.a`, `ABS-SCS-17.b`, `ABS-SCS-17.c`, `ABS-SCS-17.d`,
`ABS-SCS-17.f`, `ABS-SCS-17.g`, `ABS-SCS-17.h`, `ABS-SCS-APP-A.1`,
`ABS-SCS-APP-A.2`.

### 3.2 Module and file names

```text
Module/File Name
├── Root starts with configured module abbreviation       [CONFIG]
├── Root prefix length satisfies chosen policy            [DECISION]
├── Root prefix is unique across repository               [REPO]
├── Header uses `.h` suffix                               [PLANNED]
├── Source uses `.c` suffix                               [PLANNED]
├── Header root equals source root                        [REPO]
├── Header name does not shadow standard header           [REPO]
└── Main-bearing module filename contains `main`          [REPO]
```

Rule references: `ABS-SCS-14.1.b`, `ABS-SCS-14.1.c`, `ABS-SCS-14.1.d`.

Decision: source material conflicts on module abbreviation length (`3–6` vs
`3–5`). Store the selected length in policy; do not hard-code either silently.

### 3.3 Function names

```text
Function Name
├── Is not a keyword                                      [PLANNED]
├── Is not a standard-library function                    [REPO][CONFIG]
├── Does not start with underscore                        [PLANNED]
├── Maximum length is 31, unless exempt                   [PLANNED][CONFIG]
├── Starts with configured module prefix                  [PARTIAL][CONFIG]
├── Prefix is followed by exactly one underscore          [PLANNED]
├── First procedure word starts with uppercase letter     [PLANNED]
├── Remaining words use configured snake-case convention [PLANNED]
├── Contains no invalid character                         [PLANNED]
├── Contains no consecutive underscores                  [PLANNED]
├── Does not end with underscore                          [PLANNED]
├── Name expresses purpose/action                         [SEMANTIC]
├── Noun/verb or question form is appropriate             [SEMANTIC]
├── Setter/getter form is used where appropriate          [SEMANTIC]
├── Thread/task/process entry has required suffix         [PLANNED][CONFIG]
└── ISR has `_isr` suffix                                 [PLANNED]
```

Rule references: `ABS-SCS-16.1.a`, `ABS-SCS-16.1.b`, `ABS-SCS-16.1.c`,
`ABS-SCS-16.1.d`, `ABS-SCS-16.1.e`, `ABS-SCS-16.1.g`,
`ABS-SCS-16.1.h`, `ABS-SCS-16.1.i`, `ABS-SCS-16.4.a`,
`ABS-SCS-16.5.b`.

Current implementation is one policy regex and exclusions. Replace the single
“invalid naming pattern” failure with the independent reasons above. Generated
and third-party exemptions must be provenance-based, not name-pattern guesses.

### 3.4 Macro and preprocessor names

```text
Macro Name
├── Does not redefine a language keyword                  [PLANNED]
├── Uses uppercase letters/digits/underscores only        [EXISTING]
├── Starts with configured module prefix                  [EXISTING][CONFIG]
├── Prefix boundary is valid                              [EXISTING]
├── Contains no invalid character                         [EXISTING]
├── Contains no consecutive underscores                  [EXISTING]
├── Does not end with underscore                          [EXISTING]
├── Includes a description after the module prefix        [EXISTING]
├── Header guard matches configured file-derived form     [PLANNED][CONFIG]
└── Exclusion is explicit and attributable                [CONFIG]
```

Rule references: `ABS-SCS-11.1.d`, `ABS-SCS-15.6.a`,
`ABS-SCS-15.6.b`, `ABS-SCS-16.1.f`.

### 3.5 Type, structure, union, and enumeration names

```text
Type Name
├── Uses configured module prefix                         [PLANNED][CONFIG]
├── Contains meaningful description                      [SEMANTIC]
├── Ends with `_t`                                       [PLANNED]
├── Maximum length is 31                                 [PLANNED]
├── Public type uses owning module prefix                 [REPO][CONFIG]
├── Struct declaration is exposed through typedef        [PLANNED]
├── Union declaration is exposed through typedef         [PLANNED]
└── Enum declaration is exposed through typedef          [PLANNED]
```

Rule references: `ABS-SCS-15.1.a`, `ABS-SCS-15.1.b`,
`ABS-SCS-15.1.c`.

### 3.6 Variable names: common, pointer, scope, and schema

```text
Variable Name
├── Common identifier rules
├── Minimum length is 3, including counters               [PLANNED]
├── Does not embed a numeric value defined elsewhere      [SEMANTIC][REPO]
├── Uses required word separation                         [DECISION]
├── Describes purpose                                     [SEMANTIC]
├── Pointer ends with `_ptr`                              [PLANNED]
├── Pointer-to-pointer ends with `_ptr_ptr`               [PLANNED]
├── Narrow short-name exemption is correctly scoped       [SEMANTIC][CONFIG]
├── Global name follows full schema                       [PARTIAL][CONFIG]
│   ├── Type code is valid                                 [EXISTING][CONFIG]
│   ├── Size code is valid                                 [EXISTING][CONFIG]
│   ├── Module code is configured and valid                [EXISTING][CONFIG]
│   ├── Exactly two schema separators are present           [EXISTING]
│   ├── Unit code is controlled and valid                  [EXISTING][CONFIG]
│   ├── Description exists                                 [EXISTING][CONFIG]
│   ├── Description length is 14–22                       [EXISTING][CONFIG]
│   ├── Description uses selected lower-camel convention  [EXISTING][CONFIG]
│   └── Total identifier length does not exceed 31        [EXISTING][CONFIG]
├── Local-variable policy is applied separately           [PLANNED][CONFIG]
├── Parameter policy is applied separately                [PLANNED][CONFIG]
├── Return/output-parameter policy is applied separately  [PLANNED][CONFIG]
├── Structure-member policy is applied separately         [PLANNED][CONFIG]
└── Generated/system object exclusion is provenance-based [CONFIG]
```

Rule references: `ABS-SCS-14.1.a`, `ABS-SCS-15.5.c`, `ABS-SCS-17.a`,
`ABS-SCS-17.b`, `ABS-SCS-17.c`, `ABS-SCS-17.d`, `ABS-SCS-17.e`,
`ABS-SCS-17.f`, `ABS-SCS-17.g`, `ABS-SCS-17.h`, `ABS-SCS-17.i`,
`ABS-SCS-17.j`, `ABS-SCS-17.k`, `ABS-SCS-17.1.SCHEMA`.

Decisions required before full schema enforcement:

- module length conflict (`3–6` vs `3–5`);
- unit length conflict (`1–5` vs `3–5`) and approved short units;
- `pct` versus `pc` vocabulary;
- numeric-character prohibition versus examples containing digits;
- underscore-separated words versus lower-camel description;
- component lengths can exceed the total 31-character limit, so total maximum
  must explicitly win;
- scope of short-name exemptions;
- documented outliers such as `VITDgn` and conflicting terms such as `HVIL`.

### 3.7 Symbolic array dimensions

```text
Array Dimension
├── Dimension is symbolic rather than raw numeric literal [EXISTING]
├── Symbol resolves to a declared constant                [PARTIAL][REPO]
├── Symbol is visible at declaration site                 [PLANNED][REPO]
├── Symbol has an integral constant value                 [PLANNED]
├── Each multidimensional suffix is checked independently [EXISTING]
└── Allowed language-defined exceptions are configured    [CONFIG]
```

The current check reports each global-array dimension separately and identifies
numeric literals or numeric-only expressions. It does not yet resolve names to
declarations or establish whether an identifier is a visible integral constant.

Rule reference: `ABS-SCS-18.4.a` (loop limits) and the current project policy's
symbolic-array-size extension. The array-size requirement must remain identified
as project policy unless an exact normative rule is added to the standard.

---

## 4. Lexical Formatting

### 4.1 File-level lexical rules

```text
File Lexical Format
├── Every physical line is at most 132 characters          [PLANNED]
├── Tab character is absent                                [PLANNED]
├── Line ending uses LF                                    [PLANNED]
├── Forbidden non-printable character is absent            [PLANNED]
├── One statement appears per line                         [PLANNED]
├── File ends with required end comment and blank line     [CONFIG][PLANNED]
└── Whitespace-only change is isolated when required       [REPO][MANUAL]
```

Rule references: `ABS-SCS-11.2.a`, `ABS-SCS-13.3.a`,
`ABS-SCS-13.3.c`, `ABS-SCS-13.5.a`, `ABS-SCS-13.6.a`,
`ABS-SCS-13.6.b`, `ABS-SCS-7.6`.

### 4.2 Braces, parentheses, and indentation

```text
Block Formatting
├── Control statement body uses braces                    [PLANNED]
│   ├── if
│   ├── else
│   ├── switch
│   ├── while
│   ├── do
│   └── for
├── Opening brace placement matches convention            [PLANNED]
├── Closing brace aligns with its construct               [PLANNED]
├── Precedence-sensitive expression is parenthesized      [PLANNED]
├── && and || operands use required parentheses           [PLANNED]
├── Indentation uses configured four-column convention    [CONFIG][PLANNED]
├── switch case label and body indentation is correct     [PLANNED]
├── Continuation indentation is unambiguous               [SEMANTIC]
├── Natural code blocks use required blank lines          [SEMANTIC]
└── Optional preprocessor indentation is applied          [CONFIG]
```

Rule references: `ABS-SCS-11.3.a`, `ABS-SCS-11.3.b`,
`ABS-SCS-11.4.a`, `ABS-SCS-11.4.b`, `ABS-SCS-13.2.d`,
`ABS-SCS-13.3.b`, `ABS-SCS-13.4.a`, `ABS-SCS-13.4.b`,
`ABS-SCS-13.4.c`.

### 4.3 Token spacing

```text
Token Spacing
├── Keyword spacing                                       [PLANNED]
├── Assignment operator spacing                           [PLANNED]
├── Binary operator spacing                               [PLANNED]
├── Unary operator has no operand-side space              [PLANNED]
├── Pointer `*` spacing matches declaration/expression    [PLANNED]
├── Ternary `? :` spacing                                 [PLANNED]
├── Member access `.` and `->` have no spaces             [PLANNED]
├── Array subscript spacing                               [PLANNED]
├── Parenthesis interior spacing                          [PLANNED]
├── Function call/declaration parenthesis spacing         [PLANNED]
├── Comma spacing                                         [PLANNED]
├── for-clause semicolon spacing                          [PLANNED]
└── Statement semicolon has no preceding space            [PLANNED]
```

Rule references: `ABS-SCS-13.1.a`, `ABS-SCS-13.1.b`,
`ABS-SCS-13.1.c`, `ABS-SCS-13.1.d`, `ABS-SCS-13.1.e`,
`ABS-SCS-13.1.f`, `ABS-SCS-13.1.g`, `ABS-SCS-13.1.h`,
`ABS-SCS-13.1.i`, `ABS-SCS-13.1.j`, `ABS-SCS-13.1.k`,
`ABS-SCS-13.1.l`, `ABS-SCS-13.1.m`.

Decision: the source operator list contains questionable `~=` and `!=`
entries under assignment operators. Normalize the authoritative operator set
before implementing that leaf.

### 4.4 Visual alignment

```text
Alignment
├── Adjacent declaration names align                      [SEMANTIC][CONFIG]
├── Struct/union member names align                       [SEMANTIC][CONFIG]
└── Adjacent assignment operators align                   [SEMANTIC][CONFIG]
```

Rule references: `ABS-SCS-13.2.a`, `ABS-SCS-13.2.b`,
`ABS-SCS-13.2.c`.

---

## 5. Declarations, Types, and Qualifiers

### 5.1 Language and compiler restrictions

```text
Language Use
├── Translation unit conforms to C99 mode                  [CONFIG][REPO]
├── C++ compiler is restricted to approved C subset       [CONFIG][REPO]
├── Proprietary keyword/pragma/assembly use is minimized  [SEMANTIC]
└── Proprietary construct is localized and justified      [MANUAL]
```

Rule references: `ABS-SCS-11.1.a`, `ABS-SCS-11.1.b`,
`ABS-SCS-11.1.c`.

### 5.2 Forbidden/restricted language keywords

```text
Restricted Keyword
├── `auto` is absent                                      [PLANNED]
├── `register` is absent                                  [PLANNED]
├── `goto` handling follows resolved policy               [DECISION]
└── `continue` is absent                                  [PLANNED]
```

Rule references: `ABS-SCS-11.7.a`, `ABS-SCS-11.7.b`,
`ABS-SCS-11.7.c`, `ABS-SCS-11.7.d`, `ABS-SCS-18.5.a`.

Decision: the standard both forbids and conditionally permits `goto`. Resolve
which requirement controls before implementing one deterministic result.

### 5.3 Storage class and qualifiers

```text
Storage and Qualifiers
├── Internal-linkage function is `static`                  [REPO]
├── Internal-linkage variable is `static`                  [REPO]
├── Never-modified initialized object is `const`           [SEMANTIC]
├── Unmodified reference parameter is pointer-to-const     [SEMANTIC]
├── Unmodified struct/union field is const where intended  [SEMANTIC]
├── Numeric constant prefers typed const object            [SEMANTIC]
├── ISR-shared global is `volatile`                        [SEMANTIC][REPO]
├── Thread-shared global is `volatile` where required      [SEMANTIC][REPO]
├── Memory-mapped object access is volatile-qualified      [SEMANTIC]
└── Delay-loop counter is volatile-qualified               [SEMANTIC]
```

Rule references: `ABS-SCS-11.8.a`, `ABS-SCS-11.8.b`,
`ABS-SCS-11.8.b.i`, `ABS-SCS-11.8.b.ii`, `ABS-SCS-11.8.b.iii`,
`ABS-SCS-11.8.b.iv`, `ABS-SCS-11.8.c`, `ABS-SCS-11.8.c.i`,
`ABS-SCS-11.8.c.ii`, `ABS-SCS-11.8.c.iii`, `ABS-SCS-11.8.c.iv`.

### 5.4 Integer, character, signedness, and Boolean types

```text
Scalar Type Use
├── Width-sensitive integer uses approved fixed-width type [CONFIG]
├── `short` is absent                                     [PLANNED]
├── `long` is absent                                      [PLANNED]
├── plain `char` is used only for character strings       [SEMANTIC]
├── fallback typedefs exist when C99 types unavailable    [CONFIG][REPO]
├── fallback type widths have compile-time assertions     [REPO]
├── bit-field is not signed                               [PLANNED]
├── bitwise operand is not signed                         [PLANNED]
├── signed and unsigned operands are not mixed            [PLANNED]
├── unsigned literal has required suffix                  [PLANNED]
├── Boolean object uses approved bool type                [CONFIG]
└── Boolean conversion uses relation, not cast            [PLANNED]
```

Rule references: `ABS-SCS-15.2.a`, `ABS-SCS-15.2.b`,
`ABS-SCS-15.2.c`, `ABS-SCS-15.2.FALLBACK`, `ABS-SCS-15.3.a`,
`ABS-SCS-15.3.b`, `ABS-SCS-15.3.c`, `ABS-SCS-15.7.a`,
`ABS-SCS-15.7.b`.

### 5.5 Floating-point use

```text
Floating Point
├── Floating-point use has a need/justification            [MANUAL]
├── Floating object uses approved type                     [CONFIG]
├── Single-precision literal has `f` suffix                [PLANNED]
├── Target/toolchain double support is verified            [CONFIG][MANUAL]
├── Equality/inequality comparison on float is absent      [PLANNED]
└── Calculation result is checked with `isfinite`          [SEMANTIC]
```

Rule references: `ABS-SCS-15.4.a`, `ABS-SCS-15.4.b.i`,
`ABS-SCS-15.4.b.ii`, `ABS-SCS-15.4.b.iii`, `ABS-SCS-15.4.b.iv`,
`ABS-SCS-15.4.b.v`.

Decision: ensure the approved floating-type vocabulary includes `float128` if
the governing document intends it; earlier extracted tables were incomplete.

### 5.6 Structures, unions, bit fields, and enumerations

```text
Aggregate Type
├── Communication/hardware structure layout prevents padding [CONFIG][SEMANTIC]
├── Bit-field order is explicitly preserved                  [CONFIG][MANUAL]
├── Aggregate variables/members follow naming rules           [PLANNED]
├── Macro/enum constants are uppercase                        [PLANNED]
├── Macro/enum constants use module prefix                    [PLANNED][CONFIG]
└── Macro expression is parenthesized                         [DECISION]
```

Rule references: `ABS-SCS-15.5.a`, `ABS-SCS-15.5.b`,
`ABS-SCS-15.5.c`, `ABS-SCS-15.6.a`, `ABS-SCS-15.6.b`,
`ABS-SCS-15.6.c`.

Decision: clarify whether the parenthesization rule applies only to macros or
also to enumeration initializers.

### 5.7 Initialization and declaration placement

```text
Object Lifetime
├── Object is initialized before first read                [SEMANTIC]
├── Null pointer is initialized with `NULL`                [PLANNED]
├── Global definitions are grouped at top of source        [PLANNED]
└── Local declaration placement follows resolved policy    [DECISION]
```

Rule references: `ABS-SCS-17.2.a`, `ABS-SCS-17.2.b`,
`ABS-SCS-17.2.c`, `ABS-SCS-17.2.d`.

Decision: the source conflicts between declarations at block start and close to
first use. Select one policy or define the applicability of each.

---

## 6. Functions and Interfaces

### 6.1 Function design and visibility

```text
Function Design
├── Function metrics remain within configured limits       [REPO]
├── Function has at most one return at the bottom          [PLANNED]
├── Public function prototype is in module header          [REPO]
├── Private function has internal linkage (`static`)       [REPO]
└── Parameters are explicit and meaningful                 [SEMANTIC]
```

Rule references: `ABS-SCS-16.2.a`, `ABS-SCS-16.2.b`,
`ABS-SCS-16.2.c`, `ABS-SCS-16.2.d`, `ABS-SCS-16.2.e`.

### 6.2 Function-like macros

```text
Function-like Macro
├── Macro is justified over a function                     [SEMANTIC]
├── Whole replacement body is parenthesized                [PLANNED]
├── Every parameter occurrence is parenthesized            [PLANNED]
├── Every parameter is evaluated at most once              [PLANNED]
└── Replacement body contains no control transfer          [PLANNED]
```

Rule references: `ABS-SCS-16.3.a`, `ABS-SCS-16.3.b.i`,
`ABS-SCS-16.3.b.ii`, `ABS-SCS-16.3.b.iii`, `ABS-SCS-16.3.b.iv`.

### 6.3 Header/API quality

```text
Public API
├── Header exposes only required functions/types/constants [SEMANTIC][REPO]
├── Extern variable exposure is absent or justified        [REPO][SEMANTIC]
├── Public declaration has exactly one compatible definition [REPO]
└── Public type/function uses owning module prefix          [REPO][CONFIG]
```

Rule references: `ABS-SCS-14.2.c`, `ABS-SCS-14.2.c.i`,
`ABS-SCS-14.2.c.ii`, `ABS-SCS-15.1.c`, `ABS-SCS-16.2.c`.

---

## 7. Expressions and Control Flow

### 7.1 Casts and expressions

```text
Expression Safety
├── Cast has associated correctness comment               [SEMANTIC]
├── Declaration does not use comma operator               [PLANNED]
├── Condition contains no assignment                      [PLANNED]
├── Loop condition contains no assignment                 [PLANNED]
├── Equality comparison places constant on left           [PLANNED]
└── Operator precedence is made explicit                  [PLANNED]
```

Rule references: `ABS-SCS-11.6.a`, `ABS-SCS-18.1.a`,
`ABS-SCS-18.2.c`, `ABS-SCS-18.4.b`, `ABS-SCS-18.6.a`,
`ABS-SCS-11.4.a`.

### 7.2 Conditional statements

```text
Conditional Flow
├── Shorter branch appears first where appropriate         [SEMANTIC]
├── if/else nesting does not exceed two                   [PLANNED]
├── Condition has no assignment                           [PLANNED]
└── else-if chain ends with final else                    [PLANNED]
```

Rule references: `ABS-SCS-18.2.a`, `ABS-SCS-18.2.b`,
`ABS-SCS-18.2.c`, `ABS-SCS-18.2.d`.

### 7.3 Switch statements

```text
Switch Flow
├── `break` aligns with its case                           [PLANNED]
├── Every switch has `default`                            [PLANNED]
└── Intentional fallthrough has required comment          [PLANNED]
```

Rule references: `ABS-SCS-18.3.a`, `ABS-SCS-18.3.b`,
`ABS-SCS-18.3.c`.

### 7.4 Loops

```text
Loop Flow
├── Bound and initial values use named constants           [SEMANTIC][REPO]
├── Condition contains no assignment                      [PLANNED]
├── Intentional infinite loop uses exactly `for (;;)`     [PLANNED]
└── Empty loop has braces and explanatory comment         [PLANNED]
```

Rule references: `ABS-SCS-18.4.a`, `ABS-SCS-18.4.b`,
`ABS-SCS-18.4.c`, `ABS-SCS-18.4.d`.

### 7.5 Prohibited termination/non-local flow

```text
Non-local Control Flow
├── `goto` satisfies resolved project rule                 [DECISION]
├── `abort` is absent                                     [PLANNED]
├── `exit` is absent                                      [PLANNED]
├── `setjmp` is absent                                    [PLANNED]
└── `longjmp` is absent                                   [PLANNED]
```

Rule references: `ABS-SCS-18.5.a`, `ABS-SCS-18.5.b`.

---

## 8. Comments and Documentation

### 8.1 Comment syntax and prohibited content

```text
Comment Syntax
├── Uses permitted block/line comment form                 [PLANNED]
├── Comment body does not contain nested `/*` token        [PLANNED]
├── Comment body does not contain prohibited `//` token    [PLANNED]
├── Comment body does not end/use prohibited backslash     [PLANNED]
└── Commented-out code is replaced by conditional compile [SEMANTIC]
```

Rule references: `ABS-SCS-12.1.a`, `ABS-SCS-12.1.b`,
`ABS-SCS-12.1.c`, `ABS-SCS-12.1.c.i`.

### 8.2 Comment language, placement, and usefulness

```text
Comment Quality
├── Sentence spelling/grammar/punctuation is acceptable    [SEMANTIC]
├── Algorithm-step comment exists where required           [SEMANTIC]
├── Algorithm comment precedes associated code             [PARTIAL][SEMANTIC]
├── Algorithm comment indentation matches code block       [PARTIAL]
├── Algorithm comment has required following blank line    [PLANNED]
├── Obvious/redundant comment is absent                    [SEMANTIC]
├── End-of-line comment is used only when needed           [SEMANTIC]
├── Comment amount is proportional to complexity           [SEMANTIC]
├── External source is cited                               [SEMANTIC][MANUAL]
├── Assumptions are documented                             [SEMANTIC][MANUAL]
├── WARNING marker has actionable warning text             [SEMANTIC]
├── NOTE marker has useful note text                       [SEMANTIC]
└── TODO marker has actionable ownership/tracking data     [CONFIG][SEMANTIC]
```

Rule references: `ABS-SCS-12.2.a`, `ABS-SCS-12.2.b`,
`ABS-SCS-12.2.b.PRECEDE`, `ABS-SCS-12.2.b.INDENT`,
`ABS-SCS-12.2.c`, `ABS-SCS-12.2.d`, `ABS-SCS-12.2.e`,
`ABS-SCS-12.2.f`, `ABS-SCS-12.2.g`, `ABS-SCS-12.2.h.i`,
`ABS-SCS-12.2.h.ii`, `ABS-SCS-12.2.h.iii`.

### 8.3 Documentation process and best practices

```text
Documentation
├── Generated documentation is rebuilt with product       [CONFIG][REPO]
├── Public interfaces have suitable generated docs        [CONFIG][SEMANTIC]
├── Comment explains why/intent, not syntax                [SEMANTIC]
├── Comment remains synchronized with code                 [SEMANTIC][REPO]
└── Diagram is referenced and version controlled           [REPO][MANUAL]
```

Rule references: `ABS-SCS-12.2.REBUILD_DOCS`,
`ABS-SCS-12.2.BP1`, `ABS-SCS-12.2.BP2`, `ABS-SCS-12.2.BP3`,
`ABS-SCS-12.2.f`.

---

## 9. Concurrency, ISR, and Hardware

```text
Concurrency and Hardware
├── ISR-shared state is correctly volatile-qualified       [SEMANTIC][REPO]
├── Thread-shared state follows synchronization policy     [SEMANTIC][REPO][CONFIG]
├── Memory-mapped access uses volatile qualification       [SEMANTIC]
├── Delay loop counter is volatile                         [SEMANTIC]
├── Thread/task/process entry uses configured suffix       [CONFIG]
├── ISR uses compiler-recognized interrupt marker          [CONFIG]
├── ISR name ends `_isr`                                  [PLANNED]
├── ISR is static and/or placed at driver-module end       [CONFIG][REPO]
└── Unhandled vector has default stub                      [CONFIG][REPO]
```

Rule references: `ABS-SCS-11.8.c.i`, `ABS-SCS-11.8.c.ii`,
`ABS-SCS-11.8.c.iii`, `ABS-SCS-11.8.c.iv`, `ABS-SCS-16.4.a`,
`ABS-SCS-16.5.a`, `ABS-SCS-16.5.b`, `ABS-SCS-16.5.c`,
`ABS-SCS-16.5.d`.

---

## 10. Metrics, MISRA, and Static Analysis

### 10.1 Function and graph metrics

```text
Metrics
├── COMF comment density is 20–100                         [REPO][DECISION]
├── PATH estimated paths is 1–80                          [REPO]
├── GOTO count is 0                                       [REPO]
├── v(G) cyclomatic complexity is 1–10                    [REPO]
├── CALLING callers is 0–5                                [REPO][DECISION]
├── CALLS callees is 0–7                                  [REPO]
├── PARAM parameters is 0–5                               [PLANNED]
├── STMT statements is 1–50                               [PLANNED]
├── LEVEL nesting is 0–4                                  [PLANNED]
├── RETURN count is 0–1                                   [PLANNED]
├── S metric                                               [INACTIVE]
├── VOCF vocabulary frequency                             [INACTIVE]
└── Recursion/call-graph cycles is 0                       [REPO]
```

Rule references: `ABS-SCS-19.COMF`, `ABS-SCS-19.PATH`,
`ABS-SCS-19.GOTO`, `ABS-SCS-19.v(G)`, `ABS-SCS-19.CALLING`,
`ABS-SCS-19.CALLS`, `ABS-SCS-19.PARAM`, `ABS-SCS-19.STMT`,
`ABS-SCS-19.LEVEL`, `ABS-SCS-19.RETURN`, `ABS-SCS-19.S`,
`ABS-SCS-19.VOCF`, `ABS-SCS-19.ap_cg_cycle`.

Decisions: resolve the exact COMF formula and CALLING definition before matching
tool output. Inactive metrics must be `NOT_APPLICABLE`/`INACTIVE`, never PASS.

### 10.2 MISRA/HIS compliance

```text
Static Analysis Compliance
├── Applicable MISRA safety rules are enabled              [CONFIG][REPO]
├── HIS violations count is zero                           [REPO]
├── Mandatory MISRA violations count is zero               [REPO]
├── Unjustified MISRA deviations count is zero             [REPO][MANUAL]
├── Required manual review is complete                     [MANUAL]
└── C++ extensions comply with approved policy             [CONFIG][REPO]
```

Rule references: `ABS-SCS-5.MISRA_SAFETY`, `ABS-SCS-6.CPP`,
`ABS-SCS-19.NOMV`, `ABS-SCS-19.NOMVPR`.

---

## 11. Process and Governance Evidence

These requirements belong in a separate evidence-oriented stage or manager
view. They should not be inferred from source code alone.

```text
Governance
├── Standard scope/applicability is identified             [CONFIG][MANUAL]
├── Director responsibilities have evidence                [MANUAL]
├── Lead responsibilities have evidence                    [MANUAL]
├── Engineer responsibilities have evidence                [MANUAL]
├── Guiding principles considered in review                [MANUAL]
│   ├── Readability
│   ├── Maintainability
│   ├── Portability
│   ├── Reliability/safety
│   ├── Testability
│   ├── Performance where justified
│   └── Fallback engineering judgment
├── New/modified code complies                             [REPO][MANUAL]
├── Violations are corrected or formally deviated          [REPO][MANUAL]
├── Legacy migration is tracked                            [REPO][MANUAL]
├── Deviation documents rule, reason, risk, and scope      [MANUAL]
├── Deviation has required approval                        [MANUAL]
└── Deviation rationale/approver is close to affected code [REPO][MANUAL]
```

Rule references: `ABS-SCS-2.SCOPE`, `ABS-SCS-3.DIRECTOR`,
`ABS-SCS-3.LEAD`, `ABS-SCS-3.ENGINEER`, `ABS-SCS-4.1`,
`ABS-SCS-4.2`, `ABS-SCS-4.3`, `ABS-SCS-4.4`, `ABS-SCS-4.5`,
`ABS-SCS-4.6`, `ABS-SCS-4.FALLBACK`, `ABS-SCS-7.1`,
`ABS-SCS-7.2`, `ABS-SCS-7.3`, `ABS-SCS-7.4`, `ABS-SCS-7.5`,
`ABS-SCS-7.6`, `ABS-SCS-8.1`, `ABS-SCS-8.2`, `ABS-SCS-8.3`,
`ABS-SCS-8.4`, `ABS-SCS-9.1`.

### Supporting SCM evidence from document 0179

These are supporting-plan requirements and must retain document 0179
attribution rather than being mislabeled as ABS-SCS rule IDs.

```text
SCM Evidence
├── Repository uses configured hosting system              [CONFIG][MANUAL]
├── Main/develop branch model follows project policy       [CONFIG][REPO]
├── Feature branch uses `feature/` prefix                  [CONFIG][REPO]
├── Bug-fix branch uses `bugfix/` prefix                   [CONFIG][REPO]
├── Merge to develop has at least two peer approvals       [REPO]
├── Required pipeline succeeds before merge                [REPO]
├── Work links to configured Jira/Jama evidence            [CONFIG][REPO]
├── Baseline has a tag                                     [REPO]
├── External release tag is annotated                      [REPO]
└── Internal tag kind follows project convention           [CONFIG][REPO]
```

---

## 12. Reporting and Result Semantics

This stage owns serialization only.

```text
Reporting
├── Preserve stage order and check order
├── Preserve rule/source attribution
├── Preserve FAILED, ERROR, SKIPPED, and exceptions
├── Do not invent zero-count summaries for non-check stages
├── Include artifact/report path
├── Include stage diagnostics
├── Distinguish policy-not-configured from PASS
├── Distinguish manual-evidence-missing from code failure
└── Use one actionable reason per failed atomic validation
```

Recommended result vocabulary:

- `PASSED`: deterministic validation ran and succeeded.
- `FAILED`: validation ran and found nonconformance.
- `ERROR`: validation could not complete because of an internal/tool failure.
- `SKIPPED`: a dependency or applicability condition prevented execution.
- `NOT_APPLICABLE`: policy says the check does not apply.
- `MANUAL_REVIEW_REQUIRED`: automation cannot decide the requirement.
- `DECISION_REQUIRED`: the standard/policy is not sufficiently defined.

---

## 13. Suggested Implementation Order

```text
Priority 1 — Finish current checks
├── Split function regex failure into atomic reasons
├── Split macro regex failure into atomic reasons
├── Complete global-variable schema reasons and attribution
├── Resolve symbolic array identifiers, not just syntax
└── Add policy-not-configured and provenance-based exclusions

Priority 2 — High-value lexical/AST checks
├── Line length, tabs, line endings
├── Forbidden keywords/functions
├── Braces and switch/default/fallthrough
├── One bottom return
├── Function-like macro safety
├── Type-name and pointer suffix checks
├── Fixed-width/signedness/literal checks
└── Source/header pairing and include checks

Priority 3 — Repository-wide checks
├── Public/private API visibility
├── Include graph and unused includes
├── Call graph and recursion
├── Function metrics
├── Global initialization/linkage
└── Imported MISRA/HIS evidence

Priority 4 — Semantic and manual review
├── Comment quality and usefulness
├── Naming meaning and abbreviations
├── Const/volatile correctness
├── One-responsibility modules
├── Floating-point justification
├── Layout/hardware intent
└── Governance/deviation evidence
```

## 14. Definition of Ready for Any New Check

A new check is ready to implement only when all applicable items are known:

1. Exact rule ID and source section/page.
2. Target artifact and symbol kind.
3. Applicability conditions.
4. Accepted exceptions and their provenance.
5. Required analysis artifact/dependency.
6. Deterministic pass/fail predicate, or an explicit non-automatic result.
7. Project-specific configuration keys and defaults.
8. One actionable failure reason per atomic validation.
9. Accepted and rejected examples.
10. Expected behavior for missing data, parser failure, and unsupported input.
11. Result ownership: check, stage, pipeline, or manager evidence view.
12. Tests for PASS, FAIL, ERROR, SKIPPED, NOT_APPLICABLE, and exclusions.

## 15. Known Policy Decisions to Resolve

Do not bury these decisions inside regexes or checker code:

```text
Decision Register
├── Goto: forbidden versus conditionally permitted
├── Module abbreviation length: 3–6 versus 3–5
├── Unit length: 1–5 versus 3–5 and short-unit exceptions
├── Percent unit: `pct` versus `pc`
├── Digits in variable names versus documented examples
├── Variable word separation versus lowerCamel description
├── Local declarations: block start versus near first use
├── Macro/enum parenthesization applicability
├── Function-name capitalization after module prefix
├── Function snake-case exact grammar
├── Short variable-name exemption scope
├── Total 31-character limit versus component minima/maxima
├── Approved module outliers such as `VITDgn`
├── Conflicting vocabulary definitions such as `HVIL`
├── Floating type table completeness (`float128`)
├── Assignment-operator source list (`~=` and `!=`)
├── COMF formula
├── CALLING metric definition
└── S/VOCF phase activation
```

Until resolved, the corresponding result should be `DECISION_REQUIRED`, not a
fabricated PASS or FAIL.
