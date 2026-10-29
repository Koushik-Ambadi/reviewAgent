"""Opt-in flow evidence command. Existing run artifacts are never overwritten."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from code_intelligence.compiler import configure_libclang, sanitize_compile_args
from code_intelligence.extraction import extract_translation_unit
from code_intelligence.extraction.llvm_api import LLVM
from code_intelligence.extraction.llvm_flow import add_llvm_flow
from code_intelligence.graph import KnowledgeGraph
from code_intelligence.storage import write_snapshot
from code_intelligence.views import control_flow_graph, data_flow_graph


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate_flow(*, source: Path, repo_root: Path, output: Path,
                  clang: Path, llvm_library: Path, args: list[str],
                  directory: Path | None = None, timeout: int = 120) -> dict:
    """Generate an isolated, canonical AST+IR graph and retain its compiler inputs."""
    from clang import cindex

    source, repo_root, output = source.resolve(), repo_root.resolve(), output.resolve()
    relative = source.relative_to(repo_root).as_posix()
    directory = (directory or repo_root).resolve()
    if output.exists():
        raise ValueError(f"Output must be a new directory: {output}")
    # This command intentionally uses the project's existing host-analysis policy.
    # Never execute a compiler or shell command taken from the compilation database.
    cleaned = sanitize_compile_args(args)
    cleaned = [a for a in cleaned if not re.match(r"^-O|^-g", a)]
    effective = cleaned + ["-O0", "-g", "-fno-discard-value-names"]
    version = subprocess.run([str(clang), "--version"], capture_output=True,
                             text=True, check=True, timeout=timeout).stdout.splitlines()[0]
    llvm_version = LLVM(llvm_library).version
    match = re.search(r"clang version (\d+)", version)
    if not match or match.group(1) != llvm_version.split(".")[0]:
        raise ValueError(f"Clang and LLVM library major versions must match: {version}; {llvm_version}")
    output.mkdir(parents=True)
    manifest = {"status": "running", "source": relative, "source_sha256": digest(source.read_bytes()),
                "engine": version, "llvm_version": llvm_version, "directory": str(directory),
                "original_arguments": args, "effective_arguments": effective,
                "configuration_policy": "existing_sanitized_host_c99_analysis_not_target_build"}
    package = Path(__file__).parent
    manifest["implementation_hashes"] = {name: digest((package / name).read_bytes()) for name in (
        "flow.py", "compiler.py", "models.py", "extraction/llvm_api.py",
        "extraction/llvm_flow.py", "extraction/ast_extractor.py",
        "graph/knowledge_graph.py", "views/flow.py")}
    try:
        # Preprocess once, retaining the exact compiler input and line markers.
        command = [str(clang), *effective, "-E", str(source), "-o", str(output / "source.i")]
        manifest["preprocess_command"] = command
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=timeout)
        (output / "preprocess.stderr.txt").write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            raise ValueError(f"Preprocessing failed ({result.returncode}); see preprocess.stderr.txt")
        preprocessed = (output / "source.i").read_bytes()
        manifest["preprocessed_sha256"] = digest(preprocessed)
        command = [str(clang), *effective, "-x", "cpp-output",
                   "-S", "-emit-llvm", str(output / "source.i"),
                   "-o", str(output / "source.ll")]
        manifest["ir_command"] = command
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=timeout)
        (output / "compiler.stderr.txt").write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            raise ValueError(f"IR compilation failed ({result.returncode}); see compiler.stderr.txt")
        ir = (output / "source.ll").read_bytes()
        manifest["ir_sha256"] = digest(ir)
        configure_libclang()
        tu = cindex.Index.create().parse(str(source), args=[*effective, "-working-directory", str(directory)],
            options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
        diagnostics = [str(d) for d in tu.diagnostics]
        manifest["ast_diagnostics"] = diagnostics
        if any(d.severity >= cindex.Diagnostic.Error for d in tu.diagnostics):
            raise ValueError("AST parsing failed; see manifest diagnostics")
        inputs = {source, *(Path(str(i.include)).resolve() for i in tu.get_includes())}
        manifest["input_hashes"] = {str(p): digest(p.read_bytes()) for p in sorted(inputs) if p.is_file()}
        graph = KnowledgeGraph.from_fragments([extract_translation_unit(
            tu.cursor, repo_root=repo_root, translation_unit=source)])
        configuration = digest(json.dumps([relative, effective, manifest["preprocessed_sha256"], version]).encode())
        manifest["configuration"] = configuration
        manifest["flow"] = add_llvm_flow(graph, ir, library=llvm_library, repo_root=repo_root,
                                         translation_unit=relative, configuration=configuration)
        # Detect source/header changes during the separate AST and IR passes.
        check = subprocess.run(manifest["preprocess_command"][:-1] + ["-"], cwd=directory,
                               capture_output=True, timeout=timeout)
        if check.returncode or check.stdout.replace(b"\r\n", b"\n") != preprocessed.replace(b"\r\n", b"\n"):
            raise ValueError("Preprocessed inputs changed during extraction")
        manifest["status"] = "completed"
        write_snapshot(graph, output / "code-intelligence.json", provenance={
            "source_revision": "sha256:" + manifest["source_sha256"], "dirty": None,
            "producer": "code_intelligence.flow", "producer_version": "1",
            "flow_evidence": manifest,
        })
        manifest["graph_sha256"] = digest((output / "code-intelligence.json").read_bytes())
        for projection in (control_flow_graph(graph), data_flow_graph(graph)):
            payload = projection.to_dict()
            payload["canonical_graph_sha256"] = manifest["graph_sha256"]
            (output / (projection.kind + ".json")).write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except BaseException as exc:
        manifest.update(status="failed", error=str(exc))
        raise
    finally:
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compile-db", type=Path)
    parser.add_argument("--clang", type=Path, default=Path(shutil.which("clang") or "clang"))
    parser.add_argument("--llvm-library", type=Path, required=True)
    parser.add_argument("compiler_args", nargs=argparse.REMAINDER)
    options = parser.parse_args()
    args = options.compiler_args
    if args[:1] == ["--"]:
        args = args[1:]
    directory = options.repo
    if options.compile_db:
        from clang import cindex
        configure_libclang()
        db = cindex.CompilationDatabase.fromDirectory(str(options.compile_db.resolve()))
        commands = list(db.getCompileCommands(str(options.source.resolve())) or ())
        if len(commands) != 1:
            parser.error("Expected exactly one compilation command for source")
        command = commands[0]
        directory = Path(command.directory)
        raw = list(command.arguments)[1:]
        args = [a for a in raw if a != "--" and Path(a).as_posix() != options.source.resolve().as_posix()] + args
    result = generate_flow(source=options.source, repo_root=options.repo, output=options.output,
                           clang=options.clang, llvm_library=options.llvm_library,
                           args=args, directory=directory)
    print(json.dumps({"status": result["status"], "output": str(options.output), "flow": result["flow"]}, indent=2))


if __name__ == "__main__":
    main()
