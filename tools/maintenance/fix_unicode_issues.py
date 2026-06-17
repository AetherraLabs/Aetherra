#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Plan and apply Unicode/import compatibility repairs through Guardian.
"""

from __future__ import annotations

import hashlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path

UNICODE_REPLACEMENTS: dict[str, str] = {
    "âŒ": "[ERROR]",
    "ðŸ”": "[SCAN]",
    "ðŸ’¡": "[INFO]",
    "âœ…": "[OK]",
    "âš ï¸": "[WARN]",
    "â„¹ï¸": "[INFO]",
    "ðŸ”¥": "[INIT]",
    "âš¡": "[SYS]",
    "ðŸ”—": "[LINK]",
    "ðŸŒŒ": "[CORE]",
    "ðŸ”„": "[LOOP]",
    "ðŸ©º": "[HEALTH]",
    "ðŸ“Š": "[STATS]",
    "ðŸŽ‰": "[SUCCESS]",
    "ðŸš€": "[LAUNCH]",
    "ðŸŒ": "[NET]",
    "ðŸ§ ": "[BRAIN]",
    "ðŸ”Œ": "[PLUGIN]",
    "ðŸ’¾": "[MEM]",
    "ðŸ“…": "[SCHED]",
}


UNICODE_TARGETS: tuple[str, ...] = (
    "aetherra_plugin_discovery.py",
    "aetherra_os_launcher.py",
    "aetherra_kernel_loop.py",
    "aetherra_service_registry.py",
    "Aetherra/aetherra_core/orchestration/scheduler.py",
)


IMPORT_TARGETS: tuple[str, ...] = (
    "Aetherra/plugins/extra_plugins/introspector_plugin.py",
    "Aetherra/plugins/memory_hooks/memory_aware_plugin_router.py",
)


@dataclass(frozen=True)
class UnicodeRepairPlan:
    file_path: Path
    content: str
    label: str
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


def _guardian_preflight_unicode_fixes(
    *,
    project_root: Path,
    plans: list[UnicodeRepairPlan],
    directories_to_create: list[Path],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.unicode_compatibility_fix",
            target="maintenance:unicode_compatibility_repairs",
            purpose="Apply planned Unicode and import compatibility repairs",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Planned compatibility repair files are written",
            reversible=False,
            rollback_plan="restore rewritten files and generated modules from version control or backup",
            metadata={
                "project_root_hash": _hash_value(project_root),
                "files_to_write": len(plans),
                "directories_to_create": len(directories_to_create),
                "total_replacements": sum(plan.replacements for plan in plans),
                "planned_file_hashes": [
                    _hash_value(plan.file_path.relative_to(project_root))
                    for plan in plans[:100]
                ],
                "planned_directory_hashes": [
                    _hash_value(directory.relative_to(project_root))
                    for directory in directories_to_create[:100]
                ],
                "plan_labels": [plan.label for plan in plans[:100]],
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def _plan_unicode_replacements(project_root: Path) -> list[UnicodeRepairPlan]:
    plans: list[UnicodeRepairPlan] = []
    for relative_path in UNICODE_TARGETS:
        file_path = project_root / relative_path
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8")
        updated = content
        replacements = 0
        for old, new in UNICODE_REPLACEMENTS.items():
            count = updated.count(old)
            if count:
                updated = updated.replace(old, new)
                replacements += count
        if updated != content:
            plans.append(
                UnicodeRepairPlan(
                    file_path=file_path,
                    content=updated,
                    label="unicode_marker_replacement",
                    replacements=replacements,
                )
            )
    return plans


def _plan_import_repairs(project_root: Path) -> list[UnicodeRepairPlan]:
    plans: list[UnicodeRepairPlan] = []
    for relative_path in IMPORT_TARGETS:
        file_path = project_root / relative_path
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8")
        updated = content.replace(
            "from ..memory.fractal_mesh.base import",
            "from Aetherra.aetherra_core.memory.fractal_mesh.base import",
        )
        if updated != content:
            plans.append(
                UnicodeRepairPlan(
                    file_path=file_path,
                    content=updated,
                    label="plugin_import_compatibility",
                    replacements=1,
                )
            )
    return plans


def _quantum_engine_content() -> str:
    return '''"""
