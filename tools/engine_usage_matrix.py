# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Engine Usage Matrix
===================
Builds a classification of engine-like modules and whether they are referenced by:
- Aetherra OS paths (aetherra_os*.py, Aetherra/aetherra_core/** excluding lyrixa UI)
- Lyrixa/UI paths (Aetherra/lyrixa/**, Aetherra/gui/**, Aetherra/core/**)

Outputs:
- ENGINE_USAGE_MATRIX.md
- engine_usage_matrix.json
"""

from __future__ import annotations

# Standard library imports
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Set

REPO_ROOT = Path(__file__).resolve().parents[1]


ENGINE_CLASS_RE = re.compile(r"class\s+(\w+Engine)\b")


@dataclass
class EngineUsage:
    file: str
    module_hint: str
    classes: List[str]
    used_by_os: bool
    used_by_lyrixa: bool
    notes: str = ""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _should_skip_dir(root: str) -> bool:
    return any(
        skip in root
        for skip in [
            os.sep + ".venv",
            os.sep + "__pycache__",
            os.sep + "node_modules",
            os.sep + "final_organization_backup",
            os.sep + "comprehensive_cleanup_backup",
            os.sep + "focused_cleanup_backup",
            os.sep + "Aetherra" + os.sep + "tools",
            os.sep + "Aetherra" + os.sep + "plugins" + os.sep + "vendor",
        ]
    )


def discover_engine_files() -> List[Path]:
    candidates: List[Path] = []
    for root, _dirs, files in os.walk(REPO_ROOT):
        if _should_skip_dir(root):
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            p = Path(root) / f
            # Heuristic: scan only files likely containing engines
            if any(tok in f for tok in ["engine", "consciousness", "memory"]):
                candidates.append(p)
    return candidates


def discover_all_py_files() -> List[Path]:
    files_list: List[Path] = []
    for root, _dirs, files in os.walk(REPO_ROOT):
        if _should_skip_dir(root):
            continue
        for f in files:
            if f.endswith(".py"):
                files_list.append(Path(root) / f)
    return files_list


def classify_usage(
    file_text_index: Dict[Path, str], engine_path: Path
) -> Dict[str, bool]:
    used_by_os = False
    used_by_lyrixa = False

    engine_mod_hint = str(engine_path).replace(str(REPO_ROOT) + os.sep, "")
    engine_base = engine_path.stem

    # Simple reference keys
    keys: Set[str] = {
        engine_base,
        engine_mod_hint.replace(os.sep, "."),
    }

    for p, text in file_text_index.items():
        if p == engine_path:
            continue
        if not text:
            continue
        # Determine domain bucket
        rel = str(p).replace(str(REPO_ROOT) + os.sep, "")
        is_os_path = (
            rel.startswith("aetherra_os")
            or rel.startswith("Aetherra" + os.sep + "aetherra_core")
        ) and not rel.startswith("Aetherra" + os.sep + "lyrixa")
        is_lyrixa_path = (
            rel.startswith("Aetherra" + os.sep + "lyrixa")
            or rel.startswith("Aetherra" + os.sep + "gui")
            or rel.startswith("Aetherra" + os.sep + "core")
        )

        found = any(k in text for k in keys)
        if found:
            used_by_os = used_by_os or is_os_path
            used_by_lyrixa = used_by_lyrixa or is_lyrixa_path

    return {"used_by_os": used_by_os, "used_by_lyrixa": used_by_lyrixa}


def main() -> int:
    engine_files = discover_engine_files()

    # Pre-index all texts for faster search (index ALL python files for usage detection)
    all_py_files = discover_all_py_files()
    file_text_index: Dict[Path, str] = {p: read_text(p) for p in all_py_files}
    # Include entrypoints explicitly
    for extra in [REPO_ROOT / "aetherra_os.py", REPO_ROOT / "aetherra_os_launcher.py"]:
        if extra.exists():
            file_text_index[extra] = read_text(extra)

    usages: List[EngineUsage] = []

    for p in engine_files:
        text = file_text_index.get(p) or read_text(p)
        classes = ENGINE_CLASS_RE.findall(text)
        if not classes:
            continue
        usage = classify_usage(file_text_index, p)
        module_hint = str(p).replace(str(REPO_ROOT) + os.sep, "").replace(os.sep, ".")
        notes = ""
        # Additional hints
        if not usage["used_by_os"] and not usage["used_by_lyrixa"]:
            notes = "no references found; candidate for removal"

        usages.append(
            EngineUsage(
                file=str(p),
                module_hint=module_hint,
                classes=classes,
                used_by_os=usage["used_by_os"],
                used_by_lyrixa=usage["used_by_lyrixa"],
                notes=notes,
            )
        )

    # Write JSON
    json_path = REPO_ROOT / "engine_usage_matrix.json"
    json_path.write_text(
        json.dumps([asdict(u) for u in usages], indent=2), encoding="utf-8"
    )

    # Write Markdown
    md_lines = [
        "# Engine Usage Matrix",
        "",
        "| File | Classes | OS | Lyrixa | Notes |",
        "|---|---|:---:|:---:|---|",
    ]
    for u in sorted(
        usages, key=lambda x: (not x.used_by_os, not x.used_by_lyrixa, x.file)
    ):
        md_lines.append(
            f"| {u.file.replace(str(REPO_ROOT) + os.sep, '')} | {', '.join(u.classes)} | {'✅' if u.used_by_os else '—'} | {'✅' if u.used_by_lyrixa else '—'} | {u.notes} |"
        )
    (REPO_ROOT / "ENGINE_USAGE_MATRIX.md").write_text(
        "\n".join(md_lines), encoding="utf-8"
    )

    print(
        "Engine usage matrix generated: ENGINE_USAGE_MATRIX.md, engine_usage_matrix.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
