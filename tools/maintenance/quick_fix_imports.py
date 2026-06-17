#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Create missing package markers for common Aetherra import paths.
"""

from __future__ import annotations

import hashlib
import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InitFilePlan:
    directory: Path
    package_name: str
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


def _guardian_preflight_init_creation(
    *,
    project_root: Path,
    plans: list[InitFilePlan],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.quick_import_init_fix",
            target="maintenance:quick_import_package_markers",
            purpose="Create missing package marker files for common Aetherra import paths",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Missing package marker files are created for existing package directories",
            reversible=False,
            rollback_plan="delete generated package marker files or restore from version control",
            metadata={
                "project_root_hash": _hash_value(project_root),
                "init_files_to_create": len(plans),
                "planned_directory_hashes": [
                    _hash_value(plan.directory.relative_to(project_root))
                    for plan in plans[:100]
                ],
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def check_python_version() -> bool:
    """Check if Python version is compatible."""

    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        print(f"Python 3.8+ required, found {version_info.major}.{version_info.minor}")
        return False

    print(
        f"Python {version_info.major}.{version_info.minor}.{version_info.micro} is compatible"
    )
    return True


def _init_file_content(package_name: str) -> str:
    return f'''#!/usr/bin/env python3
"""
{package_name} Package
{"=" * (len(package_name) + 8)}
Auto-generated __init__.py file for Aetherra AI OS.
"""

__version__ = "1.0.0"

PACKAGE_AVAILABLE = True


def get_package_status():
    """Get the status of this package."""
    return {{"available": PACKAGE_AVAILABLE}}


__all__ = ["get_package_status", "PACKAGE_AVAILABLE"]
'''


def important_package_dirs(project_root: str | Path = ".") -> list[tuple[Path, str]]:
    """Return existing directories that quick import repair can mark as packages."""

    aetherra_dir = Path(project_root) / "Aetherra"
    return [
        (aetherra_dir / "aetherra_core", "Aetherra Core"),
        (aetherra_dir / "aetherra_core" / "engine", "Engine"),
        (aetherra_dir / "aetherra_core" / "orchestration", "Orchestration"),
        (aetherra_dir / "aetherra_core" / "plugins", "Plugins"),
        (aetherra_dir / "aetherra_core" / "memory", "Memory"),
        (aetherra_dir / "aetherra_core" / "system", "System"),
        (aetherra_dir / "aetherra_core" / "kernel", "Kernel"),
        (aetherra_dir / "aetherra_core" / "file_system", "File System"),
        (aetherra_dir / "aetherra_core" / "reflection", "Reflection"),
        (aetherra_dir / "aetherra_core" / "reflection_engine", "Reflection Engine"),
        (aetherra_dir / "core", "Core"),
        (aetherra_dir / "plugins", "Plugins"),
        (aetherra_dir / "runtime", "Runtime"),
    ]


def plan_missing_inits(project_root: str | Path = ".") -> list[InitFilePlan]:
    """Build a side-effect-free plan for missing package marker files."""

    plans: list[InitFilePlan] = []
    for directory, package_name in important_package_dirs(project_root):
        init_file = directory / "__init__.py"
        if directory.is_dir() and not init_file.exists():
            plans.append(
                InitFilePlan(
                    directory=directory,
                    package_name=package_name,
                    content=_init_file_content(package_name),
                )
            )
    return plans


def create_init_file(plan: InitFilePlan) -> bool:
    """Create one planned package marker file."""

    if plan.init_file.exists():
        return True

    plan.init_file.write_text(plan.content, encoding="utf-8")
    print(f"Created __init__.py in {plan.directory.name}")
    return True


def fix_missing_inits(project_root: str | Path = ".") -> bool:
    """Fix missing __init__.py files after Guardian approval."""

    root = Path(project_root)
    aetherra_dir = root / "Aetherra"
    if not aetherra_dir.exists():
        print("Aetherra directory not found.")
        return False

    plans = plan_missing_inits(root)
    if not plans:
        print("No missing __init__.py files found.")
        return True

    decision = _guardian_preflight_init_creation(project_root=root, plans=plans)
    if not decision.allowed:
        print(f"Guardian denied quick import init fix: {decision.reason}")
        return False

    for plan in plans:
        create_init_file(plan)

    print(f"Created {len(plans)} missing __init__.py files")
    return True


def test_basic_imports() -> int:
    """Test basic import patterns."""

    tests = [
        ("aetherra_core", "Aetherra.aetherra_core", "get_package_status"),
        ("kernel_loop", "aetherra_kernel_loop", "AetherraKernelLoop"),
        ("os_launcher", "aetherra_os_launcher", None),
    ]

    passed = 0
    for name, module_name, attr_name in tests:
        try:
            module = importlib.import_module(module_name)
            if attr_name is not None:
                getattr(module, attr_name)
            print(f"{name} import succeeded")
            passed += 1
        except Exception as exc:  # noqa: BLE001 - tooling-only status reporting
            print(f"{name} import failed: {exc}")

    return passed


def main(project_root: str | Path = ".") -> int:
    """Run quick import repair."""

    print("Aetherra Quick Import Fix")
    print("=" * 40)

    if not check_python_version():
        return 1

    if not fix_missing_inits(project_root):
        return 1

    passed = test_basic_imports()

    print()
    print("=" * 40)
    print(f"Quick fix completed. {passed} imports working.")
    print()
    print("If import issues remain:")
    print("1. Run the full fix: python fix_imports.py")
    print("2. Check the guide: IMPORT_FIXES.md")
    print("3. Verify your setup: python test_imports.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
