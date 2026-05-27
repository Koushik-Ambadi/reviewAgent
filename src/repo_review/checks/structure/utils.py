import pathspec

_pattern_cache = {}

def normalize(path: str) -> str:
    return path.replace("\\", "/")


def match_pattern(path: str, pattern: str) -> bool:
    path = normalize(path)
    pattern = normalize(pattern)

    if pattern not in _pattern_cache:
        _pattern_cache[pattern] = pathspec.PathSpec.from_lines(
            "gitwildmatch",
            [pattern]
        )

    return _pattern_cache[pattern].match_file(path)