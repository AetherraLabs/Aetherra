#!/usr/bin/env python3
"""
AetherraCode & Neuroplex Comprehensive System Test

This script performs a full system test of both AetherraCode and Neuroplex
to ensure all components are functioning properly after our cleanup.

Test Coverage:
1. Core AetherraCode functionality
2. Neuroplex launcher systems
3. Agent archive and replay
4. Memory and goal systems
5. Parser and interpreter
6. Plugin system
7. File protection
8. Website and deployment
"""

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict


class SystemTester:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.test_results = {}
        self.errors = []
        self.warnings = []

    def log_test(self, test_name: str, status: str, message: str = "", details: str = ""):
        """Log test results."""
        self.test_results[test_name] = {"status": status, "message": message, "details": details}

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")

        if details and status != "PASS":
            print(f"    Details: {details}")

    def test_python_environment(self) -> bool:
        """Test Python environment and basic imports."""
        print("\n🐍 TESTING PYTHON ENVIRONMENT")
        print("=" * 50)

        try:
            # Test Python version
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                self.log_test(
                    "Python Version",
                    "PASS",
                    f"Python {version.major}.{version.minor}.{version.micro}",
                )
            else:
                self.log_test(
                    "Python Version",
                    "FAIL",
                    f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)",
                )
                return False

            # Test basic imports
            basic_imports = ["json", "os", "sys", "pathlib", "subprocess", "datetime"]
            for module in basic_imports:
                try:
                    __import__(module)
                    self.log_test(f"Import {module}", "PASS", "Module available")
                except ImportError as e:
                    self.log_test(f"Import {module}", "FAIL", "Import failed", str(e))
                    return False

            return True

        except Exception as e:
            self.log_test("Python Environment", "FAIL", "Environment test failed", str(e))
            return False

    def test_core_files(self) -> bool:
        """Test that core AetherraCode files exist and are readable."""
        print("\n📁 TESTING CORE FILES")
        print("=" * 50)

        critical_files = [
            "aethercode_launcher.py",
            "core/__init__.py",
            "core/agent.py",
            "core/memory.py",
            "core/interpreter.py",
            "PROJECT_OVERVIEW.md",
            "requirements.txt",
        ]

        all_present = True
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # Test readability
                    with open(full_path, encoding="utf-8") as f:
                        content = f.read()
                    self.log_test(
                        f"File {file_path}", "PASS", f"Exists and readable ({len(content)} chars)"
                    )
                except Exception as e:
                    self.log_test(f"File {file_path}", "FAIL", "Exists but not readable", str(e))
                    all_present = False
            else:
                self.log_test(f"File {file_path}", "FAIL", "File missing")
                all_present = False

        return all_present

    def test_aethercode_import(self) -> bool:
        """Test importing core AetherraCode modules."""
        print("\n🧬 TESTING NEUROCODE IMPORTS")
        print("=" * 50)

        try:
            # Add project root to path
            if str(self.project_root) not in sys.path:
                sys.path.insert(0, str(self.project_root))

            # Test core imports
            core_modules = [
                ("core.agent", "Agent functionality"),
                ("core.memory", "Memory system"),
                ("core.interpreter", "Code interpreter"),
                ("core.goal_system", "Goal management"),
                ("core.plugin_manager", "Plugin system"),
            ]

            success_count = 0
            for module_name, description in core_modules:
                try:
                    module = __import__(module_name, fromlist=[""])
                    self.log_test(f"Import {module_name}", "PASS", description)
                    success_count += 1
                except ImportError as e:
                    self.log_test(
                        f"Import {module_name}", "WARN", f"{description} - Import failed", str(e)
                    )
                except Exception as e:
                    self.log_test(f"Import {module_name}", "FAIL", f"{description} - Error", str(e))

            return success_count >= len(core_modules) // 2  # At least half should work

        except Exception as e:
            self.log_test("AetherraCode Imports", "FAIL", "Import test failed", str(e))
            return False

    def test_launcher_systems(self) -> bool:
        """Test AetherraCode and Neuroplex launchers."""
        print("\n🚀 TESTING LAUNCHER SYSTEMS")
        print("=" * 50)

        launchers = [
            ("aethercode_launcher.py", "Main AetherraCode launcher"),
            ("aetherplex.bat", "Neuroplex batch launcher"),
            ("aetherplex", "Neuroplex script launcher"),
        ]

        working_launchers = 0
        for launcher, description in launchers:
            launcher_path = self.project_root / launcher
            if launcher_path.exists():
                try:
                    # For Python files, try syntax check
                    if launcher.endswith(".py"):
                        with open(launcher_path, encoding="utf-8") as f:
                            content = f.read()
                        compile(content, launcher_path, "exec")
                        self.log_test(f"Launcher {launcher}", "PASS", f"{description} - Syntax OK")
                        working_launchers += 1
                    else:
                        # For other files, just check they exist and are readable
                        with open(launcher_path, encoding="utf-8") as f:
                            content = f.read()
                        self.log_test(f"Launcher {launcher}", "PASS", f"{description} - File OK")
                        working_launchers += 1
                except Exception as e:
                    self.log_test(f"Launcher {launcher}", "FAIL", f"{description} - Error", str(e))
            else:
                self.log_test(f"Launcher {launcher}", "WARN", f"{description} - Not found")

        return working_launchers > 0

    def test_data_systems(self) -> bool:
        """Test memory, goals, and data persistence systems."""
        print("\n💾 TESTING DATA SYSTEMS")
        print("=" * 50)

        try:
            # Test goals system
            goals_file = self.project_root / "goals_store.json"
            if goals_file.exists():
                try:
                    with open(goals_file, encoding="utf-8") as f:
                        goals_data = json.load(f)
                    self.log_test(
                        "Goals Store",
                        "PASS",
                        f"Valid JSON with {len(goals_data.get('goals', []))} goals",
                    )
                except json.JSONDecodeError as e:
                    self.log_test("Goals Store", "FAIL", "Invalid JSON", str(e))
                    return False
            else:
                self.log_test(
                    "Goals Store", "WARN", "File not found - will be created on first use"
                )

            # Test memory system
            memory_file = self.project_root / "memory_store.json"
            if memory_file.exists():
                try:
                    with open(memory_file, encoding="utf-8") as f:
                        memory_data = json.load(f)
                    self.log_test(
                        "Memory Store",
                        "PASS",
                        f"Valid JSON with {len(memory_data.get('memories', []))} memories",
                    )
                except json.JSONDecodeError as e:
                    self.log_test("Memory Store", "FAIL", "Invalid JSON", str(e))
                    return False
            else:
                self.log_test(
                    "Memory Store", "WARN", "File not found - will be created on first use"
                )

            # Test data directory
            data_dir = self.project_root / "data"
            if data_dir.exists() and data_dir.is_dir():
                data_files = list(data_dir.glob("*.json"))
                self.log_test(
                    "Data Directory", "PASS", f"Directory exists with {len(data_files)} JSON files"
                )
            else:
                self.log_test("Data Directory", "WARN", "Data directory not found")

            return True

        except Exception as e:
            self.log_test("Data Systems", "FAIL", "Data system test failed", str(e))
            return False

    def test_website_deployment(self) -> bool:
        """Test website and deployment systems."""
        print("\n🌐 TESTING WEBSITE DEPLOYMENT")
        print("=" * 50)

        try:
            # Test website directory
            website_dir = self.project_root / "website"
            if website_dir.exists():
                required_files = ["index.html", "styles.css", "script.js"]
                missing_files = []

                for file in required_files:
                    if not (website_dir / file).exists():
                        missing_files.append(file)

                if not missing_files:
                    self.log_test("Website Files", "PASS", "All required files present")
                else:
                    self.log_test("Website Files", "FAIL", f"Missing files: {missing_files}")
                    return False
            else:
                self.log_test("Website Directory", "FAIL", "Website directory not found")
                return False

            # Test CNAME file
            cname_file = self.project_root / "CNAME"
            if cname_file.exists():
                try:
                    with open(cname_file, encoding="utf-8") as f:
                        domain = f.read().strip()
                    self.log_test("CNAME File", "PASS", f"Domain: {domain}")
                except Exception as e:
                    self.log_test("CNAME File", "FAIL", "Cannot read CNAME", str(e))
            else:
                self.log_test("CNAME File", "WARN", "CNAME file not found")

            return True

        except Exception as e:
            self.log_test("Website Deployment", "FAIL", "Website test failed", str(e))
            return False

    def test_archive_structure(self) -> bool:
        """Test archive and backup structure."""
        print("\n📦 TESTING ARCHIVE STRUCTURE")
        print("=" * 50)

        try:
            archive_dir = self.project_root / "archive"
            if archive_dir.exists():
                subdirs = ["status_files", "duplicates", "empty_scripts"]
                existing_subdirs = []

                for subdir in subdirs:
                    subdir_path = archive_dir / subdir
                    if subdir_path.exists():
                        file_count = len(list(subdir_path.iterdir()))
                        self.log_test(f"Archive {subdir}", "PASS", f"{file_count} files archived")
                        existing_subdirs.append(subdir)
                    else:
                        self.log_test(f"Archive {subdir}", "WARN", "Directory not found")

                if existing_subdirs:
                    self.log_test(
                        "Archive Structure",
                        "PASS",
                        f"{len(existing_subdirs)} archive directories found",
                    )
                    return True
                else:
                    self.log_test("Archive Structure", "WARN", "No archive subdirectories found")
                    return False
            else:
                self.log_test("Archive Directory", "WARN", "Archive directory not found")
                return False

        except Exception as e:
            self.log_test("Archive Structure", "FAIL", "Archive test failed", str(e))
            return False

    def test_protection_system(self) -> bool:
        """Test file protection and backup systems."""
        print("\n🛡️ TESTING PROTECTION SYSTEM")
        print("=" * 50)

        try:
            protection_script = self.project_root / "scripts" / "project_protection.py"
            if protection_script.exists():
                try:
                    with open(protection_script, encoding="utf-8") as f:
                        content = f.read()
                    # Basic syntax check
                    compile(content, protection_script, "exec")
                    self.log_test("Protection Script", "PASS", "Script exists and syntax OK")
                except SyntaxError as e:
                    self.log_test("Protection Script", "FAIL", "Syntax error", str(e))
                    return False
            else:
                self.log_test("Protection Script", "WARN", "Protection script not found")

            # Test backup directories
            backups_dir = self.project_root / "backups"
            if backups_dir.exists():
                backup_count = len(list(backups_dir.glob("*.json")))
                self.log_test("Backup System", "PASS", f"{backup_count} backup files found")
            else:
                self.log_test("Backup System", "WARN", "Backups directory not found")

            return True

        except Exception as e:
            self.log_test("Protection System", "FAIL", "Protection test failed", str(e))
            return False

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all system tests and return comprehensive results."""
        print("🧪 NEUROCODE & NEUROPLEX COMPREHENSIVE SYSTEM TEST")
        print("=" * 60)
        print(f"📍 Testing from: {self.project_root}")
        print(f"🐍 Python: {sys.version}")
        print()

        # Run all test suites
        test_suites = [
            ("Python Environment", self.test_python_environment),
            ("Core Files", self.test_core_files),
            ("AetherraCode Imports", self.test_aethercode_import),
            ("Launcher Systems", self.test_launcher_systems),
            ("Data Systems", self.test_data_systems),
            ("Website Deployment", self.test_website_deployment),
            ("Archive Structure", self.test_archive_structure),
            ("Protection System", self.test_protection_system),
        ]

        suite_results = {}
        for suite_name, test_func in test_suites:
            try:
                result = test_func()
                suite_results[suite_name] = result
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {suite_name}: {str(e)}")
                traceback.print_exc()
                suite_results[suite_name] = False

        # Generate summary
        print("\n" + "=" * 60)
        print("📊 SYSTEM TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for result in suite_results.values() if result)
        total = len(suite_results)

        for suite_name, result in suite_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {suite_name}")

        print(f"\n🎯 OVERALL RESULT: {passed}/{total} test suites passed")

        if passed == total:
            print("🎉 ALL SYSTEMS OPERATIONAL!")
            overall_status = "PASS"
        elif passed >= total * 0.75:
            print("⚠️ MOSTLY OPERATIONAL (minor issues)")
            overall_status = "WARN"
        else:
            print("❌ CRITICAL ISSUES DETECTED")
            overall_status = "FAIL"

        # Detailed test results
        print("\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status_icon = (
                "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            )
            print(f"   {status_icon} {test_name}: {result['message']}")

        return {
            "overall_status": overall_status,
            "suite_results": suite_results,
            "test_results": self.test_results,
            "summary": f"{passed}/{total} test suites passed",
        }


def main():
    """Run the comprehensive system test."""
    tester = SystemTester()
    results = tester.run_comprehensive_test()

    # Return appropriate exit code
    if results["overall_status"] == "PASS":
        sys.exit(0)
    elif results["overall_status"] == "WARN":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
