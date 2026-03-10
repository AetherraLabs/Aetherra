# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Engine Audit Tool for Aetherra OS
---------------------------------

Scans the repository for engine modules relevant to Aetherra OS, identifies
which are referenced by OS code paths, flags duplicates, and produces a concise
report to help deprecate or remove unused engines. Lyrixa paths are ignored.
"""

from __future__ import annotations

# Standard library imports
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Aetherra"


@dataclass
class EngineArtifact:
    path: str
    module: str
    class_names: list[str]
    used_by_os: bool = False
    notes: str = ""


ENGINE_NAME_RE = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\(?.*:\s*$")


def list_engine_files() -> list[Path]:
    files: list[Path] = []
    for p in ROOT.rglob("*.py"):
        rp = p.relative_to(ROOT).as_posix()
        if (
            "Aetherra/lyrixa/" in rp
            or "/site-packages/" in rp
            or rp.startswith("frontend/")
            or rp.startswith("focused_cleanup_backup/")
            or rp.startswith("final_organization_backup/")
            or rp.startswith("comprehensive_cleanup_backup/")
        ):
            continue
        if "engine" in p.name.lower():
            files.append(p)
    return files


def module_name_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    mod = rel[:-3].replace("/", ".")  # strip .py
    return mod


def extract_classes(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []
    names: list[str] = []
    for line in text:
        m = ENGINE_NAME_RE.match(line.strip())
        if m:
            names.append(m.group(1))
    return names


def gather_os_references() -> str:
    refs: list[str] = []
    for f in [
        ROOT / "aetherra_os_launcher.py",
        ROOT / "aetherra_kernel_loop.py",
        ROOT / "aetherra_os.py",
    ]:
        if f.exists():
            try:
                refs.append(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n".join(refs)


def build_inventory() -> list[EngineArtifact]:
    engine_files = list_engine_files()
    os_refs = gather_os_references()
    inventory: list[EngineArtifact] = []
    for path in engine_files:
        mod = module_name_for(path)
        classes = extract_classes(path)
        # Consider a module used by OS only if its module path appears in OS entrypoints
        used = mod in os_refs
        inventory.append(
            EngineArtifact(
                path=str(path.relative_to(ROOT)),
                module=mod,
                class_names=classes,
                used_by_os=used,
            )
        )
    return inventory


def classify(inventory: list[EngineArtifact]) -> dict[str, list[EngineArtifact]]:
    active: list[EngineArtifact] = []
    candidates: list[EngineArtifact] = []
    duplicates: list[EngineArtifact] = []

    # Known OS-critical modules/classes
    must_have_modules = {
        "Aetherra.aetherra_core.engine.aetherra_engine",
        "Aetherra.aetherra_core.memory.aetherra_memory_engine",
        "Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine.quantum_memory_engine",
        "Aetherra.consciousness.quantum.quantum_consciousness_engine",
    }
    class_occurrences: dict[str, list[EngineArtifact]] = {}

    for art in inventory:
        for cls in art.class_names:
            class_occurrences.setdefault(cls, []).append(art)

    for art in inventory:
        if art.module in must_have_modules or art.used_by_os:
            active.append(art)
        else:
            candidates.append(art)

    for cls, arts in class_occurrences.items():
        if len(arts) > 1 and "Engine" in cls:
            duplicates.extend(arts)

    # Deduplicate duplicate list
    dup_set: set[str] = set()
    uniq_dups: list[EngineArtifact] = []
    for a in duplicates:
        key = f"{a.module}|{a.path}"
        if key not in dup_set:
            dup_set.add(key)
            uniq_dups.append(a)

    return {"active": active, "candidates": candidates, "duplicates": uniq_dups}


def write_report(groups: dict[str, list[EngineArtifact]]):
    out_md = ROOT / "ENGINE_AUDIT_REPORT.md"

    def fmt(lst: list[EngineArtifact]) -> str:
        lines = []
        for a in sorted(lst, key=lambda x: x.path):
            cls = ", ".join(a.class_names) or "(no classes)"
            used = "yes" if a.used_by_os else "no"
            lines.append(
                f"- {a.path}  |  module: {a.module}  |  classes: {cls}  |  used_by_os: {used}"
            )
        return "\n".join(lines) if lines else "(none)"

    md = []
    md.append("# Aetherra OS Engine Audit\n")
    md.append(
        "This report lists engine modules, whether the OS references them, and potential duplicates. Lyrixa paths are excluded.\n"
    )
    md.append("## Active/Referenced by OS\n\n" + fmt(groups["active"]) + "\n")
    md.append("## Potentially Unused Candidates\n\n" + fmt(groups["candidates"]) + "\n")
    md.append("## Duplicate Class Definitions\n\n" + fmt(groups["duplicates"]) + "\n")
    out_md.write_text("\n".join(md), encoding="utf-8")

    out_json = ROOT / "engine_audit.json"
    out_json.write_text(
        json.dumps(
            {k: [asdict(a) for a in v] for k, v in groups.items()},
            indent=2,
        ),
        encoding="utf-8",
    )


def main():
    inventory = build_inventory()
    groups = classify(inventory)
    write_report(groups)
    print("Engine audit complete. See ENGINE_AUDIT_REPORT.md and engine_audit.json.")


if __name__ == "__main__":
    main()
