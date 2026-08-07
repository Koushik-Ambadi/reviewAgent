# ABS Software Coding Standard — Review and Artifact Verification Rulebook

Source: Document 0151, revision 2.4. Machine-readable rule count: **206**.

This handout is generated from the YAML source of truth. It preserves each documented rule as a separate entry, omits examples, and records both the actual file page and printed document page.

## 1 Introduction & Purpose

- **ABS-SCS-1.MIN_PROCESS** [recommended; file p.4, document p.3] The software development process should include version control, defect tracking, formal architecture or design reviews, peer code reviews, and automated source-code scans.
## 2 Application & Scope

- **ABS-SCS-2.SCOPE** [mandatory; file p.5, document p.4] All developers writing software for ABS shall conform to the format and style defined by this standard.
## 3 Responsibilities

- **ABS-SCS-3.DIRECTOR** [mandatory; file p.5, document p.4] The Director of BMS is responsible for updating this procedure.
- **ABS-SCS-3.LEAD** [mandatory; file p.5, document p.4] The Software Lead Engineer shall follow the standard and ensure all project team members follow it.
- **ABS-SCS-3.ENGINEER** [mandatory; file p.5, document p.4] The Software Engineer is responsible for following this coding standard.
## 4 Guiding Principles

- **ABS-SCS-4.1** [guideline; file p.6, document p.5] Individual programmers do not own the software they write; the product shall be constructed in a workmanlike manner.
- **ABS-SCS-4.2** [guideline; file p.6, document p.5] Prefer practices that let the compiler, linker, or static-analysis tool detect defects before execution.
- **ABS-SCS-4.3** [guideline; file p.6, document p.5] Avoid implementation-defined, unspecified, undefined, and locale-specific behavior that reduces portability.
- **ABS-SCS-4.4** [guideline; file p.6, document p.5] Reliability, readability, efficiency, and portability take priority over programmer convenience.
- **ABS-SCS-4.5** [guideline; file p.6, document p.5] Use disciplined coding, fixed-width types, and consistent commenting and style to reduce defects during development and maintenance.
- **ABS-SCS-4.6** [guideline; file p.6, document p.5] When alternative rules prevent defects equally well, prefer the rule that is easier to enforce.
- **ABS-SCS-4.FALLBACK** [guideline; file p.6, document p.5] When a needed rule is absent or rules conflict, apply the spirit of the guiding principles.
## 5 MISRA C

- **ABS-SCS-5.MISRA_SAFETY** [recommended; file p.7, document p.6] For products that could kill or injure people, MISRA C guidelines should be part of the project coding standard.
## 6 C++ vs. C

- **ABS-SCS-6.CPP** [recommended; file p.7, document p.6] When applying these C rules to C++, strongly consider adopting additional C++-specific coding-standard rules.
## 7 Enforcement Guidelines

- **ABS-SCS-7.1** [mandatory; file p.8, document p.7] Conformance with all rules in this standard is mandatory.
- **ABS-SCS-7.2** [mandatory; file p.8, document p.7] Detect nonconformance primarily by automated scans, secondarily by peer review, and otherwise by informal discovery.
- **ABS-SCS-7.3** [recommended; file p.8, document p.7] Detected nonconforming code should be corrected to meet the rules.
- **ABS-SCS-7.4** [recommended; file p.8, document p.7] Working legacy code should generally be left unchanged unless safety demands otherwise.
- **ABS-SCS-7.5** [recommended; file p.8, document p.7] Bring legacy code into conformance one module or library at a time, preferably when functional changes are also required.
- **ABS-SCS-7.6** [recommended; file p.8, document p.7] Whitespace-only changes should be committed separately from functional changes.
## 8 Deviation Procedure

- **ABS-SCS-8.1** [mandatory; file p.8, document p.7] Product-release source code shall conform to the standard unless each deviation is documented and approved.
- **ABS-SCS-8.2** [allowed_deviation; file p.8, document p.7] Project-level quantitative limits may be changed when a different quantity better fits the development tools.
- **ABS-SCS-8.3** [mandatory; file p.8, document p.7] Module-level deviations require project-manager approval.
- **ABS-SCS-8.4** [mandatory; file p.8, document p.7] The approver name and rationale shall be documented as close as possible to the deviation.
## 9 Customization

- **ABS-SCS-9.1** [policy; file p.9, document p.8] A project may adopt all or a subset of these rules as its coding standard.
## 11.1 Which C?

- **ABS-SCS-11.1.a** [mandatory; file p.10, document p.9] All programs shall comply with the C99 version of the ISO C Programming Language Standard.
- **ABS-SCS-11.1.b** [mandatory; file p.10, document p.9] When a C++ compiler is used, compiler options shall restrict the language to the selected ISO C version.
- **ABS-SCS-11.1.c** [mandatory; file p.10, document p.9] Proprietary compiler keywords, pragmas, and inline assembly shall be minimized and localized to a small number of hardware-facing driver modules.
- **ABS-SCS-11.1.d** [mandatory; file p.10, document p.9] #define shall not alter or rename a language keyword or other aspect of the programming language.
## 11.2 Line Widths

