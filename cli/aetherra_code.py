#!/usr/bin/env python3
"""Aetherra Coding System CLI (Phase 0)

Commands:
  plan --intent TEXT [--scope file1,file2]
  generate --step N [--out patch.diff]
  apply --diff patch.diff [--dry-run]
  verify [--no-spec] [--no-quality] [--lenient]
  commit -m MESSAGE
    revert --token TOKEN
    plugin scaffold --name NAME

Autonomy mode via env AETHERRA_MODE (assist|co-drive|autopilot).
"""

from __future__ import annotations

# Standard library imports
import argparse
from pathlib import Path

# Aetherra imports
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
    sp_gen.add_argument("--json", action="store_true", help="Emit JSON result")

    sp_apply = sub.add_parser("apply", help="Apply a unified diff")
    sp_apply.add_argument("--diff", required=True, help="Diff file path")
    sp_apply.add_argument("--dry-run", action="store_true")
    sp_apply.add_argument("--no-color", action="store_true")
    sp_apply.add_argument("--json", action="store_true")

    sp_verify = sub.add_parser("verify", help="Run verification gates")
    sp_verify.add_argument(
        "--no-spec", action="store_true", help="Skip spec → tests gate"
    )
    sp_verify.add_argument(
        "--no-quality", action="store_true", help="Skip quality gates script"
    )
    sp_verify.add_argument(
        "--no-format",
        action="store_true",
        help="Skip format/lint stage (or set AETHERRA_FORMAT_LINT=0)",
    )
    sp_verify.add_argument(
        "--lenient",
        action="store_true",
        help="Lenient .aether risk (disable strict signatures)",
    )
    sp_verify.add_argument(
        "--json", action="store_true", help="Emit JSON with per-gate status"
    )

    sp_commit = sub.add_parser("commit", help="Commit staged changes")
    sp_commit.add_argument("-m", "--message", required=True)

    sp_revert = sub.add_parser("revert", help="Revert using rollback token")
    sp_revert.add_argument("--token", required=True)
    sp_revert.add_argument("--json", action="store_true")

    sp_plugin = sub.add_parser("plugin", help="Plugin related operations")
    sub_plugin = sp_plugin.add_subparsers(dest="plugin_cmd", required=True)
    sp_plugin_scaffold = sub_plugin.add_parser("scaffold", help="Scaffold a new plugin")
    sp_plugin_scaffold.add_argument("--name", required=True)
    sp_plugin_scaffold.add_argument("--json", action="store_true")
    sp_plugin_list = sub_plugin.add_parser("list", help="List discovered plugins")
    sp_plugin_list.add_argument("--json", action="store_true")

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
        if args.json:
            # Standard library imports
            import json as _json

            print(
                _json.dumps(
                    {
                        "applied": pr.applied,
                        "dry_run": pr.dry_run,
                        "risk": pr.risk_level,
                        "changed_lines": pr.changed_lines,
                        "summary": pr.summary,
                        "diff": pr.diff,
                    }
                )
            )
            return 0
        if args.out:
            Path(args.out).write_text(pr.diff, encoding="utf-8")
            print(f"Diff written to {args.out}")
        else:
            print(pr.diff)
        return 0

    if args.cmd == "apply":
        diff_text = Path(args.diff).read_text(encoding="utf-8")
        result = orch.apply_patch(
            diff_text, dry_run=args.dry_run, colorize=not args.no_color
        )
        if args.json:
            # Standard library imports
            import json as _json

            print(
                _json.dumps(
                    {
                        "applied": result.applied,
                        "dry_run": result.dry_run,
                        "rollback_token": result.rollback_token,
                        "risk": result.risk_level,
                        "changed_lines": result.changed_lines,
                        "summary": result.summary,
                        "diagnostics": result.diagnostics,
                    }
                )
            )
        else:
            print(
                f"Applied={result.applied} dry_run={result.dry_run} rollback={result.rollback_token} risk={result.risk_level} changed={result.changed_lines}"
            )
            for d in result.diagnostics:
                print(d)
        return 0 if (result.applied or args.dry_run) else 1

    if args.cmd == "verify":
        ver = orch.verify(
            run_spec_tests_gate=not args.no_spec,
            run_quality_gates=not args.no_quality,
            strict_aether=not args.lenient,
            run_format_lint=not args.no_format,
        )
        if args.json:
            # Standard library imports
            import json as _json
            import os as _os

            print(
                _json.dumps(
                    {
                        "passed": ver.passed,
                        "spec_tests_gate": ver.spec_tests_gate,
                        "quality_gates": ver.quality_gates,
                        "aether_risk": ver.aether_risk,
                        "format_lint": ver.format_lint,
                        "strict": _os.getenv("AETHERRA_STRICT", "0") == "1",
                        "diagnostics": ver.diagnostics,
                    }
                )
            )
        else:
            print(
                f"Passed={ver.passed} spec={ver.spec_tests_gate} quality={ver.quality_gates} aether_risk={ver.aether_risk} format_lint={ver.format_lint}"
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

    if args.cmd == "revert":
        pr = orch.revert(token=args.token)
        if args.json:
            # Standard library imports
            import json as _json

            print(
                _json.dumps(
                    {
                        "applied": pr.applied,
                        "summary": pr.summary,
                        "diagnostics": pr.diagnostics,
                    }
                )
            )
        else:
            print(f"Reverted applied={pr.applied} summary={pr.summary}")
            for d in pr.diagnostics:
                print(d)
        return 0 if pr.applied else 1

    if args.cmd == "plugin":
        if args.plugin_cmd == "scaffold":
            pr = orch.scaffold_plugin(name=args.name)
            if args.json:
                # Standard library imports
                import json as _json

                print(
                    _json.dumps(
                        {
                            "applied": pr.applied,
                            "rollback_token": pr.rollback_token,
                            "summary": pr.summary,
                            "diagnostics": pr.diagnostics,
                        }
                    )
                )
            else:
                print(
                    f"Plugin scaffold applied={pr.applied} rollback_token={pr.rollback_token} summary={pr.summary}"
                )
                for d in pr.diagnostics:
                    print(d)
            return 0 if pr.applied else 1
        elif args.plugin_cmd == "list":
            # Aetherra imports
            from Aetherra.plugins.core import plugin_registry as _preg

            data = _preg.discover_plugins()
            if args.json:
                # Standard library imports
                import json as _json

                print(_json.dumps(data))
            else:
                for name, meta in data.items():
                    warns = meta.get("validation_warnings") or []
                    print(f"{name} v{meta.get('version', '?')} warnings={len(warns)}")
            return 0
        else:
            print("Unknown plugin subcommand")
            return 1

    print("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
