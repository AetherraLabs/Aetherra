#!/usr/bin/env python3
"""
Verify docs consistency against the codebase for:
- Environment variables referenced in code vs documented in docs/PROJECT_OVERVIEW.md
- Key HTTP endpoints (Hub, QFAC) referenced in code vs documented

Outputs a short report to stdout and a markdown file docs/DOCS_CONSISTENCY_REPORT.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Set

ROOT = Path(__file__).resolve().parents[1]
DOC_OVERVIEW = ROOT / "docs" / "PROJECT_OVERVIEW.md"
REPORT = ROOT / "docs" / "DOCS_CONSISTENCY_REPORT.md"
DOCS_CFG = ROOT / "docs" / "docs_consistency.json"

# Treat only standalone env-like tokens and avoid matching doc filenames like AETHERRA_..._SYSTEM.md
ENV_PATTERN = re.compile(r"\bAETHERRA_[A-Z0-9_]+\b(?!\.md)")
# Contextual patterns for true env-var usage in code
ENV_FETCH_PATTERNS = [
    re.compile(r"os\.environ\[(?:'|\")(?P<var>AETHERRA_[A-Z0-9_]+)(?:'|\")\]"),
    re.compile(
        r"os\.environ\.get\((?:'|\")(?P<var>AETHERRA_[A-Z0-9_]+)(?:'|\")[^)]*\)"
    ),
    re.compile(r"os\.getenv\((?:'|\")(?P<var>AETHERRA_[A-Z0-9_]+)(?:'|\")[^)]*\)"),
]
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
        # Only count variables actually fetched from environment to avoid false positives
        for pat in ENV_FETCH_PATTERNS:
            for m in pat.finditer(text):
                found.add(m.group("var"))
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


def _extract_section(text: str, heading: str) -> str:
    """Extract content under a markdown heading (any level >= 2) until the next heading of any level.

    If the heading isn't found, return an empty string to allow caller fallbacks.
    """
    # Match heading levels '##', '###', '####', etc.
    pattern = re.compile(
        rf"^##+\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE
    )
    m = pattern.search(text)
    if not m:
        return ""
    start = m.end()
    # Find next heading (any level)
    m2 = re.compile(r"^#+\s+", re.MULTILINE).search(text, pos=start)
    end = m2.start() if m2 else len(text)
    return text[start:end]


def read_doc_section_envs(doc: Path) -> Set[str]:
    if not doc.exists():
        return set()
    text = doc.read_text(encoding="utf-8", errors="ignore")
    # Prefer the explicit Environment Variables Index section
    section = _extract_section(text, "Environment Variables Index")
    if not section:
        # Fallback to a broader Configuration and Environment section if present
        section = _extract_section(text, "Configuration and Environment") or text
    return set(sorted(set(ENV_PATTERN.findall(section))))


def read_doc_endpoints(doc: Path) -> Set[str]:
    if not doc.exists():
        return set()
    text = doc.read_text(encoding="utf-8", errors="ignore")

    def _extract_paths(src: str) -> Set[str]:
        # Extract inline/code paths that may include angle-bracket segments
        paths = set(re.findall(r"(/[-a-zA-Z0-9_./<>]+)", src))
        normed = {_normalize_route(p) for p in paths if p.startswith("/")}
        # Explicitly capture root route when referenced in prose
        if "GET /" in src or "`/`" in src:
            normed.add("/")
        # Keep only relevant API/dashboard paths
        allowed_prefixes = (
            "/api",
            "/qfac",
            "/quantum",
            "/services",
            "/health",
            "/status",
            "/metrics",  # Prometheus exposition endpoint
            "/site_status",  # aggregated site status alias
            "/<",  # parameterized root catch-alls (e.g., /<param>)
        )
        filtered = {
            p for p in normed if p == "/" or p.lower().startswith(allowed_prefixes)
        }
        # Drop obvious non-API artifacts (file paths/extensions)
        filtered = {
            p
            for p in filtered
            if not re.search(r"\.(py|md|txt|json|yaml|yml)$", p, re.IGNORECASE)
        }
        return filtered

    # Collect endpoints from multiple likely sections and the full doc for stability
    sections_to_try = [
        "Service and Endpoint Summary",
        "Endpoints",
        "API Endpoints",
    ]
    collected: Set[str] = set()
    for h in sections_to_try:
        sec = _extract_section(text, h)
        if sec:
            collected |= _extract_paths(sec)
    # Always include anything found in the whole document as a safety net
    collected |= _extract_paths(text)
    return collected


def main() -> int:
    code_envs = find_env_vars_in_code()
    code_routes = find_routes_in_code()
    doc_envs = read_doc_section_envs(DOC_OVERVIEW)
    doc_routes = read_doc_endpoints(DOC_OVERVIEW)

    # Optional config to fine-tune reporting, without changing pass/fail semantics
    cfg_ignore_extra_envs: Set[str] = set()
    if DOCS_CFG.exists():
        try:
            cfg = json.loads(DOCS_CFG.read_text(encoding="utf-8"))
            ignore_list = cfg.get("ignore_extra_envs", []) or cfg.get(
                "doc_only_envs", []
            )
            if isinstance(ignore_list, list):
                cfg_ignore_extra_envs = {str(v) for v in ignore_list}
        except Exception:
            # Best-effort; ignore config errors to keep tool resilient
            pass

    missing_envs = sorted(code_envs - doc_envs)
    raw_extra_envs = doc_envs - code_envs
    # Suppress configured doc-only envs from the extra list for a cleaner report
    extra_envs = sorted([v for v in raw_extra_envs if v not in cfg_ignore_extra_envs])
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
    # If we suppressed any extras via config, annotate for transparency
    suppressed = sorted([v for v in raw_extra_envs if v in cfg_ignore_extra_envs])
    if suppressed:
        lines.append("")
        lines.append(
            f"(Note) Suppressed doc-only envs via docs_consistency.json ({len(suppressed)}):"
        )
        for v in suppressed:
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