- **ABS-SCS-11.2.a** [mandatory; file p.11, document p.10] Every source-code line shall be no longer than 132 characters.
  - Regex/template: `^.{133,}$`
## 11.3 Braces

- **ABS-SCS-11.3.a** [mandatory; file p.12, document p.11] Braces shall surround blocks following if, else, switch, while, do, and for, including single and empty statements.
- **ABS-SCS-11.3.b** [mandatory; file p.12, document p.11] Each opening brace shall appear alone on the line below the block start, and the matching closing brace shall appear alone at the same indentation.
## 11.4 Parentheses

- **ABS-SCS-11.4.a** [mandatory; file p.14, document p.13] Do not rely on operator precedence; use parentheses or split statements to make execution order explicit.
- **ABS-SCS-11.4.b** [mandatory; file p.14, document p.13] Unless it is a single identifier or constant, each operand of && and || shall be enclosed in parentheses.
## 11.5 Common Abbreviations

- **ABS-SCS-11.5.a** [recommended; file p.15, document p.14] Avoid abbreviations and acronyms unless their meanings are widely and consistently understood in the engineering community.
- **ABS-SCS-11.5.b** [mandatory; file p.15, document p.14] Maintain a version-controlled table of project-specific abbreviations and acronyms.
## 11.6 Casts

- **ABS-SCS-11.6.a** [mandatory; file p.16, document p.15] Each cast shall have an associated comment explaining how correct behavior is ensured for the possible right-side values.
## 11.7 Keywords to Avoid

- **ABS-SCS-11.7.a** [mandatory; file p.17, document p.16] The auto keyword shall not be used.
  - Regex/template: `\bauto\b`
- **ABS-SCS-11.7.b** [mandatory; file p.17, document p.16] The register keyword shall not be used.
  - Regex/template: `\bregister\b`
- **ABS-SCS-11.7.c** [mandatory; file p.17, document p.16] All use of the goto keyword shall be avoided.
  - Regex/template: `\bgoto\b`
  - Note: The reasoning text mentions an occasional exceptional use, while the metric limit is zero; treat approved deviations through the deviation procedure.
- **ABS-SCS-11.7.d** [preferred; file p.17, document p.16] Avoid all use of the continue keyword.
  - Regex/template: `\bcontinue\b`
## 11.8 Keywords to Frequent

- **ABS-SCS-11.8.a** [mandatory; file p.18, document p.17] Use static for all functions and variables that do not need visibility outside their module.
- **ABS-SCS-11.8.b.i** [mandatory_when_applicable; file p.18, document p.17] Use const for variables that shall not change after initialization.
- **ABS-SCS-11.8.b.ii** [mandatory_when_applicable; file p.18, document p.17] Use const for call-by-reference parameters that shall not be modified.
- **ABS-SCS-11.8.b.iii** [mandatory_when_applicable; file p.18, document p.17] Use const for struct or union fields that shall not be modified.
- **ABS-SCS-11.8.b.iv** [mandatory_when_applicable; file p.18, document p.17] Prefer strongly typed const objects over #define for numerical constants.
- **ABS-SCS-11.8.c.i** [mandatory_when_applicable; file p.18, document p.17] Use volatile for a global variable accessible by an interrupt service routine.
- **ABS-SCS-11.8.c.ii** [mandatory_when_applicable; file p.18, document p.17] Use volatile for a global variable accessible by two or more threads.
- **ABS-SCS-11.8.c.iii** [mandatory_when_applicable; file p.18, document p.17] Use volatile for a pointer to a memory-mapped I/O peripheral register set.
- **ABS-SCS-11.8.c.iv** [mandatory_when_applicable; file p.18, document p.17] Use volatile for a delay-loop counter.
## 12.1 Acceptable Comment Formats

