# src/repo_review/structure/tree_builder.py

try:
    from ...models import ValidationIssue
except ImportError:  # pragma: no cover
    from models import ValidationIssue

from .utils import normalize, match_pattern


from pathlib import Path
try:
    from ...models import FileNode
except ImportError:  # pragma: no cover
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
