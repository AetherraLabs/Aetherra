#!/usr/bin/env python3
"""Fail closed unless this main commit completed both production signing steps."""

from __future__ import annotations

# Standard library imports
import argparse
import json
import re
import subprocess


def verify_run(run: dict, jobs: list[dict], sha: str) -> None:
    expected = {
        "head_sha": sha,
        "head_branch": "main",
        "event": "push",
        "status": "completed",
        "conclusion": "success",
    }
    if any(run.get(key) != value for key, value in expected.items()):
        raise ValueError("the exact main commit needs a successful push CI run")
    required = {
        "Production bundle with signed release manifest",
        "Enforce signed-manifest policy",
    }
    successful = {
        step["name"]
        for job in jobs
        for step in job.get("steps", [])
        if step.get("conclusion") == "success"
    }
    if not required.issubset(successful):
        raise ValueError("production signing and signature policy must both succeed")


def fetch(path: str) -> dict:
    result = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", args.repo) or not re.fullmatch(
            r"[0-9a-f]{40}", args.sha
        ):
            raise ValueError("expected owner/repository and a full commit SHA")
        prefix = f"repos/{args.repo}/actions"
        runs = fetch(
            f"{prefix}/workflows/ci_quality_gates.yml/runs"
            f"?head_sha={args.sha}&event=push&branch=main&per_page=1"
        )["workflow_runs"]
        if not runs:
            raise ValueError("no push CI run exists for this main commit")
        run = runs[0]
        jobs = fetch(f"{prefix}/runs/{run['id']}/jobs?per_page=100")["jobs"]
        verify_run(run, jobs, args.sha)
        print(f"[RELEASE] Signed main CI verified for {args.sha}")
        return 0
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(f"[RELEASE][BLOCKED] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
