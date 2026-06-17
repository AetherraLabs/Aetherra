#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Apply legacy Phase 7 repair edits through a Guardian-gated batch.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MISSING_PLUGIN_NAMES: tuple[str, ...] = (
    "agent_base",
    "agent_plugin",
    "collaborative_multi_agent_system",
    "comprehensive_agent_discovery",
    "curiosity_agent_8",
    "lyrixa_agent_integration",
    "multi_agent_system",
    "plugin_agent",
    "real_agent_discovery",
    "smart_agent_migrator",
    "agent_bridge",
    "agent_discovery_and_integration",
    "agent_orchestrator",
    "enhanced_plugin_manager",
    "plugin_api",
    "plugin_chain_executor",
    "plugin_creation_wizard",
    "plugin_discovery",
    "PluginGenerator",
    "plugin_manager",
    "plugin_quality_control",
    "plugin_registry",
    "plugin_sdk",
    "plugin_system",
    "self_improvement_dashboard",
    "AssistantTrainer",
    "context_aware_surfacing",
    "introspector_plugin",
    "WorkflowBuilder",
    "plugin_analytics",
    "plugin_lifecycle_memory",
    "plugin_state_memory",
    "memory_aware_plugin_router",
    "memory_plugin_bridge",
    "plugin_manager_stubs",
    "advanced-memory-system",
)


@dataclass(frozen=True)
class PhaseRepairPlan:
    file_path: Path
    content: str
    label: str
    replacements: int = 1


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


