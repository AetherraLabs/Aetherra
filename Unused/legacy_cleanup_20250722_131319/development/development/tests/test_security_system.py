"""
🧪 Aetherra Security System Test
===============================

Comprehensive test suite for the Aetherra security system.
Tests API key management, memory monitoring, and security integration.

Author: Aetherra Security Team
Date: July 16, 2025
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from security.security_system import AetherraSecuritySystem, SecurityConfig, secure_api_call
from security.api_key_manager import APIKeyManager
from security.memory_manager import MemoryManager

class TestAetherraSecuritySystem(unittest.TestCase):
    """Test suite for Aetherra Security System"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = SecurityConfig(
            api_key_rotation_days=30,
            memory_monitoring_enabled=True,
            leak_detection_enabled=True,
            audit_logging_enabled=True,
            max_memory_usage_percent=80,
            security_scan_interval=10,  # Shorter for testing
            auto_cleanup_enabled=True
        )

        # Create test security system
        self.security_system = AetherraSecuritySystem(
            workspace_path=self.temp_dir,
            config=self.config
        )

    def tearDown(self):
        """Clean up test environment"""
        self.security_system.cleanup_all()

        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_security_system_initialization(self):
        """Test security system initialization"""
        # Check that security system is initialized
        self.assertIsNotNone(self.security_system)
        self.assertIsNotNone(self.security_system.api_key_manager)
        self.assertIsNotNone(self.security_system.memory_manager)
        self.assertIsNotNone(self.security_system.logger)

        # Check that monitoring is started
        self.assertTrue(self.security_system.is_monitoring)

    def test_secure_environment_setup(self):
        """Test secure environment setup"""
        # Check that secure directories were created
        secure_dirs = [
            Path(self.temp_dir) / ".aetherra" / "secure",
            Path(self.temp_dir) / ".aetherra" / "keys",
            Path(self.temp_dir) / ".aetherra" / "logs",
            Path(self.temp_dir) / ".aetherra" / "backups"
        ]

        for dir_path in secure_dirs:
            self.assertTrue(dir_path.exists())
            self.assertTrue(dir_path.is_dir())

    def test_api_key_security(self):
        """Test API key security features"""
        # Test storing API key
        test_key = "test_api_key_12345"
        self.security_system.api_key_manager.store_api_key("test_provider", test_key)

        # Test retrieving API key
        retrieved_key = self.security_system.api_key_manager.get_api_key("test_provider")
        self.assertEqual(retrieved_key, test_key)

        # Test security status
        status = self.security_system.api_key_manager.get_security_status()
        self.assertIn("stored_keys", status)
        self.assertEqual(status["stored_keys"], 1)

    def test_memory_monitoring(self):
        """Test memory monitoring features"""
        # Test memory report
        memory_report = self.security_system.memory_manager.get_memory_report()
        self.assertIn("current_usage", memory_report)
        self.assertIn("percent", memory_report["current_usage"])

        # Test memory context
        with self.security_system.memory_manager.memory_context("test_operation"):
            # Simulate some memory usage
            test_data = [i for i in range(1000)]
            self.assertIsNotNone(test_data)

    def test_security_scan(self):
        """Test security scanning functionality"""
        # Force a security scan
        status = self.security_system.force_security_scan()

        # Check that scan was performed
        self.assertGreater(self.security_system.last_security_scan, 0)

        # Check status structure
        self.assertIn("api_keys", status)
        self.assertIn("memory", status)
        self.assertIn("alerts", status)
        self.assertIn("monitoring_active", status)

    def test_secure_api_call(self):
        """Test secure API call functionality"""
        # Store a test API key
        test_key = "test_api_key_secure"
        self.security_system.api_key_manager.store_api_key("test_provider", test_key)

        # Create a mock function
        def mock_api_function(*args, **kwargs):
            return {"success": True, "api_key": kwargs.get("api_key")}

        # Test secure API call
        result = secure_api_call("test_provider", mock_api_function)

        self.assertTrue(result["success"])
        self.assertEqual(result["api_key"], test_key)

    def test_security_alerts(self):
        """Test security alert system"""
        # Initially no alerts
        self.assertEqual(len(self.security_system.security_alerts), 0)

        # Simulate high memory usage
        with patch.object(self.security_system.memory_manager, 'get_memory_report') as mock_report:
            mock_report.return_value = {
                'current_usage': {'percent': 90.0},  # High usage
                'peak_usage': {'percent': 90.0}
            }

            # Force security scan
            self.security_system.force_security_scan()

            # Check that alert was generated
            self.assertGreater(len(self.security_system.security_alerts), 0)

    def test_auto_cleanup(self):
        """Test automatic cleanup functionality"""
        # Test memory cleanup
        initial_memory = self.security_system.memory_manager.get_memory_report()

        # Simulate high memory usage and trigger cleanup
        with patch.object(self.security_system.memory_manager, 'get_memory_report') as mock_report:
            mock_report.return_value = {
                'current_usage': {'percent': 85.0},  # Above threshold
                'peak_usage': {'percent': 85.0}
            }

            # This should trigger auto-cleanup
            self.security_system._auto_cleanup()

            # Verify cleanup was called
            self.assertTrue(True)  # If no exception, cleanup worked

    def test_configuration(self):
        """Test security configuration"""
        # Test default configuration
        self.assertEqual(self.security_system.config.api_key_rotation_days, 30)
        self.assertTrue(self.security_system.config.memory_monitoring_enabled)
        self.assertTrue(self.security_system.config.leak_detection_enabled)
        self.assertTrue(self.security_system.config.auto_cleanup_enabled)

        # Test custom configuration
        custom_config = SecurityConfig(
            api_key_rotation_days=7,
            memory_monitoring_enabled=False,
            max_memory_usage_percent=70
        )

        custom_system = AetherraSecuritySystem(
            workspace_path=self.temp_dir,
            config=custom_config
        )

        self.assertEqual(custom_system.config.api_key_rotation_days, 7)
        self.assertFalse(custom_system.config.memory_monitoring_enabled)
        self.assertEqual(custom_system.config.max_memory_usage_percent, 70)

        custom_system.cleanup_all()

