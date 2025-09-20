#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Classify failing .aether workflows at scale (initial skeleton).

Problem: User reports >2,700 workflow failures (likely .aether scripts) but they are
ignored by .gitignore (glob '*.aether') so enumeration requires explicit scanning
in working tree (including untracked) or external index (advanced_project_intelligence.json).

Current capabilities:
 1. Discover .aether files via recursive scan (including gitignored) if present.
 2. Parse + execute using interpreter fast parse check first.
 3. Consume structured error codes when interpreter invoked with --json-status / --emit-error-code.
 4. Bucket failures by structured code-name (preferred) else heuristic fallback.
 5. Optional parallel execution with --jobs.
 6. Historical run persistence with --history-dir and rolling trends summary.

Planned (future):
    - Failure fingerprinting (hash of exception type + first line)
    - Auto-suppression list generation for known intentional failures

Usage:
  python tools/classify_aether_workflow_failures.py --output workflow_failures.json

Artifacts:
  workflow_failures.json  (machine readable)
  workflow_failures.md    (human summary)

Exit code: 0 always (informational). Downstream gating can decide thresholds.
"""

from __future__ import annotations

# Standard library imports
import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SUPPRESSION_FILE = Path(".aetherra/workflow_suppressions.txt")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AETHER_INTERPRETER = [sys.executable, "aether.py"]  # Base command
DEFAULT_JOBS = max(1, os.cpu_count() or 1)


@dataclass
class WorkflowResult:
    path: str
    ok: bool
    category: str
    error: str | None = None
    signature_verified: bool | None = None
    risk_score: int | None = None
    code: int | None = None
    code_name: str | None = None
    phase: str | None = None
    line: int | None = None
    fingerprint: str | None = None
    suppressed: bool | None = None


def discover_aether_files(root: Path) -> List[Path]:
    ignore_dirs = {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".venv",
        "venv",
        "build",
        "dist",
    }
    files: List[Path] = []
    for p in root.rglob("*.aether"):
        if not p.is_file():
            continue
        if any(part in ignore_dirs for part in p.parts):
            continue
        files.append(p)
    return sorted(files)


def verify_signature_and_risk(path: Path) -> Tuple[bool | None, int | None]:
    try:
        # Aetherra imports
        from Aetherra.analysis.static_risk import analyze_paths  # type: ignore
        from Aetherra.security.script_signing import (
            verify_embedded_signature,  # type: ignore
        )
    except Exception:
        return None, None
    text = path.read_text(encoding="utf-8", errors="ignore")
    ok, _reason = verify_embedded_signature(text)
    try:
        res = analyze_paths([path])
        return ok, int(res.get("total_score", 0))
    except Exception:
        return ok, None


def categorize_exception(stderr: str) -> str:
    lower = stderr.lower()
    if "signature" in lower and "missing" in lower:
        return "SignatureMissing"
    if "parse" in lower and "error" in lower:
        return "ParseError"
    if "timeout" in lower:
        return "Timeout"
    if "permission" in lower:
        return "Permission"
    if "not implemented" in lower:
        return "NotImplemented"
    if "traceback" in lower:
        return "RuntimeError"
    return "Other"


def execute_workflow(path: Path, timeout: int = 8) -> Tuple[WorkflowResult, str]:
    """Execute a workflow with structured interpreter integration.

    Returns (WorkflowResult, raw_combined_output_or_error_text)
    """
    base_env = {
        **os.environ,
        "AETHERRA_PROFILE": os.getenv("AETHERRA_PROFILE", "test"),
        "AETHERRA_QUIET": "1",
    }
    # Always ask for structured outputs; fall back if interpreter older
    parse_cmd = AETHER_INTERPRETER + [
        "--check",
        "--emit-error-code",
        "--json-status",
        str(path),
    ]
    try:
        parse_proc = subprocess.run(
            parse_cmd,
            capture_output=True,
            text=True,
            timeout=min(4, timeout),
            env=base_env,
        )
    except subprocess.TimeoutExpired:
        wr = WorkflowResult(
            path=str(path),
            ok=False,
            category="Timeout",
            error="Timeout during parse check",
        )
        return wr, wr.error or "Timeout"

    parse_json: Optional[Dict[str, Any]] = None
    for line in parse_proc.stdout.splitlines():
        if line.strip().startswith("{") and '"code"' in line:
            try:
                parse_json = json.loads(line)
            except Exception:
                pass
    if parse_json and not parse_json.get("ok"):
        # Parse failure
        category = parse_json.get("code_name", "ParseError")
        wr = WorkflowResult(
            path=str(path),
            ok=False,
            category=category,
            error=parse_proc.stderr or parse_proc.stdout,
            code=parse_json.get("code"),
            code_name=parse_json.get("code_name"),
            phase=parse_json.get("phase"),
            line=parse_json.get("line"),
        )
        return wr, wr.error or "Parse failed"

    if parse_proc.returncode != 0 and not parse_json:
        # Older interpreter or unexpected failure
        err_text = parse_proc.stderr or parse_proc.stdout or "Parse failed"
        wr = WorkflowResult(
            path=str(path),
            ok=False,
            category=categorize_exception(err_text),
            error=err_text,
        )
        return wr, err_text

    # Parse OK -> full execution
    run_cmd = AETHER_INTERPRETER + ["--emit-error-code", "--json-status", str(path)]
    try:
        run_proc = subprocess.run(
            run_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=base_env,
        )
    except subprocess.TimeoutExpired:
        wr = WorkflowResult(
            path=str(path),
            ok=False,
            category="Timeout",
            error="Timeout executing workflow",
        )
        return wr, wr.error or "Timeout"

    run_json: Optional[Dict[str, Any]] = None
    for line in run_proc.stdout.splitlines():
        if line.strip().startswith("{") and '"code"' in line:
            try:
                run_json = json.loads(line)
            except Exception:
                pass
    if run_json:
        ok = run_json.get("ok", False)
        category = run_json.get("code_name", "OK" if ok else "RuntimeError")
        wr = WorkflowResult(
            path=str(path),
            ok=ok,
            category=category if ok else category,
            error=None if ok else (run_proc.stderr or run_proc.stdout),
            code=run_json.get("code"),
            code_name=run_json.get("code_name"),
            phase=run_json.get("phase"),
            line=run_json.get("line"),
        )
        return wr, wr.error or ""

    # Fallback heuristic
    ok = run_proc.returncode == 0
    err_text = "" if ok else (run_proc.stderr or run_proc.stdout)
    wr = WorkflowResult(
        path=str(path),
        ok=ok,
        category="OK" if ok else categorize_exception(err_text),
        error=err_text if not ok else None,
    )
    return wr, err_text


def _classify_single(p: Path, timeout: int) -> WorkflowResult:
    sig_ok, risk = verify_signature_and_risk(p)
    wr, err_text = execute_workflow(p, timeout=timeout)
    wr.signature_verified = sig_ok
    wr.risk_score = risk
    # Build fingerprint for failures (or any non-success code != 0)
    if not wr.ok:
        parts = [
            wr.code_name or wr.category,
            str(wr.line) if wr.line is not None else "-",
            (wr.error or "").strip().splitlines()[0] if wr.error else "",
        ]
        raw = "|".join(parts)
        wr.fingerprint = hashlib.sha256(
            raw.encode("utf-8", errors="ignore")
        ).hexdigest()[:16]
    if wr.error:
        wr.error = wr.error[:5000]
    return wr


def classify(
    paths: List[Path], jobs: int = 1, timeout: int = 8
) -> List[WorkflowResult]:
    if jobs <= 1:
        return [_classify_single(p, timeout) for p in paths]
    results: List[WorkflowResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        future_map = {ex.submit(_classify_single, p, timeout): p for p in paths}
        for fut in concurrent.futures.as_completed(future_map):
            try:
                results.append(fut.result())
            except Exception as e:  # defensive
                results.append(
                    WorkflowResult(
                        path=str(future_map[fut]),
                        ok=False,
                        category="InternalError",
                        error=str(e),
                    )
                )
    return results


def aggregate(results: List[WorkflowResult]) -> Dict[str, Any]:
    by_cat: Dict[str, List[WorkflowResult]] = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)
    cat_summary = {
        k: {"count": len(v), "examples": [x.path for x in v[:5]]}
        for k, v in sorted(by_cat.items(), key=lambda kv: -len(kv[1]))
    }
    total = len(results)
    failed = sum(1 for r in results if not r.ok)
    suppressed = sum(1 for r in results if (r.suppressed or False))
    return {
        "total": total,
        "failed": failed,
        "failure_rate": round(failed / total, 4) if total else 0.0,
        "suppressed_failures": suppressed,
        "categories": cat_summary,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def write_artifacts(
    results: List[WorkflowResult], summary: Dict[str, Any], output: str, md: str
):
    Path(output).write_text(
        json.dumps(
            {"workflows": [asdict(r) for r in results], "summary": summary}, indent=2
        ),
        encoding="utf-8",
    )
    lines = [
        "# Workflow Failure Classification",
        "",
        f"Total: {summary['total']}  Failures: {summary['failed']}  Failure Rate: {summary['failure_rate'] * 100:.2f}%",
        "",
    ]
    lines.append("## Categories")
    lines.append("| Category | Count | Example(s) |")
    lines.append("|----------|-------|-----------|")
    for cat, info in summary["categories"].items():
        lines.append(f"| {cat} | {info['count']} | {', '.join(info['examples'])} |")
    lines.append("\n## Notes\n")
    lines.append(
        "- This is an initial pass. Categories are heuristic (stderr pattern based)."
    )
    lines.append(
        "- Consider adding structured failure codes to the interpreter for precision."
    )
    Path(md).write_text("\n".join(lines), encoding="utf-8")


def persist_history(summary: Dict[str, Any], history_dir: Path, artifact_json: Path):
    history_dir.mkdir(parents=True, exist_ok=True)
    ts = summary.get("timestamp", datetime.now(UTC).isoformat())
    stamp = ts.replace(":", "").replace("-", "")[:15]
    snapshot_path = history_dir / f"{stamp}_classification.json"
    snapshot_path.write_text(
        artifact_json.read_text(encoding="utf-8"), encoding="utf-8"
    )

    # Build trends (last N = 20)
    entries = sorted(history_dir.glob("*_classification.json"))[-20:]
    trends: List[Dict[str, Any]] = []
    for p in entries:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            trends.append(
                {
                    "file": p.name,
                    "timestamp": data.get("summary", {}).get("timestamp"),
                    "failed": data.get("summary", {}).get("failed"),
                    "total": data.get("summary", {}).get("total"),
                }
            )
        except Exception:
            continue
    (history_dir / "trends.json").write_text(
        json.dumps(trends, indent=2), encoding="utf-8"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.cwd()))
    ap.add_argument("--output", default="workflow_failures.json")
    ap.add_argument("--markdown", default="workflow_failures.md")
    ap.add_argument(
        "--limit", type=int, default=0, help="Process only first N workflows (debug)"
    )
    ap.add_argument(
        "--jobs",
        type=int,
        default=DEFAULT_JOBS,
        help="Parallel worker threads (default: CPU count)",
    )
    ap.add_argument(
        "--timeout", type=int, default=8, help="Per-workflow timeout seconds"
    )
    ap.add_argument(
        "--history-dir",
        default=".aetherra/workflow_history",
        help="Directory to persist historical summaries",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = discover_aether_files(root)
    if args.limit > 0:
        files = files[: args.limit]
    results = classify(files, jobs=max(1, args.jobs), timeout=args.timeout)
    # Load suppression fingerprints (each line: fingerprint[#comment])
    suppressions: set[str] = set()
    if SUPPRESSION_FILE.exists():
        try:
            for raw in SUPPRESSION_FILE.read_text(
                encoding="utf-8", errors="ignore"
            ).splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                # take first token (allow optional inline comment)
                token = line.split()[0]
                if len(token) >= 8:  # minimal length safeguard
                    suppressions.add(token)
        except Exception:
            pass
    # Mark suppressed
    for r in results:
        if r.fingerprint and r.fingerprint in suppressions:
            r.suppressed = True
            if not r.ok:
                r.category = f"Suppressed-{r.category}"
    summary = aggregate(results)
    write_artifacts(results, summary, args.output, args.markdown)
    print(json.dumps(summary, indent=2))
    print(f"Artifacts: {args.output}, {args.markdown}")
    # Persist history
    try:
        hist_dir = Path(args.history_dir)
        persist_history(summary, hist_dir, Path(args.output))
        print(f"History updated in {hist_dir}")
    except Exception as e:
        print(f"History persistence error: {e}")


if __name__ == "__main__":  # pragma: no cover
    main()