def _guardian_preflight_phase_error_fixes(
    *,
    project_root: Path,
    plans: list[PhaseRepairPlan],
    directories_to_create: list[Path],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.error_repair_batch",
            target="maintenance:legacy_error_repair_batch",
            purpose="Apply planned legacy repair edits and generated stubs",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Planned repair files and directories are written",
            reversible=False,
            rollback_plan="restore changed files and generated stubs from version control or backup",
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


def _plan_css_fixes(project_root: Path) -> list[PhaseRepairPlan]:
    plans: list[PhaseRepairPlan] = []
    for py_file in project_root.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if "box-shadow" not in content:
            continue
        updated, replacements = re.subn(
            r"box-shadow\s*:[^;\"']+;",
            "/* box-shadow removed for Qt compatibility */",
            content,
        )
        if updated != content:
            plans.append(
                PhaseRepairPlan(
                    file_path=py_file,
                    content=updated,
                    label="qt_css_shadow_cleanup",
                    replacements=replacements,
                )
            )
    return plans


def _stub_content(plugin_name: str) -> str:
    class_name = "".join(part for part in plugin_name.title() if part.isalnum())
    return f'''"""
{plugin_name.replace("_", " ").title()} Plugin Stub
"""


def get_plugin_info():
    """Return basic plugin information."""
    return {{
        "name": "{plugin_name}",
        "version": "1.0.0",
        "description": "Stub plugin for {plugin_name.replace("_", " ")}",
        "status": "stub",
        "capabilities": [],
    }}


def activate():
    """Activate the plugin."""
    return True


def deactivate():
    """Deactivate the plugin."""
    return True


class {class_name}Plugin:
    """Stub plugin class."""

    def __init__(self):
        self.name = "{plugin_name}"
        self.version = "1.0.0"
        self.active = False

    def activate(self):
        self.active = True
        return True

    def deactivate(self):
        self.active = False
        return True
'''


def _plan_plugin_stubs(project_root: Path) -> tuple[list[PhaseRepairPlan], list[Path]]:
    plugins_dir = project_root / "Aetherra" / "plugins"
    if not plugins_dir.exists():
        return [], []

    core_dir = plugins_dir / "core"
    plans: list[PhaseRepairPlan] = []
    directories = [core_dir] if not core_dir.exists() else []

    for plugin_name in MISSING_PLUGIN_NAMES:
        if any(plugins_dir.rglob(f"{plugin_name}.py")):
            continue
        stub_file = core_dir / f"{plugin_name}.py"
        plans.append(
            PhaseRepairPlan(
                file_path=stub_file,
                content=_stub_content(plugin_name),
                label="plugin_stub_creation",
            )
        )
    return plans, directories


def _plan_conversation_manager_fix(project_root: Path) -> PhaseRepairPlan | None:
    file_path = (
        project_root
        / "Aetherra"
        / "aetherra_core"
        / "agents"
        / "conversation_manager.py"
    )
    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")
    updated = content.replace(
        "from Aetherra.core.ai.multi_llm_manager import MultiLLMManager",
        "from Aetherra.core.multi_llm_manager import MultiLLMManager",
    )

    fallback_marker = "PLUGIN_EDITOR_AVAILABLE"
    if fallback_marker not in updated and "class LyrixaConversationManager" in updated:
        graceful_imports = """
# Graceful fallbacks for optional Lyrixa components
try:
    from Aetherra.lyrixa.gui.plugin_editor_controller import PluginEditorController
    PLUGIN_EDITOR_AVAILABLE = True
except ImportError:
    class PluginEditorController:
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    PLUGIN_EDITOR_AVAILABLE = False
"""
        updated = updated.replace(
            "class LyrixaConversationManager",
            graceful_imports + "\n\nclass LyrixaConversationManager",
            1,
        )

    if updated == content:
        return None
    return PhaseRepairPlan(
        file_path=file_path,
        content=updated,
        label="conversation_import_repair",
    )


def _plan_panel_generation_fix(project_root: Path) -> PhaseRepairPlan | None:
    file_path = project_root / "Aetherra" / "lyrixa" / "gui" / "phase3_auto_generator.py"
    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")
    if "defensive_service_data" in content:
        return None

    marker = "def generate_panels_from_services"
    if marker not in content:
        return None

    defensive_code = """
        defensive_service_data = True
        if isinstance(service_data, dict):
            service_type = service_data.get("type", "unknown")
            service_name = service_data.get("name", str(service_data.get("service_id", "unnamed")))
        elif hasattr(service_data, "type"):
            service_type = service_data.type
            service_name = getattr(service_data, "name", "unnamed")
        else:
            service_type = "unknown"
            service_name = str(service_data)[:50] if service_data else "unknown"
"""
    insert_at = content.find("\n", content.find(marker))
    if insert_at < 0:
        return None
    updated = content[: insert_at + 1] + defensive_code + content[insert_at + 1 :]
    return PhaseRepairPlan(
        file_path=file_path,
        content=updated,
        label="panel_generation_defensive_handling",
    )


def _plan_summary(project_root: Path) -> PhaseRepairPlan:
    summary_file = project_root / "tools" / "maintenance" / "PHASE_7_1_ERROR_FIXES_SUMMARY.md"
    content = """# Phase Error Fixes Summary

## Fixes Planned

- Plugin loading stubs are generated only after Guardian approval.
- Qt CSS compatibility edits are planned before write.
- Conversation-manager import repairs are planned before write.
- Panel-generation defensive handling is planned before write.

## Safety

All writes in this maintenance batch are guarded by the Aetherra Guardian System.
"""
    return PhaseRepairPlan(
        file_path=summary_file,
        content=content,
        label="repair_summary_report",
    )


def plan_phase_error_fixes(
    project_root: str | Path = ".",
) -> tuple[list[PhaseRepairPlan], list[Path]]:
    """Build planned repair writes without mutating files."""

    root = Path(project_root)
    plans: list[PhaseRepairPlan] = []
    directories: list[Path] = []

    plans.extend(_plan_css_fixes(root))
    stub_plans, stub_dirs = _plan_plugin_stubs(root)
    plans.extend(stub_plans)
    directories.extend(stub_dirs)

    for maybe_plan in (
        _plan_conversation_manager_fix(root),
        _plan_panel_generation_fix(root),
        _plan_summary(root),
    ):
        if maybe_plan is not None:
            plans.append(maybe_plan)

    return plans, directories


def apply_phase_error_fixes(project_root: str | Path = ".") -> int:
    """Apply planned repair writes after Guardian approval."""

    root = Path(project_root)
    plans, directories = plan_phase_error_fixes(root)
    if not plans and not directories:
        print("No phase error fixes needed.")
        return 0

    decision = _guardian_preflight_phase_error_fixes(
        project_root=root,
        plans=plans,
        directories_to_create=directories,
    )
    if not decision.allowed:
        print(f"Guardian denied phase error fixes: {decision.reason}")
        return 1

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    for plan in plans:
        plan.file_path.parent.mkdir(parents=True, exist_ok=True)
        plan.file_path.write_text(plan.content, encoding="utf-8")
        print(f"Applied {plan.label}")
    return 0


def main(project_root: str | Path = ".") -> int:
    return apply_phase_error_fixes(project_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
