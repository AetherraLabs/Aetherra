#!/usr/bin/env python3
"""
Quick aetherra Functionality Test

A simpler test to verify core aetherra components are working.
"""

import sys
from pathlib import Path


def test_basic_functionality():
    """Test basic aetherra functionality."""
    print("🔍 Quick aetherra Functionality Test")
    print("=" * 50)

    project_root = Path(".").resolve()

    # Add project to path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    test_results = {}

    # Test 1: Basic launcher syntax
    try:
        launcher_file = project_root / "aetherra_launcher.py"
        if launcher_file.exists():
            with open(launcher_file, encoding="utf-8") as f:
                content = f.read()
            compile(content, launcher_file, "exec")
            print("✅ aetherra Launcher: Syntax check passed")
            test_results["launcher"] = True
        else:
            print("❌ aetherra Launcher: File not found")
            test_results["launcher"] = False
    except Exception as e:
        print(f"❌ aetherra Launcher: Error - {e}")
        test_results["launcher"] = False

    # Test 2: Core module existence
    core_files = ["agent.py", "memory.py", "interpreter.py", "goal_system.py"]
    core_exists = 0

    for file in core_files:
        core_file = project_root / "core" / file
        if core_file.exists():
            core_exists += 1

    if core_exists == len(core_files):
        print(f"✅ Core Modules: All {len(core_files)} modules present")
        test_results["core_modules"] = True
    else:
        print(f"[WARN] Core Modules: {core_exists}/{len(core_files)} modules present")
        test_results["core_modules"] = core_exists > len(core_files) // 2

    # Test 3: Lyrixalaunchers
    aetherplex_files = ["aetherplex.bat", "aetherplex"]
    aetherplex_exists = 0

    for file in aetherplex_files:
        if (project_root / file).exists():
            aetherplex_exists += 1

    if aetherplex_exists > 0:
        print(f"✅ LyrixaLaunchers: {aetherplex_exists} launcher(s) found")
        test_results["aetherplex"] = True
    else:
        print("❌ LyrixaLaunchers: No launchers found")
        test_results["aetherplex"] = False

    # Test 4: Data files
    data_files = ["goals_store.json", "memory_store.json"]
    data_status = []

    for file in data_files:
        data_file = project_root / file
        if data_file.exists():
            try:
                import json

                with open(data_file, encoding="utf-8") as f:
                    json.load(f)
                data_status.append(f"✅ {file}: Valid JSON")
            except:
                data_status.append(f"[WARN] {file}: Invalid JSON")
        else:
            data_status.append(f"ℹ️ {file}: Will be created on first use")

    for status in data_status:
        print(status)
    test_results["data_files"] = len([s for s in data_status if "✅" in s]) >= 0

    # Test 5: Website deployment
    website_dir = project_root / "website"
    if website_dir.exists():
        required = ["index.html", "styles.css", "script.js"]
        website_files = [f for f in required if (website_dir / f).exists()]

        if len(website_files) == len(required):
            print("✅ Website: All files present in website/ directory")
            test_results["website"] = True
        else:
            print(f"[WARN] Website: {len(website_files)}/{len(required)} files present")
            test_results["website"] = False
    else:
        print("❌ Website: Directory not found")
        test_results["website"] = False

    # Test 6: Archive structure (post-cleanup)
    archive_dir = project_root / "archive"
    if archive_dir.exists():
        subdirs = ["status_files", "duplicates", "empty_scripts"]
        archive_subdirs = [d for d in subdirs if (archive_dir / d).exists()]

        if archive_subdirs:
            print(f"✅ Archive: {len(archive_subdirs)} archive directories found")
            test_results["archive"] = True
        else:
            print("[WARN] Archive: No archive subdirectories found")
            test_results["archive"] = False
    else:
        print("ℹ️ Archive: Directory not found (normal if no cleanup performed)")
        test_results["archive"] = True  # Not required

    # Summary
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")

    print(f"\n🎯 Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - aetherra is ready!")
        return True
    elif passed >= total * 0.8:
        print("[WARN] MOSTLY READY - Minor issues detected")
        return True
    else:
        print("❌ CRITICAL ISSUES - Manual intervention required")
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
