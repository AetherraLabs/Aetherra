# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Regression guard: ensure Lyrixa memory modules don't accidentally grow
duplicate future imports or duplicate class definitions.

This catches issues like a second appended module body or copy-paste merges
that reintroduce `from __future__ import ...` or the same class twice.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def test_memory_modules_have_no_duplicate_future_imports_or_class_redefs():
    root = Path.cwd()
    mem_dir = root / "Aetherra" / "lyrixa" / "memory"
    assert mem_dir.is_dir(), f"memory directory missing: {mem_dir}"

    py_files = sorted(mem_dir.glob("*.py"))
    assert py_files, f"no memory modules found under {mem_dir}"

    future_import_re = re.compile(r"^\s*from\s+__future__\s+import\s+(.+)$", re.M)
    class_def_re = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\(|:)", re.M)

    problems: list[str] = []

    for f in py_files:
        text = _read(f)

        # 1) Duplicate future imports (same feature set imported more than once)
        future_lines = [m.group(1).strip() for m in future_import_re.finditer(text)]
        future_counts = Counter(future_lines)
        dups_future = [feat for feat, c in future_counts.items() if c > 1]
        if dups_future:
            problems.append(
                f"{f}: duplicate future import(s): " + ", ".join(dups_future)
            )

        # 2) Duplicate class definitions of the same name in a single file
        class_names = [m.group(1) for m in class_def_re.finditer(text)]
        class_counts = Counter(class_names)
        dups_classes = [cls for cls, c in class_counts.items() if c > 1]
        if dups_classes:
            problems.append(
                f"{f}: duplicate class definition(s): " + ", ".join(dups_classes)
            )

    assert not problems, "\n".join(["Integrity problems found:"] + problems)
