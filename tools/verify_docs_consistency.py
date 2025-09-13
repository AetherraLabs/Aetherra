#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Verify docs consistency against the codebase for:
- Environment variables referenced in code vs documented in docs/PROJECT_OVERVIEW.md
- Key HTTP endpoints (Hub, QFAC) referenced in code vs documented

Outputs a short report to stdout and a markdown file docs/DOCS_CONSISTENCY_REPORT.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
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
    # Drop trailing punctuation commonly used in prose
    route = route.rstrip(".,;:)")
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
    """Extract documented environment variable names from the overview doc.

    Enhancements (Sept 2025):
    - Recognize vars inside markdown tables (| col | col |) even if not prefixed by dash.
    - Capture backticked references `AETHERRA_X` anywhere.
    - Be resilient to trailing punctuation, parentheses, or descriptive text.
    """
    if not doc.exists():
        return set()
    text = doc.read_text(encoding="utf-8", errors="ignore")

    # Base pattern scan
    envs_all = set(ENV_PATTERN.findall(text))

    # Additional: parse table cells explicitly to ensure no inline formatting breaks detection
    table_envs: Set[str] = set()
    for line in text.splitlines():
        if "|" in line:
            # Split columns, scan each token
            for token in [c.strip() for c in line.split("|")]:
                for m in ENV_PATTERN.finditer(token):
                    table_envs.add(m.group(0))

    envs_all |= table_envs

    return set(sorted(envs_all))