- **ABS-SCS-12.1.a** [allowed; file p.20, document p.19] Both // comments and /* ... */ comments are acceptable.
- **ABS-SCS-12.1.b** [mandatory; file p.20, document p.19] Comments shall never contain the preprocessor tokens /*, //, or backslash.
- **ABS-SCS-12.1.c** [mandatory; file p.20, document p.19] Production-release code shall never contain commented-out code.
- **ABS-SCS-12.1.c.i** [mandatory; file p.20, document p.19] Temporarily disable a block of code with conditional compilation rather than commenting it out.
## 12.2 Comment Locations and Content

- **ABS-SCS-12.2.a** [mandatory; file p.21, document p.20] Comments shall use clear, complete sentences with correct spelling, grammar, and punctuation.
- **ABS-SCS-12.2.b** [mandatory; file p.21, document p.20] A block comment that introduces an algorithm step should precede the code at the same indentation, and a blank line shall follow the code block.
- **ABS-SCS-12.2.c** [recommended; file p.21, document p.20] Avoid obvious or redundant comments; use end-of-line comments only when a short explanation adds necessary clarity.
- **ABS-SCS-12.2.d** [mandatory; file p.21, document p.20] The number and length of comment blocks shall be proportional to the complexity of the code described.
- **ABS-SCS-12.2.e** [mandatory; file p.21, document p.20] When an algorithm or technical detail comes from an external reference, a comment shall identify the source sufficiently for a reader to locate it.
- **ABS-SCS-12.2.f** [mandatory; file p.21, document p.20] When a diagram is needed to document code, keep it under version control and reference it by file name or title in the comments.
- **ABS-SCS-12.2.g** [mandatory; file p.21, document p.20] All assumptions shall be stated in comments.
- **ABS-SCS-12.2.h.i** [mandatory_when_applicable; file p.21, document p.20] Use the capitalized marker WARNING: to identify risk in changing the code.
  - Regex/template: `\bWARNING:`
- **ABS-SCS-12.2.h.ii** [mandatory_when_applicable; file p.21, document p.20] Use the capitalized marker NOTE: for explanatory comments about why the code is written that way.
  - Regex/template: `\bNOTE:`
- **ABS-SCS-12.2.h.iii** [mandatory_when_applicable; file p.21, document p.20] Use the capitalized marker TODO: for unfinished code and state what remains to be done; optional uppercase initials may precede TODO:.
  - Regex/template: `\b(?:[A-Z]{2,4}\s+)?TODO:`
- **ABS-SCS-12.2.REBUILD_DOCS** [recommended; file p.22, document p.21] Automatically generated documentation should be rebuilt whenever the software is built.
- **ABS-SCS-12.2.BP1** [best_practice; file p.22, document p.21] It is best practice to write comments before writing the code that implements the described behavior.
- **ABS-SCS-12.2.BP2** [best_practice; file p.22, document p.21] Keep documentation as close to the source code as possible to reduce drift.
- **ABS-SCS-12.2.BP3** [best_practice; file p.22, document p.21] When a question reveals that code is unclear, add a nearby comment that addresses the question.
## 13.1 Spaces

- **ABS-SCS-13.1.a** [mandatory; file p.23, document p.22] Each if, while, for, switch, and return keyword shall be followed by one space when more program text appears on the same line.
- **ABS-SCS-13.1.b** [mandatory; file p.23, document p.22] Each assignment operator =, +=, -=, *=, /=, %=, &=, |=, ^=, ~=, and != shall have one space before and after it.
- **ABS-SCS-13.1.c** [mandatory; file p.23, document p.22] Each binary operator +, -, *, /, %, <, <=, >, >=, ==, !=, <<, >>, &, |, ^, &&, and || shall have one space before and after it.
- **ABS-SCS-13.1.d** [mandatory; file p.23, document p.22] Each unary operator +, -, ++, --, !, and ~ shall have no space on the operand side.
- **ABS-SCS-13.1.e** [mandatory; file p.23, document p.22] Pointer operators * and & shall have whitespace on both sides in declarations and no space on the operand side in other uses.
- **ABS-SCS-13.1.f** [mandatory; file p.23, document p.22] Each ? and : in a ternary expression shall have one space before and after it.
- **ABS-SCS-13.1.g** [mandatory; file p.23, document p.22] The -> and . member-access operators shall have no surrounding spaces.
- **ABS-SCS-13.1.h** [mandatory; file p.23, document p.22] Array subscript brackets shall have no surrounding spaces except where another whitespace rule requires them.
- **ABS-SCS-13.1.i** [mandatory; file p.23, document p.22] Expressions inside parentheses shall have no spaces adjacent to either parenthesis.
- **ABS-SCS-13.1.j** [mandatory; file p.23, document p.22] Function-call parentheses shall have no surrounding spaces; a function declaration shall contain one space between the function name and opening parenthesis.
- **ABS-SCS-13.1.k** [mandatory; file p.23, document p.22] A comma separating function parameters shall be followed by one space unless it ends the line.
- **ABS-SCS-13.1.l** [mandatory; file p.23, document p.22] Each semicolon separating for-loop clauses shall be followed by one space.
- **ABS-SCS-13.1.m** [mandatory; file p.23, document p.22] A semicolon shall immediately follow the statement it terminates without a preceding space.
## 13.2 Alignment

- **ABS-SCS-13.2.a** [mandatory; file p.24, document p.23] Align the first characters of variable names within a series of declarations.
- **ABS-SCS-13.2.b** [mandatory; file p.24, document p.23] Align the first characters of struct and union member names.
- **ABS-SCS-13.2.c** [mandatory; file p.24, document p.23] Align assignment operators within adjacent assignment statements.
- **ABS-SCS-13.2.d** [allowed; file p.24, document p.23] The # in a preprocessor directive may be indented inside an #if or #ifdef sequence.
## 13.3 Blank Lines

- **ABS-SCS-13.3.a** [mandatory; file p.25, document p.24] A source-code line shall contain no more than one statement.
- **ABS-SCS-13.3.b** [mandatory; file p.25, document p.24] Place a blank line before and after each natural code block, including loops, if-else statements, switch statements, and consecutive declarations.
- **ABS-SCS-13.3.c** [mandatory; file p.25, document p.24] Each source file shall end with an end-of-file comment followed by a blank line.
## 13.4 Indentation

- **ABS-SCS-13.4.a** [recommended; file p.26, document p.25] Each indentation level should align to a multiple of four characters from the start of the line.
- **ABS-SCS-13.4.b** [mandatory; file p.26, document p.25] Within a switch, align case labels and indent each case body once from the labels.
- **ABS-SCS-13.4.c** [mandatory; file p.26, document p.25] When a statement exceeds the line-width limit, indent continuation lines in the most readable manner.
## 13.5 Tabs

- **ABS-SCS-13.5.a** [mandatory; file p.27, document p.26] The tab character ASCII 0x09 shall never appear in a source-code file.
  - Regex/template: `\t`
## 13.6 Non-Printing Characters

- **ABS-SCS-13.6.a** [mandatory_when_possible; file p.28, document p.27] Whenever possible, source-code lines shall end with LF only, not CR-LF.
- **ABS-SCS-13.6.b** [mandatory; file p.28, document p.27] The only non-printable character permitted in source code other than LF is form feed ASCII 0x0C.
## 14.1 Module Naming Conventions

- **ABS-SCS-14.1.a** [mandatory; file p.29, document p.28] Variable names shall follow the variable naming conventions in Section 17.
- **ABS-SCS-14.1.b** [mandatory; file p.29, document p.28] Module names shall be unique in their first six characters and use .h and .c suffixes for headers and sources.
- **ABS-SCS-14.1.c** [mandatory; file p.29, document p.28] A module header root name shall not duplicate a C or C++ Standard Library header name.
- **ABS-SCS-14.1.d** [mandatory; file p.29, document p.28] A module containing main() shall include the word main in its source-file name.
  - Regex/template: `(?i).*main.*\.c$`
## 14.2 Header Files

- **ABS-SCS-14.2.a** [mandatory; file p.30, document p.29] There shall be exactly one header file for each source file, with the same root name.
- **ABS-SCS-14.2.b** [mandatory; file p.30, document p.29] Each header file shall contain a preprocessor guard against multiple inclusion.
- **ABS-SCS-14.2.c** [mandatory; file p.30, document p.29] A header shall expose only procedures, constants, and data types that other modules strictly need.
- **ABS-SCS-14.2.c.i** [preferred; file p.30, document p.29] Prefer not to declare variables with extern in a header file.
  - Regex/template: `\bextern\b`
- **ABS-SCS-14.2.c.ii** [mandatory; file p.30, document p.29] A header file shall not allocate storage for any variable.
- **ABS-SCS-14.2.d** [mandatory; file p.30, document p.29] A public header file shall not include a private header file.
## 14.3 Source Files

- **ABS-SCS-14.3.a** [mandatory; file p.31, document p.30] Each source file shall contain only behaviors appropriate to control one entity.
- **ABS-SCS-14.3.b** [mandatory; file p.31, document p.30] Source-file sections shall appear in this order when present: comment block, includes, type or constant or macro definitions, static data, private prototypes, public function bodies, private function bodies.
- **ABS-SCS-14.3.c** [mandatory; file p.31, document p.30] Each source file shall include the header file with the same root name.
- **ABS-SCS-14.3.d** [mandatory; file p.31, document p.30] Include directives shall not use absolute paths.
  - Regex/template: `^\s*#\s*include\s*[<\"](?:[A-Za-z]:\\|/|\\\\)`
- **ABS-SCS-14.3.e** [mandatory; file p.31, document p.30] Source files shall not contain unused include directives.
- **ABS-SCS-14.3.f** [mandatory; file p.31, document p.30] A source file shall not include another source file.
  - Regex/template: `^\s*#\s*include\s*[<\"][^>\"]+\.c[>\"]`
## 14.4 File Templates

- **ABS-SCS-14.4.a** [mandatory; file p.32, document p.31] Maintain project-level templates for header and source files.
## 15.1 Data-Type Naming Conventions

- **ABS-SCS-15.1.a** [mandatory; file p.33, document p.32] Every new data type, including a struct, union, or enum, shall start with the module name and underscore, include a descriptive name, and end with _t.
  - Regex/template: `^(?=.{1,31}$){MODULE}_[A-Za-z][A-Za-z0-9_]*_t$`
- **ABS-SCS-15.1.b** [mandatory; file p.33, document p.32] Every new struct, union, and enum shall be named through a typedef.
- **ABS-SCS-15.1.c** [mandatory; file p.33, document p.32] Every public data type shall start with its module name and an underscore.
  - Regex/template: `^{MODULE}_`
## 15.2 Fixed-Width Integers

- **ABS-SCS-15.2.a** [mandatory_when_applicable; file p.34, document p.33] When integer or floating width matters, use the fixed-width types bool, sint8_t, uint8_t, sint16_t, uint16_t, sint32_t, uint32_t, sint64_t, uint64_t, float32_t, or float64_t instead of char, short, int, long, or long long.
- **ABS-SCS-15.2.b** [mandatory; file p.34, document p.33] The short and long keywords shall not be used.
  - Regex/template: `\b(?:short|long)\b`
- **ABS-SCS-15.2.c** [mandatory; file p.34, document p.33] Use char only for declarations and operations concerning strings.
- **ABS-SCS-15.2.FALLBACK** [allowed_with_condition; file p.34, document p.33] If a C99-compatible compiler is unavailable, define the fixed-width types with typedefs and verify their widths at compile time.
## 15.3 Signed and Unsigned Integers

- **ABS-SCS-15.3.a** [mandatory; file p.35, document p.34] Bit-fields shall not use signed integer types.
- **ABS-SCS-15.3.b** [mandatory; file p.35, document p.34] Do not apply &, |, ~, ^, <<, or >> to signed integer data.
- **ABS-SCS-15.3.c** [mandatory; file p.35, document p.34] Do not mix signed and unsigned integers in comparisons or expressions; append u to decimal constants intended to be unsigned.
## 15.4 Floating Point

- **ABS-SCS-15.4.a** [preferred; file p.36, document p.35] Avoid floating-point constants and variables whenever possible; fixed-point math may be used instead.
- **ABS-SCS-15.4.b.i** [mandatory_when_applicable; file p.36, document p.35] When floating-point calculations are necessary, use float32_t, float64_t, or float128_t.
- **ABS-SCS-15.4.b.ii** [mandatory_when_applicable; file p.36, document p.35] Append f to every single-precision floating-point constant.
- **ABS-SCS-15.4.b.iii** [mandatory_when_applicable; file p.36, document p.35] Verify compiler double-precision support when calculations depend on it.
- **ABS-SCS-15.4.b.iv** [mandatory; file p.36, document p.35] Never test floating-point values for equality or inequality.
- **ABS-SCS-15.4.b.v** [mandatory_when_applicable; file p.36, document p.35] Invoke isfinite() to verify prior floating-point calculations produced neither INFINITY nor NAN.
## 15.5 Structures and Unions

- **ABS-SCS-15.5.a** [mandatory_when_applicable; file p.37, document p.36] Prevent compiler-inserted padding in structs or unions used for peripheral, bus, or inter-processor communication.
- **ABS-SCS-15.5.b** [mandatory_when_applicable; file p.37, document p.36] Prevent the compiler from changing the intended order of bits within bit-fields.
- **ABS-SCS-15.5.c** [mandatory; file p.37, document p.36] Structure variables and structure members shall follow the variable naming conventions.
## 15.6 Macros and Enums

- **ABS-SCS-15.6.a** [recommended; file p.38, document p.37] Macros should use uppercase letters only.
  - Regex/template: `^[A-Z][A-Z0-9_]*$`
- **ABS-SCS-15.6.b** [mandatory; file p.38, document p.37] Names in this section shall start with the module name.
  - Regex/template: `^{MODULE_UPPER}(?:_|$)`
- **ABS-SCS-15.6.c** [recommended; file p.38, document p.37] A macro expression should be enclosed in parentheses.
  - Note: The section title includes enums, but an expression-parenthesis rule is only directly applicable to macro replacement expressions.
## 15.7 Booleans

- **ABS-SCS-15.7.d** [mandatory; file p.39, document p.38] Boolean variables shall be declared with type bool.
- **ABS-SCS-15.7.e** [mandatory; file p.39, document p.38] Convert non-Boolean values to Boolean with relational operators, not casts.
## 16.1 Procedure Naming Conventions

- **ABS-SCS-16.1.a** [mandatory; file p.40, document p.39] A procedure name shall not be a keyword in any standard version of C or C++.
- **ABS-SCS-16.1.b** [mandatory; file p.40, document p.39] A procedure name shall not overlap a C Standard Library function name.
- **ABS-SCS-16.1.c** [mandatory; file p.40, document p.39] A procedure name shall not begin with an underscore.
  - Regex/template: `^[^_]`
- **ABS-SCS-16.1.d** [mandatory; file p.40, document p.39] A procedure name shall be no longer than 31 characters, except in autogenerated or third-party code.
  - Regex/template: `^.{1,31}$`
  - Exceptions: autogenerated_code, third_party_code
- **ABS-SCS-16.1.e** [mandatory; file p.40, document p.39] Every function name shall start with a configured module name followed by an underscore.
  - Regex/template: `^(?=.{1,31}$){MODULE}_`
- **ABS-SCS-16.1.f** [mandatory; file p.40, document p.39] A macro name shall not contain lowercase letters.
  - Regex/template: `^[A-Z0-9_]+$`
- **ABS-SCS-16.1.g** [mandatory; file p.40, document p.39] Use underscores to separate words in procedure names.
  - Regex/template: `^{MODULE}_[a-z][a-z0-9]*(?:_[a-z0-9]+)*$`
- **ABS-SCS-16.1.h** [mandatory; file p.40, document p.39] Each procedure name shall describe its purpose; noun-verb ordering or a name stating the question answered is recommended.
- **ABS-SCS-16.1.i** [encouraged; file p.40, document p.39] Use of set and get function names is encouraged.
## 16.2 Functions

- **ABS-SCS-16.2.a** [mandatory; file p.41, document p.40] Keep each function within the source-code metric limits.
- **ABS-SCS-16.2.b** [mandatory; file p.41, document p.40] Each function shall have one exit point through a return at the bottom of the function, subject to the return-point metric.
- **ABS-SCS-16.2.c** [mandatory; file p.41, document p.40] Declare a prototype for each public function in the module header file.
- **ABS-SCS-16.2.d** [mandatory; file p.41, document p.40] Declare every private function static.
- **ABS-SCS-16.2.e** [mandatory; file p.41, document p.40] Explicitly declare and meaningfully name every function parameter.
## 16.3 Function-Like Macros

- **ABS-SCS-16.3.a** [mandatory; file p.42, document p.41] Do not use a parameterized macro when a function can provide the same behavior.
- **ABS-SCS-16.3.b.i** [mandatory_when_applicable; file p.42, document p.41] When a parameterized macro is used, enclose the entire macro body in parentheses.
- **ABS-SCS-16.3.b.ii** [mandatory_when_applicable; file p.42, document p.41] When a parameterized macro is used, enclose every use of each parameter in parentheses.
- **ABS-SCS-16.3.b.iii** [mandatory_when_applicable; file p.42, document p.41] When a parameterized macro is used, reference each parameter no more than once.
- **ABS-SCS-16.3.b.iv** [mandatory_when_applicable; file p.42, document p.41] A parameterized macro shall not contain a transfer of control such as return.
  - Regex/template: `\b(?:return|goto|break|continue)\b`
## 16.4 Threads of Execution

- **ABS-SCS-16.4.a** [mandatory; file p.43, document p.42] A function that implements a thread, task, or process shall end with _thread, _task, or _process.
  - Regex/template: `.*_(?:thread|task|process)$`
## 16.5 Interrupt Service Routines

- **ABS-SCS-16.5.a** [mandatory; file p.44, document p.43] An ISR shall be identified to the compiler with a pragma or compiler-specific ISR keyword.
- **ABS-SCS-16.5.b** [mandatory; file p.44, document p.43] Every ISR function name shall end with _isr.
  - Regex/template: `.*_isr$`
- **ABS-SCS-16.5.c** [mandatory; file p.44, document p.43] Each ISR shall be static and/or placed at the end of the associated driver module as permitted by the platform.
- **ABS-SCS-16.5.d** [mandatory; file p.44, document p.43] Install a stub or default ISR in the vector table for every unexpected or unhandled interrupt source.
## 17 Variable Rules

- **ABS-SCS-17.a** [mandatory; file p.46, document p.45] A variable name shall not be a keyword of C, C++, K&R C, C99, or another well-known C extension.
- **ABS-SCS-17.b** [mandatory; file p.46, document p.45] A variable name shall not overlap a C Standard Library variable name.
- **ABS-SCS-17.c** [mandatory; file p.46, document p.45] A variable name shall not begin with an underscore.
  - Regex/template: `^[^_]`
- **ABS-SCS-17.d** [mandatory; file p.46, document p.45] A variable name shall be no longer than 31 characters, except in autogenerated or third-party code.
  - Regex/template: `^.{1,31}$`
  - Exceptions: autogenerated_code, third_party_code
- **ABS-SCS-17.e** [mandatory; file p.46, document p.45] A variable name shall contain at least three characters, including loop counters.
  - Regex/template: `^.{3,}$`
- **ABS-SCS-17.f** [mandatory; file p.46, document p.45] A variable name shall not embed a numeric value that is specified elsewhere, such as array length or underlying type width.
- **ABS-SCS-17.g** [mandatory; file p.46, document p.45] Use underscores to separate words in variable names.
- **ABS-SCS-17.h** [mandatory; file p.46, document p.45] Each variable name shall describe its purpose.
- **ABS-SCS-17.i** [mandatory; file p.46, document p.45] A pointer variable name shall end with _ptr.
  - Regex/template: `.*_ptr$`
- **ABS-SCS-17.j** [mandatory; file p.46, document p.45] A pointer-to-pointer variable name shall end with _ptr_ptr.
  - Regex/template: `.*_ptr_ptr$`
- **ABS-SCS-17.k** [mandatory; file p.46, document p.45] Loop counters, function parameters, return parameters, and local temporary variables are exempt from the other variable-name rules but shall contain at least three characters.
  - Regex/template: `^.{3,}$`
## 17.2 Initialization

- **ABS-SCS-17.2.a** [mandatory; file p.50, document p.49] Every variable shall be initialized before use.
- **ABS-SCS-17.2.b** [preferred; file p.50, document p.49] Prefer defining local variables at the top of a function.
  - Note: The reasoning on the same page also favors declarations close to first use; this is a document-level tension.
- **ABS-SCS-17.2.c** [mandatory_when_applicable; file p.50, document p.49] Group project-global and file-global variable definitions together at the top of the source file.
- **ABS-SCS-17.2.d** [mandatory; file p.50, document p.49] Initialize a pointer with no initial address to NULL.
## 18.1 Variable Declarations

- **ABS-SCS-18.1.a** [mandatory; file p.51, document p.50] Do not use the comma operator within variable declarations.
## 18.2 Conditional Statements

- **ABS-SCS-18.2.a** [preferred; file p.52, document p.51] Prefer placing the shortest if or else-if clause first unless priority is more important.
- **ABS-SCS-18.2.b** [mandatory; file p.52, document p.51] Nested if-else statements shall not exceed two levels.
- **ABS-SCS-18.2.c** [mandatory; file p.52, document p.51] Do not make an assignment inside an if or else-if condition.
- **ABS-SCS-18.2.d** [mandatory; file p.52, document p.51] An if statement containing an else-if clause shall end with an else clause.
## 18.3 Switch Statements

- **ABS-SCS-18.3.a** [mandatory; file p.53, document p.52] Align each case break with its case label, not with the case body.
- **ABS-SCS-18.3.b** [mandatory; file p.53, document p.52] Every switch statement shall contain a default block.
- **ABS-SCS-18.3.c** [mandatory_when_applicable; file p.53, document p.52] A case that intentionally falls through shall contain a comment explaining the missing break.
## 18.4 Loops

- **ABS-SCS-18.4.a** [mandatory; file p.54, document p.53] Do not use magic numbers as loop initial values or endpoint tests in while, do-while, or for loops.
- **ABS-SCS-18.4.b** [mandatory; file p.54, document p.53] Except for for-loop counter initialization and update clauses, do not assign values in a loop control expression.
- **ABS-SCS-18.4.c** [mandatory; file p.54, document p.53] Implement infinite loops as for (;;).
  - Regex/template: `for\s*\(\s*;\s*;\s*\)`
- **ABS-SCS-18.4.d** [mandatory; file p.54, document p.53] An empty loop body shall use braces containing a comment that explains the empty body.
## 18.5 Jumps

- **ABS-SCS-18.5.a** [mandatory; file p.55, document p.54] Restrict goto use according to the keyword rule and source-code metric.
- **ABS-SCS-18.5.b** [mandatory; file p.55, document p.54] Do not use abort(), exit(), setjmp(), or longjmp().
  - Regex/template: `\b(?:abort|exit|setjmp|longjmp)\s*\(`
## 18.6 Equivalence Tests

- **ABS-SCS-18.6.1** [mandatory; file p.56, document p.55] When comparing a variable with a constant using ==, place the constant on the left.
## 19 Source Code Metrics

- **ABS-SCS-19.COMF** [mandatory; file p.57, document p.56] Comment Density shall remain within 20 to 100 percent.
- **ABS-SCS-19.PATH** [mandatory; file p.57, document p.56] Number of Paths shall remain within 1 to 80 count.
- **ABS-SCS-19.GOTO** [mandatory; file p.57, document p.56] Number of Goto Statements shall remain within 0 to 0 count.
- **ABS-SCS-19.v(G)** [mandatory; file p.57, document p.56] Cyclomatic Complexity shall remain within 1 to 10 count.
- **ABS-SCS-19.CALLING** [mandatory; file p.57, document p.56] Number of Calling Functions shall remain within 0 to 5 count.
- **ABS-SCS-19.CALLS** [mandatory; file p.57, document p.56] Number of Called Functions shall remain within 0 to 7 count.
- **ABS-SCS-19.PARAM** [mandatory; file p.57, document p.56] Number of Function Parameters shall remain within 0 to 5 count.
- **ABS-SCS-19.STMT** [mandatory; file p.57, document p.56] Number of Instructions per Function shall remain within 1 to 50 count.
- **ABS-SCS-19.LEVEL** [mandatory; file p.57, document p.56] Number of Call Levels shall remain within 0 to 4 count.
- **ABS-SCS-19.RETURN** [mandatory; file p.57, document p.56] Number of Return Points shall remain within 0 to 1 count.
- **ABS-SCS-19.S** [inactive_phase_1; file p.57, document p.56] Stability Index has a documented range of 0 to 1 but is marked not applicable for Phase 1.
- **ABS-SCS-19.VOCF** [inactive_phase_1; file p.57, document p.56] Language Scope has a documented range of 1 to 4 but is marked not applicable for Phase 1.
- **ABS-SCS-19.NOMV** [mandatory; file p.57, document p.56] HIS Violations shall remain within 0 to 0 count.
- **ABS-SCS-19.NOMVPR** [mandatory; file p.57, document p.56] MISRA mandatory violations shall be zero and unjustified MISRA violations shall be zero; the review shall be complete.
- **ABS-SCS-19.ap_cg_cycle** [mandatory; file p.57, document p.56] Number of Recursions shall remain within 0 to 0 count.
## 20 Appendix A: Acronyms and Abbreviations

- **ABS-SCS-APP-A.1** [allowed; file p.60, document p.59] The abbreviations listed in Appendix A are accepted in source code without local explanation.
- **ABS-SCS-APP-A.2** [best_practice; file p.61, document p.60] Generally avoid abbreviations in variable names; when needed, choose clear and concise abbreviations and document their meaning.

## Variable Naming Schema

- Format: `TsMxxx_Uxxx_Dxxx`
- Total maximum length: 31 characters.
- T: one uppercase data-type code from C, F, K, L, N, V, M.
- s: one lowercase size code from a, e, m, s, t.
- Mxxx: configured module abbreviation, generally 3-6 characters with one uppercase followed by lowercase.
- Uxxx: value from the controlled unit vocabulary.
- Dxxx: descriptive lowerCamelCase, documented length 14-22 characters.

## Source-Code Metrics

- **COMF — Comment Density**: 20–100 percent. Comments outside and inside functions divided by statements, multiplied by 100.
- **PATH — Number of Paths**: 1–80 count. Direct non-cyclic execution paths in a function.
- **GOTO — Number of Goto Statements**: 0–0 count. Goto statements in a function or module.
- **v(G) — Cyclomatic Complexity**: 1–10 count. Decision points plus one.
- **CALLING — Number of Calling Functions**: 0–5 count. Distinct functions that call the function.
- **CALLS — Number of Called Functions**: 0–7 count. Distinct functions called by the function.
- **PARAM — Number of Function Parameters**: 0–5 count. Parameters in the function interface.
- **STMT — Number of Instructions per Function**: 1–50 count. Instructions or statements in a function.
- **LEVEL — Number of Call Levels**: 0–4 count. Maximum depth of nested function calls.
- **RETURN — Number of Return Points**: 0–1 count. Return points inside a function.
- **S — Stability Index**: 0–1 ratio; status: not_applicable_phase_1. Stability index.
- **VOCF — Language Scope**: 1–4 count; status: not_applicable_phase_1. Language scope metric.
- **NOMV — HIS Violations**: 0–0 count. HIS subset violations.
- **NOMVPR — MISRA Violations per Rule**: 0 mandatory and 0 unjustified. Mandatory and unjustified MISRA violations; review must be completed.
- **ap_cg_cycle — Number of Recursions**: 0–0 count. Call-graph recursion cycles.

## Controlled Vocabularies

- Units: A, Ah, bi, cnt, day, degC, degF, frc, hrs, Hz, ix, kA, kAh, kHz, kV, kW, kWh, mA, mF, ms, mV, nu, ohm, pct, sec, tau, us, V, W, Wh
- Accepted abbreviations: ABS, ATD, BAL, BATT, BMS, BSW, CAN, CON, CTL, CUR, DIAG, DGN, DRV, EA, EEPROM, EMC, HIS, HIST, HVIL, IF, INHIB, LMT, MDL, MD, MGMT, MGR, MNT, PWR, RAM, ROM, SAD, SM, SRB, STGR, TMP, TYP, TO, UART, USB
- Module abbreviations: Adcmgr, Auxcon, Balctl, Battsm, Cantcv, Canstk, Calmgr, Cellmdl, Cellmnt, Chrg, Conctl, Coul, Curlmt, Crcmgr, Cvtnsm, Dcfc, Dchrg, Dcmmgr, Didmgr, Dtcmgr, Hall, Hwio, Htrctl, Hvil, Inhibt, Iso, Limctl, Nmsm, Nvmmgr, Packsm, Pchrg, Pwrmnt, Pyro, Qrcode, Rtcmgr, Shunt, Soc, Soe, Sohc, Sop, Srs, Syssm, Therm, Tmpmnt, Udsstk, Uepm, VITDgn

## Document Ambiguities to Resolve in Review Manager Configuration

- goto is described as mandatory to avoid, later as restricted, and has a metric limit of zero; approved exceptions should use the deviation process.
- Module abbreviation length is stated as 3-6 characters in one place and 3-5 characters in another.
- Unit length is shown as 1-5 characters in the table heading but described as 3-5 characters; the allowed list includes one- and two-character units.
- The allowed unit list contains pct, while variable examples use pc.
- Variable names are told not to contain numeric values called out elsewhere, while an example description uses the digit 2 as shorthand for to.
- The rule prefers local declarations at the top of a function, while the reasoning also favors declarations close to first use.
- Section 15.6 is titled Macros and Enums, but the expression-parentheses constraint is directly meaningful only for macros.
- Stability index and language scope are struck through and have review comments stating NA for Phase 1.
- VITDgn in the module list does not follow the general one-uppercase-followed-by-lowercase module-format statement.
- mF is described as microfarad in the document; the rulebook preserves the document text rather than correcting the unit.
- float128_t is required in the floating-point section but is not included in the fixed-width type table on the preceding pages.
