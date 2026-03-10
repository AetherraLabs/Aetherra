#!/usr/bin/env python3
"""
Quick Fix Script for Aetherra Workflow Failures
==============================================

This script provides a simple way to automatically fix Unicode encoding issues
that are causing workflow failures in the Aetherra repository.

Usage:
    python quick_fix_workflows.py [scope]

    scope options:
    - critical: Fix only critical files (default)
    - all: Fix all files with Unicode issues
    - test: Only test, don't apply fixes
"""

# Standard library imports
import os
import sys
from pathlib import Path


def setup_unicode_environment():
    """Set up Unicode environment variables"""
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    print("✅ Unicode environment configured")


def main():
    scope = sys.argv[1] if len(sys.argv) > 1 else "critical"

    print("🔧 Aetherra Workflow Quick Fix")
    print("=" * 40)
    print(f"Scope: {scope}")
    print()

    # Set up environment
    setup_unicode_environment()

    # Add tools directory to path
    tools_dir = Path(__file__).parent / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

    try:
        # Import and run the comprehensive fix
        # Third party imports
        from auto_fix_workflow_failures import WorkflowFixer

        if scope == "test":
            print("🧪 Testing current state...")
            # Just run the test
            # Standard library imports
            import subprocess

            result = subprocess.run([sys.executable, "test_unicode_workflow_fix.py"])
            sys.exit(result.returncode)
        elif scope == "critical":
            print("🔧 Applying critical fixes...")
            fixer = WorkflowFixer()
            critical_files = [
                "aether.py",
                "aetherra_os.py",
                "Aetherra/cli/main.py",
                "Aetherra/runtime/aether_executor.py",
                "Aetherra/aetherra_core/orchestration/scheduler.py",
            ]
            for file_path in critical_files:
                full_path = Path(file_path)
                if full_path.exists():
                    fixer.fix_unicode_in_file(full_path)
        elif scope == "all":
            print("🔧 Applying comprehensive fixes...")
            fixer = WorkflowFixer()
            fixer.run_comprehensive_fix()
        else:
            print(f"❌ Unknown scope: {scope}")
            print("Available scopes: critical, all, test")
            sys.exit(1)

        print("\n✅ Fixes applied successfully!")

        # Test the fixes
        print("\n🧪 Testing fixes...")
        # Standard library imports
        import subprocess

        result = subprocess.run([sys.executable, "test_unicode_workflow_fix.py"])

        if result.returncode == 0:
            print("\n🎉 All workflow failures should now be fixed!")
            print("\n📋 What was fixed:")
            print("  • Unicode characters replaced with ASCII alternatives")
            print("  • Encoding declarations added to Python files")
            print("  • Environment configured for Unicode support")
            print("  • UnicodeEncodeError on Windows systems resolved")
        else:
            print("\n⚠️ Some issues may remain - check the test output above")

    except ImportError as e:
        print(f"❌ Could not import WorkflowFixer: {e}")
        print("   Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during fix process: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
