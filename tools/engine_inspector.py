# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Engine Inspector
================
Classifies engine modules by purpose (OS, Lyrixa, UI, Experimental), detects duplicates,
finds references, and proposes actions (keep/move/deprecate/remove). No changes are made.

Outputs:
- ENGINE_INSPECTION_REPORT.md
- engine_inspection.json
"""

from __future__ import annotations

# Standard library imports
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".venv",
    "__pycache__",
    "node_modules",
    "final_organization_backup",
    "comprehensive_cleanup_backup",
    "focused_cleanup_backup",
}

ENGINE_NAME_RE = re.compile(r"class\s+(\w+Engine)\b")
DOCSTRING_RE = re.compile(r"^\s*\"\"\"(.*?)\"\"\"", re.DOTALL)
IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+([\w\.]+)", re.MULTILINE)


@dataclass
class EngineInfo:
    file: str
    module: str
    classes: List[str]
    doc: str
    imports: List[str]
    references_os: List[str]
    references_lyrixa: List[str]
    references_ui: List[str]
    references_tests: List[str]
    references_docs: List[str]
    bucket: str  # memory | consciousness | cognitive | analytics | other
    intended_for: str  # OS | Lyrixa | Shared | Unknown
    suggested_move: Optional[str]
    duplicate_of: Optional[str]
    action: str  # keep | keep-move | deprecate | remove
    reasons: List[str]


def iter_py_files() -> List[Path]:
    files: List[Path] = []
    for root, dirs, fs in os.walk(ROOT):
        if any(part in SKIP_DIRS for part in Path(root).parts):
            continue
        for f in fs:
            if f.endswith(".py"):
                files.append(Path(root) / f)
    return files


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def path_to_module(p: Path) -> str:
    rel = str(p).replace(str(ROOT) + os.sep, "").replace("\\", "/")
    return rel.replace("/", ".")


def bucket_for(p: Path, classes: List[str], doc: str) -> str:
    s = f"{p.as_posix()}\n{doc}".lower()
    if "/consciousness/" in s or "consciousness" in s:
        return "consciousness"
    if "/memory/" in s or "memory" in s:
        return "memory"
    if "reasoning" in s or "cognitive" in s:
        return "cognitive"
    if "analytics" in s or "insight" in s:
        return "analytics"
    return "other"


def intended_for_area(
    p: Path, imports: List[str], refs_os: bool, refs_lyrixa: bool, refs_ui: bool
) -> str:
    path_s = p.as_posix()
    if path_s.startswith("Aetherra/consciousness/"):
        # Core consciousness under OS, visualized by UI/Lyrixa
        return "Shared"
    if path_s.startswith("Aetherra/lyrixa/"):
        return "Lyrixa"
    if path_s.startswith("Aetherra/aetherra_core/"):
        return "OS"
    if refs_os and refs_lyrixa:
        return "Shared"
    if refs_os:
        return "OS"
    if refs_ui or refs_lyrixa:
        return "Lyrixa"
    return "Unknown"


def collect_references(
    target_module: str, class_names: List[str], all_files: List[Path]
) -> tuple[List[str], List[str], List[str], List[str], List[str]]:
    os_refs: Set[str] = set()
    lyrixa_refs: Set[str] = set()
    ui_refs: Set[str] = set()
    tests_refs: Set[str] = set()
    docs_refs: Set[str] = set()

    mod_key = target_module.replace(".py", "")
    class_re = (
        re.compile(r"\b(" + "|".join(re.escape(c) for c in class_names) + r")\b")
        if class_names
        else None
    )

    for f in all_files:
        s = str(f).replace("\\", "/")
        txt = read_text(f)
        if not txt:
            continue
        found = (mod_key in txt) or (class_re.search(txt) if class_re else False)
        if not found:
            continue
        rel = s.replace(str(ROOT).replace("\\", "/") + "/", "")
        if rel in (target_module,):
            continue
        if rel.startswith("aetherra_os") or rel in {
            "aetherra_os.py",
            "aetherra_os_launcher.py",
            "aether.py",
        }:
            os_refs.add(rel)
        elif rel.startswith("Aetherra/lyrixa/"):
            lyrixa_refs.add(rel)
        elif rel.startswith("Aetherra/gui/"):
            ui_refs.add(rel)
        elif "/test" in rel or rel.startswith("tests/") or rel.startswith("phase_"):
            tests_refs.add(rel)
        elif rel.endswith(".md"):
            docs_refs.add(rel)
        else:
            # general code – ignore for area bucketing
            pass

    return (
        sorted(os_refs),
        sorted(lyrixa_refs),
        sorted(ui_refs),
        sorted(tests_refs),
        sorted(docs_refs),
    )


def suggest_move(p: Path, bucket: str, intended: str) -> Optional[str]:
    s = p.as_posix()
    if intended == "OS":
        if bucket == "memory" and not s.startswith("Aetherra/aetherra_core/memory/"):
            return "Aetherra/aetherra_core/memory/"
        if bucket == "cognitive" and not s.startswith(
            "Aetherra/aetherra_core/cognitive/"
        ):
            return "Aetherra/aetherra_core/cognitive/"
        if bucket == "consciousness" and not s.startswith("Aetherra/consciousness/"):
            return "Aetherra/consciousness/"
    if intended == "Lyrixa":
        if not s.startswith("Aetherra/lyrixa/"):
            return "Aetherra/lyrixa/"
    return None


def main() -> int:
    py_files = iter_py_files()

    engines: List[EngineInfo] = []

    # First pass: collect classes and docs
    for p in py_files:
        name = p.name
        if not (
            "engine" in name
            or "/consciousness/" in p.as_posix()
            or "/memory/" in p.as_posix()
        ):
            continue
        text = read_text(p)
        if not text:
            continue
        classes = ENGINE_NAME_RE.findall(text)
        if not classes:
            continue
        m = DOCSTRING_RE.search(text)
        doc = m.group(1).strip() if m else ""
        imports = [imp.strip() for imp in IMPORT_RE.findall(text)]

        module = path_to_module(p)
        (refs_os, refs_lyrixa, refs_ui, refs_tests, refs_docs) = collect_references(
            module, classes, py_files
        )

        bucket = bucket_for(p, classes, doc)
        intended = intended_for_area(
            p, imports, bool(refs_os), bool(refs_lyrixa), bool(refs_ui)
        )
        move_to = suggest_move(p, bucket, intended)

        engines.append(
            EngineInfo(
                file=p.as_posix(),
                module=module,
                classes=classes,
                doc=doc[:300],
                imports=imports[:40],
                references_os=refs_os,
                references_lyrixa=refs_lyrixa,
                references_ui=refs_ui,
                references_tests=refs_tests,
                references_docs=refs_docs,
                bucket=bucket,
                intended_for=intended,
                suggested_move=move_to,
                duplicate_of=None,
                action="keep",  # default, may change next pass
                reasons=[],
            )
        )

    # Detect duplicates by class name across files
    class_map: Dict[str, List[EngineInfo]] = {}
    for e in engines:
        for c in e.classes:
            class_map.setdefault(c, []).append(e)

    for cname, infos in class_map.items():
        if len(infos) <= 1:
            continue

        def rank(info: EngineInfo) -> tuple[int, int]:
            """Ranking heuristic to pick canonical implementation."""
            path = info.file
            if (
                "Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/quantum_memory_engine.py"
                in path
            ):
                return (0, len(path))
            if "/aetherra_core/engine/" in path:
                return (1, len(path))
            if "/consciousness/quantum/" in path:
                return (2, len(path))
            return (9, len(path))

        canonical = sorted(infos, key=rank)[0]
        for info in infos:
            if info is canonical:
                continue
            info.duplicate_of = canonical.file
            info.action = "deprecate"
            info.reasons.append(f"Duplicate class {cname}; canonical: {canonical.file}")

    # Propose actions
    for e in engines:
        if e.duplicate_of:
            continue
        if e.intended_for in {"OS", "Lyrixa", "Shared"}:
            if e.suggested_move:
                e.action = "keep-move"
                e.reasons.append(
                    f"Suggest moving to {e.suggested_move} for consistency"
                )
            else:
                e.action = "keep"
        else:
            # No references and unknown purpose => quarantine instead of remove
            has_refs = any(
                [
                    e.references_os,
                    e.references_lyrixa,
                    e.references_ui,
                    e.references_tests,
                ]
            )
            if not has_refs:
                e.action = "deprecate"
                e.reasons.append("No runtime references found; mark deprecated/legacy")
            else:
                e.action = "keep"
                e.reasons.append("Referenced in tests/docs; keep for now")

    # Emit JSON
    out_json = ROOT / "engine_inspection.json"
    out_json.write_text(
        json.dumps([asdict(e) for e in engines], indent=2), encoding="utf-8"
    )

    # Emit Markdown
    lines: List[str] = [
        "# Engine Inspection Report",
        "",
        "| File | Classes | Bucket | Intended | OS | Lyrixa | UI | Tests | Action |",
        "|---|---|---|---|:---:|:---:|:---:|:---:|---|",
    ]
    for e in sorted(engines, key=lambda x: (x.intended_for, x.bucket, x.file)):
        lines.append(
            f"| {e.file.replace(str(ROOT) + '/', '')} | {', '.join(e.classes)} | {e.bucket} | {e.intended_for} | "
            f"{'✅' if e.references_os else '—'} | {'✅' if e.references_lyrixa else '—'} | {'✅' if e.references_ui else '—'} | {'✅' if e.references_tests else '—'} | {e.action} |"
        )
    lines.append("")
    lines.append("## Notes")
    for e in engines:
        if e.reasons:
            lines.append(f"- {e.file}:")
            for r in e.reasons:
                lines.append(f"  - {r}")

    (ROOT / "ENGINE_INSPECTION_REPORT.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print(
        "Engine inspection complete -> ENGINE_INSPECTION_REPORT.md, engine_inspection.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
