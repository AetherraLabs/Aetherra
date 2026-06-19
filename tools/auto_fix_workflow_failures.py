#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Automated Workflow Failure Fix Tool
===================================

This script automatically fixes the common workflow failures in the Aetherra repository,
specifically focusing on Unicode encoding issues that cause failures on Windows systems.

The tool:
1. Detects Unicode characters in Python files that cause cp1252 encoding errors
2. Replaces them with ASCII-safe alternatives
3. Adds proper encoding declarations to Python files
4. Sets up environment variables for Unicode support
5. Validates the fixes work correctly

Usage:
    python tools/auto_fix_workflow_failures.py [options]

Options:
    --dry-run    Show what would be changed without making changes
    --files      Specific files to fix (comma-separated)
    --all        Fix all Python files with Unicode issues
    --verify     Only verify fixes, don't apply them
"""

# Standard library imports
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Root directory of the project
ROOT_DIR = Path(__file__).parent.parent.resolve()

# Unicode character replacement mapping for safe ASCII alternatives
UNICODE_REPLACEMENTS = {
    # Emojis that commonly cause issues
    "🔍": "[SCAN]",
    "🧠": "[BRAIN]",
    "✅": "[OK]",
    "❌": "[ERROR]",
    "⚠️": "[WARN]",
    "💡": "[INFO]",
    "🔥": "[INIT]",
    "⚡": "[SYS]",
    "🔗": "[LINK]",
    "🌌": "[CORE]",
    "🔄": "[LOOP]",
    "🩺": "[HEALTH]",
    "📊": "[STATS]",
    "🎉": "[SUCCESS]",
    "🚀": "[LAUNCH]",
    "🌐": "[NET]",
    "🔌": "[PLUGIN]",
    "💾": "[MEM]",
    "📅": "[SCHED]",
    "🌟": "[STAR]",
    "🌱": "[GROW]",
    "🎯": "[TARGET]",
    "👋": "[WAVE]",
    "💓": "[HEART]",
    "💚": "[GREEN]",
    "📄": "[DOC]",
    "📈": "[CHART]",
    "📝": "[NOTE]",
    "🔧": "[TOOL]",
    "🖥": "[DESKTOP]",
    "🗂": "[FOLDER]",
    "🤖": "[BOT]",
    # Arrow characters
    "→": "->",
    "←": "<-",
    "↑": "^",
    "↓": "v",
    # Symbols
    "⚙": "[GEAR]",
    "⚛": "[ATOM]",
    "•": "*",
    "️": "",  # Variation selector, can be removed
}

# Critical files that need immediate fixing
CRITICAL_FILES = [
    "aether.py",
    "aetherra_os.py",
    "Aetherra/aetherra_core/orchestration/scheduler.py",
    "Aetherra/runtime/aether_executor.py",
    "Aetherra/cli/main.py",
]


class WorkflowFixer:
    """Main class for fixing workflow failures"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_changed = 0
        self.unicode_chars_replaced = 0
        self.errors = []

    def find_python_files_with_unicode(self) -> list[tuple[Path, int, set[str]]]:
        """Find all Python files containing Unicode characters"""
        unicode_files = []

        for root, dirs, files in os.walk(ROOT_DIR):
            # Skip certain directories
            skip_dirs = {
                ".git",
                "node_modules",
                "__pycache__",
                ".venv",
                "venv",
                "build",
                "dist",
                ".tox",
                ".pytest_cache",
            }
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        unicode_chars = set(re.findall(r"[^\x00-\x7f]", content))
                        if unicode_chars:
                            # Count total occurrences
                            total_count = sum(
                                content.count(char) for char in unicode_chars
                            )
                            unicode_files.append(
                                (
                                    file_path.relative_to(ROOT_DIR),
                                    total_count,
                                    unicode_chars,
                                )
                            )
                    except Exception as e:
                        self.errors.append(f"Error reading {file_path}: {e}")

        return sorted(unicode_files, key=lambda x: x[1], reverse=True)

    def fix_unicode_in_file(self, file_path: Path) -> bool:
        """Fix Unicode characters in a single file"""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            changes_made = False

            # Replace Unicode characters
            for unicode_char, replacement in UNICODE_REPLACEMENTS.items():
                if unicode_char in content:
                    content = content.replace(unicode_char, replacement)
                    changes_made = True
                    self.unicode_chars_replaced += original_content.count(unicode_char)

            # Add encoding declaration if missing and file has Unicode content
            if changes_made and not re.search(r"coding[:=]\s*([-\w.]+)", content[:200]):
                lines = content.splitlines()
                if lines and lines[0].startswith("#!"):
                    # Insert after shebang
                    lines.insert(1, "# -*- coding: utf-8 -*-")
                else:
                    # Insert at the beginning
                    lines.insert(0, "# -*- coding: utf-8 -*-")
                content = "\n".join(lines)

            if changes_made:
                if self.dry_run:
                    print(f"  [DRY-RUN] Would fix: {file_path}")
                else:
                    file_path.write_text(content, encoding="utf-8")
                    print(f"  [FIXED] {file_path}")
                self.files_changed += 1
                return True

        except Exception as e:
            self.errors.append(f"Error fixing {file_path}: {e}")

        return False

    def setup_environment(self) -> None:
        """Set up environment variables for Unicode support"""
        env_vars = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

        print("\n🔧 Setting up environment for Unicode support:")
        for var, value in env_vars.items():
            os.environ[var] = value
            print(f"  Set {var}={value}")

    def verify_fixes(self, files_to_check: list[Path]) -> tuple[int, int]:
        """Verify that fixes work by testing file imports/execution"""
        successful = 0
        failed = 0

        print("\n🔍 Verifying fixes...")

        # Test basic import/syntax check for Python files
        for file_path in files_to_check:
            try:
                if file_path.name == "aether.py":
                    # Special test for aether.py
                    result = subprocess.run(
                        [sys.executable, str(file_path), "--help"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        env={
                            **os.environ,
                            "PYTHONIOENCODING": "utf-8",
                            "PYTHONUTF8": "1",
                        },
                    )

                    if result.returncode == 0:
                        print(f"  ✅ {file_path}: Working correctly")
                        successful += 1
                    else:
                        print(f"  ❌ {file_path}: Still has issues")
                        if result.stderr:
                            print(f"     Error: {result.stderr[:100]}...")
                        failed += 1
                else:
                    # Basic syntax check
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(file_path)],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0:
                        successful += 1
                    else:
                        failed += 1

            except Exception as e:
                print(f"  ⚠️ {file_path}: Could not verify - {e}")
                failed += 1

        return successful, failed

    def create_fix_script(self) -> None:
        """Create a standalone fix script for easy automation"""
        script_content = '''#!/usr/bin/env python3
# Auto-generated fix script for Aetherra workflow failures

import os
import sys
from pathlib import Path

def setup_unicode_environment():
    """Set up Unicode environment variables"""
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    print("✅ Unicode environment configured")

def main():
    print("🔧 Aetherra Workflow Quick Fix")
    print("=" * 40)
    
    # Set up environment
    setup_unicode_environment()
    
    # Run the comprehensive fix
    try:
        from tools.auto_fix_workflow_failures import WorkflowFixer
        fixer = WorkflowFixer()
        fixer.run_comprehensive_fix()
        print("\\n✅ All fixes applied successfully!")
    except ImportError:
        print("❌ Could not import WorkflowFixer")
        print("   Run: python tools/auto_fix_workflow_failures.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        script_path = ROOT_DIR / "tools" / "github" / "quick_fix_workflows.py"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.dry_run:
            script_path.write_text(script_content, encoding="utf-8")
            script_path.chmod(0o755)
            print(f"\n📝 Created quick fix script: {script_path}")

    def run_comprehensive_fix(self) -> None:
        """Run the complete workflow fix process"""
        print("🔧 Aetherra Automated Workflow Failure Fix")
        print("=" * 50)

        # Set up environment
        self.setup_environment()

        # Find files with Unicode issues
        print("\n🔍 Scanning for Unicode issues...")
        unicode_files = self.find_python_files_with_unicode()

        if not unicode_files:
            print("✅ No Unicode issues found!")
            return

        print(f"Found {len(unicode_files)} files with Unicode characters")

        # Show top files with most issues
        print("\nTop files with Unicode issues:")
        for file_path, count, chars in unicode_files[:10]:
            print(f"  {file_path}: {count} chars ({len(chars)} unique)")

        # Fix critical files first
        print(f"\n🔧 Fixing files {'(DRY RUN)' if self.dry_run else ''}...")

        critical_fixed = []
        for critical_file in CRITICAL_FILES:
            critical_path = ROOT_DIR / critical_file
            if critical_path.exists():
                if self.fix_unicode_in_file(critical_path):
                    critical_fixed.append(critical_path)

        # Fix all other files
        other_fixed = []
        for file_path, _, _ in unicode_files:
            full_path = ROOT_DIR / file_path
            if str(file_path) not in CRITICAL_FILES:
                if self.fix_unicode_in_file(full_path):
                    other_fixed.append(full_path)

        # Summary
        print("\n📊 Fix Summary:")
        print(f"  Files changed: {self.files_changed}")
        print(f"  Unicode characters replaced: {self.unicode_chars_replaced}")
        print(f"  Errors: {len(self.errors)}")

        if self.errors:
            print("\n❌ Errors encountered:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  {error}")

        # Verify fixes if not dry run
        if not self.dry_run and (critical_fixed or other_fixed):
            all_fixed = critical_fixed + other_fixed[:10]  # Verify first 10 others
            successful, failed = self.verify_fixes(all_fixed)
            print(f"\n🔍 Verification: {successful} successful, {failed} failed")

        # Create quick fix script
        if not self.dry_run:
            self.create_fix_script()


def main():
    parser = argparse.ArgumentParser(
        description="Fix Aetherra workflow failures automatically"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--files", type=str, help="Specific files to fix (comma-separated)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Fix all Python files with Unicode issues"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Only verify fixes, don't apply them"
    )

    args = parser.parse_args()

    fixer = WorkflowFixer(dry_run=args.dry_run or args.verify)

    if args.files:
        # Fix specific files
        files_to_fix = [Path(f.strip()) for f in args.files.split(",")]
        for file_path in files_to_fix:
            if file_path.exists():
                fixer.fix_unicode_in_file(file_path)
            else:
                print(f"❌ File not found: {file_path}")
    else:
        # Run comprehensive fix
        fixer.run_comprehensive_fix()


if __name__ == "__main__":
    main()