def read_doc_endpoints(doc: Path) -> Set[str]:
    if not doc.exists():
        return set()
    text = doc.read_text(encoding="utf-8", errors="ignore")

    def _extract_paths(src: str) -> Set[str]:
        # Extract inline/code paths that may include angle-bracket segments
        paths = set(re.findall(r"(/[-a-zA-Z0-9_./<>]+)", src))
        normed = {_normalize_route(p) for p in paths if p.startswith("/")}
        # Explicitly capture root route when referenced in prose
        if "GET /" in src or "`/`" in src or re.search(r"(?m)^\s*[-*]\s*/\s*$", src):
            normed.add("/")
        # Keep only relevant API/dashboard paths
        allowed_prefixes = (
            "/api",
            "/ws",  # WebSocket routes
            "/qfac",
            "/quantum",
            "/services",
            "/health",
            "/status",
            "/metrics",  # Prometheus exposition endpoint
            "/site_status",  # aggregated site status alias
            "/memory",  # memory dashboards/UI endpoints
            "/<",  # parameterized root catch-alls (e.g., /<param>)
        )
        filtered = {
            p for p in normed if (p == "/" or p.lower().startswith(allowed_prefixes))
        }
        # Drop uppercase artifacts like "/API" captured from prose headings
        filtered = {p for p in filtered if p == p.lower()}
        # Drop obvious non-API artifacts (file paths/extensions)
        # Keep certain .json API endpoints (e.g., OpenAPI schema) while filtering file-like paths
        exceptions = {"/api/openapi.json"}
        filtered = {
            p
            for p in filtered
            if (p in exceptions)
            or not re.search(r"\.(py|md|txt|json|yaml|yml)$", p, re.IGNORECASE)
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
    parser = argparse.ArgumentParser(description="Verify docs consistency")
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    debug = args.debug or os.environ.get("AETHERRA_DOCS_DEBUG") == "1"
    code_envs = find_env_vars_in_code()
    code_routes = find_routes_in_code()
    doc_envs = read_doc_section_envs(DOC_OVERVIEW)
    doc_routes = read_doc_endpoints(DOC_OVERVIEW)

    if debug:
        print("[debug] code_envs count:", len(code_envs))
        print("[debug] first 15 code_envs:", sorted(list(code_envs))[:15])
        print("[debug] doc_envs count:", len(doc_envs))
        print("[debug] first 15 doc_envs:", sorted(list(doc_envs))[:15])
        print("[debug] code_routes count:", len(code_routes))
        print("[debug] doc_routes count:", len(doc_routes))

    # Consciousness metrics consistency (best-effort): ensure key metrics added to METRICS_REFERENCE
    metrics_doc = ROOT / "docs" / "METRICS_REFERENCE.md"
    consciousness_required = {
        "aetherra_consciousness_identity_coherence",
        "aetherra_consciousness_narrative_coherence",
        "aetherra_consciousness_workspace_queue_size",
        "aetherra_consciousness_narrative_chapters_total",
    }
    consciousness_hist_bases = {
        "aetherra_consciousness_workspace_latency_seconds",
        "aetherra_consciousness_narrative_generation_seconds",
    }
    missing_consciousness_metrics = set()
    if metrics_doc.exists():
        try:
            text = metrics_doc.read_text(encoding="utf-8", errors="ignore")
            for m in consciousness_required:
                if m not in text:
                    missing_consciousness_metrics.add(m)
            for base in consciousness_hist_bases:
                # Check any bucket line to confirm presence
                if base not in text:
                    missing_consciousness_metrics.add(base + "_bucket")
        except Exception:
            # If read fails, mark all as missing
            missing_consciousness_metrics |= consciousness_required | {
                b + "_bucket" for b in consciousness_hist_bases
            }
    else:
        missing_consciousness_metrics = consciousness_required | {
            b + "_bucket" for b in consciousness_hist_bases
        }

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

    if debug:
        print("[debug] missing_envs count:", len(missing_envs))
        print("[debug] extra_envs (raw) count:", len(raw_extra_envs))
        if missing_envs:
            print("[debug] sample missing_envs:", missing_envs[:10])
        if raw_extra_envs:
            print("[debug] sample raw_extra_envs:", sorted(list(raw_extra_envs))[:10])
    # Suppress configured doc-only envs from the extra list for a cleaner report
    extra_envs = sorted([v for v in raw_extra_envs if v not in cfg_ignore_extra_envs])
    missing_routes = sorted(code_routes - doc_routes)
    extra_routes = sorted([r for r in doc_routes if r not in code_routes])

    debug_json_path = ROOT / "docs" / "DOCS_CONSISTENCY_DEBUG.json"
    if debug:
        print("[debug] missing_routes count:", len(missing_routes))
        print("[debug] extra_routes count:", len(extra_routes))
        if missing_routes:
            print("[debug] sample missing_routes:", missing_routes[:10])
        if extra_routes:
            print("[debug] sample extra_routes:", extra_routes[:10])
        # Persist structured debug info for CI artifact / further analysis
        try:
            debug_payload = {
                "timestamp": time.time(),
                "code_envs_count": len(code_envs),
                "doc_envs_count": len(doc_envs),
                "missing_envs": missing_envs,
                "raw_extra_envs": sorted(list(raw_extra_envs)),
                "suppressed_doc_only_envs": sorted(
                    list(cfg_ignore_extra_envs & raw_extra_envs)
                ),
                "extra_envs_reported": extra_envs,
                "code_routes_count": len(code_routes),
                "doc_routes_count": len(doc_routes),
                "missing_routes": missing_routes,
                "extra_routes": extra_routes,
                "missing_consciousness_metrics": sorted(
                    list(missing_consciousness_metrics)
                ),
                "report_path": str(REPORT),
                "config_ignore_count": len(cfg_ignore_extra_envs),
            }
            debug_json_path.write_text(
                json.dumps(debug_payload, indent=2), encoding="utf-8"
            )
            print(f"[debug] wrote structured debug JSON: {debug_json_path}")
        except Exception as e:
            print(f"[debug] failed to write debug JSON ({debug_json_path}): {e}")

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

    # Consciousness metrics section
    lines.append("## Consciousness Metrics Documentation")
    lines.append("")
    if missing_consciousness_metrics:
        lines.append(
            f"Missing consciousness metrics in METRICS_REFERENCE.md ({len(missing_consciousness_metrics)}):"
        )
        for m in sorted(missing_consciousness_metrics):
            lines.append(f"- {m}")
    else:
        lines.append("All required consciousness metrics documented.")
    lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

    # Non-zero exit only if there are critical gaps (envs or routes missing)
    # Fail if critical gaps OR missing consciousness metrics
    if missing_envs or missing_routes or missing_consciousness_metrics:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
