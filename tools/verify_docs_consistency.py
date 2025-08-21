#!/usr/bin/env python3
"""
Verify docs consistency against the codebase for:
- Environment variables referenced in code vs documented in docs/PROJECT_OVERVIEW.md
- Key HTTP endpoints (Hub, QFAC) referenced in code vs documented

Outputs a short report to stdout and a markdown file docs/DOCS_CONSISTENCY_REPORT.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

ROOT = Path(__file__).resolve().parents[1]
DOC_OVERVIEW = ROOT / "docs" / "PROJECT_OVERVIEW.md"
REPORT = ROOT / "docs" / "DOCS_CONSISTENCY_REPORT.md"

ENV_PATTERN = re.compile(r"AETHERRA_[A-Z0-9_]+")
ROUTE_PATTERN = re.compile(r"@app\.route\((?P<q>['\"])\s*([^'\"]+)\1.*?\)")
BLUEPRINT_ROUTE_PATTERN = re.compile(r"@\w+\.route\((?P<q>['\"])\s*([^'\"]+)\1.*?\)")


def find_env_vars_in_code() -> Set[str]:
    found: Set[str] = set()
    for path in ROOT.rglob("*.py"):
        if any(
            part in {".venv", "__pycache__", "node_modules", ".git"}
            for part in path.parts
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in ENV_PATTERN.finditer(text):
            found.add(m.group(0))
    return found


def _normalize_route(route: str) -> str:
    route = route.strip()
    if not route:
        return route
    # Normalize parameter segments
    route = re.sub(r"<[^>]+>", "<param>", route)
    # Normalize trailing slashes (keep root as "/")
    if route != "/":
        route = route.rstrip("/")
    return route


def find_routes_in_code() -> Set[str]:
    found: Set[str] = set()
    for path in ROOT.rglob("*.py"):
        if any(
            part in {".venv", "__pycache__", "node_modules", ".git"}
            for part in path.parts
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in ROUTE_PATTERN.finditer(text):
            found.add(_normalize_route(m.group(2)))
        for m in BLUEPRINT_ROUTE_PATTERN.finditer(text):
            found.add(_normalize_route(m.group(2)))
    return found


def read_doc_section_envs(doc: Path) -> Set[str]:
    if not doc.exists():
        return set()
    text = doc.read_text(encoding="utf-8", errors="ignore")
    return set(sorted(set(ENV_PATTERN.findall(text))))


def read_doc_endpoints(doc: Path) -> Set[str]:
    if not doc.exists():
        return set()
    text = doc.read_text(encoding="utf-8", errors="ignore")
    # Extract inline/code paths that may include angle-bracket segments
    paths = set(re.findall(r"(/[-a-zA-Z0-9_./<>]+)", text))
    normed = {_normalize_route(p) for p in paths if p.startswith("/")}
    # Explicitly capture root route when referenced in prose
    if "GET /" in text or "`/`" in text:
        normed.add("/")
    # Keep only relevant API/dashboard paths
    allowed_prefixes = (
        "/api",
        "/qfac",
        "/quantum",
        "/services",
        "/health",
        "/status",
        "/",
    )
    filtered = {p for p in normed if p == "/" or p.startswith(allowed_prefixes)}
    return filtered


def main() -> int:
    code_envs = find_env_vars_in_code()
    code_routes = find_routes_in_code()
    doc_envs = read_doc_section_envs(DOC_OVERVIEW)
    doc_routes = read_doc_endpoints(DOC_OVERVIEW)

    missing_envs = sorted(code_envs - doc_envs)
    extra_envs = sorted(doc_envs - code_envs)
    missing_routes = sorted(code_routes - doc_routes)
    extra_routes = sorted([r for r in doc_routes if r not in code_routes])

    lines: List[str] = []
    lines.append("# Docs Consistency Report\n")
    lines.append(f"Document: {DOC_OVERVIEW}")
    lines.append("")
    lines.append("## Environment Variables")
    lines.append("")
    lines.append(f"Missing in docs ({len(missing_envs)}):")
    for v in missing_envs:
        lines.append(f"- {v}")
    lines.append("")
    lines.append(f"Documented but not found in code ({len(extra_envs)}):")
    for v in extra_envs:
        lines.append(f"- {v}")
    lines.append("")
    lines.append("## Endpoints")
    lines.append("")
    lines.append(f"Missing in docs ({len(missing_routes)}):")
    for r in missing_routes:
        lines.append(f"- {r}")
    lines.append("")
    lines.append(f"Documented but not found in code ({len(extra_routes)}):")
    for r in extra_routes:
        lines.append(f"- {r}")
    lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

    # Non-zero exit only if there are critical gaps (envs or routes missing)
    if missing_envs or missing_routes:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
