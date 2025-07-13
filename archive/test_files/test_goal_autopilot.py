#!/usr/bin/env python3
"""
Test script for goal_autopilot.aether system plugin
Validates the goal autopilot functionality and integration
"""

import json
import os
import sys
import unittest
from datetime import datetime


class TestGoalAutopilot(unittest.TestCase):
    """Test suite for goal_autopilot.aether plugin"""

    def setUp(self):
        """Set up test environment"""
        self.test_results = []
        self.plugin_file = "Aetherra/system/goal_autopilot.aether"

    def test_plugin_file_exists(self):
        """Test that goal_autopilot.aether file exists"""
        self.assertTrue(
            os.path.exists(self.plugin_file),
            f"Plugin file {self.plugin_file} does not exist",
        )
        self.test_results.append(f"✅ Plugin file exists: {self.plugin_file}")

    def test_plugin_syntax_validation(self):
        """Test that goal_autopilot.aether has valid syntax"""
        with open(self.plugin_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required plugin structure
        self.assertIn("plugin goal_autopilot", content)
        self.assertIn("description:", content)
        self.assertIn("memory_access:", content)
        self.assertIn("on_run", content)

        self.test_results.append("✅ Plugin syntax validation passed")

    def test_supporting_modules_exist(self):
        """Test that all supporting modules exist"""
        required_modules = [
            "Aetherra/system/goals.aether",
            "Aetherra/system/agents.aether",
            "Aetherra/system/logger.aether",
            "Aetherra/system/utils.aether",
        ]

        for module in required_modules:
            self.assertTrue(
                os.path.exists(module), f"Required module {module} does not exist"
            )

        self.test_results.append("✅ All supporting modules exist")

    def test_goal_autopilot_configuration(self):
        """Test that goal_autopilot has proper configuration"""
        with open(self.plugin_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for configuration options
        self.assertIn("config:", content)
        self.assertIn("max_retry_attempts:", content)
        self.assertIn("retry_delay_minutes:", content)

        self.test_results.append("✅ Configuration structure is correct")

    def test_function_calls(self):
        """Test that goal_autopilot calls required functions"""
        with open(self.plugin_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required function calls
        self.assertIn("call system/goals.", content)
        self.assertIn("call system/agents.", content)
        self.assertIn("call system/logger.", content)

        self.test_results.append("✅ Function call structure is correct")

    def generate_test_report(self):
        """Generate test report"""
        report = {
            "test_name": "Goal Autopilot Test",
            "timestamp": datetime.now().isoformat(),
            "plugin_file": self.plugin_file,
            "test_results": self.test_results,
            "status": "PASSED"
            if all("✅" in result for result in self.test_results)
            else "FAILED",
        }

        with open("goal_autopilot_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Run all tests and generate report"""
    print("🔍 Testing Goal Autopilot System...")
    print("=" * 60)

    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGoalAutopilot)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate report
    test_instance = TestGoalAutopilot()
    test_instance.setUp()

    # Run individual test methods to populate test_results
    try:
        test_instance.test_plugin_file_exists()
        test_instance.test_plugin_syntax_validation()
        test_instance.test_supporting_modules_exist()
        test_instance.test_goal_autopilot_configuration()
        test_instance.test_function_calls()
    except Exception as e:
        test_instance.test_results.append(f"❌ Test execution error: {str(e)}")

    report = test_instance.generate_test_report()

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    for result in test_instance.test_results:
        print(result)

    print(f"\n🎯 Overall Status: {report['status']}")
    print("📄 Report saved to: goal_autopilot_test_report.json")

    return report["status"] == "PASSED"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
