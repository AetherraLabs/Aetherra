#!/usr/bin/env python3
"""Root cleanup orchestrator (non-destructive by default).

Phases:
  --plan        Emit intended operations (JSON) to stdout and optionally file
  --apply       Perform moves (copy then remove original only with --prune-originals)

Policies:
  * Only operate on whitelisted source → destination mappings encoded below.
  * Skip if path already under an allowed destination.
  * Always log journal entries (id, action, src, dest, status).

Exit codes:
  0 success / no-op
  1 unexpected error
  2 partial (some failures) – still continue CI but surface warning
"""

from __future__ import annotations

# Standard library imports
import argparse
import hashlib
import json
import os
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mapping categories → (glob patterns or explicit names, destination relative path)
PLANS: list[dict[str, object]] = [
    {
        "name": "backups",
        "paths": [
            "backups",
            "comprehensive_cleanup_backup",
            "final_organization_backup",
            "focused_cleanup_backup",
            "smart_cleanup_backup",
        ],
        "dest": "archive/backups",
    },
    {
        "name": "backup_info",
        "paths": [
            "plugins_cleanup_backup_info.json",
            "lyrixa_cleanup_backup_info.json",
        ],
        "dest": "archive/metadata",
    },
    {
        "name": "phase_tests",
        "paths": [
            "phase_7_4_test.py",
            "phase_7_4_ultimate_test.py",
            "phase_7_5_test.py",
            "phase_8_1_test.py",
            "phase_8_2_test.py",
            "phase_8_3_test.py",
        ],
        "dest": "tests/legacy",
    },
    {
        "name": "experimental_scripts",
        "paths": [
            "beyond_transcendence_engine.py",
            "cosmic_consciousness_engine.py",
            "intelligent_error_handler_8.py",
            "enhanced_conversation_manager_7.py",
        ],
        "dest": "experiments",
    },
    {
        "name": "cleanup_plans",
        "paths": ["PROJECT_CLEANUP_PLAN.json", "PROJECT_CLEANUP_APPLIED.json"],
        "dest": "archive/plans",
    },
]

ALREADY_DEST_PREFIXES = {"archive", "experiments", "tests/legacy"}


def _hash_file(p: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except Exception:
        return "0" * 16


def build_operations() -> list[dict]:
    ops = []
    for spec in PLANS:
        dest_val = spec.get("dest")
        if not isinstance(dest_val, str):
            continue
        dest_root = ROOT / dest_val
        paths = spec.get("paths")
        if not isinstance(paths, list):
            continue
        for rel in paths:
            src = ROOT / rel
            if not src.exists():
                continue
            # Skip if already in a destination bucket
            parts = src.relative_to(ROOT).parts
            if parts and parts[0] in ALREADY_DEST_PREFIXES:
                continue
            dest = dest_root / src.name
            ops.append(
                {
                    "category": spec.get("name"),
                    "src": str(src),
                    "dest": str(dest),
                    "src_hash": _hash_file(src) if src.is_file() else None,
                    "type": "dir" if src.is_dir() else "file",
                }
            )
    return ops


def _cleanup_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance" and capability in {
        "maintenance:cleanup",
        "fs:write",
        "fs:delete",
    }:
        return True
    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _op_path_hashes(ops: list[dict], key: str) -> tuple[str, ...]:
    values = []
    for op in ops:
        value = op.get(key)
        if value:
            values.append(hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16])
    return tuple(sorted(values))


def _guardian_preflight_apply(ops: list[dict], prune: bool) -> object:
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    categories = tuple(sorted({str(op.get("category") or "unknown") for op in ops}))
    op_types = tuple(sorted({str(op.get("type") or "unknown") for op in ops}))
    capabilities = ["maintenance:cleanup", "fs:write"]
    if prune:
        capabilities.append("fs:delete")

    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.root_cleanup",
            target="maintenance:root_cleanup",
            purpose="Apply root cleanup copy/move operations",
            capabilities=tuple(capabilities),
            expected_outcome="Cleanup operations are applied to approved archive destinations",
            reversible=not prune,
            rollback_plan=(
                "restore files from copied archive destinations before removing originals"
                if prune
                else "remove copied archive files if cleanup should be reverted"
            ),
            evidence=("tools.root_cleanup.apply_operations",),
            metadata={
                "operation_count": len(ops),
                "categories": categories,
                "operation_types": op_types,
                "prune_originals": bool(prune),
                "source_path_hashes": _op_path_hashes(ops, "src"),
                "destination_path_hashes": _op_path_hashes(ops, "dest"),
            },
        ),
        approval_id=approval_id,
        capability_checker=_cleanup_capability_checker,
    )


def apply_operations(ops: list[dict], prune: bool = False) -> tuple[int, list[dict]]:
    from Aetherra.guardian import GuardianStatus

    guardian_decision = _guardian_preflight_apply(ops, prune)
    if guardian_decision.status not in {
        GuardianStatus.ALLOW,
        GuardianStatus.ALLOW_LIMITED,
    }:
        return len(ops), [
            {
                **op,
                "status": f"guardian_denied:{guardian_decision.reason}",
                "guardian": guardian_decision.to_audit_dict(),
            }
            for op in ops
        ]

    failures = 0
    results = []
    for op in ops:
        src = Path(op["src"])
        dest = Path(op["dest"])
        status = "skipped"
        if not src.exists():
            status = "missing"
        else:
            try:
                if src.is_dir():
                    if not dest.exists():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(src, dest)
                        status = "copied"
                    else:
                        status = "exists"
                    # Even if dest exists from prior copy phase, honor prune by removing original now
                    if prune and src.exists():
                        try:
                            shutil.rmtree(src)
                            status = "moved"
                        except Exception as e:
                            status = f"prune_failed:{e.__class__.__name__}"
                            failures += 1
                else:
                    if not dest.exists():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dest)
                        status = "copied"
                    else:
                        status = "exists"
                    if prune and src.exists():
                        try:
                            src.unlink(missing_ok=True)  # type: ignore[arg-type]
                            status = "moved"
                        except Exception as e:
                            status = f"prune_failed:{e.__class__.__name__}"
                            failures += 1
            except Exception as e:
                status = f"error:{e.__class__.__name__}"
                failures += 1
        rec = {**op, "status": status}
        results.append(rec)
    return failures, results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true", help="Emit plan JSON and exit")
    ap.add_argument(
        "--apply", action="store_true", help="Execute copy (non-destructive)"
    )
    ap.add_argument(
        "--prune-originals",
        action="store_true",
        help="After copy remove originals (destructive)",
    )
    ap.add_argument("--output", help="Optional write journal to path")
    args = ap.parse_args()

    ops = build_operations()
    journal = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": str(ROOT),
        "count": len(ops),
        "ops": ops,
    }
    if args.plan and not args.apply:
        data = json.dumps(journal, indent=2)
        print(data)
        if args.output:
            Path(args.output).write_text(data, encoding="utf-8")
        return 0

    if args.apply:
        failures, results = apply_operations(ops, prune=args.prune_originals)
        journal["results"] = results
        journal["failures"] = failures
        data = json.dumps(journal, indent=2)
        print(data)
        if args.output:
            Path(args.output).write_text(data, encoding="utf-8")
        return 2 if failures else 0

    ap.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
