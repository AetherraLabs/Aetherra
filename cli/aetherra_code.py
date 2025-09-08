#!/usr/bin/env python3
"""Aetherra Coding System CLI (Phase 0)

Commands:
  plan --intent TEXT [--scope file1,file2]
  generate --step N [--out patch.diff]
  apply --diff patch.diff [--dry-run]
  verify [--no-spec] [--no-quality] [--lenient]
  commit -m MESSAGE

Autonomy mode via env AETHERRA_MODE (assist|co-drive|autopilot).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aetherra_coding import CodeOrchestrator


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aetherra_code", description="Lyrixa Code Studio CLI"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_plan = sub.add_parser("plan", help="Create a plan for an intent")
    sp_plan.add_argument("--intent", required=True)
    sp_plan.add_argument("--scope", help="Comma-separated file paths", default="")

    sp_gen = sub.add_parser("generate", help="Generate candidate patch for a plan step")
    sp_gen.add_argument("--step", type=int, required=True)
    sp_gen.add_argument("--out", help="Write diff to file")

    sp_apply = sub.add_parser("apply", help="Apply a unified diff")
    sp_apply.add_argument("--diff", required=True, help="Diff file path")
    sp_apply.add_argument("--dry-run", action="store_true")

    sp_verify = sub.add_parser("verify", help="Run verification gates")
    sp_verify.add_argument("--no-spec", action="store_true")
    sp_verify.add_argument("--no-quality", action="store_true")
    sp_verify.add_argument(
        "--lenient", action="store_true", help="Lenient .aether risk"
    )

    sp_commit = sub.add_parser("commit", help="Commit staged changes")
    sp_commit.add_argument("-m", "--message", required=True)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    orch = CodeOrchestrator()

    if args.cmd == "plan":
        scope = [s for s in args.scope.split(",") if s.strip()]
        plan = orch.plan(intent=args.intent, scope=scope)
        print(f"Plan created with {len(plan.steps)} step(s)")
        for i, step in enumerate(plan.steps):
            print(f"[{i}] {step.description} -> {step.target_files}")
        return 0

    if args.cmd == "generate":
        pr = orch.generate(step_index=args.step)
        if args.out:
            Path(args.out).write_text(pr.diff, encoding="utf-8")
            print(f"Diff written to {args.out}")
        else:
            print(pr.diff)
        return 0

    if args.cmd == "apply":
        diff_text = Path(args.diff).read_text(encoding="utf-8")
        result = orch.apply_patch(diff_text, dry_run=args.dry_run)
        print(
            f"Applied={result.applied} dry_run={result.dry_run} rollback={result.rollback_token}"
        )
        for d in result.diagnostics:
            print(d)
        return 0 if (result.applied or args.dry_run) else 1

    if args.cmd == "verify":
        ver = orch.verify(
            run_spec_tests_gate=not args.no_spec,
            run_quality_gates=not args.no_quality,
            strict_aether=not args.lenient,
        )
        print(
            f"Passed={ver.passed} spec={ver.spec_tests_gate} quality={ver.quality_gates} aether_risk={ver.aether_risk}"
        )
        for d in ver.diagnostics:
            print(d)
        return 0 if ver.passed else 1

    if args.cmd == "commit":
        res = orch.commit(message=args.message)
        print(f"Committed={res.committed} sha={res.sha}")
        for d in res.diagnostics:
            print(d)
        return 0 if res.committed else 1

    print("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
