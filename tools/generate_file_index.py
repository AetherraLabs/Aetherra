#!/usr/bin/env python3
"""
Generate a repository file index appendix with brief purpose hints.

Outputs a Markdown file (default: docs/FILE_INDEX.md) with a hierarchical
listing of key project files. Attempts to extract the first line of a module
docstring or a leading comment for Python files to summarize purpose.

Usage (PowerShell):
  python tools/generate_file_index.py --root . --output docs/FILE_INDEX.md
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

DEFAULT_INCLUDE_EXT = {".py", ".md", ".aether", ".json"}
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".plugin_history",
}

TOP_LEVEL_ONLY = set()  # keep empty to allow full traversal


def extract_python_summary(path: Path) -> Optional[str]:
    """Best-effort: return first line of top-level docstring or leading comment."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    # Try triple-quoted docstring
    m = re.search(r"^[ \t]*[\"\']{3}([^\n\r]+).*?[\"\']{3}", text, re.S | re.M)
    if m:
        line = m.group(1).strip()
        return line if line else None

    # Fallback: first non-empty comment line
    for line in text.splitlines():
        if line.strip().startswith("#"):
            s = line.strip("# ")
            if s:
                return s
        elif line.strip():
            break
    return None


def summarize_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".py":
        s = extract_python_summary(path)
        if s:
            return s
    # Markdown: first heading
    if ext == ".md":
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.lstrip().startswith("#"):
                        return line.lstrip("# ").strip()
        except Exception:
            pass
    return ""


def should_skip_dir(path: Path) -> bool:
    name = path.name
    return name in DEFAULT_EXCLUDE_DIRS


def collect_files(root: Path, include_ext: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        p = Path(dirpath)
        # prune excluded
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS]
        if any(part in DEFAULT_EXCLUDE_DIRS for part in p.parts):
            continue
        for fn in filenames:
            ext = Path(fn).suffix.lower()
            if ext in include_ext:
                files.append(p / fn)
    return files


def make_tree_lines(paths: List[Path], root: Path) -> List[str]:
    # Build a nested map of directories to children
    tree: Dict[str, Dict] = {}
    for path in paths:
        rel = path.relative_to(root).as_posix()
        parts = rel.split("/")
        cursor = tree
        for i, part in enumerate(parts):
            is_file = i == len(parts) - 1
            key = part
            if is_file:
                cursor.setdefault("__files__", []).append(path)
            else:
                cursor = cursor.setdefault(key, {})
    lines: List[str] = []

    def walk(node: Dict, prefix: str, base: Path):
        # Folders first (sorted), then files
        for name in sorted(k for k in node.keys() if k != "__files__"):
            lines.append(f"{prefix}{name}/")
            walk(node[name], prefix + "  ", base / name)
        for path in sorted(node.get("__files__", []), key=lambda p: p.name.lower()):
            summary = summarize_file(path)
            if summary:
                lines.append(f"{prefix}{path.name} — {summary}")
            else:
                lines.append(f"{prefix}{path.name}")

    walk(tree, "", root)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Root folder to index")
    ap.add_argument(
        "--output", default="docs/FILE_INDEX.md", help="Output markdown file"
    )
    ap.add_argument(
        "--ext",
        nargs="*",
        default=sorted(DEFAULT_INCLUDE_EXT),
        help="File extensions to include",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.output)
    include_ext = {
        e.lower() if e.startswith(".") else f".{e.lower()}" for e in args.ext
    }

    # Collect from important subtrees to keep scope relevant
    candidates: List[Path] = []
    include_paths = [
        root / "Aetherra",
        root / "tools",
        root / "tests",
        root / "docs",
    ]
    # also add selected top-level python files
    for item in root.iterdir():
        if item.is_file() and item.suffix.lower() in include_ext:
            candidates.append(item)

    for p in include_paths:
        if p.exists():
            candidates.extend(collect_files(p, include_ext))

    # Deduplicate
    paths = sorted(set(candidates))

    # Build lines
    lines = [
        "# Aetherra File Index",
        "",
        f"Generated from: {root}",
        "",
        "Note: This appendix focuses on key project files. Some generated or cache files are excluded.",
        "",
        "```text",
    ]
    lines.extend(make_tree_lines(paths, root))
    lines.append("```")
    lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] File index written to {out}")


if __name__ == "__main__":
    sys.exit(main())
