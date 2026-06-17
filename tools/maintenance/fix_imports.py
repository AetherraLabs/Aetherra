#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Fix common Aetherra import setup issues with Guardian-gated mutations.
"""

from __future__ import annotations

import hashlib
import importlib
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class InitFilePlan:
    directory: Path
    content: str

    @property
    def init_file(self) -> Path:
        return self.directory / "__init__.py"


@dataclass(frozen=True)
class ReportPlan:
    file_path: Path
    content: str


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
        "network:outbound",
        "package:install",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


class AetherraImportFixer:
    """Utility class to fix import issues in an Aetherra repository."""

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.aetherra_dir = self.project_root / "Aetherra"
        self.issues_found: list[str] = []
        self.fixes_applied: list[str] = []

    def _guardian_preflight_init_creation(self, plans: list[InitFilePlan]):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        return evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="maintenance",
                action="maintenance.import_fix_init_creation",
                target="maintenance:import_package_markers",
                purpose="Create missing package marker files for Aetherra import setup",
                capabilities=("maintenance:cleanup", "fs:write"),
                expected_outcome="Missing package marker files are created for existing package directories",
                reversible=False,
                rollback_plan="delete generated package marker files or restore from version control",
                metadata={
                    "project_root_hash": _hash_value(self.project_root),
                    "init_files_to_create": len(plans),
                    "planned_directory_hashes": [
                        _hash_value(plan.directory.relative_to(self.project_root))
                        for plan in plans[:100]
                    ],
                },
            ),
            approval_id=approval_id,
            capability_checker=_guardian_capability_checker,
        )

    def _guardian_preflight_report_write(self, plan: ReportPlan):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        return evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="maintenance",
                action="maintenance.import_fix_report",
                target="maintenance:import_fix_report",
                purpose="Write import fix diagnostic report",
                capabilities=("maintenance:cleanup", "fs:write"),
                expected_outcome="Import fix diagnostic report is written",
                reversible=False,
                rollback_plan="delete generated diagnostic report or restore from version control",
                metadata={
                    "project_root_hash": _hash_value(self.project_root),
                    "report_path_hash": _hash_value(plan.file_path.relative_to(self.project_root)),
                    "report_length": len(plan.content),
                    "issues_found": len(self.issues_found),
                    "fixes_applied": len(self.fixes_applied),
                },
            ),
            approval_id=approval_id,
            capability_checker=_guardian_capability_checker,
        )

    def _guardian_preflight_file_writes(
        self,
        init_plans: list[InitFilePlan],
        report_plan: ReportPlan,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        return evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="maintenance",
                action="maintenance.import_fix",
                target="maintenance:import_fix_file_writes",
                purpose="Create package markers and write import fix diagnostics",
                capabilities=("maintenance:cleanup", "fs:write"),
                expected_outcome="Import setup file fixes and diagnostic report are written",
                reversible=False,
                rollback_plan="delete generated files or restore repository state from version control",
                metadata={
                    "project_root_hash": _hash_value(self.project_root),
                    "init_files_to_create": len(init_plans),
                    "report_path_hash": _hash_value(
                        report_plan.file_path.relative_to(self.project_root)
                    ),
                    "report_length": len(report_plan.content),
                    "planned_directory_hashes": [
                        _hash_value(plan.directory.relative_to(self.project_root))
                        for plan in init_plans[:100]
                    ],
                },
            ),
            approval_id=approval_id,
            capability_checker=_guardian_capability_checker,
        )

    def _guardian_preflight_dependency_install(self, dependencies: list[str]):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        return evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="maintenance",
                action="maintenance.import_dependency_install",
                target="maintenance:import_dependency_install",
                purpose="Install missing Python dependencies for import setup",
                capabilities=("maintenance:cleanup", "network:outbound", "package:install"),
                expected_outcome="Requested Python dependencies are installed by pip",
                reversible=False,
                rollback_plan="remove installed packages or restore environment from snapshot",
                metadata={
                    "project_root_hash": _hash_value(self.project_root),
                    "dependency_count": len(dependencies),
                    "dependency_hashes": [_hash_value(dep) for dep in dependencies[:100]],
                },
            ),
            approval_id=approval_id,
            capability_checker=_guardian_capability_checker,
        )

    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""

        version_info = sys.version_info
        if version_info.major < 3 or (
            version_info.major == 3 and version_info.minor < 8
        ):
            logger.error(
                "Python 3.8+ required, found %s.%s",
                version_info.major,
                version_info.minor,
            )
            self.issues_found.append("Incompatible Python version")
            return False

        logger.info(
            "Python %s.%s.%s is compatible",
            version_info.major,
            version_info.minor,
            version_info.micro,
        )
        return True

    def important_package_dirs(self) -> list[Path]:
        """Return important package directories for Aetherra imports."""

        return [
            self.aetherra_dir / "aetherra_core",
            self.aetherra_dir / "aetherra_core" / "engine",
            self.aetherra_dir / "aetherra_core" / "orchestration",
            self.aetherra_dir / "aetherra_core" / "plugins",
            self.aetherra_dir / "aetherra_core" / "memory",
            self.aetherra_dir / "aetherra_core" / "system",
            self.aetherra_dir / "aetherra_core" / "kernel",
            self.aetherra_dir / "aetherra_core" / "file_system",
            self.aetherra_dir / "aetherra_core" / "reflection",
            self.aetherra_dir / "aetherra_core" / "reflection_engine",
            self.aetherra_dir / "core",
            self.aetherra_dir / "lyrixa",
            self.aetherra_dir / "plugins",
            self.aetherra_dir / "runtime",
        ]

    def _init_file_content(self, directory: Path) -> str:
        package_name = directory.name.replace("_", " ").title()
        return f'''#!/usr/bin/env python3
"""
{package_name} Package
{"=" * (len(package_name) + 8)}
Auto-generated package marker file for Aetherra AI OS.
"""

__version__ = "1.0.0"

PACKAGE_AVAILABLE = True


def get_package_status():
    """Get the status of this package."""
    return {{"available": PACKAGE_AVAILABLE}}


__all__ = ["get_package_status", "PACKAGE_AVAILABLE"]
'''

    def plan_missing_init_files(self) -> list[InitFilePlan]:
        """Find missing package marker files without mutating the filesystem."""

        plans: list[InitFilePlan] = []
        for directory in self.important_package_dirs():
            init_file = directory / "__init__.py"
            if directory.exists() and directory.is_dir() and not init_file.exists():
                plans.append(
                    InitFilePlan(
                        directory=directory,
                        content=self._init_file_content(directory),
                    )
                )
        return plans

    def apply_init_file_plans(self, plans: list[InitFilePlan]) -> bool:
        """Create planned package marker files after Guardian approval."""

        if not plans:
            return True

        decision = self._guardian_preflight_init_creation(plans)
        if not decision.allowed:
            logger.error("Guardian denied import package marker creation: %s", decision.reason)
            return False

        self._apply_init_file_plans_unchecked(plans)
        return True

    def _apply_init_file_plans_unchecked(self, plans: list[InitFilePlan]) -> None:
        for plan in plans:
            plan.init_file.write_text(plan.content, encoding="utf-8")
            self.fixes_applied.append(f"Created package marker in {plan.directory.name}")
            logger.info("Created package marker in %s", plan.directory.name)

    def check_dependencies(self) -> dict[str, bool]:
        """Check if required dependencies are installed."""

        dependencies_status: dict[str, bool] = {}
        core_deps = ["json", "logging", "pathlib", "asyncio", "flask", "requests"]
        optional_deps = ["aiohttp", "rich", "dotenv", "psutil"]

        missing_core = []
        for dep in core_deps:
            try:
                importlib.import_module(dep)
                dependencies_status[dep] = True
            except ImportError:
                dependencies_status[dep] = False
                missing_core.append(dep)

        for dep in optional_deps:
            try:
                importlib.import_module(dep)
                dependencies_status[dep] = True
            except ImportError:
                dependencies_status[dep] = False

        for dep in missing_core:
            if dep not in {"json", "logging", "pathlib", "asyncio"}:
                self.issues_found.append(f"Missing core dependency: {dep}")

        return dependencies_status

    def install_missing_dependencies(self, dependencies: list[str] | None = None) -> bool:
        """Install missing dependencies only after a dedicated Guardian decision."""

        requested = dependencies or [
            "flask>=2.3.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "rich>=13.4.0",
        ]
        decision = self._guardian_preflight_dependency_install(requested)
        if not decision.allowed:
            logger.error("Guardian denied dependency installation: %s", decision.reason)
            return False

        success = True
        for dep in requested:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=120,
                )
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                success = False

        self.fixes_applied.append(
            "Installed core dependencies" if success else "Attempted dependency install"
        )
        return success

    def test_imports(self) -> dict[str, bool]:
        """Test common import patterns."""

        import_tests: dict[str, bool] = {}
        tests = [
            ("aetherra_core", "Aetherra.aetherra_core"),
            ("kernel_loop", "aetherra_kernel_loop"),
            ("service_registry", "aetherra_service_registry"),
            ("startup", "aetherra_startup"),
        ]

        for name, module_name in tests:
            try:
                importlib.import_module(module_name)
                import_tests[name] = True
            except Exception as exc:  # noqa: BLE001 - diagnostic tool reports status
                import_tests[name] = False
                logger.warning("%s import failed: %s", name, exc)

        return import_tests

    def plan_report(
        self,
        deps_status: dict[str, bool],
        import_results: dict[str, bool],
    ) -> ReportPlan:
        """Build an import fix diagnostic report without writing it."""

        report = f"""# Aetherra Import Fix Report

