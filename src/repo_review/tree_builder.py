# src/repo_review/tree_builder.py

from pathlib import Path

from models import FileNode


def build_tree(root: Path) -> list[FileNode]:
    nodes = []

    for path in root.rglob("*"):
        stat = path.stat()

        relative = path.relative_to(root).as_posix()

        nodes.append(
            FileNode(
                relative_path=relative,
                is_dir=path.is_dir(),
                size=stat.st_size,
                extension=path.suffix.lower(),
                depth=len(Path(relative).parts),
                name=path.name,
            )
        )

    return nodes