#!/usr/bin/env python3
"""
Diagnose why the API server doesn't start from the launcher
"""

import sys
import os
from pathlib import Path

print("🔍 DIAGNOSING API SERVER STARTUP ISSUE")
print("=" * 50)

# Test path resolution like the launcher does
launcher_path = Path("Aetherra/lyrixa/launcher.py")
utils_path = Path("Aetherra/utils/launch_utils.py")

print(f"📁 File Locations:")
print(f"   • Launcher: {launcher_path}")
print(f"   • Utils: {utils_path}")
print(f"   • Utils exists: {utils_path.exists()}")

# Test the path calculation from utils to project root
if utils_path.exists():
    utils_dir = utils_path.parent  # Aetherra/utils
    project_root_from_utils = utils_dir.parent.parent  # Should be project root
    api_script_path = project_root_from_utils / "run_self_improvement_api.py"

    print(f"\n🧮 Path Calculation:")
    print(f"   • Utils directory: {utils_dir}")
    print(f"   • Project root calculated: {project_root_from_utils}")
    print(f"   • API script expected at: {api_script_path}")
    print(f"   • API script exists: {api_script_path.exists()}")

    # Check what's actually in the project root
    print(f"\n📂 Project Root Contents:")
    if project_root_from_utils.exists():
        api_files = list(project_root_from_utils.glob("*api*.py"))
        print(f"   • API files found: {[f.name for f in api_files]}")

    # Check the actual project root (current directory)
    actual_project_root = Path(".")
    actual_api_script = actual_project_root / "run_self_improvement_api.py"

    print(f"\n✅ Actual Locations:")
    print(f"   • Current directory: {actual_project_root.absolute()}")
    print(f"   • API script at current: {actual_api_script.exists()}")

    if actual_api_script.exists():
        print(f"   • ✅ Found: {actual_api_script.absolute()}")
    else:
        print(f"   • ❌ Not found at: {actual_api_script.absolute()}")

# Test if we can import and run launch_utils
print(f"\n🧪 Testing launch_utils import:")
try:
    sys.path.insert(0, str(Path("Aetherra")))
    from utils.launch_utils import run_self_improvement_api
    print(f"   • ✅ Import successful")

    # Check what the function would do
    print(f"\n🎯 Testing API startup function:")
    print(f"   • Function exists: {callable(run_self_improvement_api)}")

except Exception as e:
    print(f"   • ❌ Import failed: {e}")

print(f"\n💡 DIAGNOSIS COMPLETE")
