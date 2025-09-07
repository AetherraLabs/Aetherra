#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Verify .aether scripts for signing and static risk.

- Validates embedded signatures when --strict or AETHERRA_SCRIPT_VERIFY_STRICT=1.
- Runs static risk analysis and fails non-zero when score exceeds threshold.
- Outputs a markdown report by default.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path
from typing import List

try:
    import numpy as _np  # type: ignore
except Exception:
    _np = None

from Aetherra.analysis.static_risk import analyze_paths  # type: ignore
from Aetherra.security.script_signing import verify_embedded_signature  # type: ignore


def find_aether_files(root: Path) -> List[Path]:
    """Return all .aether files under the repo, excluding transient/ignored dirs.

    Previous implementation only looked in a narrow set (scripts/, workflows/ ...)
    which missed system and example workflows. We now do a full recursive scan
    while skipping common virtualenv / VCS / build directories for signal clarity.
    """
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
    candidates = []
    for p in root.rglob("*.aether"):
        if not p.is_file():
            continue
        if any(part in ignore_dirs for part in p.parts):
            continue
        candidates.append(p)
    return sorted(set(candidates))


def _apply_profile(profile: str | None):
    if not profile:
        profile = os.getenv("AETHERRA_PROFILE", "").lower() or None
    if profile != "test":
        return
    os.environ.setdefault("AETHERRA_PROFILE", "test")
    os.environ.setdefault("AETHERRA_DETERMINISTIC", "1")
    os.environ.setdefault("PYTHONHASHSEED", "0")
    try:
        random.seed(0)
    except Exception:
        pass
    if _np is not None:
        try:
            _np.random.seed(0)
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path.cwd()))
    ap.add_argument("--output", default="aether_static_report.md")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--risk-threshold", type=int, default=5)
    ap.add_argument(
        "--fail-on-any-risk",
        action="store_true",
        help="Exit non-zero if total risk score > 0 (overrides --risk-threshold logic)",
    )
    ap.add_argument("--profile", default=os.getenv("AETHERRA_PROFILE", ""))
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Glob(s) to exclude from scanning (repeatable)",
    )
    ap.add_argument(
        "--max-findings-per-file",
        type=int,
        default=50,
        help="Cap the number of risky-line entries printed per file",
    )
    args = ap.parse_args()

    _apply_profile(getattr(args, "profile", None))

    root = Path(args.root).resolve()
    files = find_aether_files(root)
    # Apply excludes
    excludes = getattr(args, "exclude", []) or []
    if excludes:
        import fnmatch

        files = [
            f
            for f in files
            if not any(fnmatch.fnmatch(str(f), pat) for pat in excludes)
        ]
    # Known mutable artifacts to ignore for signature checks but include in risk: evolution_history.aether
    sig_ignored = {str((root / "evolution_history.aether").resolve())}

    strict_env = os.getenv("AETHERRA_SCRIPT_VERIFY_STRICT", "0") == "1"
    strict = args.strict or strict_env

    lines = ["# .aether Verification Report", ""]
    lines.append(f"Root: {root}")
    lines.append(f"Files found: {len(files)}")
    prof = os.getenv("AETHERRA_PROFILE") or getattr(args, "profile", "")
    if prof:
        lines.append(f"Profile: {prof}")
    lines.append("")
    # Always list all discovered .aether files for full transparency (helps reviewers)
    if files:
        lines.append("## Discovered .aether Files")
        for f in files:
            lines.append(f"- {f}")
        lines.append("")

    fail = False

    # Signature checks
    if strict:
        lines.append("## Signature Verification (strict)")
        for f in files:
            fstr = str(f.resolve())
            if fstr in sig_ignored:
                lines.append(f"- {f}: SKIP (signature not required for evolving log)")
                continue
            ok, reason = verify_embedded_signature(
                f.read_text(encoding="utf-8", errors="ignore")
            )
            status = "OK" if ok else f"FAIL ({reason})"
            lines.append(f"- {f}: {status}")
            if not ok:
                fail = True
        lines.append("")

    # Static risk analysis
    if files:
        result = analyze_paths(files)
        lines.append("## Static Risk Analysis")
        lines.append(f"Total risk score: {result['total_score']}")
        if getattr(args, "fail_on_any_risk", False) and result["total_score"] > 0:
            fail = True
        # Sort files by score descending
        sorted_items = sorted(
            result["files"].items(), key=lambda kv: kv[1].get("score", 0), reverse=True
        )
        # Top 5 summary
        top5 = sorted_items[:5]
        if top5:
            lines.append("Top risky files:")
            for path, info in top5:
                lines.append(
                    f"- {path}: score={info['score']} findings={len(info.get('findings', []))}"
                )
            lines.append("")
        for path, info in sorted_items:
            findings = info.get("findings", [])
            lines.append(f"- {path}: score={info['score']} findings={len(findings)}")
            # Print per-file risky lines for easier review in PRs
            max_lines = max(0, int(args.max_findings_per_file))
            shown = 0
            for f in findings:
                kind = f.get("kind")
                line_no = f.get("line")
                snippet = f.get("snippet", "").strip()
                if len(snippet) > 180:
                    snippet = snippet[:177] + "..."
                lines.append(f"  - L{line_no}: [{kind}] {snippet}")
                shown += 1
                if shown >= max_lines:
                    remaining = max(0, len(findings) - shown)
                    if remaining:
                        lines.append(f"  ...and {remaining} more lines (capped)")
                    break
            if not getattr(args, "fail_on_any_risk", False):
                if info.get("score", 0) > args.risk_threshold:
                    fail = True
        lines.append("")
    else:
        lines.append("No .aether files found.")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")

    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
