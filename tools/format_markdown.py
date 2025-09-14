"""Lightweight Markdown formatter for line wrapping.

Features:
  * Wraps lines longer than --line-length outside fenced code blocks
  * Preserves indentation & list markers
  * Skips lines containing raw URLs longer than limit (to avoid breaking links)
  * Skips tables (lines containing pipe '|' with multiple columns) and headings

Usage (fix in-place):
  python tools/format_markdown.py --fix file1.md file2.md

Pre-commit integration uses --fix. For a dry run, omit --fix to just report.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def wrap_text(line: str, limit: int) -> list[str]:
    if len(line) <= limit:
        return [line]
    out: list[str] = []
    current = line
    while len(current) > limit:
        # Find break position before limit
        break_pos = current.rfind(" ", 0, limit)
        if break_pos == -1:
            # No space; hard break
            break_pos = limit
        out.append(current[:break_pos].rstrip())
        current = current[break_pos:].lstrip()
    if current:
        out.append(current)
    return out


def process(content: str, limit: int) -> str:
    lines = content.splitlines()
    in_code = False
    fence_re = re.compile(r"^\s*```")
    processed: list[str] = []
    for line in lines:
        if fence_re.match(line):
            in_code = not in_code
            processed.append(line)
            continue
        if in_code:
            processed.append(line)
            continue
        if (
            len(line) <= limit
            or line.lstrip().startswith("#")
            or "http://" in line
            or "https://" in line
            or line.count("|") >= 2  # likely a table row
        ):
            processed.append(line)
            continue
        # Respect list indentation
        leading_ws = re.match(r"^\s*", line).group(0)  # type: ignore[arg-type]
        bullet_match = re.match(r"^(\s*[-*+] |\s*\d+\.)", line)
        prefix = bullet_match.group(0) if bullet_match else leading_ws
        core = line[len(prefix) :]
        wrapped = wrap_text(core, limit - len(prefix))
        for i, seg in enumerate(wrapped):
            processed.append(
                (
                    prefix
                    if i == 0
                    else leading_ws + (" " * (len(prefix) - len(leading_ws)))
                )
                + seg
            )
    return "\n".join(processed) + "\n"


def handle_file(path: Path, limit: int, fix: bool) -> int:
    original = path.read_text(encoding="utf-8")
    new = process(original, limit)
    if new != original:
        if fix:
            path.write_text(new, encoding="utf-8")
            print(f"Reformatted: {path}")
        else:
            print(f"Would reformat: {path}")
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Format markdown to wrap long lines")
    parser.add_argument("files", nargs="*", help="Markdown files to format")
    parser.add_argument("--line-length", type=int, default=120)
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args(argv)

    if not args.files:
        return 0
    status = 0
    for f in args.files:
        path = Path(f)
        if not path.exists() or path.suffix.lower() not in {".md", ".markdown"}:
            continue
        status |= handle_file(path, args.line_length, args.fix)
    return status


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
