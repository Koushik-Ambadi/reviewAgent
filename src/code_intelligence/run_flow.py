"""Generate bounded compiler flow evidence inside a review run."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

from code_intelligence.compiler import configure_libclang
from code_intelligence.flow import generate_flow


def _toolchain(policy: dict) -> tuple[Path | None, Path | None]:
    options = policy.get("flow", {})
    clang = Path(options.get("clang") or shutil.which("clang") or "clang")
    library = Path(options.get("llvm_library") or os.getenv("LLVM_C_LIBRARY") or
                   ("C:/Program Files/LLVM/bin/LLVM-C.dll" if os.name == "nt" else "/usr/lib/llvm-22/lib/libLLVM.so"))
    return (clang if clang.is_file() else None, library if library.is_file() else None)


def generate_run_flow(*, repo_root: Path, analysis_dir: Path, sources: list[str],
                      policy: dict | None = None) -> dict:
    """Continue per source after failures; never replace an existing flow bundle."""
    from clang import cindex

    policy = policy or {}
    options = policy.get("flow", {})
    root = (analysis_dir / "flow").resolve()
    root.mkdir(parents=True, exist_ok=True)
    summary = {"schema_version": "1.0", "status": "pending", "sources": [],
               "boundary": "sanitized host C99/LLVM IR; flow is static and memory coverage is partial"}
    unique = sorted(set(sources))
    max_sources = max(1, min(int(options.get("max_sources", 32)), 128))
    clang, library = _toolchain(policy)
    if options.get("enabled", True) is False:
        summary.update(status="disabled", reason="flow.enabled is false")
    elif not clang or not library:
        summary.update(status="unavailable", reason="matching clang and LLVM C library required")
    else:
        configure_libclang()
        db = cindex.CompilationDatabase.fromDirectory(str(analysis_dir / "cmake_build"))
        for relative in unique[:max_sources]:
            source = (repo_root / relative).resolve()
            if not source.is_file() or not source.is_relative_to(repo_root.resolve()) or source.suffix.lower() != ".c":
                summary["sources"].append({"source": relative, "status": "skipped", "reason": "not a repository C source"})
                continue
            name = source.stem + "-" + hashlib.sha256(relative.encode()).hexdigest()[:12]
            output = root / name
            if output.exists():
                summary["sources"].append({"source": relative, "status": "skipped", "reason": "bundle already exists", "bundle": f"flow/{name}"})
                continue
            try:
                commands = list(db.getCompileCommands(str(source)) or ())
                if len(commands) != 1:
                    raise ValueError("expected exactly one compilation command")
                command = commands[0]
                args = list(command.arguments)[1:]
                args = [a for a in args if a != "--" and Path(a).as_posix() != source.as_posix()]
                result = generate_flow(source=source, repo_root=repo_root, output=output,
                    clang=clang, llvm_library=library, args=args, directory=Path(command.directory),
                    timeout=int(options.get("timeout_seconds", 120)))
                summary["sources"].append({"source": relative, "status": "completed", "bundle": f"flow/{name}",
                                           "flow": result["flow"]})
            except (OSError, RuntimeError, ValueError) as exc:
                summary["sources"].append({"source": relative, "status": "failed", "bundle": f"flow/{name}", "reason": str(exc)})
        if len(unique) > max_sources:
            summary["sources"].extend({"source": s, "status": "skipped", "reason": "max_sources limit"} for s in unique[max_sources:])
        statuses = {item["status"] for item in summary["sources"]}
        summary["status"] = "partial" if "failed" in statuses or "skipped" in statuses else "completed"
    (root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--llvm-library", type=Path)
    parser.add_argument("--max-sources", type=int, default=32)
    args = parser.parse_args()
    symbols = json.loads((args.analysis / "symbols.json").read_text(encoding="utf-8"))
    policy = {"flow": {"max_sources": args.max_sources}}
    if args.llvm_library: policy["flow"]["llvm_library"] = str(args.llvm_library)
    print(json.dumps(generate_run_flow(repo_root=args.repo, analysis_dir=args.analysis,
        sources=[s["file"] for s in symbols], policy=policy), indent=2))


if __name__ == "__main__": main()
