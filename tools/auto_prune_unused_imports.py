#!/usr/bin/env python3
"""Bulk prune unused imports reported by ruff F401.

Strategy:
1. Run `ruff check --select F401` beforehand and pipe output to ruff_f401.txt
2. Parse file for lines matching pattern `<path>:<line>:<col>: F401`.
3. For each file, load content, build map of line numbers to remove tokens.
4. Remove entire import line if fully unused and not multi-symbol with still-used names (heuristic: if multiple names separated by commas, drop only offending name; if after removal line becomes just `import` or `from x import` with no names, remove line).
5. Skip lines containing KEEP_F401 or a noqa F401 marker.
6. Skip dynamic/optional heavy imports (PySide6, torch, tensorflow) if behind try/except – leave them; we can add `# noqa: F401` automatically instead.

Idempotent: Safe to re-run; will not remove lines already cleaned.

Limitations: Does not perform static reference analysis; trusts ruff output.
"""

from __future__ import annotations

# Standard library imports
import re
from pathlib import Path

RUFV_FILE = Path("ruff_f401.txt")
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

OPTIONAL_IMPORT_PREFIXES = (
    "PySide6.",
    "torch",
    "tensorflow",
    "cv2",
)


def parse_ruff_report() -> dict[str, list[int]]:
    pattern = re.compile(r"^(?P<path>.+?):(?P<line>\d+):\d+: F401")
    mapping: dict[str, list[int]] = {}
    if not RUFV_FILE.exists():
        print(
            "No ruff_f401.txt found. Run 'ruff check --select F401 | Out-File ruff_f401.txt' first."
        )
        return mapping
    for raw in RUFV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = pattern.match(raw)
        if not m:
            continue
        rel_path = m.group("path").strip()
        line_no = int(m.group("line"))
        mapping.setdefault(rel_path, []).append(line_no)
    return mapping


def prune_file(path: Path, target_lines: set[int]) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    lines = text.splitlines()
    changed = False
    for idx, line in enumerate(lines):
        lineno = idx + 1
        if lineno not in target_lines:
            continue
        # Safeguards
        if "KEEP_F401" in line or "# noqa" in line:
            continue
        stripped = line.strip()
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            continue
        # Optional heavy imports: prefer noqa append
        if any(p in line for p in OPTIONAL_IMPORT_PREFIXES):
            if "# noqa: F401" not in line:
                lines[idx] = line + ("  # noqa: F401 (optional runtime import)")
                changed = True
            continue
        # If multi import list, remove only the symbol hinted by ruff token if possible
        if "," in line and " import " in line:
            # Split at ' import '
            try:
                before, after = line.split(" import ", 1)
            except ValueError:
                before, after = line, ""
            symbols = [s.strip() for s in after.split(",") if s.strip()]
            if len(symbols) > 1:
                # Heuristic: remove last symbol first (cannot know which); if later still flagged, rerun
                symbols = symbols[:-1]
                if symbols:
                    lines[idx] = f"{before} import {', '.join(symbols)}"
                else:
                    lines[idx] = ""  # will be pruned later
                changed = True
                continue
        # Fallback: remove whole line
        lines[idx] = ""
        changed = True
    if changed:
        # Remove consecutive blank lines collapse to max two
        compact: list[str] = []
        blank_run = 0
        for line_content in lines:
            if line_content.strip() == "":
                blank_run += 1
                if blank_run <= 2:
                    compact.append("")
            else:
                blank_run = 0
                compact.append(line_content)
        new_text = "\n".join(compact) + "\n"
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
    return changed


def main():
    mapping = parse_ruff_report()
    if not mapping:
        return
    total_files = 0
    total_changes = 0
    for rel, lines in mapping.items():
        file_path = WORKSPACE_ROOT / rel
        if not file_path.exists():
            continue
        if not file_path.suffix == ".py":
            continue
        if prune_file(file_path, set(lines)):
            total_changes += 1
        total_files += 1
    print(
        f"Prune attempt complete. Files scanned: {total_files}, files modified: {total_changes}."
    )


if __name__ == "__main__":
    main()
