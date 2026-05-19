import pathspec
try:
    from .models import ValidationIssue
except ImportError:  # pragma: no cover
    from models import ValidationIssue

# =========================================================
# PATH NORMALIZATION
# =========================================================

def normalize(path: str) -> str:
    return path.replace("\\", "/")


# =========================================================
# PATTERN CACHE (IMPORTANT PERFORMANCE FIX)
# =========================================================

_pattern_cache = {}

def match_pattern(path: str, pattern: str) -> bool:
    """
    Git-like glob matching using pathspec (gitwildmatch)
    with caching for performance.
    """
    path = normalize(path)
    pattern = normalize(pattern)

    if pattern not in _pattern_cache:
        _pattern_cache[pattern] = pathspec.PathSpec.from_lines(
            "gitwildmatch",
            [pattern]
        )

    return _pattern_cache[pattern].match_file(path)


# =========================================================
# REQUIRED PATHS
# =========================================================

def validate_required_paths(nodes, policy):
    issues = []

    files = [
        normalize(n.relative_path)
        for n in nodes
        if not n.is_dir
    ]

    dirs = {
        normalize(n.relative_path)
        for n in nodes
        if n.is_dir
    }

    for required in policy.get("required_paths", []):
        req = normalize(required)

        # directory rule
        if req.endswith("/"):
            req_dir = req.rstrip("/")

            if req_dir not in dirs:
                issues.append(
                    ValidationIssue(
                        severity="HIGH",
                        rule="required_paths",
                        path=req,
                        message=f"Missing required directory: {req}",
                    )
                )
            continue

        # file/pattern rule
        found = False

        for file_path in files:
            if match_pattern(file_path, req):
                found = True
                break

        if not found:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="required_paths",
                    path=req,
                    message=f"Missing required path: {req}",
                )
            )

    return issues


# =========================================================
# FORBIDDEN PATHS
# =========================================================

def validate_forbidden_paths(nodes, policy):
    issues = []

    for forbidden in policy.get("forbidden_paths", []):
        for node in nodes:
            path = normalize(node.relative_path)

            if match_pattern(path, forbidden):
                issues.append(
                    ValidationIssue(
                        severity="HIGH",
                        rule="forbidden_paths",
                        path=node.relative_path,
                        message=f"Forbidden path exists: {node.relative_path}",
                    )
                )

    return issues


# =========================================================
# ALLOWED EXTENSIONS
# =========================================================

def validate_allowed_extensions(nodes, policy):
    issues = []

    rules = policy.get("allowed_extensions", {})

    for base, allowed in rules.items():
        base = normalize(base).rstrip("/")

        for node in nodes:
            if node.is_dir:
                continue

            path = normalize(node.relative_path)

            if match_pattern(path, base + "/**"):
                if node.extension not in allowed:
                    issues.append(
                        ValidationIssue(
                            severity="MEDIUM",
                            rule="allowed_extensions",
                            path=node.relative_path,
                            message=f"Extension {node.extension} not allowed in {base}",
                        )
                    )

    return issues


# =========================================================
# FORBIDDEN EXTENSIONS
# =========================================================

def validate_forbidden_extensions(nodes, policy):
    issues = []

    rules = policy.get("forbidden_extensions", {})

    for base, forbidden in rules.items():
        base = normalize(base).rstrip("/")

        for node in nodes:
            if node.is_dir:
                continue

            path = normalize(node.relative_path)

            if match_pattern(path, base + "/**"):
                if node.extension in forbidden:
                    issues.append(
                        ValidationIssue(
                            severity="HIGH",
                            rule="forbidden_extensions",
                            path=node.relative_path,
                            message=f"Forbidden extension {node.extension}",
                        )
                    )

    return issues


# =========================================================
# REQUIRED FILE TYPES
# =========================================================

def validate_required_file_types(nodes, policy):
    issues = []

    rules = policy.get("required_file_types", {})

    for base, required_exts in rules.items():
        base = normalize(base).rstrip("/")

        found = any(
            (not n.is_dir)
            and match_pattern(normalize(n.relative_path), base + "/**")
            and (n.extension in required_exts)
            for n in nodes
        )

        if not found:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="required_file_types",
                    path=base,
                    message=f"Missing required file types: {required_exts}",
                )
            )

    return issues


# =========================================================
# TREE RULES
# =========================================================

def validate_tree_rules(nodes, policy):
    issues = []

    rules = policy.get("tree_rules", {})

    max_depth = rules.get("max_depth")
    max_files = rules.get("max_total_files")
    max_dirs = rules.get("max_total_dirs")

    if max_depth:
        for node in nodes:
            if node.depth > max_depth:
                issues.append(
                    ValidationIssue(
                        severity="MEDIUM",
                        rule="tree_rules",
                        path=node.relative_path,
                        message=f"Exceeded max depth {max_depth}",
                    )
                )

    if max_files:
        file_count = sum(1 for n in nodes if not n.is_dir)

        if file_count > max_files:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="tree_rules",
                    path="/",
                    message=f"Too many files: {file_count}",
                )
            )

    if max_dirs:
        dir_count = sum(1 for n in nodes if n.is_dir)

        if dir_count > max_dirs:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="tree_rules",
                    path="/",
                    message=f"Too many directories: {dir_count}",
                )
            )

    return issues


# =========================================================
# SIZE RULES
# =========================================================

def validate_size_rules(nodes, policy):
    issues = []

    rules = policy.get("size_rules", {})

    global_limit = rules.get("max_file_size_mb", 0)
    ext_limits = rules.get("extension_limits", {})
    path_limits = rules.get("path_limits", {})
    min_size = rules.get("min_file_size_bytes", 0)

    for node in nodes:
        if node.is_dir:
            continue

        size_mb = node.size / (1024 * 1024)
        path = normalize(node.relative_path)

        if global_limit and size_mb > global_limit:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    rule="size_rules",
                    path=node.relative_path,
                    message=f"Exceeded global size limit {global_limit} MB",
                )
            )

        if node.extension in ext_limits:
            if size_mb > ext_limits[node.extension]:
                issues.append(
                    ValidationIssue(
                        severity="MEDIUM",
                        rule="size_rules",
                        path=node.relative_path,
                        message=f"{node.extension} exceeds limit",
                    )
                )

        for pattern, limit in path_limits.items():
            if match_pattern(path, pattern):
                if size_mb > limit:
                    issues.append(
                        ValidationIssue(
                            severity="HIGH",
                            rule="size_rules",
                            path=node.relative_path,
                            message=f"Exceeded path limit {limit} MB",
                        )
                    )

        if node.size < min_size:
            issues.append(
                ValidationIssue(
                    severity="LOW",
                    rule="size_rules",
                    path=node.relative_path,
                    message="Empty file detected",
                )
            )

    return issues


# =========================================================
# MAIN ENTRY
# =========================================================

def run_structure_validations(nodes, policy):
    issues = []

    issues += validate_required_paths(nodes, policy)
    issues += validate_forbidden_paths(nodes, policy)
    issues += validate_allowed_extensions(nodes, policy)
    issues += validate_forbidden_extensions(nodes, policy)
    issues += validate_required_file_types(nodes, policy)
    issues += validate_tree_rules(nodes, policy)
    issues += validate_size_rules(nodes, policy)

    return issues


def run_validations(nodes, policy):
    """Backward-compatible alias for the structure validation pipeline."""

    return run_structure_validations(nodes, policy)