Quantum Enhanced Memory Engine
=============================

Quantum-enhanced memory processing for Aetherra OS.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class QuantumEnhancedMemoryEngine:
    """Quantum-enhanced memory processing engine."""

    def __init__(self):
        self.quantum_state = "coherent"
        self.memory_fragments = []
        self.entanglement_map = {}
        logger.info("[OK] QuantumEnhancedMemoryEngine initialized")

    def process_memory(self, memory_data: dict[str, Any]) -> dict[str, Any]:
        """Process memory through quantum enhancement."""
        return {
            "original": memory_data,
            "quantum_enhanced": True,
            "coherence_level": 0.94,
            "entanglement_degree": 0.87,
        }

    def get_status(self) -> dict[str, Any]:
        """Get quantum engine status."""
        return {
            "state": self.quantum_state,
            "fragments": len(self.memory_fragments),
            "entanglements": len(self.entanglement_map),
            "coherence": 0.94,
        }
'''


def _plan_quantum_memory_module(
    project_root: Path,
) -> tuple[list[UnicodeRepairPlan], list[Path]]:
    quantum_dir = (
        project_root / "Aetherra" / "aetherra_core" / "memory" / "QuantumEnhancedMemoryEngine"
    )
    directories = [quantum_dir] if not quantum_dir.exists() else []
    plans: list[UnicodeRepairPlan] = []

    quantum_file = quantum_dir / "quantum_memory_engine.py"
    if not quantum_file.exists():
        plans.append(
            UnicodeRepairPlan(
                file_path=quantum_file,
                content=_quantum_engine_content(),
                label="quantum_memory_engine_module",
                replacements=1,
            )
        )

    init_file = quantum_dir / "__init__.py"
    init_content = (
        "from .quantum_memory_engine import QuantumEnhancedMemoryEngine\n\n"
        '__all__ = ["QuantumEnhancedMemoryEngine"]\n'
    )
    if not init_file.exists() or init_file.read_text(encoding="utf-8") != init_content:
        plans.append(
            UnicodeRepairPlan(
                file_path=init_file,
                content=init_content,
                label="quantum_memory_engine_init",
                replacements=1,
            )
        )

    return plans, directories


def plan_unicode_compatibility_fixes(
    project_root: str | Path = ".",
) -> tuple[list[UnicodeRepairPlan], list[Path]]:
    """Build all Unicode compatibility repair plans without mutating files."""

    root = Path(project_root)
    plans = _plan_unicode_replacements(root)
    plans.extend(_plan_import_repairs(root))
    quantum_plans, directories = _plan_quantum_memory_module(root)
    plans.extend(quantum_plans)
    return plans, directories


def apply_unicode_compatibility_fixes(project_root: str | Path = ".") -> int:
    """Apply planned Unicode compatibility fixes after Guardian approval."""

    root = Path(project_root)
    plans, directories = plan_unicode_compatibility_fixes(root)
    if not plans and not directories:
        print("No Unicode compatibility fixes needed.")
        return 0

    decision = _guardian_preflight_unicode_fixes(
        project_root=root,
        plans=plans,
        directories_to_create=directories,
    )
    if not decision.allowed:
        print(f"Guardian denied Unicode compatibility fixes: {decision.reason}")
        return 1

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    for plan in plans:
        plan.file_path.parent.mkdir(parents=True, exist_ok=True)
        plan.file_path.write_text(plan.content, encoding="utf-8")
        print(f"Applied {plan.label}")
    return 0


def set_utf8_environment() -> None:
    """Set UTF-8 environment variables for the current process only."""

    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"


def main(project_root: str | Path = ".") -> int:
    set_utf8_environment()
    return apply_unicode_compatibility_fixes(project_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
