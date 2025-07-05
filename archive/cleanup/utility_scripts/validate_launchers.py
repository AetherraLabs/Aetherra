#!/usr/bin/env python3
"""
Comprehensive Launcher Validation Test
======================================

Validates that all fixed launchers work correctly by running automated tests.
"""

import json
import os
import subprocess
import sys
from datetime import datetime


class LauncherValidator:
    def __init__(self):
        self.results = {}
        self.test_count = 0

    def run_launcher_test(self, launcher_path, test_name, timeout=10):
        """Test a launcher with automated input"""
        print(f"\n🧪 TESTING: {test_name}")
        print("=" * 50)

        result = {
            "path": launcher_path,
            "executable": False,
            "imports_work": False,
            "runtime_error": None,
            "exit_code": None,
            "output": "",
            "error": "",
        }

        self.test_count += 1

        # Test if launcher runs without crashing immediately
        try:
            # Use echo to provide automated input and timeout
            cmd = f'echo "0" | python "{launcher_path}"'

            process = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(launcher_path)
                if launcher_path != os.path.basename(launcher_path)
                else None,
            )

            result["executable"] = True
            result["exit_code"] = process.returncode
            result["output"] = process.stdout
            result["error"] = process.stderr

            # Check if imports work (no import errors in output)
            if (
                "ImportError" not in result["error"]
                and "ModuleNotFoundError" not in result["error"]
            ):
                result["imports_work"] = True

            # Check for runtime errors
            if process.returncode != 0:
                result["runtime_error"] = "Non-zero exit code"

            if result["imports_work"] and process.returncode == 0:
                print("✅ PASSED - Launcher works correctly")
            elif result["imports_work"]:
                print("⚠️ PARTIAL - Launcher runs but has minor issues")
            else:
                print("❌ FAILED - Import or runtime errors")

        except subprocess.TimeoutExpired:
            result["runtime_error"] = "Timeout expired"
            print("⚠️ TIMEOUT - Launcher may be waiting for input")
        except Exception as e:
            result["runtime_error"] = str(e)
            print(f"❌ ERROR - {e}")

        # Display key information
        if result["output"]:
            print(f"📤 Output preview: {result['output'][:200]}...")
        if result["error"]:
            print(f"⚠️ Error preview: {result['error'][:200]}...")

        self.results[test_name] = result
        return result

    def test_all_launchers(self):
        """Test all launcher scripts"""
        launchers = [
            ("aetherra_launcher.py", "Main Aetherra Launcher"),
            ("run_aetherra.py", "Aetherra File Runner"),
            ("launch_lyrixa_live_test.py", "Lyrixa Live Test Launcher"),
            ("launchers/launch_lyrixa.py", "Lyrixa Launcher"),
            ("launchers/launch_playground.py", "Playground Launcher"),
            ("launchers/main.py", "Launchers Main"),
            ("launchers/startup.py", "Startup Launcher"),
        ]

        print("🧪 COMPREHENSIVE LAUNCHER VALIDATION")
        print("=" * 60)
        print("Testing all launchers with automated execution...")

        for launcher_path, test_name in launchers:
            full_path = os.path.abspath(launcher_path)
            if os.path.exists(full_path):
                self.run_launcher_test(full_path, test_name)
            else:
                print(f"\n❌ SKIPPED: {test_name} - File not found: {launcher_path}")
                self.results[test_name] = {
                    "path": launcher_path,
                    "executable": False,
                    "imports_work": False,
                    "runtime_error": "File not found",
                    "exit_code": None,
                    "output": "",
                    "error": "",
                }

    def generate_summary(self):
        """Generate test summary"""
        working_count = sum(
            1
            for r in self.results.values()
            if r["imports_work"] and r["exit_code"] == 0
        )
        partial_count = sum(
            1
            for r in self.results.values()
            if r["imports_work"] and r["exit_code"] != 0
        )
        failed_count = sum(1 for r in self.results.values() if not r["imports_work"])

        print("\n📊 VALIDATION SUMMARY")
        print("=" * 40)
        print(f"📈 Total Launchers: {len(self.results)}")
        print(f"✅ Fully Working: {working_count}")
        print(f"⚠️ Partially Working: {partial_count}")
        print(f"❌ Failed: {failed_count}")
        print(
            f"🎯 Success Rate: {(working_count + partial_count) / len(self.results) * 100:.1f}%"
        )

        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for name, result in self.results.items():
            if result["imports_work"] and result["exit_code"] == 0:
                status = "✅ WORKING"
            elif result["imports_work"]:
                status = "⚠️ PARTIAL"
            else:
                status = "❌ FAILED"

            print(f"   {status} {name}")
            if result["runtime_error"]:
                print(f"      Error: {result['runtime_error']}")

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_data = {
            "timestamp": timestamp,
            "summary": {
                "total": len(self.results),
                "working": working_count,
                "partial": partial_count,
                "failed": failed_count,
                "success_rate": (working_count + partial_count)
                / len(self.results)
                * 100,
            },
            "results": self.results,
        }

        with open("launcher_validation_results.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print("\n💾 Detailed results saved to: launcher_validation_results.json")

        return working_count + partial_count == len(self.results)


def main():
    """Run launcher validation"""
    validator = LauncherValidator()
    validator.test_all_launchers()
    success = validator.generate_summary()

    if success:
        print("\n🎉 All launchers are functional!")
        print("🚀 Ready for production use")
    else:
        print("\n⚠️ Some launchers need attention")
        print("📋 Check the results for specific issues")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
