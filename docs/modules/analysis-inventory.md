# C/C++ Analysis Inventory

## Navigation

- Project index: [docs README](../README.md)
- Architecture: [analysis modules](../engineering/architecture.md#repo_reviewanalysissource_index)
- Code entry points: `analysis/source_index/generator.py`,
  `analysis/symbol_inventory/extractor.py`, `analysis/runner.py`
- Upstream: isolated repository root, YAML compilation/AST policy, CMake,
  compilation database, and libclang.
- Downstream: `analysis/symbols.json`, `analysis/code-intelligence.json`, typed
  inventory evidence, graph views, and naming checks.
- Decisions and limits: [D001](../engineering/decisions-and-lessons.md#d001--use-the-real-compilation-database-for-c-analysis), [D002](../engineering/decisions-and-lessons.md#d002--use-ast-plus-targeted-source-text-recovery), and [P001](../engineering/decisions-and-lessons.md#p001--compilerpreprocessor-visibility-changes-what-can-be-reviewed)

## Responsibility and flow

The source-index generator configures CMake with compile-command export in the
run-local `analysis/cmake_build` directory. The extractor filters compile entries
to configured folders/extensions, sanitizes arguments, and parses each source
file with libclang detailed preprocessing enabled. The AST walker builds
per-file dictionaries of functions, variables, parameters, types, and macros;
the result is JSON for later check stages. `run_analysis` makes a typed stage
result and retains skipped-file evidence.

## Data and implementation constructs

The module uses `Path` for file authority, JSON-compatible dictionaries,
`set[str]` to deduplicate compile entries, and lists to retain evidence order.
`subprocess.run(..., check=True, capture_output=True, text=True)` preserves
CMake failure output. Only the run-local build directory is removed before
configuration; the source repository must never be the deletion target.

## Boundaries and update trigger

This is translation-unit analysis, not proof of final binary behavior. Inactive
preprocessor paths, missing compile commands, parse failures, and link-time
changes remain outside coverage. Update when compiler setup, extraction scope,
symbol JSON, parsing-failure handling, or inventory grouping changes.
