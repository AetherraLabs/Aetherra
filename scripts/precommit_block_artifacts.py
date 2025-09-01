#!/usr/bin/env python
"""
Pre-commit hook: block committing runtime/generated artifacts.

This enforces repo hygiene by preventing common transient files from being committed
even if .gitignore is bypassed. Patterns mirror .gitignore entries added for
outbox/audit/metrics/reports and local temp assets.
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys

FORBIDDEN_GLOBS = [
    # Outbox and audit logs
    "outbox/*.jsonl",
    "outbox/**/*.jsonl",
    "audit/*.jsonl",
    "audit/**/*.jsonl",
    "*audit*.json",
    "*report*.json",
    # Metrics and reports
    "aetherra_kernel_metrics.json",
    "data/aetherra_kernel_metrics.json",
    "ui_standards_report.md",
    "aether_static_report.md",
    # Vendored envs or local temp
    "frontend/Lib/**",
    "frontend/Scripts/**",
    "deployments/local/tmp*/**",
    ".plugin_history/**",
    # Logs likely generated locally
    "*.log",
]


def get_staged_files() -> list[str]:
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(
            "precommit_block_artifacts: failed to list staged files:",
            e,
            file=sys.stderr,
        )
        return []
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


def matches_forbidden(path: str) -> bool:
    # Normalize to forward slashes for glob matching consistency across OSes
    norm = path.replace("\\", "/")
    for pat in FORBIDDEN_GLOBS:
        if fnmatch.fnmatch(norm, pat):
            return True
    return False


def main() -> int:
    staged = get_staged_files()
    if not staged:
        return 0

    blocked = [p for p in staged if matches_forbidden(p)]
    if not blocked:
        return 0

    print(
        "[BLOCKED] The following staged files look like runtime/generated artifacts and should not be committed:"
    )
    for p in blocked:
        print(f"  - {p}")

    print("\nAction:")
    print("  - Unstage them and consider adding/adjusting .gitignore if needed.")
    print("  - If this is intentional, rename/move to a tracked docs/examples path.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
