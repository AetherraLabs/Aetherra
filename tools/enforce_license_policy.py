#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""License Policy Enforcement (Warn Mode / Alpha)

Reads licenses_report.json (from tools/license_report.py) and applies baseline
policy checks. Currently non-fatal unless explicit env flags elevate.

Env Vars:
  LICENSE_REPORT_JSON       : path to JSON report (default licenses_report.json)
  LICENSE_DENY              : comma/space separated substrings that if found in a license id cause failure (future, now warn)
  LICENSE_FAIL_ON_UNKNOWN   : 1 to fail if any UNKNOWN licenses (default 0)
  LICENSE_UNKNOWN_MAX       : integer threshold; warn if above (default None)
  LICENSE_OVERRIDES_FILE    : path to overrides YAML (default license_overrides.yml)

Overrides file schema (YAML):
  packages:
    <name>:
      license: <SPDX-ID>
      reason: <text>
      approved_by: <string>

Exit codes:
  0 success (or only warnings)
  2 policy violation (when fail flags active)

This script is intentionally minimal; it will evolve for Beta (deny categories,
prohibited runtime set differentiation, provenance embedding).
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception as e:
        print(f"[LICENSE_ENFORCE][ERROR] Failed to read {path}: {e}", file=sys.stderr)
        return None


def load_overrides(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.is_file():
        return {}
    if yaml is None:
        print(
            "[LICENSE_ENFORCE][WARN] PyYAML not installed; cannot parse overrides (ignored)"
        )
        return {}
    try:
        data = yaml.safe_load(path.read_text("utf-8")) or {}
        pkgs = data.get("packages") or {}
        out: Dict[str, Dict[str, str]] = {}
        for name, meta in pkgs.items():
            if not isinstance(meta, dict):
                continue
            lic = meta.get("license")
            if lic:
                out[name.lower()] = {
                    "license": str(lic),
                    "reason": str(meta.get("reason", "")),
                }
        return out
    except Exception as e:  # pragma: no cover - defensive
        print(f"[LICENSE_ENFORCE][WARN] Failed to parse overrides: {e}")
        return {}


def normalize_license(raw: str | None) -> str:
    if not raw:
        return "UNKNOWN"
    # Collapse excessive whitespace / punctuation phrases
    s = re.sub(r"\s+", " ", raw.strip())
    # Shorten common verbose headers (best effort)
    return s[:200]


def main(argv=None) -> int:
    report_path = Path(os.getenv("LICENSE_REPORT_JSON", "licenses_report.json"))
    if not report_path.is_file():
        print(
            f"[LICENSE_ENFORCE][WARN] Missing {report_path}; nothing to enforce (pass)"
        )
        return 0
    data = load_json(report_path)
    if not isinstance(data, dict):
        return 0
    rows = data.get("rows") or []
    overrides = load_overrides(
        Path(os.getenv("LICENSE_OVERRIDES_FILE", "license_overrides.yml"))
    )

    deny_terms_raw = os.getenv("LICENSE_DENY", "").replace(",", " ")
    deny_terms = [t.lower() for t in deny_terms_raw.split() if t.strip()]
    fail_on_unknown = os.getenv("LICENSE_FAIL_ON_UNKNOWN", "0") == "1"
    unknown_max = os.getenv("LICENSE_UNKNOWN_MAX")
    unknown_threshold = (
        int(unknown_max) if unknown_max and unknown_max.isdigit() else None
    )

    unknown_count = 0
    violations: list[str] = []
    warnings: list[str] = []

    for r in rows:
        name = str(r.get("name", "")).strip()
        lic_raw = r.get("license")
        lic = normalize_license(lic_raw)
        if name.lower() in overrides and lic == "UNKNOWN":
            lic = overrides[name.lower()]["license"]
        if lic == "UNKNOWN":
            unknown_count += 1
        lower_lic = lic.lower()
        for term in deny_terms:
            if term and term in lower_lic:
                msg = f"deny-term '{term}' matched license '{lic}' for {name}"
                warnings.append(msg)
                # escalate to violation only in future strict mode
        # Future: categorize strong copyleft etc.

    if unknown_threshold is not None and unknown_count > unknown_threshold:
        warnings.append(
            f"UNKNOWN license count {unknown_count} exceeds threshold {unknown_threshold}"
        )
    if fail_on_unknown and unknown_count > 0:
        violations.append(
            f"UNKNOWN license count {unknown_count} > 0 (fail_on_unknown)"
        )

    # Emit summary
    print(
        f"[LICENSE_ENFORCE] scanned={len(rows)} unknown={unknown_count} overrides={len(overrides)}"
    )
    # Emit a simple metrics-style line for future scraping / integration
    try:
        print(f"license_unknown_total {unknown_count}")
    except Exception:
        pass
    # Append to simple trend log (date, unknown count) for tracking reduction over time
    try:
        trend_path = Path(os.getenv("LICENSE_TREND_LOG", "license_unknown_trend.log"))
        ts = datetime.now(timezone.utc).isoformat()
        trend_line = f"{ts} unknown={unknown_count} overrides={len(overrides)}\n"
        # Append new line
        with trend_path.open("a", encoding="utf-8") as fp:
            fp.write(trend_line)
        # Compute delta vs previous entry (if any)
        try:
            lines = trend_path.read_text("utf-8").strip().splitlines()
            if len(lines) >= 2:
                last = lines[-1]
                prev = lines[-2]
                # Extract unknown counts using simple parse
                def extract_unknown(s: str) -> int:
                    m = re.search(r"unknown=(\d+)", s)
                    return int(m.group(1)) if m else -1
                cur_u = extract_unknown(last)
                prev_u = extract_unknown(prev)
                if cur_u >= 0 and prev_u >= 0:
                    delta = cur_u - prev_u
                    direction = "down" if delta < 0 else ("up" if delta > 0 else "flat")
                    print(f"[LICENSE_ENFORCE] trend_delta={delta} direction={direction} (prev={prev_u} -> cur={cur_u})")
        except Exception:
            pass
    except Exception:
        # Non-fatal; silently ignore logging issues
        pass
    for w in warnings:
        print(f"[LICENSE_ENFORCE][WARN] {w}")
    for v in violations:
        print(f"[LICENSE_ENFORCE][VIOLATION] {v}")

    if violations:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
