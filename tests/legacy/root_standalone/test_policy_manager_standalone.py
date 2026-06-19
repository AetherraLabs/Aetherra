#!/usr/bin/env python
"""
Standalone test runner for PolicyManager.

Avoids Aetherra engine initialization to prevent Unicode encoding issues
in Windows cmd.exe environment.

Run: python tests/legacy/root_standalone/test_policy_manager_standalone.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent))

from Aetherra.aetherra_core.system.policy_manager import (
    EthicsProfile,
    PolicyManager,
    PolicyValidator,
)


class TestPolicyManagerStandalone(unittest.TestCase):
    """Standalone tests for PolicyManager without engine dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PolicyManager()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.manager.clear_cache()

    def test_01_predefined_strict_profile(self):
        """Test loading predefined strict profile."""
        success, policy, msg = self.manager.load_policy("strict")
        assert success, f"Failed to load strict profile: {msg}"
        assert policy is not None, "Policy object is None"
        assert policy.constraints.max_autonomy_level == 1
        assert policy.constraints.require_verification == True

    def test_02_predefined_balanced_profile(self):
        """Test loading predefined balanced profile."""
        success, policy, msg = self.manager.load_policy("balanced")
        assert success, f"Failed to load balanced profile: {msg}"
        assert policy is not None
        assert policy.constraints.max_autonomy_level == 3

    def test_03_predefined_permissive_profile(self):
        """Test loading predefined permissive profile."""
        success, policy, msg = self.manager.load_policy("permissive")
        assert success, f"Failed to load permissive profile: {msg}"
        assert policy is not None
        assert policy.constraints.max_autonomy_level == 4
        assert policy.constraints.require_verification == False

    def test_04_get_ethics_weights(self):
        """Test retrieving ethics weights from policy."""
        weights = self.manager.get_ethics_weights("balanced")
        assert "utilitarian" in weights
        assert "deontological" in weights
        assert "virtue" in weights
        assert "care" in weights
        total = (
            weights["utilitarian"]
            + weights["deontological"]
            + weights["virtue"]
            + weights["care"]
        )
        assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, not 1.0"

    def test_05_validate_allowed_operation(self):
        """Test validating allowed operation."""
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "balanced", code_size=100
        )
        assert is_allowed, f"Operation should be allowed: {reason}"

    def test_06_validate_disallowed_operation(self):
        """Test validating explicitly disallowed operation."""
        is_allowed, reason = self.manager.validate_operation("rm -rf", "balanced")
        assert not is_allowed, "rm -rf should be disallowed"
        assert "disallowed" in reason

    def test_07_validate_oversized_code_strict(self):
        """Test validation rejects code exceeding size limit in strict mode."""
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=2000
        )
        assert not is_allowed, "Oversized code should be rejected"
        assert "exceeds" in reason

    def test_08_policy_caching(self):
        """Test that policies are cached."""
        success1, policy1, _ = self.manager.load_policy("balanced")
        success2, policy2, _ = self.manager.load_policy("balanced")
        assert success1, "First load failed"
        assert success2, "Second load failed"
        # Same object reference indicates caching
        assert policy1 is policy2, "Policies should be cached (same object)"

    def test_09_clear_cache(self):
        """Test clearing policy cache."""
        self.manager.load_policy("balanced")
        assert len(self.manager.policies) > 0
        self.manager.clear_cache()
        assert len(self.manager.policies) == 0

    def test_10_list_available_profiles(self):
        """Test listing available profiles."""
        profiles = self.manager.list_available_profiles()
        assert "strict" in profiles
        assert "balanced" in profiles
        assert "permissive" in profiles

    def test_11_get_policy_info(self):
        """Test retrieving policy information."""
        info = self.manager.get_policy_info("balanced")
        assert info is not None
        assert "version" in info
        assert "max_autonomy_level" in info
        assert "profiles" in info
        assert info["max_autonomy_level"] == 3

    def test_12_policy_hash_calculation(self):
        """Test policy hash is calculated correctly."""
        success, policy, _ = self.manager.load_policy("balanced")
        assert success
        assert policy.policy_hash is not None
        assert len(policy.policy_hash) == 64  # SHA-256 is 64 hex chars

    def test_13_ethics_profile_validation(self):
        """Test EthicsProfile weight validation."""
        try:
            # Invalid weights: 0.5 + 0.5 + 0.1 + 0.1 = 1.2 (not 1.0)
            bad_profile = EthicsProfile(
                utilitarian=0.5,
                deontological=0.5,
                virtue=0.1,
                care=0.1,  # Sum = 1.2, will fail on init
            )
            assert False, "Should have raised ValueError for invalid weights"
        except ValueError as e:
            assert "sum to 1.0" in str(e)

    def test_14_policy_validator_schema(self):
        """Test PolicyValidator schema validation."""
        validator = PolicyValidator()
        valid_policy = {
            "version": "1.0",
            "metadata": {
                "version": "1.0",
                "created_by": "Test",
            },
            "profiles": {
                "test": {
                    "utilitarian": 0.25,
                    "deontological": 0.25,
                    "virtue": 0.25,
                    "care": 0.25,
                }
            },
            "constraints": {
                "max_autonomy_level": 3,
            },
        }
        is_valid, errors = validator.validate_schema(valid_policy)
        assert is_valid, f"Valid policy failed validation: {errors}"
        assert len(errors) == 0

    def test_15_strict_mode_code_size_limit(self):
        """Test strict mode enforces code size limit."""
        # 1000 line limit in strict mode, so 500 should be ALLOWED
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=500
        )
        assert is_allowed, f"500 lines should be under strict limit of 1000: {reason}"

        # But 1500 should NOT be allowed
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=1500
        )
        assert not is_allowed, "1500 lines should exceed strict limit of 1000"


def run_tests():
    """Run all tests with formatted output."""
    print("=" * 70)
    print("TASK 1.2: POLICY MANAGER - UNIT TESTS")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPolicyManagerStandalone)

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    print()

    if result.wasSuccessful():
        print("PASS ALL TESTS PASSED")
        return 0
    print("FAIL SOME TESTS FAILED")
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