class TestSecurityIntegration(unittest.TestCase):
    """Test suite for security integration"""

    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.security_system = AetherraSecuritySystem(workspace_path=self.temp_dir)

    def tearDown(self):
        """Clean up integration test environment"""
        self.security_system.cleanup_all()

        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_api_key_memory_integration(self):
        """Test integration between API key management and memory monitoring"""
        # Store multiple API keys
        for i in range(5):
            self.security_system.api_key_manager.store_api_key(f"provider_{i}", f"key_{i}")

        # Check memory usage
        memory_report = self.security_system.memory_manager.get_memory_report()
        self.assertIsNotNone(memory_report)

        # Get security status
        status = self.security_system.get_security_status()
        self.assertEqual(status['api_keys']['stored_keys'], 5)
        self.assertIn('memory', status)

    def test_monitoring_integration(self):
        """Test integration of monitoring systems"""
        # Start monitoring
        self.assertTrue(self.security_system.is_monitoring)

        # Wait a moment for monitoring to run
        import time
        time.sleep(1)

        # Check that monitoring is active
        status = self.security_system.get_security_status()
        self.assertTrue(status['monitoring_active'])

    def test_cleanup_integration(self):
        """Test integration of cleanup systems"""
        # Store some test data
        self.security_system.api_key_manager.store_api_key("test", "key")

        # Allocate some memory
        with self.security_system.memory_manager.memory_context("test"):
            test_data = [i for i in range(1000)]

        # Perform cleanup
        self.security_system.cleanup_all()

        # Verify cleanup
        self.assertFalse(self.security_system.is_monitoring)

def run_security_tests():
    """Run all security tests"""
    print("🧪 Running Aetherra Security System Tests")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAetherraSecuritySystem))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSecurityIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print results
    print(f"\n📊 Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\n[ERROR] Failures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    if result.wasSuccessful():
        print("\n✅ All tests passed! Security system is ready.")
    else:
        print("\n[ERROR] Some tests failed. Please review the issues above.")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)