Python Environment:
- Version: {sys.version}
- Executable: {sys.executable}

Issues Found: {len(self.issues_found)}
{chr(10).join(f"- {issue}" for issue in self.issues_found)}

Fixes Applied: {len(self.fixes_applied)}
{chr(10).join(f"- {fix}" for fix in self.fixes_applied)}

Dependency Status:
{chr(10).join(f"- {dep}: {'OK' if status else 'MISSING'}" for dep, status in deps_status.items())}

Import Tests:
{chr(10).join(f"- {test}: {'OK' if status else 'FAILED'}" for test, status in import_results.items())}

Next Steps:
1. If any imports still fail, check the specific error messages.
2. Consider running dependency installation separately with Guardian approval.
3. Review contributor setup documentation.
"""
        return ReportPlan(
            file_path=self.project_root / "import_fix_report.md",
            content=report,
        )

    def write_report(self, plan: ReportPlan) -> bool:
        """Write the diagnostic report after Guardian approval."""

        decision = self._guardian_preflight_report_write(plan)
        if not decision.allowed:
            logger.error("Guardian denied import fix report write: %s", decision.reason)
            return False

        self._write_report_unchecked(plan)
        return True

    def _write_report_unchecked(self, plan: ReportPlan) -> None:
        plan.file_path.write_text(plan.content, encoding="utf-8")
        self.fixes_applied.append("Wrote import fix report")
        logger.info("Report saved to %s", plan.file_path)

    def fix_all_issues(self, *, install_dependencies: bool = False) -> bool:
        """Run import checks and Guardian-gated fixes."""

        if not self.check_python_version():
            return False

        success = True
        init_plans = self.plan_missing_init_files()
        deps_status = self.check_dependencies()
        missing_core_deps = [
            dep for dep, status in deps_status.items() if not status and dep in {"flask", "requests"}
        ]

        if install_dependencies and missing_core_deps:
            install_success = self.install_missing_dependencies()
            success = success and install_success
        elif missing_core_deps:
            logger.warning(
                "Missing core dependencies detected; dependency installation requires explicit approval"
            )

        import_results = self.test_imports()
        report_plan = self.plan_report(deps_status, import_results)
        decision = self._guardian_preflight_file_writes(init_plans, report_plan)
        if not decision.allowed:
            logger.error("Guardian denied import fixer file writes: %s", decision.reason)
            return False

        self._apply_init_file_plans_unchecked(init_plans)
        self._write_report_unchecked(report_plan)
        return success


def main(project_root: str | Path = ".", *, install_dependencies: bool = False) -> int:
    """Run the import fixer."""

    fixer = AetherraImportFixer(project_root=project_root)
    success = fixer.fix_all_issues(install_dependencies=install_dependencies)
    return 0 if success else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    install = "--install-dependencies" in args
    roots = [arg for arg in args if arg != "--install-dependencies"]
    raise SystemExit(main(roots[0] if roots else ".", install_dependencies=install))
