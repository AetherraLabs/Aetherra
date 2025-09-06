#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Lightweight license policy enforcement / telemetry.

Reads the JSON produced by tools/license_report.py (path via env
LICENSE_REPORT_JSON or default licenses_report.json) and emits trend
metrics for UNKNOWN licenses plus optional gating rules.

State is tracked in a small sidecar file (licenses_unknown_history.json)
containing an array of historical UNKNOWN counts with timestamps.

Environment variables (all optional, alpha-stage):
  LICENSE_REPORT_JSON          : path to license report (default licenses_report.json)
  LICENSE_UNKNOWN_TOLERANCE    : integer allowed increase (delta) in UNKNOWN count before failing gate (default 0 => any increase beyond tolerance fails if gating enabled)
  LICENSE_UNKNOWN_TREND_FAIL   : '1' to enable failing when UNKNOWN increases beyond tolerance
  LICENSE_UNKNOWN_ABS_MAX      : absolute maximum UNKNOWN count allowed (fail if current > value)
  LICENSE_UNKNOWN_FAIL_IF_GT   : synonym for ABS_MAX (checked first if set)
  LICENSE_ENFORCE_HISTORY_FILE : override history file path (default licenses_unknown_history.json)

Exit codes:
  0 success / non-fatal metrics
  1 policy violation (trend up beyond tolerance or absolute max exceeded)
  2 usage / file issues (missing report etc.)

Outputs key telemetry lines prefixed with [LICENSE_ENFORCE] so that
quality_gates.py or external collectors can parse easily.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


def load_report(path: Path) -> list[dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[LICENSE_ENFORCE][ERROR] Report missing: {path}")
        raise
    except Exception as e:  # pragma: no cover - defensive
        print(f"[LICENSE_ENFORCE][ERROR] Failed to parse {path}: {e}")
        raise


def count_unknown(rows: list[dict[str, Any]]) -> int:
    return sum(1 for r in rows if (r.get("license") or "").strip().upper() == "UNKNOWN")


def load_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:  # pragma: no cover
        pass
    return []


def append_history(path: Path, count: int) -> list[dict[str, Any]]:
    hist = load_history(path)
    hist.append({"ts": int(time.time()), "unknown": count})
    # Retain only last 50 entries to keep file small
    hist = hist[-50:]
    try:
        path.write_text(json.dumps(hist, indent=2), encoding="utf-8")
    except Exception as e:  # pragma: no cover
        print(f"[LICENSE_ENFORCE][WARN] Failed to write history file: {e}")
    return hist


def main() -> int:
    report_path = Path(os.getenv("LICENSE_REPORT_JSON", "licenses_report.json"))
    history_path = Path(
        os.getenv("LICENSE_ENFORCE_HISTORY_FILE", "licenses_unknown_history.json")
    )

    try:
        rows = load_report(report_path)
    except Exception:
        return 2

    unknown_now = count_unknown(rows)

    hist_before = load_history(history_path)
    prev_unknown = hist_before[-1]["unknown"] if hist_before else None

    hist_after = append_history(history_path, unknown_now)

    trend_delta = None
    if prev_unknown is not None:
        trend_delta = unknown_now - prev_unknown

    # Emit telemetry lines
    print(
        f"[LICENSE_ENFORCE] unknown_current={unknown_now} prev={prev_unknown} trend_delta={trend_delta} history_len={len(hist_after)}"
    )

    # Optional Prometheus metrics export (best-effort, non-fatal)
    try:  # pragma: no cover - side-effect only
        from prometheus_client import Gauge  # type: ignore

        g_unknown = Gauge(
            "aetherra_license_unknown_current",
            "Current number of dependencies with UNKNOWN license metadata",
        )
        g_trend = Gauge(
            "aetherra_license_unknown_trend_delta",
            "Delta vs previous run for UNKNOWN license count (positive means regression)",
        )
        g_unknown.set(unknown_now)
        if trend_delta is not None:
            g_trend.set(trend_delta)
    except Exception:
        pass

    # Optional gating logic
    fail = False
    # Absolute max first (either of the vars)
    abs_max_raw = os.getenv("LICENSE_UNKNOWN_FAIL_IF_GT") or os.getenv(
        "LICENSE_UNKNOWN_ABS_MAX"
    )
    if abs_max_raw is not None:
        try:
            abs_max = int(abs_max_raw)
            if unknown_now > abs_max:
                print(
                    f"[LICENSE_ENFORCE][FAIL] UNKNOWN count {unknown_now} exceeds absolute max {abs_max}"
                )
                fail = True
        except ValueError:
            print(
                f"[LICENSE_ENFORCE][WARN] Invalid ABS_MAX value: {abs_max_raw} (ignored)"
            )

    # Trend gating
    if os.getenv("LICENSE_UNKNOWN_TREND_FAIL", "0") == "1" and trend_delta is not None:
        tol_raw = os.getenv("LICENSE_UNKNOWN_TOLERANCE", "0").strip()
        try:
            tol = int(tol_raw)
        except ValueError:
            tol = 0
        if trend_delta > tol:
            print(
                f"[LICENSE_ENFORCE][FAIL] UNKNOWN trend increased by {trend_delta} (tolerance {tol})"
            )
            fail = True
        else:
            print(
                f"[LICENSE_ENFORCE] Trend within tolerance (delta {trend_delta} <= {tol})"
            )
    else:
        # Provide guidance if gating disabled
        if trend_delta is not None:
            print(
                "[LICENSE_ENFORCE] Trend gating disabled (set LICENSE_UNKNOWN_TREND_FAIL=1 to enforce)"
            )

    return 1 if fail else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
