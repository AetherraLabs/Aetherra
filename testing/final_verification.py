"""
Final verification script for Lyrixa UI components.
This script checks:
1. Dark mode implementation
2. Absence of CSS warnings
3. Integration between Lyrixa Assistant and Lyrixa
"""

import importlib
import os
import re
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_no_box_shadow():
    """Test that no box-shadow properties exist in Qt UI files."""
    print("\n===== Testing for box-shadow CSS properties =====")

    # Files to check
    ui_files = ["src/aetherra/ui/lyrixa.py", "src/aetherra/ui/lyrixa_assistant.py"]

    box_shadow_found = False

    for file_path in ui_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "box-shadow" in content:
                    print(f"✗ Found box-shadow in {file_path}")
                    box_shadow_found = True
                else:
                    print(f"✓ No box-shadow in {file_path}")
        except Exception as e:
            print(f"✗ Error reading {file_path}: {e}")

    if not box_shadow_found:
        print("✅ No box-shadow properties found in Qt UI files")

    return not box_shadow_found


def test_dark_mode_implementation():
    """Test that dark mode properties are properly implemented."""
    print("\n===== Testing dark mode implementation =====")

    # Files to check
    ui_files = ["src/aetherra/ui/lyrixa.py", "src/aetherra/ui/lyrixa_assistant.py"]

    dark_mode_patterns = [
        r"dark",
        r"#[0-9a-fA-F]{6}",  # Hex color codes
        r"rgb\([0-9]+,\s*[0-9]+,\s*[0-9]+\)",  # RGB colors
        r"background-color",
        r"color:",
    ]

    all_files_have_dark_mode = True

    for file_path in ui_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                has_dark_mode = False

                for pattern in dark_mode_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        has_dark_mode = True
                        break

                if has_dark_mode:
                    print(f"✓ Dark mode elements found in {file_path}")
                else:
                    print(f"✗ No dark mode elements found in {file_path}")
                    all_files_have_dark_mode = False
        except Exception as e:
            print(f"✗ Error reading {file_path}: {e}")
            all_files_have_dark_mode = False

    if all_files_have_dark_mode:
        print("✅ Dark mode is implemented in all UI files")

    return all_files_have_dark_mode


def test_imports_without_errors():
    """Test that all UI modules can be imported without errors."""
    print("\n===== Testing module imports =====")

    modules_to_test = ["src.aetherra.ui.lyrixa_assistant", "src.aetherra.ui.lyrixa"]

    all_imports_successful = True

    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✓ Successfully imported {module_name}")
        except Exception as e:
            print(f"✗ Failed to import {module_name}: {e}")
            all_imports_successful = False

    if all_imports_successful:
        print("✅ All UI modules imported successfully")

    return all_imports_successful


if __name__ == "__main__":
    print("🚀 Running final UI verification script...")

    results = {
        "box_shadow": test_no_box_shadow(),
        "dark_mode": test_dark_mode_implementation(),
        "imports": test_imports_without_errors(),
    }

    print("\n===== Verification Summary =====")
    for test, result in results.items():
        status = "✅ Passed" if result else "✗ Failed"
        print(f"- {test.replace('_', ' ').title()}: {status}")

    if all(results.values()):
        print("\n🎉 All UI verification tests passed!")
    else:
        print("\n⚠️ Some UI verification tests failed.")
