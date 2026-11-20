#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Apply remaining Phase 7.1 error fixes after Guardian approval.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FileRewritePlan:
    file_path: Path
    content: str
    replacements: int
    label: str


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


def _guardian_preflight_round2_fixes(
    *,
    project_root: Path,
    plans: list[FileRewritePlan],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.round_two_error_fix",
            target="maintenance:phase7_round2_error_fixes",
            purpose="Apply remaining Phase 7.1 GUI repair edits",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Planned Phase 7.1 GUI repair edits are written to selected files",
            reversible=False,
            rollback_plan="restore rewritten files from version control or backup",
            metadata={
                "project_root_hash": _hash_value(project_root),
                "files_to_update": len(plans),
                "total_replacements": sum(plan.replacements for plan in plans),
                "planned_file_hashes": [
                    _hash_value(plan.file_path.relative_to(project_root))
                    for plan in plans[:100]
                ],
                "plan_labels": [plan.label for plan in plans[:100]],
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def _plan_phase3_type_handling(project_root: Path) -> FileRewritePlan | None:
    file_path = project_root / "Aetherra" / "lyrixa" / "gui" / "phase3_auto_generator.py"
    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")
    updated = content
    replacements = 0

    substitutions = (
        (
            r"def _generate_plugin_panel\(self, component: ComponentState, template: str\) -> str:",
            "def _generate_plugin_panel(self, component, template: str) -> str:",
        ),
        (
            r"def _generate_agent_panel\(self, component: ComponentState, template: str\) -> str:",
            "def _generate_agent_panel(self, component, template: str) -> str:",
        ),
        (
            r"def _generate_memory_panel\(self, component: ComponentState, template: str\) -> str:",
            "def _generate_memory_panel(self, component, template: str) -> str:",
        ),
        (
            r"def _generate_service_panel\(self, component: ComponentState, template: str\) -> str:",
            "def _generate_service_panel(self, component, template: str) -> str:",
        ),
        (
            r"def _generate_metrics_panel\(self, component: ComponentState, template: str\) -> str:",
            "def _generate_metrics_panel(self, component, template: str) -> str:",
        ),
    )

    for pattern, replacement in substitutions:
        updated, count = re.subn(pattern, replacement, updated)
        replacements += count

    if "_safe_get_attr" not in updated:
        helper = '''
    def _safe_get_attr(self, component, attr_name, default=None):
        """Safely get attribute from component objects or dictionaries."""
        if isinstance(component, dict):
            return component.get(attr_name, default)
        return getattr(component, attr_name, default)
'''
        updated, count = re.subn(
            r'(class .*?:\s*""".*?"""\s*)',
            rf"\1{helper}\n    ",
            updated,
            count=1,
            flags=re.DOTALL,
        )
        replacements += count

    attr_substitutions = (
        (r"component\.capabilities", 'self._safe_get_attr(component, "capabilities", [])'),
        (r"component\.name", 'self._safe_get_attr(component, "name", "Unknown")'),
        (r"component\.status", 'self._safe_get_attr(component, "status", "unknown")'),
        (r"component\.metrics", 'self._safe_get_attr(component, "metrics", {})'),
        (
            r"component\.memory_stats",
            'self._safe_get_attr(component, "memory_stats", {})',
        ),
        (
            r"component\.active_memories",
            'self._safe_get_attr(component, "active_memories", [])',
        ),
        (
            r"component\.service_type",
            'self._safe_get_attr(component, "service_type", "unknown")',
        ),
        (r"component\.health", 'self._safe_get_attr(component, "health", "unknown")'),
    )
    for pattern, replacement in attr_substitutions:
        updated, count = re.subn(pattern, replacement, updated)
        replacements += count

    if updated == content:
        return None
    return FileRewritePlan(
        file_path=file_path,
        content=updated,
        replacements=replacements,
        label="phase3_auto_generator_type_handling",
    )


def plan_round2_fixes(project_root: str | Path = ".") -> list[FileRewritePlan]:
    """Build all Round 2 repair plans without mutating files."""

    root = Path(project_root)
    plans = [
        _plan_phase3_type_handling(root),
    ]
    return [plan for plan in plans if plan is not None]


def apply_round2_fixes(project_root: str | Path = ".") -> int:
    """Apply planned Round 2 fixes after Guardian approval."""

    root = Path(project_root)
    plans = plan_round2_fixes(root)
    if not plans:
        logger.info("No Round 2 error fixes needed.")
        return 0

    decision = _guardian_preflight_round2_fixes(project_root=root, plans=plans)
    if not decision.allowed:
        logger.error("Guardian denied Phase 7.1 Round 2 fixes: %s", decision.reason)
        return 1

    for plan in plans:
        plan.file_path.write_text(plan.content, encoding="utf-8")
        logger.info("Applied %s", plan.label)
    return 0


def main(project_root: str | Path = ".") -> int:
    return apply_round2_fixes(project_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
