#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Generate docs/SYSTEM_INDEX.md from current system documents with purpose and status.

Heuristics:
- Purpose: try to extract the first descriptive line ("This document describes...")
  or the first bullet under a "Purpose and scope" section; fallback to a static map.
- Status: scan for keywords in the doc (Implemented/Partial/Planned) under "At-a-glance"
  and reduce to one of: implemented (✅), partial (🚧), planned (🔮).

Run: python tools/update_system_index.py
"""

from __future__ import annotations

import datetime as _dt
import io
import os
import re
import sys
from typing import Dict, List, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DOCS_DIR = os.path.join(ROOT, "docs")
OUT_FILE = os.path.join(DOCS_DIR, "SYSTEM_INDEX.md")


DOCS: List[Tuple[str, str]] = [
    ("Aether Script Language System", "Aether_Script_Language_System.md"),
    ("Aetherra Kernel System", "AETHERRA_KERNEL_SYSTEM.md"),
    (
        "Aetherra Artificial Intelligence System",
        "AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md",
    ),
    ("Aetherra Agent System", "AETHERRA_AGENT_SYSTEM.md"),
    ("Aetherra Memory System", "AETHERRA_MEMORY_SYSTEM.md"),
    ("Aetherra Security System", "AETHERRA_SECURITY_SYSTEM.md"),
    ("Aetherra Coding System (Lyrixa Code Studio)", "AETHERRA_CODING_SYSTEM.md"),
    ("Aetherra AI Trainer System", "AETHERRA_AI_TRAINER_SYSTEM.md"),
    ("Aetherra Lyrixa System", "AETHERRA_LYRIXA_SYSTEM.md"),
    ("Aetherra Chat System", "AETHERRA_CHAT_SYSTEM.md"),
]


FALLBACK_PURPOSE: Dict[str, str] = {
    "Aether Script Language System": "Grammar, execution rules, policies, and signing/verification for `.aether`.",
    "Aetherra Kernel System": "Kernel runtime loop, service registry, launcher phases, control-plane, backpressure, metrics.",
    "Aetherra Artificial Intelligence System": "AetherraEngine (reasoning, memory integration, task execution), developer AI APIs, evaluation hooks.",
    "Aetherra Agent System": "Agent orchestrator and task lifecycle; Hub Agents API; Prometheus metrics.",
    "Aetherra Memory System": "Core/advanced memory layers, RAG-oriented recall, narratives, QFAC/quantum bridges, health/pulse.",
    "Aetherra Security System": "Signing (scripts/plugins), secrets, sandbox/capabilities, network policy, telemetry privacy, scans.",
    "Aetherra Coding System (Lyrixa Code Studio)": "AI-native coding orchestration (plan → code → test → secure → sign → ship), Spec → Tests gate, tooling.",
    "Aetherra AI Trainer System": "Training/evaluation pipeline, datasets and curation, model registry, trainer orchestrator, and Prometheus/Hub surfaces.",
    "Aetherra Lyrixa System": "Conversational and interface layer: chat service, Hub chat bridge, GUI/CLI integration, and Lyrixa plugin system.",
    "Aetherra Chat System": "Platform-level chat transport and contracts (JSON ask, SSE stream, safety middleware, backpressure, observability).",
}

# Optional phases and dependencies hints. Fill in as known; omitted items render nothing.
PHASES: Dict[str, str] = {
    # Example: "2/4" → shown as "(Phase 2 of 4)"
    # Provide one as requested example:
    "Aetherra Memory System": "2/4",
}

DEPENDENCIES: Dict[str, str] = {
    "Aetherra Kernel System": "required by all",
    "Aetherra Memory System": "required by Lyrixa, AI System, Agents",
    "Aetherra Security System": "hooks into Kernel and Memory",
}

FOUNDATIONAL_FILES: List[Tuple[str, List[str]]] = [
    (
        "Aetherra Manifesto",
        [
            os.path.join(DOCS_DIR, "AETHERRA_MANIFESTO.md"),
            os.path.join(ROOT, "Aetherra", "docs", "AETHERRA_MANIFESTO.md"),
            os.path.join(ROOT, "docs-organized", "manifesto", "AETHERRA_MANIFESTO.md"),
        ],
    ),
    (
        "AI OS Manifesto",
        [
            os.path.join(DOCS_DIR, "AI_OS_MANIFESTO.md"),
            os.path.join(ROOT, "Aetherra", "docs", "AI_OS_MANIFESTO.md"),
            os.path.join(ROOT, "docs-organized", "manifesto", "AI_OS_MANIFESTO.md"),
        ],
    ),
    (
        "Aetherra Labs Vision",
        [
            os.path.join(DOCS_DIR, "aetherra_labs_vision.md"),
            os.path.join(ROOT, "Aetherra", "docs", "aetherra_labs_vision.md"),
            os.path.join(
                ROOT, "docs-organized", "manifesto", "aetherra_labs_vision.md"
            ),
        ],
    ),
]


def _rel_from_docs(abs_path: str) -> str:
    return os.path.relpath(abs_path, DOCS_DIR).replace("\\", "/")


def find_foundational_docs() -> List[Tuple[str, str]]:
    found: List[Tuple[str, str]] = []
    for title, candidates in FOUNDATIONAL_FILES:
        for p in candidates:
            if os.path.exists(p):
                found.append((title, _rel_from_docs(p)))
                break
    return found


def _read_text(path: str) -> str:
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def extract_purpose(name: str, text: str) -> str:
    # 1) Look for an explicit descriptive sentence near the top
    for line in text.splitlines()[:60]:
        s = line.strip()
        if s.lower().startswith("this document describes"):
            return s.rstrip(".") + "."
    # 2) Look for the Purpose and scope section and take the first bullet
    purpose_sec = re.search(
        r"^##\s*Purpose and scope\s*$", text, re.IGNORECASE | re.MULTILINE
    )
    if purpose_sec:
        # slice from section to next header
        start = purpose_sec.end()
        nxt = re.search(r"^##\s+", text[start:], re.MULTILINE)
        block = text[start:] if not nxt else text[start : start + nxt.start()]
        for line in block.splitlines():
            ls = line.strip()
            if ls.startswith("-"):
                return ls.lstrip("- ")
    # 3) Fallback static mapping
    return FALLBACK_PURPOSE.get(name, "")


def extract_status(text: str) -> Tuple[str, str]:
    """Return (emoji, label) reduced status from doc content."""
    # Narrow to At-a-glance section if present to avoid noise
    block = text
    m = re.search(r"^##\s*At.?a.?glance status\s*$", text, re.IGNORECASE | re.MULTILINE)
    if m:
        start = m.end()
        nxt = re.search(r"^##\s+", text[start:], re.MULTILINE)
        block = text[start:] if not nxt else text[start : start + nxt.start()]

    impl = len(re.findall(r"\bImplemented\b", block, re.IGNORECASE))
    part = len(re.findall(r"\bPartial|Partially\b", block, re.IGNORECASE))
    plan = len(re.findall(r"\bPlanned\b", block, re.IGNORECASE))

    # Reduce to a single status
    if impl > 0 and plan == 0 and part == 0:
        return "✅", "Implemented"
    if impl > 0 and (plan > 0 or part > 0):
        return "🚧", "Partial"
    if impl == 0 and (plan > 0 or part > 0):
        return "🔮", "Planned"
    # Fallback
    return "🚧", "Partial"


def generate() -> str:
    today = _dt.date.today().isoformat()
    lines: List[str] = []
    lines.append("# Aetherra System Index")
    lines.append("")
    lines.append(f"Last updated: {today}")
    lines.append("")
    lines.append(
        "This dashboard lists the core system documents, their purpose, and current implementation status across the Aetherra architecture."
    )
    lines.append("")
    lines.append("Legend: ✅ implemented · 🚧 partial · 🔮 planned")
    lines.append("")

    # Foundational Documents section (if any discovered)
    fdocs = find_foundational_docs()
    if fdocs:
        lines.append("## Foundational Documents")
        lines.append("")
        for title, rel in fdocs:
            lines.append(f"- {title} — ./{rel}")
        lines.append("")

    impl_count = part_count = plan_count = 0
    for name, rel in DOCS:
        path = os.path.join(DOCS_DIR, rel)
        txt = _read_text(path)
        purpose = extract_purpose(name, txt)
        emoji, label = extract_status(txt)
        if emoji == "✅":
            impl_count += 1
        elif emoji == "🚧":
            part_count += 1
        elif emoji == "🔮":
            plan_count += 1
        lines.append(f"- {name} — ./{rel}")
        if purpose:
            lines.append(f"  - Purpose: {purpose}")
        # Optional phase
        phase = PHASES.get(name)
        phase_str = f" (Phase {phase})" if phase else ""
        lines.append(f"  - Status: {emoji} {label}{phase_str}")
        # Dependencies notes (optional)
        dep = DEPENDENCIES.get(name)
        if dep:
            lines.append(f"  - Dependencies: {dep}")
        # Memory extension note
        if name == "Aetherra Memory System":
            lines.append(
                "  - Extension: DNA-inspired encoding & Living Memory Genome (see separate spec)."
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    # Quick status heatmap
    lines.append(
        f"Quick status: ✅ Implemented: {impl_count} · 🚧 Partial: {part_count} · 🔮 Planned: {plan_count}"
    )
    lines.append("")
    lines.append("How to use")
    lines.append("")
    lines.append(
        "- Start here for system overviews and contracts; each doc links to files, APIs, and env flags."
    )
    lines.append("- For a full repository file index, see ./FILE_INDEX.md.")
    lines.append(
        '- To verify behavior locally, use VS Code tasks under Test/Build (e.g., "Verify Aetherra OS (Headless Smoke)" and "Verify Claims").'
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: List[str]) -> int:
    out = generate()
    os.makedirs(DOCS_DIR, exist_ok=True)
    with io.open(OUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print(f"[OK] Wrote {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
