#!/usr/bin/env python3
"""
Test script for daily_reflector.aether system plugin
Validates all supporting functions and daily reflection functionality
"""

import json
import os
import sys
import unittest
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestDailyReflector(unittest.TestCase):
    """Test suite for daily_reflector.aether plugin"""

    def setUp(self):
        """Set up test environment"""
        self.test_results = []
        self.plugin_files = [
            "Aetherra/system/daily_reflector.aether",
            "Aetherra/system/logger.aether",
            "Aetherra/system/goals.aether",
            "Aetherra/system/agents.aether",
            "Aetherra/system/plugins.aether",
            "Aetherra/system/utils.aether",
        ]

    def test_plugin_file_exists(self):
        """Test that daily_reflector.aether file exists"""
        plugin_file = "Aetherra/system/daily_reflector.aether"
        self.assertTrue(
            os.path.exists(plugin_file), f"Plugin file {plugin_file} does not exist"
        )
        self.test_results.append(f"✅ Plugin file exists: {plugin_file}")

    def test_plugin_syntax_validation(self):
        """Test that daily_reflector.aether has valid syntax"""
        plugin_file = "Aetherra/system/daily_reflector.aether"

        with open(plugin_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required plugin structure
        self.assertIn("plugin daily_reflector", content)
        self.assertIn("description:", content)
        self.assertIn("memory_access:", content)
        self.assertIn("schedule:", content)
        self.assertIn("on_run", content)

        # Check for required configuration
        self.assertIn("config:", content)
        self.assertIn("reflection_window_hours:", content)
        self.assertIn("include_goals:", content)
        self.assertIn("include_plugins:", content)
        self.assertIn("include_agents:", content)

        self.test_results.append("✅ Plugin syntax validation passed")

    def test_supporting_functions_exist(self):
        """Test that all required supporting functions exist in their respective modules"""

        # Test logger.aether functions
        with open("Aetherra/system/logger.aether", "r", encoding="utf-8") as f:
            logger_content = f.read()
        self.assertIn("fn get_logs_since(", logger_content)
        self.assertIn("fn log_event(", logger_content)
        self.test_results.append("✅ Logger functions exist: get_logs_since, log_event")

        # Test goals.aether functions
        with open("Aetherra/system/goals.aether", "r", encoding="utf-8") as f:
            goals_content = f.read()
        self.assertIn("fn get_recent_goal_summary(", goals_content)
        self.test_results.append("✅ Goals functions exist: get_recent_goal_summary")

        # Test agents.aether functions
        with open("Aetherra/system/agents.aether", "r", encoding="utf-8") as f:
            agents_content = f.read()
        self.assertIn("fn get_recent_agent_activity(", agents_content)
        self.test_results.append("✅ Agents functions exist: get_recent_agent_activity")

        # Test plugins.aether functions
        with open("Aetherra/system/plugins.aether", "r", encoding="utf-8") as f:
            plugins_content = f.read()
        self.assertIn("fn get_recent_plugin_summary(", plugins_content)
        self.test_results.append(
            "✅ Plugins functions exist: get_recent_plugin_summary"
        )

        # Test utils.aether functions
        with open("Aetherra/system/utils.aether", "r", encoding="utf-8") as f:
            utils_content = f.read()
        self.assertIn("fn hours_ago(", utils_content)
        self.test_results.append("✅ Utils functions exist: hours_ago")

    def test_function_call_structure(self):
        """Test that daily_reflector.aether calls supporting functions correctly"""

        with open("Aetherra/system/daily_reflector.aether", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for correct function calls
        self.assertIn("call system/utils.hours_ago(", content)
        self.assertIn("call system/logger.get_logs_since(", content)
        self.assertIn("call system/goals.get_recent_goal_summary(", content)
        self.assertIn("call system/agents.get_recent_agent_activity(", content)
        self.assertIn("call system/plugins.get_recent_plugin_summary(", content)
        self.assertIn("call system/logger.log_event(", content)

        self.test_results.append("✅ Function call structure is correct")

    def test_plugin_logic_flow(self):
        """Test that daily_reflector.aether has proper logic flow"""

        with open("Aetherra/system/daily_reflector.aether", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required logic components
        self.assertIn("let since =", content)
        self.assertIn("let logs =", content)
        self.assertIn("let summary =", content)
        self.assertIn("if config.include_goals", content)
        self.assertIn("if config.include_agents", content)
        self.assertIn("if config.include_plugins", content)
        self.assertIn("let reflection_text =", content)
        self.assertIn("let reflection_entry =", content)
        self.assertIn("store_memory(reflection_entry)", content)

        self.test_results.append("✅ Plugin logic flow is correct")

    def test_memory_integration(self):
        """Test that daily_reflector.aether properly integrates with memory system"""

        with open("Aetherra/system/daily_reflector.aether", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for memory operations
        self.assertIn("store_memory(reflection_entry)", content)
        self.assertIn('type: "reflection"', content)
        self.assertIn("timestamp: now()", content)

        self.test_results.append("✅ Memory integration is correct")

    def test_reflection_configuration(self):
        """Test that daily_reflector.aether has proper configuration"""

        with open("Aetherra/system/daily_reflector.aether", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for configuration options
        self.assertIn("reflection_window_hours: 24", content)
        self.assertIn("use_summarizer_plugin: true", content)
        self.assertIn("include_goals: true", content)
        self.assertIn("include_plugins: true", content)
        self.assertIn("include_agents: true", content)
        self.assertIn("log_reflection: true", content)

        self.test_results.append("✅ Configuration structure is correct")

    def test_schedule_configuration(self):
        """Test that daily_reflector.aether has proper schedule configuration"""

        with open("Aetherra/system/daily_reflector.aether", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for schedule
        self.assertIn("schedule: every 24 hours", content)

        self.test_results.append("✅ Schedule configuration is correct")

    def test_error_handling(self):
        """Test that daily_reflector.aether has proper error handling"""

        with open("Aetherra/system/daily_reflector.aether", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for error handling patterns
        self.assertIn("plugin_exists(", content)
        self.assertIn("simple_reflection(", content)

        self.test_results.append("✅ Error handling patterns are present")

    def test_all_file_integrations(self):
        """Test that all referenced files exist and have required functions"""

        # Check all plugin files exist
        for file_path in self.plugin_files:
            self.assertTrue(
                os.path.exists(file_path), f"Required file {file_path} does not exist"
            )

        self.test_results.append("✅ All required plugin files exist")

    def generate_test_report(self):
        """Generate comprehensive test report"""

        report = {
            "test_name": "Daily Reflector Plugin Test",
            "timestamp": datetime.now().isoformat(),
            "plugin_file": "Aetherra/system/daily_reflector.aether",
            "supporting_modules": [
                "logger.aether",
                "goals.aether",
                "agents.aether",
                "plugins.aether",
                "utils.aether",
            ],
            "test_results": self.test_results,
            "status": "PASSED"
            if all("✅" in result for result in self.test_results)
            else "FAILED",
        }

        with open("daily_reflector_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Run all tests and generate report"""
    print("🔍 Testing Daily Reflector Plugin System...")
    print("=" * 60)

    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDailyReflector)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate report
    test_instance = TestDailyReflector()
    test_instance.setUp()

    # Run individual test methods to populate test_results
    try:
        test_instance.test_plugin_file_exists()
        test_instance.test_plugin_syntax_validation()
        test_instance.test_supporting_functions_exist()
        test_instance.test_function_call_structure()
        test_instance.test_plugin_logic_flow()
        test_instance.test_memory_integration()
        test_instance.test_reflection_configuration()
        test_instance.test_schedule_configuration()
        test_instance.test_error_handling()
        test_instance.test_all_file_integrations()
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
    print("📄 Report saved to: daily_reflector_test_report.json")

    return report["status"] == "PASSED"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
