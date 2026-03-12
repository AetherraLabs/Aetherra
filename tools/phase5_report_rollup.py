#!/usr/bin/env python3
"""Phase 5 report rollup utility.

Aggregates one or more JSON reports produced by tools/phase5_validation_harness.py
and emits a compact summary JSON for release/gate evidence.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any, cast


def _load_report(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return cast(dict[str, Any], payload)


def _load_optional_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(payload, dict):
        return cast(dict[str, Any], payload)
    return None


def _rollup_categories(reports: list[dict[str, Any]]) -> dict[str, Any]:
    categories: dict[str, dict[str, Any]] = {}
    for report in reports:
        for row in list(report.get("category_summaries", []) or []):
            category = str(row.get("category") or "")
            if not category:
                continue
            summary = categories.setdefault(
                category,
                {
                    "category": category,
                    "reports": 0,
                    "passing_reports": 0,
                    "failing_reports": 0,
                    "passed": 0,
                    "failed": 0,
                    "total": 0,
                    "scenarios": set(),
                },
            )
            summary["reports"] = int(summary["reports"]) + 1
            summary["passed"] = int(summary["passed"]) + int(row.get("passed", 0) or 0)
            summary["failed"] = int(summary["failed"]) + int(row.get("failed", 0) or 0)
            summary["total"] = int(summary["total"]) + int(row.get("total", 0) or 0)
            if str(row.get("status", "fail")) == "pass":
                summary["passing_reports"] = int(summary["passing_reports"]) + 1
            else:
                summary["failing_reports"] = int(summary["failing_reports"]) + 1
            for scenario in list(row.get("scenarios", []) or []):
                summary["scenarios"].add(str(scenario))

    results: list[dict[str, Any]] = []
    for category in sorted(categories):
        summary = categories[category]
        total = int(summary["total"])
        passed = int(summary["passed"])
        results.append(
            {
                "category": category,
                "reports": int(summary["reports"]),
                "passing_reports": int(summary["passing_reports"]),
                "failing_reports": int(summary["failing_reports"]),
                "passed": passed,
                "failed": int(summary["failed"]),
                "total": total,
                "aggregate_pass_rate": round((passed / total) if total else 0.0, 4),
                "status": "pass"
                if int(summary["failed"]) == 0 and total > 0
                else "fail",
                "scenarios": sorted(s for s in summary["scenarios"] if s),
            }
        )
    return {"results": results}


def _build_performance_evidence(reports: list[dict[str, Any]]) -> dict[str, Any]:
    scenario_metrics: dict[str, dict[str, Any]] = {}
    for report in reports:
        for row in list(report.get("scenarios", []) or []):
            if str(row.get("category") or "") != "performance":
                continue
            name = str(row.get("name") or "")
            if not name:
                continue
            metric = scenario_metrics.setdefault(
                name,
                {
                    "name": name,
                    "samples": 0,
                    "passed": 0,
                    "duration_sum_sec": 0.0,
                    "min_duration_sec": None,
                    "max_duration_sec": 0.0,
                },
            )
            duration = float(row.get("duration_sec", 0.0) or 0.0)
            metric["samples"] = int(metric["samples"]) + 1
            metric["duration_sum_sec"] = float(metric["duration_sum_sec"]) + duration
            metric["max_duration_sec"] = max(
                float(metric["max_duration_sec"]), duration
            )
            metric["min_duration_sec"] = (
                duration
                if metric["min_duration_sec"] is None
                else min(float(metric["min_duration_sec"]), duration)
            )
            if bool(row.get("ok", False)):
                metric["passed"] = int(metric["passed"]) + 1

    scenarios: list[dict[str, Any]] = []
    total_samples = 0
    total_duration = 0.0
    max_duration = 0.0
    for name in sorted(scenario_metrics):
        metric = scenario_metrics[name]
        samples = int(metric["samples"])
        duration_sum = float(metric["duration_sum_sec"])
        max_duration = max(max_duration, float(metric["max_duration_sec"]))
        total_samples += samples
        total_duration += duration_sum
        scenarios.append(
            {
                "name": name,
                "samples": samples,
                "pass_rate": round(
                    (int(metric["passed"]) / samples) if samples else 0.0, 4
                ),
                "avg_duration_sec": round(
                    (duration_sum / samples) if samples else 0.0, 4
                ),
                "min_duration_sec": round(float(metric["min_duration_sec"] or 0.0), 4),
                "max_duration_sec": round(float(metric["max_duration_sec"]), 4),
            }
        )

    return {
        "scenario_count": len(scenarios),
        "samples": total_samples,
        "avg_duration_sec": round(
            (total_duration / total_samples) if total_samples else 0.0, 4
        ),
        "max_duration_sec": round(max_duration, 4),
        "scenarios": scenarios,
    }


def _evaluate_performance_thresholds(
    performance_evidence: dict[str, Any],
    min_pass_rate: float | None = None,
    max_avg_duration_sec: float | None = None,
    max_scenario_duration_sec: float | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    aggregate_avg = float(performance_evidence.get("avg_duration_sec", 0.0) or 0.0)
    if max_avg_duration_sec is not None:
        rows.append(
            {
                "name": "performance.avg_duration_sec",
                "observed": aggregate_avg,
                "threshold": float(max_avg_duration_sec),
                "operator": "<=",
                "passed": aggregate_avg <= float(max_avg_duration_sec),
            }
        )

    max_scenario_observed = float(
        max(
            [
                float(row.get("max_duration_sec", 0.0) or 0.0)
                for row in list(performance_evidence.get("scenarios", []) or [])
            ]
            or [0.0]
        )
    )
    if max_scenario_duration_sec is not None:
        rows.append(
            {
                "name": "performance.max_scenario_duration_sec",
                "observed": max_scenario_observed,
                "threshold": float(max_scenario_duration_sec),
                "operator": "<=",
                "passed": max_scenario_observed <= float(max_scenario_duration_sec),
            }
        )

    min_scenario_pass_rate = float(
        min(
            [
                float(row.get("pass_rate", 0.0) or 0.0)
                for row in list(performance_evidence.get("scenarios", []) or [])
            ]
            or [0.0]
        )
    )
    if min_pass_rate is not None:
        rows.append(
            {
                "name": "performance.min_scenario_pass_rate",
                "observed": min_scenario_pass_rate,
                "threshold": float(min_pass_rate),
                "operator": ">=",
                "passed": min_scenario_pass_rate >= float(min_pass_rate),
            }
        )

    return {
        "min_pass_rate": min_pass_rate,
        "max_avg_duration_sec": max_avg_duration_sec,
        "max_scenario_duration_sec": max_scenario_duration_sec,
        "checks": rows,
        "passed": all(bool(row.get("passed", False)) for row in rows),
    }


def _build_grouped_trends(
    previous_rollup: dict[str, Any] | None,
    current_categories: dict[str, Any],
    current_performance: dict[str, Any],
) -> dict[str, Any]:
    if not previous_rollup:
        return {
            "has_previous": False,
            "category_deltas": [],
            "performance_deltas": [],
        }

    prev_categories = {
        str(row.get("category")): float(row.get("aggregate_pass_rate", 0.0) or 0.0)
        for row in list(
            (previous_rollup.get("categories") or {}).get("results", []) or []
        )
        if row.get("category")
    }
    cur_categories = {
        str(row.get("category")): float(row.get("aggregate_pass_rate", 0.0) or 0.0)
        for row in list((current_categories.get("results") or []) or [])
        if row.get("category")
    }

    category_deltas: list[dict[str, Any]] = []
    for name in sorted(set(prev_categories) | set(cur_categories)):
        category_deltas.append(
            {
                "category": name,
                "previous": prev_categories.get(name),
                "current": cur_categories.get(name),
                "delta": (
                    None
                    if name not in prev_categories or name not in cur_categories
                    else round(cur_categories[name] - prev_categories[name], 4)
                ),
            }
        )

    prev_perf = previous_rollup.get("performance_evidence") or {}
    perf_rows = [
        (
            "avg_duration_sec",
            float(prev_perf.get("avg_duration_sec", 0.0) or 0.0),
            float(current_performance.get("avg_duration_sec", 0.0) or 0.0),
        ),
        (
            "max_duration_sec",
            float(prev_perf.get("max_duration_sec", 0.0) or 0.0),
            float(current_performance.get("max_duration_sec", 0.0) or 0.0),
        ),
    ]
    performance_deltas = [
        {
            "name": name,
            "previous": prev,
            "current": cur,
            "delta": round(cur - prev, 4),
        }
        for name, prev, cur in perf_rows
    ]

    return {
        "has_previous": True,
        "category_deltas": category_deltas,
        "performance_deltas": performance_deltas,
    }


def rollup_reports(
    paths: list[str],
    previous_rollup: dict[str, Any] | None = None,
    performance_min_pass_rate: float | None = None,
    performance_max_avg_duration_sec: float | None = None,
    performance_max_scenario_duration_sec: float | None = None,
) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    for path in paths:
        try:
            payload = _load_report(path)
            payload["_path"] = path
            reports.append(payload)
        except Exception as exc:
            reports.append(
                {
                    "_path": path,
                    "status": "error",
                    "runs": 0,
                    "full_pass_runs": 0,
                    "run_pass_rate": 0.0,
                    "error": f"failed_to_read: {type(exc).__name__}: {exc}",
                }
            )

    total_reports = len(reports)
    passing_reports = sum(1 for r in reports if r.get("status") == "pass")
    total_runs = sum(int(r.get("runs", 0) or 0) for r in reports)
    total_full_pass_runs = sum(int(r.get("full_pass_runs", 0) or 0) for r in reports)
    aggregate_pass_rate = (total_full_pass_runs / total_runs) if total_runs else 0.0

    by_report = []
    for r in reports:
        by_report.append(
            {
                "path": r.get("_path", ""),
                "status": r.get("status", "unknown"),
                "runs": int(r.get("runs", 0) or 0),
                "full_pass_runs": int(r.get("full_pass_runs", 0) or 0),
                "run_pass_rate": float(r.get("run_pass_rate", 0.0) or 0.0),
                "failed_scenarios": int(r.get("failed", 0) or 0),
                "total_scenarios": int(r.get("total", 0) or 0),
                "error": r.get("error"),
            }
        )

    category_rollup = _rollup_categories(reports)
    performance_evidence = _build_performance_evidence(reports)
    performance_thresholds = _evaluate_performance_thresholds(
        performance_evidence,
        min_pass_rate=performance_min_pass_rate,
        max_avg_duration_sec=performance_max_avg_duration_sec,
        max_scenario_duration_sec=performance_max_scenario_duration_sec,
    )
    grouped_trends = _build_grouped_trends(
        previous_rollup=previous_rollup,
        current_categories=category_rollup,
        current_performance=performance_evidence,
    )

    return {
        "summary": {
            "reports": total_reports,
            "passing_reports": passing_reports,
            "failing_reports": total_reports - passing_reports,
            "total_runs": total_runs,
            "full_pass_runs": total_full_pass_runs,
            "aggregate_run_pass_rate": round(aggregate_pass_rate, 4),
        },
        "categories": category_rollup,
        "performance_evidence": performance_evidence,
        "performance_thresholds": performance_thresholds,
        "grouped_trends": grouped_trends,
        "reports": by_report,
    }


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Roll up phase5 validation reports")
    p.add_argument(
        "--inputs",
        nargs="+",
        default=["phase5_validation_report*.json"],
        help="Input files or glob patterns",
    )
    p.add_argument(
        "--previous-rollup",
        default=None,
        help="Optional prior rollup JSON for grouped trend deltas",
    )
    p.add_argument("--performance-min-pass-rate", type=float, default=None)
    p.add_argument("--performance-max-avg-duration-sec", type=float, default=None)
    p.add_argument("--performance-max-scenario-duration-sec", type=float, default=None)
    p.add_argument("--output", default="phase5_validation_rollup.json")
    return p.parse_args()


def _expand_patterns(patterns: list[str]) -> list[str]:
    out: list[str] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            out.extend(matches)
        elif Path(pattern).exists():
            out.append(pattern)
    # Deduplicate preserving order
    seen = set()
    deduped: list[str] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def main() -> int:
    args = _parse_args()
    inputs = _expand_patterns(args.inputs)
    if not inputs:
        print("No input reports found")
        return 1

    previous_rollup = _load_optional_json(args.previous_rollup)

    payload = rollup_reports(
        inputs,
        previous_rollup=previous_rollup,
        performance_min_pass_rate=args.performance_min_pass_rate,
        performance_max_avg_duration_sec=args.performance_max_avg_duration_sec,
        performance_max_scenario_duration_sec=args.performance_max_scenario_duration_sec,
    )
    Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = payload["summary"]
    threshold_passed = bool(
        (payload.get("performance_thresholds") or {}).get("passed", True)
    )
    print(
        f"Rollup: {summary['passing_reports']}/{summary['reports']} reports passing, "
        f"aggregate run pass-rate {summary['aggregate_run_pass_rate']}, "
        f"performance_thresholds_passed={threshold_passed}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
