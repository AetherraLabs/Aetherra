#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Generate a baseline parse status JSON for all .aether workflows.

This script runs the interpreter in --check mode with structured output flags
and aggregates counts by structured error code (or heuristics if older
interpreter). Intended for CI baseline + local regression tracking.

Output (default parse_baseline.json):
{
  "timestamp": "2025-09-12T12:34:56Z",
  "total": 123,
  "by_code": {"SUCCESS": 100, "PARSE_ERROR": 20, "IO_ERROR": 3},
  "failure_rate": 0.18699,
  "files": [
     {"path": "workflows/x.aether", "code": 20, "code_name": "PARSE_ERROR", "line": 5, "message": "..."},
     ...
  ]
}

Exit code: always 0 (informational).
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

AETHER = [sys.executable, "aether.py"]


def discover(root: Path) -> List[Path]:
    ignore = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "build", "dist"}
    out: List[Path] = []
    for p in root.rglob("*.aether"):
        if not p.is_file():
            continue
        if any(part in ignore for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def run_check(path: Path, timeout: int) -> Dict[str, Any]:
    env = {
        **os.environ,
        "AETHERRA_PROFILE": os.getenv("AETHERRA_PROFILE", "test"),
        "AETHERRA_QUIET": "1",
    }
    cmd = AETHER + ["--check", "--emit-error-code", "--json-status", str(path)]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env
        )
    except subprocess.TimeoutExpired:
        return {
            "path": str(path),
            "code": 23,
            "code_name": "TIMEOUT_ERROR",
            "ok": False,
            "message": "timeout",
        }
    record: Dict[str, Any] = {"path": str(path), "ok": proc.returncode == 0}
    parsed_json: Optional[Dict[str, Any]] = None
    for line in proc.stdout.splitlines():
        if line.strip().startswith("{") and '"code"' in line:
            try:
                parsed_json = json.loads(line)
            except Exception:
                pass
    if parsed_json:
        record.update(
            {
                "ok": parsed_json.get("ok", record["ok"]),
                "code": parsed_json.get("code"),
                "code_name": parsed_json.get("code_name"),
                "line": parsed_json.get("line"),
                "message": parsed_json.get("message"),
            }
        )
    else:
        # Heuristic fallback
        if not record["ok"]:
            stderr = proc.stderr.lower()
            if "parse" in stderr and "error" in stderr:
                record.update(
                    {
                        "code": 20,
                        "code_name": "PARSE_ERROR",
                        "message": proc.stderr.strip() or proc.stdout.strip(),
                    }
                )
            else:
                record.update(
                    {
                        "code": 1,
                        "code_name": "GENERIC_FAILURE",
                        "message": proc.stderr.strip() or proc.stdout.strip(),
                    }
                )
        else:
            record.update({"code": 0, "code_name": "SUCCESS"})
    return record


def aggregate(file_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(file_records)
    by_code: Dict[str, int] = {}
    for rec in file_records:
        name = rec.get("code_name", "UNKNOWN") or "UNKNOWN"
        by_code[name] = by_code.get(name, 0) + 1
    failed = total - by_code.get("SUCCESS", 0)
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "total": total,
        "by_code": by_code,
        "failure_rate": round(failed / total, 4) if total else 0.0,
        "files": file_records,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.cwd()))
    ap.add_argument("--output", default="parse_baseline.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument(
        "--timeout", type=int, default=4, help="Per-file parse timeout seconds"
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = discover(root)
    if args.limit > 0:
        files = files[: args.limit]

    records: List[Dict[str, Any]] = []
    for p in files:
        records.append(run_check(p, args.timeout))

    baseline = aggregate(records)
    Path(args.output).write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    print(json.dumps(baseline["by_code"], indent=2))
    print(f"Baseline written: {args.output}")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
