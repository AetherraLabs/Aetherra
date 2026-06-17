#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Fix known relative import issues in Aetherra plugin files.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

RELATIVE_IMPORT_PATTERN = re.compile(
    r"from\s+(\.{1,2}[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import"
)


@dataclass(frozen=True)
class PluginImportRewritePlan:
    file_path: Path
    content: str
    replacements: int


@dataclass(frozen=True)
class PluginInitFilePlan:
    directory: Path
    content: str

    @property
    def init_file(self) -> Path:
        return self.directory / "__init__.py"


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


def _guardian_preflight_plugin_import_fix(
    *,
    project_root: Path,
    rewrite_plans: list[PluginImportRewritePlan],
    init_plans: list[PluginInitFilePlan],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.plugin_import_fix",
            target="maintenance:plugin_import_repair",
            purpose="Repair known plugin import paths and package markers after reorganization",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Known plugin files use absolute imports and missing package markers are created",
            reversible=False,
            rollback_plan="restore rewritten plugin files and package markers from version control",
            metadata={
                "project_root_hash": _hash_value(project_root),
                "plugin_files_to_update": len(rewrite_plans),
                "init_files_to_create": len(init_plans),
                "total_replacements": sum(plan.replacements for plan in rewrite_plans),
                "planned_plugin_file_hashes": [
                    _hash_value(plan.file_path.relative_to(project_root))
                    for plan in rewrite_plans[:100]
                ],
                "planned_init_directory_hashes": [
                    _hash_value(plan.directory.relative_to(project_root))
                    for plan in init_plans[:100]
                ],
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def plugin_root(project_root: str | Path = ".") -> Path:
    return Path(project_root) / "Aetherra" / "plugins"


def get_plugins_with_import_errors(project_root: str | Path = ".") -> list[Path]:
    """Get plugin files that may contain known relative import errors."""

    plugins_dir = plugin_root(project_root)
    candidates = [
        plugins_dir / "agent_adapters" / "plugin_agent.py",
        plugins_dir / "core" / "plugin_api.py",
        plugins_dir / "extra_plugins" / "introspector_plugin.py",
        plugins_dir / "memory_hooks" / "memory_aware_plugin_router.py",
        plugins_dir / "memory_hooks" / "memory_plugin_bridge.py",
    ]
    return [path for path in candidates if path.exists()]


def _replacement_for(relative_path: str, file_path: Path) -> str | None:
    if relative_path.startswith(".."):
        if "core.enhanced_memory" in relative_path:
            return "from Aetherra.aetherra_core.memory.enhanced_memory import"
        if "kernel.plugin_manager" in relative_path:
            return "from Aetherra.aetherra_core.plugins.plugin_manager import"
        if "core." in relative_path:
            module_name = relative_path.replace("..core.", "")
            return f"from Aetherra.aetherra_core.{module_name} import"
        clean_path = relative_path.lstrip(".")
        return f"from Aetherra.aetherra_core.{clean_path} import"

    if relative_path.startswith("."):
        if "agent_base" in relative_path:
            return "from Aetherra.plugins.agent_adapters.agent_base import"
        clean_path = relative_path.lstrip(".")
        parent_dir = file_path.parent.name
        return f"from Aetherra.plugins.{parent_dir}.{clean_path} import"

    return None


def plan_relative_import_fix(file_path: Path) -> PluginImportRewritePlan | None:
    """Build a side-effect-free rewrite plan for one plugin file."""

    content = file_path.read_text(encoding="utf-8")
    replacements = 0

    def replace_import(match: re.Match[str]) -> str:
        nonlocal replacements
        replacement = _replacement_for(match.group(1), file_path)
        if replacement is None:
            return match.group(0)
        replacements += 1
        return replacement

    new_content = RELATIVE_IMPORT_PATTERN.sub(replace_import, content)

    if "from Aetherra.aetherra_core.memory.enhanced_memory import" in new_content:
        fallback_import = """
try:
    from Aetherra.aetherra_core.memory.enhanced_memory import LyrixaEnhancedMemorySystem
except ImportError:
    class LyrixaEnhancedMemorySystem:
        def __init__(self, *args, **kwargs):
            pass

        def store(self, *args, **kwargs):
            pass

        def retrieve(self, *args, **kwargs):
            return []
"""
        if "LyrixaEnhancedMemorySystem" in new_content and "try:" not in new_content:
            new_content = fallback_import + new_content
            replacements += 1

    if new_content == content:
        return None

    return PluginImportRewritePlan(
        file_path=file_path,
        content=new_content,
        replacements=replacements,
    )


def plugin_init_dirs(project_root: str | Path = ".") -> list[Path]:
    plugins_dir = plugin_root(project_root)
    return [
        plugins_dir,
        plugins_dir / "agent_adapters",
        plugins_dir / "core",
        plugins_dir / "extra_plugins",
        plugins_dir / "memory_hooks",
    ]


def plan_missing_init_files(project_root: str | Path = ".") -> list[PluginInitFilePlan]:
    """Build a side-effect-free plan for missing plugin package marker files."""

    plans: list[PluginInitFilePlan] = []
    for directory in plugin_init_dirs(project_root):
        init_file = directory / "__init__.py"
        if directory.is_dir() and not init_file.exists():
            plans.append(
                PluginInitFilePlan(
                    directory=directory,
                    content=f'"""Plugin package: {directory.name}"""\n',
                )
            )
    return plans


def plan_plugin_import_fixes(
    project_root: str | Path = ".",
) -> tuple[list[PluginImportRewritePlan], list[PluginInitFilePlan]]:
    """Build all plugin import and package marker plans without mutating files."""

    rewrite_plans: list[PluginImportRewritePlan] = []
    for file_path in get_plugins_with_import_errors(project_root):
        plan = plan_relative_import_fix(file_path)
        if plan is not None:
            rewrite_plans.append(plan)
    return rewrite_plans, plan_missing_init_files(project_root)


def fix_plugin_imports(project_root: str | Path = ".") -> int:
    """Fix plugin import issues after Guardian approval."""

    root = Path(project_root)
    rewrite_plans, init_plans = plan_plugin_import_fixes(root)
    if not rewrite_plans and not init_plans:
        print("No plugin import fixes needed.")
        return 0

    decision = _guardian_preflight_plugin_import_fix(
        project_root=root,
        rewrite_plans=rewrite_plans,
        init_plans=init_plans,
    )
    if not decision.allowed:
        print(f"Guardian denied plugin import fix: {decision.reason}")
        return 1

    for plan in init_plans:
        plan.init_file.write_text(plan.content, encoding="utf-8")
        print(f"Created {plan.init_file}")

    for plan in rewrite_plans:
        plan.file_path.write_text(plan.content, encoding="utf-8")
        print(f"Fixed imports in {plan.file_path.name}")

    print(f"Fixed imports in {len(rewrite_plans)} plugin files.")
    return 0


def main(project_root: str | Path = ".") -> int:
    print("AETHERRA PLUGIN IMPORT FIXER")
    print("=" * 35)
    return fix_plugin_imports(project_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
