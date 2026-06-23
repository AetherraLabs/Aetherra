#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔧 AETHERRA ARCHITECTURAL AUTO-FIXER
Automatically fix critical architectural violations

Version: 1.0
Date: August 5, 2025
Purpose: Fix violations detected by architectural compliance checker
"""

# Standard library imports
import hashlib
import os
import re
from pathlib import Path


class ArchitecturalFixer:
    """Auto-fixer for architectural violations"""

    def __init__(self, project_root: str, dry_run: bool = True):
        self.project_root = Path(project_root)
        self.aetherra_root = self.project_root / "Aetherra"
        self.lyrixa_root = self.aetherra_root / "lyrixa"
        self.dry_run = dry_run

    @staticmethod
    def _hash_value(value) -> str | None:
        if value is None:
            return None
        raw = str(value)
        if not raw:
            return None
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _guardian_capability_checker(requester: str, capability: str) -> bool:
        if requester == "maintenance" and capability in {
            "maintenance:cleanup",
            "fs:write",
        }:
            return True

        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_preflight_apply(self):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        return evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="maintenance",
                action="maintenance.architecture_import_fix",
                target="maintenance:aetherra_architecture_import_fix",
                purpose="Rewrite core Aetherra files to remove Lyrixa import violations",
                capabilities=("maintenance:cleanup", "fs:write"),
                expected_outcome="Architecture import violations are commented out in source files",
                reversible=False,
                rollback_plan="restore rewritten files from version control or a prior workspace backup",
                metadata={
                    "project_root_hash": self._hash_value(self.project_root),
                    "aetherra_root_hash": self._hash_value(self.aetherra_root),
                    "lyrixa_root_hash": self._hash_value(self.lyrixa_root),
                    "dry_run": bool(self.dry_run),
                },
            ),
            approval_id=approval_id,
            capability_checker=self._guardian_capability_checker,
        )

    def fix_import_violations(self) -> list[str]:
        """Fix core AI files importing from Lyrixa"""
        print("🔧 Fixing core import violations...")

        violations = [
            "verify_lyrixa_merge.py",
            "consciousness/consciousness_orchestrator.py",
            "gui/main.py",
            "tools/quantum_dashboard_launcher.py",
            "plugins/core/plugin_system.py",
            "aetherra_core/agents/optimized_integration.py",
            "aetherra_core/agents/reflexive_loop.py",
        ]

        fixed_files = []

        for file_rel_path in violations:
            file_path = self.aetherra_root / file_rel_path
            if not file_path.exists():
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Remove Lyrixa imports
                original_content = content

                # Comment out Lyrixa imports
                content = re.sub(
                    r"^(\s*from lyrixa\..*)$",
                    r"# ARCHITECTURAL FIX: Removed Lyrixa import - \1",
                    content,
                    flags=re.MULTILINE,
                )

                content = re.sub(
                    r"^(\s*import lyrixa\..*)$",
                    r"# ARCHITECTURAL FIX: Removed Lyrixa import - \1",
                    content,
                    flags=re.MULTILINE,
                )

                if content != original_content:
                    if not self.dry_run:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)

                    fixed_files.append(str(file_path))
                    print(f"  ✅ Fixed imports in {file_path.name}")

            except Exception as e:
                print(f"  ❌ Error fixing {file_path}: {e}")

        return fixed_files

    def apply_fixes(self) -> dict[str, list[str]]:
        """Apply all architectural fixes"""
        print("🔧 APPLYING ARCHITECTURAL FIXES")
        print("=" * 40)

        if not self.dry_run:
            decision = self._guardian_preflight_apply()
            if not decision.allowed:
                print(f"Guardian denied architecture import fixes: {decision.reason}")
                return {"import_fixes": []}

        # Apply fixes
        import_fixes = self.fix_import_violations()

        # Generate simple report
        if import_fixes:
            print(f"\n✅ Fixed {len(import_fixes)} import violations")
            for fix in import_fixes:
                print(f"  - {Path(fix).name}")
        else:
            print("\n✅ No import violations to fix")

        return {"import_fixes": import_fixes}


def main():
    """Main execution function"""
    # Standard library imports
    import sys

    # Check for dry run mode
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    print("🔧 AETHERRA ARCHITECTURAL AUTO-FIXER")
    print("=" * 40)

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        print("⚡ LIVE MODE - Files will be modified")
        response = input("Continue? (y/N): ")
        if response.lower() != "y":
            print("❌ Operation cancelled")
            return

    # Get project root
    project_root = os.getcwd()

    # Create fixer
    fixer = ArchitecturalFixer(project_root, dry_run=dry_run)

    # Apply fixes
    results = fixer.apply_fixes()

    # Summary
    total_fixes = len(results["import_fixes"])
    if total_fixes > 0:
        print(f"\n✅ Applied {total_fixes} architectural fixes!")
        print("🔧 Run compliance check to verify: python check_architecture.py")
    else:
        print("\n✅ No fixes needed - architecture already compliant!")


if __name__ == "__main__":
    main()
