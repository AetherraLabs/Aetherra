#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Repository analyzer for Aetherra: builds a descriptive, narrative overview
of the project (not just lists) and appends it to docs/PROJECT_OVERVIEW.md.

Outputs:
- docs/PROJECT_ANALYSIS.json: machine-readable snapshot of findings
- docs/PROJECT_OVERVIEW.md: appended "Auto-Generated Overview" with narrative + lists

Safe by default: if no marker blocks exist, we only append an appendix; the
manual sections remain intact. To enable in-place updates, add markers later.
"""

from __future__ import annotations

# Standard library imports
import ast
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    ".next",
    "coverage",
    ".cache",
}

PY_EXT = {".py"}
JS_EXT = {".js", ".mjs", ".cjs", ".ts", ".tsx"}

ENV_VAR_RE = re.compile(r"AETHERRA_[A-Z0-9_]+")
ENV_GET_RE = re.compile(r"(?:os\.getenv\(|os\.environ\[\s*['\"])(AETHERRA_[A-Z0-9_]+)")

FLASK_ROUTE_RE = re.compile(r"@[\w\.]*app\.route\(\s*['\"]([^'\"]+)['\"]")
EXPRESS_ROUTE_RE = re.compile(
    r"(?:(?:app|router)\.)((?:get|post|put|delete|patch|options|head))\(\s*['\"]([^'\"]+)['\"]",
    re.I,
)

REGISTER_SERVICE_RE = re.compile(r"register_service\(\s*['\"]([^'\"]+)['\"]\s*\)")


@dataclass
class ModuleInfo:
    path: str
    doc: Optional[str]
    classes: List[tuple[str, Optional[str]]]
    functions: List[tuple[str, Optional[str]]]


def walk_files(root: Path) -> List[Path]:
    out: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix in PY_EXT or p.suffix in JS_EXT or p.suffix.lower() == ".md":
                out.append(p)
    return out


def safe_read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def parse_py(text: str) -> ModuleInfo:
    try:
        tree = ast.parse(text)
    except Exception:
        return ModuleInfo(path="", doc=None, classes=[], functions=[])
    doc = ast.get_docstring(tree)
    classes: List[tuple[str, Optional[str]]] = []
    functions: List[tuple[str, Optional[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append((node.name, ast.get_docstring(node)))
        elif isinstance(node, ast.FunctionDef):
            # ignore dunder
            if not node.name.startswith("__"):
                functions.append((node.name, ast.get_docstring(node)))
    return ModuleInfo(path="", doc=doc, classes=classes, functions=functions)


def extract_env_vars(text: str) -> Set[str]:
    found = set(ENV_VAR_RE.findall(text))
    found |= set(ENV_GET_RE.findall(text))
    return found


def extract_flask_routes(text: str) -> List[str]:
    return sorted(set(FLASK_ROUTE_RE.findall(text)))


def extract_express_routes(text: str) -> List[tuple[str, str]]:
    return EXPRESS_ROUTE_RE.findall(text)


def extract_services(text: str) -> List[str]:
    return sorted(set(REGISTER_SERVICE_RE.findall(text)))


def collect_tests(root: Path) -> Dict[str, List[str]]:
    tests: Dict[str, List[str]] = {"capabilities": [], "unit": []}
    for p in root.rglob("tests/**/*.py"):
        rel = str(p.relative_to(root)).replace("\\", "/")
        if "/capabilities/" in rel:
            tests["capabilities"].append(rel)
        elif "/unit/" in rel:
            tests["unit"].append(rel)
    tests["capabilities"].sort()
    tests["unit"].sort()
    return tests


def categorize_env_vars(envs: List[str]) -> Dict[str, List[str]]:
    cats = {"QFAC": [], "HUB": [], "GENERAL": []}
    for e in envs:
        if "QFAC" in e:
            cats["QFAC"].append(e)
        elif "HUB" in e or e.startswith("AETHERRA_PEERS"):
            cats["HUB"].append(e)
        else:
            cats["GENERAL"].append(e)
    for k in cats:
        cats[k].sort()
    return cats


def summarize_presence(root: Path) -> Dict[str, Any]:
    """Detect key subsystems by presence of canonical files and dirs."""

    def exists(rel: str) -> bool:
        return (root / rel).exists()

    core = {
        "engine": exists("Aetherra/aetherra_core/engine"),
        "kernel": exists("Aetherra/aetherra_core/kernel"),
        "memory": exists("Aetherra/aetherra_core/memory"),
        "plugins": exists("Aetherra/aetherra_core/plugins"),
        "config": exists("Aetherra/aetherra_core/config"),
    }
    lyrixa = {
        "intelligence": exists("Aetherra/lyrixa/intelligence"),
        "gui": exists("Aetherra/lyrixa/gui"),
        "plugins": exists("Aetherra/lyrixa/plugins"),
        "memory": exists("Aetherra/lyrixa/memory"),
        "launcher": exists("Aetherra/lyrixa/launcher.py"),
    }
    # Hub presence now determined by compatibility module directory (blueprint impl)
    hub = {
        "server": exists("aetherra_hub/compat.py"),
        "federation": exists("Aetherra/hub"),
        "node_assets": exists("Aetherra/aetherra_hub/aetherra_hub"),
    }
    qfac = {
        "integration": exists("Aetherra/aetherra_core/memory/qfac_integration.py"),
        "dashboard": exists("Aetherra/aetherra_core/memory/qfac_dashboard.py"),
        "analyzer": exists(
            "Aetherra/aetherra_core/file_system/compression_analyzer.py"
        ),
    }
    return {"core": core, "lyrixa": lyrixa, "hub": hub, "qfac": qfac}


def read_snippet(path: Path, needle: str) -> Optional[str]:
    """Read file and return a small snippet line containing needle, if any."""
    try:
        for i, line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines()
        ):
            if needle in line:
                return line.strip()
    except Exception:
        pass
    return None


def build_narrative(root: Path, analysis: Dict[str, Any]) -> str:
    pres = summarize_presence(root)
    envs = analysis.get("env_vars", [])
    env_cats = categorize_env_vars(envs)
    flask_routes = analysis.get("flask_routes", [])
    express_routes = analysis.get("express_routes", [])
    services = analysis.get("services", [])
    tests = analysis.get("tests", {})

    # Quick size metrics
    all_py = [p for p in walk_files(root) if p.suffix in PY_EXT]
    core_py = [
        p for p in all_py if "Aetherra/aetherra_core" in str(p).replace("\\", "/")
    ]
    lyrixa_py = [p for p in all_py if "Aetherra/lyrixa" in str(p).replace("\\", "/")]

    # Memory engine adapter hint
    mem_adapter_hint = ""
    mem_path = root / "Aetherra/aetherra_core/memory/aetherra_memory_engine.py"
    if mem_path.exists():
        snippet = read_snippet(
            mem_path, "DEPRECATED: AetherraMemoryEngine is now an adapter"
        )
        if snippet:
            mem_adapter_hint = (
                "The primary memory engine (AetherraMemoryEngine) wraps the QuantumEnhancedMemoryEngine, "
                "providing compatibility while delegating persistence and recall to the canonical engine."
            )

    # Services narrative
    nice_service_names = {
        "memory_system": "Core memory system",
        "plugin_manager": "Plugin manager",
        "aetherra_engine": "Aetherra cognitive engine",
        "kernel_loop": "Kernel event loop",
        "lyrixa_chat": "Lyrixa chat service",
        "qfac_memory_system": "QFAC extension (optional)",
    }
    service_descs = []
    for s in sorted(services):
        service_descs.append(
            f"- {s}: {nice_service_names.get(s, 'registered service')}"
        )

    # Endpoints narrative
    endpoint_lines = []
    if flask_routes:
        endpoint_lines.append("Flask endpoints exposed by the local Hub server:")
        for r in flask_routes:
            endpoint_lines.append(f"  - {r}")
    if express_routes:
        endpoint_lines.append("Node/Express endpoints:")
        for method, r in sorted(express_routes):
            endpoint_lines.append(f"  - {method} {r}")

    # Tests narrative
    caps_count = len(tests.get("capabilities", []))
    unit_count = len(tests.get("unit", []))

    lines: List[str] = []
    lines.append("### Auto-Generated Overview (Repository Analysis)\n")
    lines.append(
        f"This repository contains the Aetherra AI Operating System and Lyrixa assistant. "
        f"It comprises ~{len(all_py)} Python modules, with ~{len(core_py)} in the core OS and ~{len(lyrixa_py)} in Lyrixa."
    )

    # Core
    core_bits = pres["core"]
    core_subs = [k for k, v in core_bits.items() if v]
    if core_subs:
        lines.append(
            f"\nCore (Aetherra/aetherra_core) includes {', '.join(core_subs)}. "
            + (
                mem_adapter_hint
                or "The memory stack includes FractalMesh, quantum bridge, and optional QFAC."
            )
        )

    # Lyrixa
    lyr_bits = pres["lyrixa"]
    lyr_subs = [k for k, v in lyr_bits.items() if v]
    if lyr_subs:
        lines.append(
            f"\nLyrixa (assistant) spans {', '.join(lyr_subs)} and integrates with the OS through the registry and Hub. "
            "The chat service is workspace-aware and can suggest/apply safe fixes with deterministic fallbacks when offline."
        )

    # Hub
    hub_bits = pres["hub"]
    if any(hub_bits.values()):
        hub_items = [k for k, v in hub_bits.items() if v]
        lines.append(
            f"\nHub & Federation includes {', '.join(hub_items)}. "
            "When Flask is present, the local Hub exposes health, stats, plugin registry, federation sync, and a Lyrixa chat bridge."
        )

    # QFAC
    qfac_bits = pres["qfac"]
    if any(qfac_bits.values()):
        qitems = [k for k, v in qfac_bits.items() if v]
        lines.append(
            f"\nQFAC (Quantum Fractal Adaptive Compression) is present ({', '.join(qitems)}). "
            "It is an optional extension that can be enabled via environment flags and verified via capability tests."
        )

    # Services
    if service_descs:
        lines.append("\nKey runtime services detected:")
        lines.extend(service_descs)

    # Endpoints
    if endpoint_lines:
        lines.append("\nEndpoints summary:")
        lines.extend(endpoint_lines)

    # Env vars
    if envs:
        lines.append(
            f"\nEnvironment configuration is active with {len(envs)} AETHERRA_* variables referenced across the codebase. "
            f"Breakdown: QFAC({len(env_cats['QFAC'])}), HUB({len(env_cats['HUB'])}), GENERAL({len(env_cats['GENERAL'])})."
        )

    # Tests
    lines.append(
        f"\nTests provide end-to-end validation (capabilities: {caps_count}) and unit coverage (unit: {unit_count}), "
        "including OS boot, registry collaboration, hub endpoints/federation, memory recall, QFAC-in-OS, and self-maintenance wiring."
    )

    return "\n".join(lines).rstrip() + "\n"


def analyze(root: Path) -> Dict[str, Any]:
    env_vars: Set[str] = set()
    flask_routes: Set[str] = set()
    express_routes: Set[tuple[str, str]] = set()
    services: Set[str] = set()
    modules: Dict[str, ModuleInfo] = {}

    for p in walk_files(root):
        text = safe_read(p)
        if not text:
            continue
        # env
        env_vars |= extract_env_vars(text)
        # endpoints/services/modules
        if p.suffix in PY_EXT:
            flask_routes |= set(extract_flask_routes(text))
            services |= set(extract_services(text))
            mi = parse_py(text)
            mi.path = str(p)
            modules[mi.path] = mi
        elif p.suffix in JS_EXT:
            for method, route in extract_express_routes(text):
                express_routes.add((method.upper(), route))

    tests = collect_tests(root)
    return {
        "generated_at": int(time.time()),
        "env_vars": sorted(env_vars),
        "flask_routes": sorted(flask_routes),
        "express_routes": sorted(list(express_routes)),
        "services": sorted(services),
        "modules_indexed": len(modules),
        "tests": tests,
    }


def append_appendix(
    overview_path: Path, narrative: str, analysis: Dict[str, Any]
) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(analysis["generated_at"]))
    content = safe_read(overview_path)
    appendix_parts = [
        "\n\n---\n",
        f"## Auto-Generated Overview (analyze_project.py)\n\n_Generated at: {stamp}_\n\n",
        narrative,
        "\n",
        "### Auto Lists\n",
    ]

    # Lists
    envs = analysis.get("env_vars", [])
    flask_routes = analysis.get("flask_routes", [])
    express_routes = analysis.get("express_routes", [])
    services = analysis.get("services", [])
    tests = analysis.get("tests", {})

    # Env
    appendix_parts.append("#### Environment Variables\n")
    if envs:
        for v in sorted(envs):
            appendix_parts.append(f"- {v}\n")
    else:
        appendix_parts.append("_None_\n")

    # Endpoints
    appendix_parts.append("\n#### Endpoints\n")
    if flask_routes:
        appendix_parts.append("Flask:\n")
        for r in flask_routes:
            appendix_parts.append(f"- {r}\n")
    if express_routes:
        appendix_parts.append("Express:\n")
        for method, r in sorted(express_routes):
            appendix_parts.append(f"- {method} {r}\n")
    if not flask_routes and not express_routes:
        appendix_parts.append("_None_\n")

    # Services
    appendix_parts.append("\n#### Services\n")
    if services:
        for s in services:
            appendix_parts.append(f"- {s}\n")
    else:
        appendix_parts.append("_None_\n")

    # Tests
    appendix_parts.append("\n#### Tests\n")
    caps = tests.get("capabilities", []) or []
    unit = tests.get("unit", []) or []
    if caps:
        appendix_parts.append("Capabilities:\n")
        for t in caps:
            appendix_parts.append(f"- {t}\n")
    if unit:
        appendix_parts.append("Unit:\n")
        for t in unit:
            appendix_parts.append(f"- {t}\n")
    if not caps and not unit:
        appendix_parts.append("_None_\n")

    updated = content + "".join(appendix_parts)
    overview_path.write_text(updated, encoding="utf-8")


def main(argv: List[str]) -> int:
    # Standard library imports
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze repo and append a narrative overview to docs/PROJECT_OVERVIEW.md"
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--overview", default="docs/PROJECT_OVERVIEW.md")
    parser.add_argument("--json-out", default="docs/PROJECT_ANALYSIS.json")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    analysis = analyze(root)
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_out).write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    overview_path = root / args.overview
    if not overview_path.exists():
        print(f"Overview not found: {overview_path}")
        return 1

    narrative = build_narrative(root, analysis)
    append_appendix(overview_path, narrative, analysis)
    print(f"Wrote {args.json_out}")
    print(f"Updated {overview_path} (appended Auto-Generated Overview)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
