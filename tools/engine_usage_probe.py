# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Engine Usage Probe (dry-run)
----------------------------
Scans repository for static references to engine modules/classes and reports
which areas reference them (OS launcher, Lyrixa, tests, docs).

This does not move or delete anything. Use it to validate ENGINE_USAGE_MATRIX.md.
"""

from __future__ import annotations

# Standard library imports
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Target:
    file: str
    classes: list[str]
    module_hints: list[str]


TARGETS: list[Target] = [
    Target(
        file="Aetherra/consciousness/quantum/quantum_consciousness_engine.py",
        classes=["QuantumConsciousnessEngine"],
        module_hints=["Aetherra.consciousness.quantum.quantum_consciousness_engine"],
    ),
    Target(
        file="Aetherra/aetherra_core/memory/aetherra_memory_engine.py",
        classes=["AetherraMemoryEngine"],
        module_hints=["Aetherra.aetherra_core.memory.aetherra_memory_engine"],
    ),
    Target(
        file="Aetherra/aetherra_core/memory/QuantumEnhancedMemoryEngine/quantum_memory_engine.py",
        classes=["QuantumEnhancedMemoryEngine"],
        module_hints=[
            "Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine.quantum_memory_engine"
        ],
    ),
    Target(
        file="Aetherra/lyrixa/memory/lyrixa_memory_engine.py",
        classes=["LyrixaMemoryEngine"],
        module_hints=["Aetherra.lyrixa.memory.lyrixa_memory_engine"],
    ),
]


AREAS = {
    "os": [
        "aetherra_os_launcher.py",
        "aetherra_os.py",
        "aetherra_kernel_loop.py",
        "aetherra_service_registry.py",
    ],
    "lyrixa": ["Aetherra/lyrixa/"],
    "tests": ["tests/", "phase_", "test_"],
    "docs": [".md"],
}


def file_matches_area(path: Path, patterns: list[str]) -> bool:
    p = str(path).replace("\\", "/")
    return any(s in p for s in patterns)


def scan_references(target: Target) -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {k: set() for k in AREAS}
    class_names = set(target.classes)
    mod_hints = set(target.module_hints)
    class_regex = re.compile(
        r"\b(" + "|".join(re.escape(c) for c in class_names) + r")\b"
    )
    mod_regex = re.compile(r"(" + "|".join(re.escape(m) for m in mod_hints) + r")")

    for root, _, files in os.walk(ROOT):
        for fname in files:
            # Only scan text-like files
            if not (
                fname.endswith((".py", ".md", ".txt", ".json"))
                or fname.startswith("aetherra_")
            ):
                continue
            fpath = Path(root) / fname
            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            has_ref = class_regex.search(text) or mod_regex.search(text)
            if not has_ref:
                continue

            for area, patterns in AREAS.items():
                if file_matches_area(fpath, patterns):
                    refs[area].add(str(fpath))
    return refs


def main():
    report: dict[str, dict] = {}
    for tgt in TARGETS:
        refs = scan_references(tgt)
        report[tgt.file] = {
            "classes": tgt.classes,
            "module_hints": tgt.module_hints,
            "references": {k: sorted(list(v)) for k, v in refs.items()},
        }

    out = ROOT / "engine_usage_probe_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Engine usage probe written to {out}")


if __name__ == "__main__":
    main()
