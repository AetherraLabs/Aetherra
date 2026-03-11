#!/usr/bin/env python3
"""Phase 5 artifact bundler.

Runs the validation harness and rollup utility in one command and stores
outputs in a target artifact directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_previous_bundle_summary(output_dir: Path, summary_path: Path) -> Path | None:
    candidates = sorted(
        output_dir.glob("phase5_bundle_*.json"), key=lambda p: p.stat().st_mtime
    )
    candidates = [p for p in candidates if p.resolve() != summary_path.resolve()]
    return candidates[-1] if candidates else None


def _build_trend(
    previous_summary_path: Path | None, current_payload: dict[str, Any]
) -> dict[str, Any]:
    if previous_summary_path is None:
        return {
            "has_previous": False,
            "previous_summary": None,
            "delta_observed_run_pass_rate": None,
            "category_deltas": [],
            "rollup_category_deltas": [],
            "rollup_performance_deltas": [],
            "scenario_deltas": [],
        }

    try:
        previous = json.loads(previous_summary_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "has_previous": True,
            "previous_summary": str(previous_summary_path),
            "delta_observed_run_pass_rate": None,
            "category_deltas": [],
            "rollup_category_deltas": [],
            "rollup_performance_deltas": [],
            "scenario_deltas": [],
            "error": f"failed_to_load_previous: {type(exc).__name__}: {exc}",
        }

    cur_rate = float(
        (current_payload.get("gates") or {}).get("observed_run_pass_rate", 0.0) or 0.0
    )
    prev_rate = float(
        (previous.get("gates") or {}).get("observed_run_pass_rate", 0.0) or 0.0
    )

    prev_scenarios = {
        str(row.get("name")): float(row.get("observed_pass_rate", 0.0) or 0.0)
        for row in list((previous.get("gates") or {}).get("scenario_results", []) or [])
        if row.get("name")
    }
    cur_scenarios = {
        str(row.get("name")): float(row.get("observed_pass_rate", 0.0) or 0.0)
        for row in list(
            (current_payload.get("gates") or {}).get("scenario_results", []) or []
        )
        if row.get("name")
    }

    prev_categories = {
        str(row.get("category")): float(row.get("observed_pass_rate", 0.0) or 0.0)
        for row in list((previous.get("categories") or {}).get("results", []) or [])
        if row.get("category")
    }
    cur_categories = {
        str(row.get("category")): float(row.get("observed_pass_rate", 0.0) or 0.0)
        for row in list(
            (current_payload.get("categories") or {}).get("results", []) or []
        )
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

    prev_rollup_categories = {
        str(row.get("category")): float(row.get("aggregate_pass_rate", 0.0) or 0.0)
        for row in list(
            (((previous.get("rollup_analysis") or {}).get("categories") or {}).get("results", []) or [])
        )
        if row.get("category")
    }
    cur_rollup_categories = {
        str(row.get("category")): float(row.get("aggregate_pass_rate", 0.0) or 0.0)
        for row in list(
            ((((current_payload.get("rollup_analysis") or {}).get("categories") or {}).get("results", [])) or [])
        )
        if row.get("category")
    }

    rollup_category_deltas: list[dict[str, Any]] = []
    for name in sorted(set(prev_rollup_categories) | set(cur_rollup_categories)):
        rollup_category_deltas.append(
            {
                "category": name,
                "previous": prev_rollup_categories.get(name),
                "current": cur_rollup_categories.get(name),
                "delta": (
                    None
                    if name not in prev_rollup_categories or name not in cur_rollup_categories
                    else round(cur_rollup_categories[name] - prev_rollup_categories[name], 4)
                ),
            }
        )

    previous_rollup_performance = ((previous.get("rollup_analysis") or {}).get("performance_evidence") or {})
    current_rollup_performance = ((current_payload.get("rollup_analysis") or {}).get("performance_evidence") or {})
    rollup_performance_deltas = [
        {
            "name": key,
            "previous": float(previous_rollup_performance.get(key, 0.0) or 0.0),
            "current": float(current_rollup_performance.get(key, 0.0) or 0.0),
            "delta": round(
                float(current_rollup_performance.get(key, 0.0) or 0.0)
                - float(previous_rollup_performance.get(key, 0.0) or 0.0),
                4,
            ),
        }
        for key in ["avg_duration_sec", "max_duration_sec"]
    ]

    scenario_deltas: list[dict[str, Any]] = []
    for name in sorted(set(prev_scenarios) | set(cur_scenarios)):
        scenario_deltas.append(
            {
                "name": name,
                "previous": prev_scenarios.get(name),
                "current": cur_scenarios.get(name),
                "delta": (
                    None
                    if name not in prev_scenarios or name not in cur_scenarios
                    else round(cur_scenarios[name] - prev_scenarios[name], 4)
                ),
            }
        )

    return {
        "has_previous": True,
        "previous_summary": str(previous_summary_path),
        "previous_observed_run_pass_rate": prev_rate,
        "current_observed_run_pass_rate": cur_rate,
        "delta_observed_run_pass_rate": round(cur_rate - prev_rate, 4),
        "category_deltas": category_deltas,
        "rollup_category_deltas": rollup_category_deltas,
        "rollup_performance_deltas": rollup_performance_deltas,
        "scenario_deltas": scenario_deltas,
    }


def _build_category_rollup(report_data: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    failing: list[str] = []
    for row in list(report_data.get("category_summaries", []) or []):
        category = str(row.get("category") or "")
        if not category:
            continue
        observed = float(row.get("pass_rate", 0.0) or 0.0)
        total = int(row.get("total", 0) or 0)
        failed = int(row.get("failed", 0) or 0)
        passed_all = failed == 0 and total > 0
        results.append(
            {
                "category": category,
                "observed_pass_rate": observed,
                "total": total,
                "failed": failed,
                "passed": passed_all,
                "scenarios": list(row.get("scenarios", []) or []),
            }
        )
        if not passed_all:
            failing.append(category)
    return {"results": results, "failing": failing}


def bundle_artifacts(
    repo_root: Path,
    profile: str,
    runs: int,
    timeout: int,
    output_dir: Path,
    stamp: str,
    min_run_pass_rate: float | None = None,
    scenario_min_pass_rate: dict[str, float] | None = None,
    category_min_pass_rate: dict[str, float] | None = None,
    allowed_scenario_failures: int | None = None,
    performance_min_pass_rate: float | None = None,
    performance_max_avg_duration_sec: float | None = None,
    performance_max_scenario_duration_sec: float | None = None,
    emit_release_manifest: bool = False,
    release_manifest_version: str | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"phase5_validation_{stamp}.json"
    rollup_path = output_dir / f"phase5_rollup_{stamp}.json"
    summary_path = output_dir / f"phase5_bundle_{stamp}.json"

    harness_cmd = [
        sys.executable,
        "tools/phase5_validation_harness.py",
        "--profile",
        profile,
        "--runs",
        str(runs),
        "--timeout",
        str(timeout),
        "--output",
        str(report_path),
    ]
    harness = _run(harness_cmd, repo_root)

    rollup_cmd = [
        sys.executable,
        "tools/phase5_report_rollup.py",
        "--inputs",
        str(report_path),
        "--output",
        str(rollup_path),
    ]
    if performance_min_pass_rate is not None:
        rollup_cmd += ["--performance-min-pass-rate", str(performance_min_pass_rate)]
    if performance_max_avg_duration_sec is not None:
        rollup_cmd += [
            "--performance-max-avg-duration-sec",
            str(performance_max_avg_duration_sec),
        ]
    if performance_max_scenario_duration_sec is not None:
        rollup_cmd += [
            "--performance-max-scenario-duration-sec",
            str(performance_max_scenario_duration_sec),
        ]
    rollup = _run(rollup_cmd, repo_root)

    report_data: dict[str, Any] = {}
    rollup_data: dict[str, Any] = {}
    try:
        report_data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        report_data = {}
    try:
        rollup_data = json.loads(rollup_path.read_text(encoding="utf-8"))
    except Exception:
        rollup_data = {}

    observed_rate = float(
        (rollup_data.get("summary") or {}).get(
            "aggregate_run_pass_rate",
            report_data.get("run_pass_rate", 0.0),
        )
        or 0.0
    )
    gate_enabled = min_run_pass_rate is not None
    min_rate_value = float(min_run_pass_rate) if min_run_pass_rate is not None else None
    gate_passed = (
        (observed_rate >= min_rate_value) if min_rate_value is not None else True
    )

    scenario_failures = sum(
        1
        for row in list(report_data.get("scenarios", []) or [])
        if not bool(row.get("ok"))
    )
    budget_applies = allowed_scenario_failures is not None and profile != "full"
    budget_passed = (
        scenario_failures <= int(allowed_scenario_failures)
        if budget_applies and allowed_scenario_failures is not None
        else True
    )

    scenario_thresholds = scenario_min_pass_rate or {}
    scenario_stats: dict[str, dict[str, float | int]] = {}
    for row in list(report_data.get("scenarios", []) or []):
        name = str(row.get("name", ""))
        if not name:
            continue
        stat = scenario_stats.setdefault(name, {"total": 0, "passed": 0, "rate": 0.0})
        stat["total"] = int(stat["total"]) + 1
        if bool(row.get("ok", False)):
            stat["passed"] = int(stat["passed"]) + 1

    for stat in scenario_stats.values():
        total = int(stat["total"])
        passed = int(stat["passed"])
        stat["rate"] = (passed / total) if total else 0.0

    scenario_gate_rows: list[dict[str, Any]] = []
    for name, threshold in scenario_thresholds.items():
        observed = float((scenario_stats.get(name) or {}).get("rate", 0.0) or 0.0)
        scenario_gate_rows.append(
            {
                "name": name,
                "min_pass_rate": float(threshold),
                "observed_pass_rate": observed,
                "passed": observed >= float(threshold),
            }
        )
    scenario_gates_passed = all(row["passed"] for row in scenario_gate_rows)
    category_rollup = _build_category_rollup(report_data)
    category_thresholds = category_min_pass_rate or {}
    category_gate_rows: list[dict[str, Any]] = []
    category_rate_map = {
        str(row.get("category")): float(row.get("observed_pass_rate", 0.0) or 0.0)
        for row in list(category_rollup.get("results", []) or [])
        if row.get("category")
    }
    for name, threshold in category_thresholds.items():
        observed = float(category_rate_map.get(name, 0.0) or 0.0)
        category_gate_rows.append(
            {
                "category": name,
                "min_pass_rate": float(threshold),
                "observed_pass_rate": observed,
                "passed": observed >= float(threshold),
            }
        )
    category_gates_passed = all(row["passed"] for row in category_gate_rows)
    performance_thresholds = (rollup_data.get("performance_thresholds") or {})
    performance_thresholds_passed = bool(performance_thresholds.get("passed", True))

    payload = {
        "created_at": datetime.now(UTC).isoformat(),
        "profile": profile,
        "runs": runs,
        "timeout": timeout,
        "artifacts": {
            "report": str(report_path),
            "rollup": str(rollup_path),
            "summary": str(summary_path),
        },
        "steps": {
            "harness": harness,
            "rollup": rollup,
        },
        "rollup_analysis": {
            "categories": rollup_data.get("categories") or {"results": []},
            "performance_evidence": rollup_data.get("performance_evidence") or {},
            "performance_thresholds": performance_thresholds,
            "grouped_trends": rollup_data.get("grouped_trends") or {},
        },
        "gates": {
            "min_run_pass_rate": min_run_pass_rate,
            "observed_run_pass_rate": observed_rate,
            "scenario_min_pass_rate": scenario_thresholds,
            "scenario_results": scenario_gate_rows,
            "category_min_pass_rate": category_thresholds,
            "allowed_scenario_failures": allowed_scenario_failures,
            "budget_applies": budget_applies,
            "observed_scenario_failures": scenario_failures,
            "budget_passed": budget_passed,
            "category_results": category_rollup["results"],
            "category_threshold_results": category_gate_rows,
            "performance_thresholds": performance_thresholds,
            "performance_thresholds_passed": performance_thresholds_passed,
            "passed": (
                gate_passed
                and scenario_gates_passed
                and category_gates_passed
                and budget_passed
                and performance_thresholds_passed
            ),
        },
        "categories": category_rollup,
    }

    payload["integrity"] = {
        "report_sha256": _sha256_file(report_path),
        "report_size_bytes": report_path.stat().st_size if report_path.exists() else 0,
        "rollup_sha256": _sha256_file(rollup_path),
        "rollup_size_bytes": rollup_path.stat().st_size if rollup_path.exists() else 0,
    }

    previous_summary = _find_previous_bundle_summary(output_dir, summary_path)
    payload["trend"] = _build_trend(previous_summary, payload)

    release_manifest: dict[str, Any] = {
        "enabled": bool(emit_release_manifest),
        "version": release_manifest_version,
    }
    if emit_release_manifest:
        manifest_version = release_manifest_version or f"phase5-{stamp}"
        manifest_path = output_dir / f"phase5_release_manifest_{stamp}.json"
        manifest_cmd = [
            sys.executable,
            "tools/sign_release_manifest.py",
            "--dist",
            str(output_dir),
            "--version",
            manifest_version,
            "--output",
            str(manifest_path),
        ]
        manifest_run = _run(manifest_cmd, repo_root)
        signature_path = manifest_path.with_suffix(manifest_path.suffix + ".sig")
        release_manifest.update(
            {
                "path": str(manifest_path),
                "step": manifest_run,
                "sha256": _sha256_file(manifest_path),
                "size_bytes": (
                    manifest_path.stat().st_size if manifest_path.exists() else 0
                ),
                "signature_path": str(signature_path),
                "signature_exists": signature_path.exists(),
                "signature_sha256": _sha256_file(signature_path),
            }
        )
    payload["release_manifest"] = release_manifest

    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bundle phase5 validation artifacts")
    p.add_argument("--profile", choices=["quick", "full"], default="quick")
    p.add_argument("--runs", type=int, default=10)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--output-dir", default=".aetherra/reports/phase5")
    p.add_argument("--min-run-pass-rate", type=float, default=None)
    p.add_argument(
        "--allowed-scenario-failures",
        type=int,
        default=None,
        help="Non-prod budget for total failed scenario rows across all runs",
    )
    p.add_argument(
        "--scenario-min-pass-rate",
        action="append",
        default=[],
        help="Scenario threshold in the form <scenario_name>=<rate>",
    )
    p.add_argument(
        "--category-min-pass-rate",
        action="append",
        default=[],
        help="Category threshold in the form <category>=<rate>",
    )
    p.add_argument("--performance-min-pass-rate", type=float, default=None)
    p.add_argument("--performance-max-avg-duration-sec", type=float, default=None)
    p.add_argument(
        "--performance-max-scenario-duration-sec", type=float, default=None
    )
    p.add_argument(
        "--emit-release-manifest",
        action="store_true",
        help="Emit a signed/unsigned release manifest for generated artifacts",
    )
    p.add_argument(
        "--release-manifest-version",
        default=None,
        help="Explicit manifest version passed to sign_release_manifest.py",
    )
    p.add_argument("--stamp", default=datetime.now(UTC).strftime("%Y%m%d_%H%M%S"))
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = repo_root / out_dir

    if args.dry_run:
        preview = {
            "profile": args.profile,
            "runs": int(args.runs),
            "timeout": int(args.timeout),
            "output_dir": str(out_dir),
            "min_run_pass_rate": args.min_run_pass_rate,
            "allowed_scenario_failures": args.allowed_scenario_failures,
            "scenario_min_pass_rate": args.scenario_min_pass_rate,
            "category_min_pass_rate": args.category_min_pass_rate,
            "performance_min_pass_rate": args.performance_min_pass_rate,
            "performance_max_avg_duration_sec": args.performance_max_avg_duration_sec,
            "performance_max_scenario_duration_sec": args.performance_max_scenario_duration_sec,
            "emit_release_manifest": args.emit_release_manifest,
            "release_manifest_version": args.release_manifest_version,
            "stamp": args.stamp,
        }
        print(json.dumps(preview, indent=2))
        return 0

    if (
        args.allowed_scenario_failures is not None
        and args.allowed_scenario_failures < 0
    ):
        print("Invalid --allowed-scenario-failures: must be >= 0")
        return 2

    scenario_thresholds: dict[str, float] = {}
    category_thresholds: dict[str, float] = {}
    try:
        for raw in list(args.scenario_min_pass_rate or []):
            if "=" not in raw:
                raise ValueError(
                    "--scenario-min-pass-rate entries must be in form <scenario_name>=<rate>"
                )
            name, value = raw.split("=", 1)
            scenario_thresholds[name.strip()] = float(value)
        for raw in list(args.category_min_pass_rate or []):
            if "=" not in raw:
                raise ValueError(
                    "--category-min-pass-rate entries must be in form <category>=<rate>"
                )
            name, value = raw.split("=", 1)
            category_thresholds[name.strip()] = float(value)
    except ValueError as exc:
        print(f"Invalid scenario threshold argument: {exc}")
        return 2

    payload = bundle_artifacts(
        repo_root=repo_root,
        profile=args.profile,
        runs=max(1, int(args.runs)),
        timeout=max(1, int(args.timeout)),
        output_dir=out_dir,
        stamp=args.stamp,
        min_run_pass_rate=args.min_run_pass_rate,
        scenario_min_pass_rate=scenario_thresholds,
        category_min_pass_rate=category_thresholds,
        allowed_scenario_failures=args.allowed_scenario_failures,
        performance_min_pass_rate=args.performance_min_pass_rate,
        performance_max_avg_duration_sec=args.performance_max_avg_duration_sec,
        performance_max_scenario_duration_sec=args.performance_max_scenario_duration_sec,
        emit_release_manifest=args.emit_release_manifest,
        release_manifest_version=args.release_manifest_version,
    )

    harness_ok = bool(payload["steps"]["harness"]["ok"])
    rollup_ok = bool(payload["steps"]["rollup"]["ok"])
    release_manifest_ok = bool(
        (payload.get("release_manifest") or {}).get("step", {}).get("ok", True)
    )
    gates_ok = bool(payload["gates"]["passed"])
    print(
        f"Bundle complete: harness_ok={harness_ok}, rollup_ok={rollup_ok}, release_manifest_ok={release_manifest_ok}, gates_ok={gates_ok}, "
        f"summary={payload['artifacts']['summary']}"
    )
    return 0 if harness_ok and rollup_ok and release_manifest_ok and gates_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
