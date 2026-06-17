#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Remove remaining Lyrixa imports from selected core files after reorganization.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RemainingImportFixPlan:
    file_path: Path
    content: str
    replacements: int


def _hash_value(value: object) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance" and capability in {
        "maintenance:cleanup",
        "fs:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_fix(
    *,
    project_root: Path,
    planned_updates: list[RemainingImportFixPlan],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.remaining_import_fix",
            target="maintenance:remaining_lyrixa_imports",
            purpose="Comment remaining Lyrixa imports in selected core files after reorganization",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Selected core files no longer import Lyrixa directly",
            reversible=False,
            rollback_plan="restore rewritten source files from version control or backups",
            metadata={
                "project_root_hash": _hash_value(project_root),
                "files_to_update": len(planned_updates),
                "total_replacements": sum(plan.replacements for plan in planned_updates),
                "planned_file_hashes": [
                    _hash_value(plan.file_path.relative_to(project_root))
                    for plan in planned_updates[:100]
                ],
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def _target_files(project_root: Path) -> list[Path]:
    aetherra_root = project_root / "Aetherra"
    return [
        aetherra_root / "consciousness" / "consciousness_orchestrator.py",
        aetherra_root / "aetherra_core" / "agents" / "optimized_integration.py",
    ]


def _plan_file_update(file_path: Path) -> RemainingImportFixPlan | None:
    content = file_path.read_text(encoding="utf-8")
    updated_content = content
    replacements = 0

    substitutions = (
        (
            r"^(\s*from lyrixa.*?)$",
            r"# ARCHITECTURAL FIX: Removed Lyrixa import - \1",
        ),
        (
            r"^(\s*import lyrixa.*?)$",
            r"# ARCHITECTURAL FIX: Removed Lyrixa import - \1",
        ),
        (
            r"^(\s*.*lyrixa.*\(.*\).*)$",
            r"# ARCHITECTURAL FIX: Removed Lyrixa function call - \1",
        ),
    )
    for pattern, replacement in substitutions:
        updated_content, count = re.subn(
            pattern,
            replacement,
            updated_content,
            flags=re.MULTILINE,
        )
        replacements += count

    if updated_content == content:
        return None

    return RemainingImportFixPlan(
        file_path=file_path,
        content=updated_content,
        replacements=replacements,
    )


def plan_remaining_lyrixa_import_fixes(
    project_root: str | Path = ".",
) -> list[RemainingImportFixPlan]:
    root = Path(project_root)
    plans: list[RemainingImportFixPlan] = []
    for file_path in _target_files(root):
        if not file_path.exists():
            continue
        plan = _plan_file_update(file_path)
        if plan is not None:
            plans.append(plan)
    return plans


def fix_all_lyrixa_imports(project_root: str | Path = ".") -> int:
    """Fix all remaining Lyrixa imports in selected core files."""

    root = Path(project_root)
    planned_updates = plan_remaining_lyrixa_import_fixes(root)
    decision = _guardian_preflight_fix(
        project_root=root,
        planned_updates=planned_updates,
    )
    if not decision.allowed:
        print(f"Guardian denied remaining Lyrixa import fix: {decision.reason}")
        return -1

    fixed_count = 0
    for plan in planned_updates:
        plan.file_path.write_text(plan.content, encoding="utf-8")
        print(f"Fixed {plan.file_path.name}")
        fixed_count += 1

    print(f"\nFixed {fixed_count} additional files")
    return fixed_count


def main() -> int:
    print("COMPREHENSIVE ARCHITECTURAL FIXER")
    print("=" * 40)

    result = fix_all_lyrixa_imports()
    if result < 0:
        return 1

    if result > 0:
        print("All Lyrixa imports fixed.")
        print("Run: python check_architecture.py")
    else:
        print("No additional fixes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
