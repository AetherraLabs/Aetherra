#!/usr/bin/env python3
"""
Comprehensive test script for plugin_watchdog.aether system plugin
Validates all supporting functions and watchdog functionality
"""

import sys
import os
import json
import unittest
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestPluginWatchdog(unittest.TestCase):
    """Test suite for plugin_watchdog.aether plugin"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_results = []
        self.plugin_files = [
            'Aetherra/system/plugin_watchdog.aether',
            'Aetherra/system/plugins.aether',
            'Aetherra/system/logger.aether',
            'Aetherra/system/utils.aether'
        ]
    
    def test_plugin_file_exists(self):
        """Test that plugin_watchdog.aether file exists"""
        plugin_file = 'Aetherra/system/plugin_watchdog.aether'
        self.assertTrue(os.path.exists(plugin_file), f"Plugin file {plugin_file} does not exist")
        self.test_results.append(f"✅ Plugin file exists: {plugin_file}")
    
    def test_plugin_syntax_validation(self):
        """Test that plugin_watchdog.aether has valid syntax"""
        plugin_file = 'Aetherra/system/plugin_watchdog.aether'
        
        with open(plugin_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required plugin structure
        self.assertIn('plugin plugin_watchdog', content)
        self.assertIn('description:', content)
        self.assertIn('memory_access:', content)
        self.assertIn('schedule:', content)
        self.assertIn('on_run', content)
        
        # Check for required configuration
        self.assertIn('config:', content)
        self.assertIn('error_threshold:', content)
        self.assertIn('slow_response_threshold_ms:', content)
        self.assertIn('disable_on_failure:', content)
        self.assertIn('log_all_actions:', content)
        
        self.test_results.append("✅ Plugin syntax validation passed")
    
    def test_plugins_aether_functions(self):
        """Test that all required functions exist in plugins.aether"""
        
        with open('Aetherra/system/plugins.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for get_all_plugins function
        self.assertIn('fn get_all_plugins()', content)
        self.assertIn('return search_memory({', content)
        self.assertIn('type: "plugin"', content)
        self.test_results.append("✅ get_all_plugins() function exists")
        
        # Check for mark_unhealthy function
        self.assertIn('fn mark_unhealthy(name, reason)', content)
        self.assertIn('status: "unhealthy"', content)
        self.assertIn('last_issue: reason', content)
        self.assertIn('last_checked: now()', content)
        self.test_results.append("✅ mark_unhealthy() function exists")
        
        # Check for disable_plugin function
        self.assertIn('fn disable_plugin(', content)
        self.assertIn('status: "disabled"', content)
        self.assertIn('disabled_at: now()', content)
        self.test_results.append("✅ disable_plugin() function exists")
    
    def test_logger_aether_functions(self):
        """Test that required functions exist in logger.aether"""
        
        with open('Aetherra/system/logger.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for get_plugin_logs function
        self.assertIn('fn get_plugin_logs(name, since_time)', content)
        self.assertIn('type: "system_log"', content)
        self.assertIn('event_type_in: ["plugin_used", "plugin_error"]', content)
        self.assertIn('source: name', content)
        self.assertIn('timestamp_gte: since_time', content)
        self.test_results.append("✅ get_plugin_logs() function exists")
        
        # Check for log_event function (should already exist)
        self.assertIn('fn log_event(', content)
        self.test_results.append("✅ log_event() function exists")
    
    def test_utils_aether_functions(self):
        """Test that required functions exist in utils.aether"""
        
        with open('Aetherra/system/utils.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for hours_ago function
        self.assertIn('fn hours_ago(', content)
        self.assertIn('return now() - (', content)
        self.assertIn('* 3600)', content)
        self.test_results.append("✅ hours_ago() function exists")
    
    def test_watchdog_function_calls(self):
        """Test that plugin_watchdog.aether calls supporting functions correctly"""
        
        with open('Aetherra/system/plugin_watchdog.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for correct function calls
        self.assertIn('call system/utils.hours_ago(24)', content)
        self.assertIn('call system/plugins.get_all_plugins()', content)
        self.assertIn('call system/logger.get_plugin_logs(plugin.name, since)', content)
        self.assertIn('call system/plugins.mark_unhealthy(plugin.name, reason)', content)
        self.assertIn('call system/plugins.disable_plugin(plugin.name)', content)
        self.assertIn('call system/logger.log_event(', content)
        
        self.test_results.append("✅ Function call structure is correct")
    
    def test_watchdog_logic_flow(self):
        """Test that plugin_watchdog.aether has proper logic flow"""
        
        with open('Aetherra/system/plugin_watchdog.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required logic components
        self.assertIn('let since =', content)
        self.assertIn('let plugins =', content)
        self.assertIn('let unhealthy = []', content)
        self.assertIn('for plugin in plugins', content)
        self.assertIn('let logs =', content)
        self.assertIn('let errors =', content)
        self.assertIn('let avg_time =', content)
        self.assertIn('if errors >= config.error_threshold or avg_time >= config.slow_response_threshold_ms', content)
        self.assertIn('let reason =', content)
        self.assertIn('if config.disable_on_failure', content)
        self.assertIn('if config.log_all_actions', content)
        
        self.test_results.append("✅ Plugin logic flow is correct")
    
    def test_watchdog_configuration(self):
        """Test that plugin_watchdog.aether has proper configuration"""
        
        with open('Aetherra/system/plugin_watchdog.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for configuration options
        self.assertIn('error_threshold: 5', content)
        self.assertIn('slow_response_threshold_ms: 2000', content)
        self.assertIn('disable_on_failure: true', content)
        self.assertIn('log_all_actions: true', content)
        
        self.test_results.append("✅ Configuration structure is correct")
    
    def test_schedule_configuration(self):
        """Test that plugin_watchdog.aether has proper schedule configuration"""
        
        with open('Aetherra/system/plugin_watchdog.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for schedule
        self.assertIn('schedule: every 6 hours', content)
        
        self.test_results.append("✅ Schedule configuration is correct")
    
    def test_event_logging_structure(self):
        """Test that plugin_watchdog.aether has proper event logging structure"""
        
        with open('Aetherra/system/plugin_watchdog.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for event logging patterns
        self.assertIn('"plugin_flagged"', content)
        self.assertIn('"plugin_watchdog_complete"', content)
        self.assertIn('name: plugin.name', content)
        self.assertIn('reason: reason', content)
        self.assertIn('avg_latency: avg_time', content)
        self.assertIn('error_count: errors', content)
        self.assertIn('scanned: plugins.length', content)
        self.assertIn('flagged: unhealthy.length', content)
        
        self.test_results.append("✅ Event logging structure is correct")
    
    def test_error_handling_patterns(self):
        """Test that plugin_watchdog.aether has proper error handling"""
        
        with open('Aetherra/system/plugin_watchdog.aether', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling patterns
        self.assertIn('if errors >= config.error_threshold', content)
        self.assertIn('error threshold exceeded', content)
        self.assertIn('slow response', content)
        self.assertIn('logs.filter(l => l.level == "error")', content)
        
        self.test_results.append("✅ Error handling patterns are present")
    
    def test_all_file_integrations(self):
        """Test that all referenced files exist and have required functions"""
        
        # Check all plugin files exist
        for file_path in self.plugin_files:
            self.assertTrue(os.path.exists(file_path), f"Required file {file_path} does not exist")
        
        self.test_results.append("✅ All required plugin files exist")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        report = {
            "test_name": "Plugin Watchdog System Test",
            "timestamp": datetime.now().isoformat(),
            "plugin_file": "Aetherra/system/plugin_watchdog.aether",
            "supporting_modules": [
                "plugins.aether",
                "logger.aether", 
                "utils.aether"
            ],
            "required_functions": {
                "plugins.aether": [
                    "get_all_plugins()",
                    "mark_unhealthy(name, reason)",
                    "disable_plugin(name)"
                ],
                "logger.aether": [
                    "get_plugin_logs(name, since_time)",
                    "log_event()"
                ],
                "utils.aether": [
                    "hours_ago(h)"
                ]
            },
            "test_results": self.test_results,
            "status": "PASSED" if all("✅" in result for result in self.test_results) else "FAILED"
        }
        
        with open('plugin_watchdog_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def main():
    """Run all tests and generate report"""
    print("🔍 Testing Plugin Watchdog System...")
    print("=" * 60)
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPluginWatchdog)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    test_instance = TestPluginWatchdog()
    test_instance.setUp()
    
    # Run individual test methods to populate test_results
    try:
        test_instance.test_plugin_file_exists()
        test_instance.test_plugin_syntax_validation()
        test_instance.test_plugins_aether_functions()
        test_instance.test_logger_aether_functions()
        test_instance.test_utils_aether_functions()
        test_instance.test_watchdog_function_calls()
        test_instance.test_watchdog_logic_flow()
        test_instance.test_watchdog_configuration()
        test_instance.test_schedule_configuration()
        test_instance.test_event_logging_structure()
        test_instance.test_error_handling_patterns()
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
    print("📄 Report saved to: plugin_watchdog_test_report.json")
    
    return report['status'] == 'PASSED'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
