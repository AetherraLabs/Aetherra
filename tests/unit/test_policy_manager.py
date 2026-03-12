"""
Unit tests for PolicyManager - Ethical policy loading and validation.

Tests cover:
- Policy file loading (YAML, JSON)
- Schema validation
- Semantic validation
- Profile management
- Caching and TTL
- Environment variable overrides
- Operation validation
- Ethics weight calculation
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Aetherra.aetherra_core.system.policy_manager import (
    EthicsProfile,
    Policy,
    PolicyManager,
    PolicyMetadata,
    PolicyValidator,
    SafetyConstraints,
)


class TestEthicsProfile(unittest.TestCase):
    """Test EthicsProfile dataclass."""

    def test_01_create_valid_profile(self):
        """Test creating valid ethics profile."""
        profile = EthicsProfile(
            utilitarian=0.25,
            deontological=0.25,
            virtue=0.25,
            care=0.25,
        )
        self.assertEqual(profile.utilitarian, 0.25)
        self.assertEqual(profile.deontological, 0.25)
        self.assertEqual(profile.virtue, 0.25)
        self.assertEqual(profile.care, 0.25)

    def test_02_invalid_weights_sum(self):
        """Test that weights must sum to 1.0."""
        with self.assertRaises(ValueError):
            EthicsProfile(
                utilitarian=0.5,
                deontological=0.5,
                virtue=0.0,
                care=0.0,
            )

    def test_03_normalize_weights(self):
        """Test weight normalization."""
        profile = EthicsProfile(
            utilitarian=2.0,
            deontological=2.0,
            virtue=2.0,
            care=2.0,
        )
        profile.normalize()
        total = (
            profile.utilitarian + profile.deontological + profile.virtue + profile.care
        )
        self.assertAlmostEqual(total, 1.0, places=2)


class TestSafetyConstraints(unittest.TestCase):
    """Test SafetyConstraints dataclass."""

    def test_01_default_constraints(self):
        """Test default safety constraints."""
        constraints = SafetyConstraints()
        self.assertEqual(constraints.max_autonomy_level, 3)
        self.assertTrue(constraints.require_verification)
        self.assertTrue(constraints.audit_trail)

    def test_02_custom_constraints(self):
        """Test custom safety constraints."""
        constraints = SafetyConstraints(
            max_autonomy_level=5,
            require_verification=False,
            max_code_generation_size=50000,
        )
        self.assertEqual(constraints.max_autonomy_level, 5)
        self.assertFalse(constraints.require_verification)
        self.assertEqual(constraints.max_code_generation_size, 50000)

    def test_03_disallowed_operations(self):
        """Test disallowed operations list."""
        constraints = SafetyConstraints()
        self.assertIn("rm -rf", constraints.disallowed_operations)
        self.assertIn("format C:", constraints.disallowed_operations)


class TestPolicyValidator(unittest.TestCase):
    """Test PolicyValidator schema and semantic validation."""

    def setUp(self):
        """Set up validator for tests."""
        self.validator = PolicyValidator()

    def test_01_valid_policy_schema(self):
        """Test validation of valid policy schema."""
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
        is_valid, errors = self.validator.validate_schema(valid_policy)
        self.assertTrue(is_valid, f"Valid policy failed: {errors}")
        self.assertEqual(len(errors), 0)

    def test_02_missing_required_fields(self):
        """Test validation catches missing required fields."""
        invalid_policy = {
            "version": "1.0",
            "metadata": {"version": "1.0"},
            # Missing profiles and constraints
        }
        is_valid, errors = self.validator.validate_schema(invalid_policy)
        self.assertFalse(is_valid)
        self.assertTrue(any("profiles" in e for e in errors))

    def test_03_invalid_weights_sum(self):
        """Test validation catches illegal weight sums."""
        invalid_policy = {
            "version": "1.0",
            "metadata": {
                "version": "1.0",
                "created_by": "Test",
            },
            "profiles": {
                "test": {
                    "utilitarian": 0.5,
                    "deontological": 0.5,
                    "virtue": 0.0,
                    "care": 0.0,  # Sum = 1.0, but test the invalid case
                }
            },
            "constraints": {},
        }
        # Change to invalid sum
        invalid_policy["profiles"]["test"]["virtue"] = 0.1
        is_valid, errors = self.validator.validate_schema(invalid_policy)
        self.assertFalse(is_valid)

    def test_04_invalid_autonomy_level(self):
        """Test validation catches invalid autonomy levels."""
        invalid_policy = {
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
                "max_autonomy_level": 10,  # Invalid: > 5
            },
        }
        is_valid, errors = self.validator.validate_schema(invalid_policy)
        self.assertFalse(is_valid)

    def test_05_invalid_code_size_limit(self):
        """Test validation catches invalid code size limits."""
        invalid_policy = {
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
                "max_code_generation_size": 50,  # Invalid: < 100
            },
        }
        is_valid, errors = self.validator.validate_schema(invalid_policy)
        self.assertFalse(is_valid)


class TestPolicyManager(unittest.TestCase):
    """Test PolicyManager loading and validation."""

    def setUp(self):
        """Set up manager and temporary directory for testing."""
        self.manager = PolicyManager()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.manager.clear_cache()

    def test_01_predefined_strict_profile(self):
        """Test loading predefined strict profile."""
        success, policy, msg = self.manager.load_policy("strict")
        self.assertTrue(success)
        self.assertIsNotNone(policy)
        self.assertEqual(policy.constraints.max_autonomy_level, 1)
        self.assertTrue(policy.constraints.require_verification)

    def test_02_predefined_balanced_profile(self):
        """Test loading predefined balanced profile."""
        success, policy, msg = self.manager.load_policy("balanced")
        self.assertTrue(success)
        self.assertIsNotNone(policy)
        self.assertEqual(policy.constraints.max_autonomy_level, 3)

    def test_03_predefined_permissive_profile(self):
        """Test loading predefined permissive profile."""
        success, policy, msg = self.manager.load_policy("permissive")
        self.assertTrue(success)
        self.assertIsNotNone(policy)
        self.assertEqual(policy.constraints.max_autonomy_level, 4)
        self.assertFalse(policy.constraints.require_verification)

    def test_04_get_ethics_weights(self):
        """Test retrieving ethics weights from policy."""
        weights = self.manager.get_ethics_weights("balanced")
        self.assertIn("utilitarian", weights)
        self.assertIn("deontological", weights)
        self.assertIn("virtue", weights)
        self.assertIn("care", weights)
        total = (
            weights["utilitarian"]
            + weights["deontological"]
            + weights["virtue"]
            + weights["care"]
        )
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_05_validate_allowed_operation(self):
        """Test validating allowed operation."""
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "balanced", code_size=100
        )
        self.assertTrue(is_allowed)

    def test_06_validate_disallowed_operation(self):
        """Test validating explicitly disallowed operation."""
        is_allowed, reason = self.manager.validate_operation("rm -rf", "balanced")
        self.assertFalse(is_allowed)
        self.assertIn("disallowed", reason)

    def test_07_validate_oversized_code(self):
        """Test validation rejects code exceeding size limit."""
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=2000
        )
        self.assertFalse(is_allowed)
        self.assertIn("exceeds", reason)

    def test_08_policy_caching(self):
        """Test that policies are cached."""
        success1, policy1, _ = self.manager.load_policy("balanced")
        success2, policy2, _ = self.manager.load_policy("balanced")
        self.assertTrue(success1)
        self.assertTrue(success2)
        # Same object reference indicates caching
        self.assertIs(policy1, policy2)

    def test_09_cache_expiration(self):
        """Test cache TTL expiration."""
        manager = PolicyManager(cache_ttl=1)  # 1 second TTL
        # Load policy
        success, policy, _ = manager.load_policy("balanced")
        self.assertTrue(success)
        # Check it's cached
        self.assertIn("balanced", manager.policies)
        # Simulate expiration
        manager.policies["balanced"].loaded_at = datetime.now() - timedelta(seconds=2)
        # Load again (should reload)
        success, policy2, msg = manager.load_policy("balanced", force_refresh=False)
        self.assertIn("loaded", msg.lower())

    def test_10_clear_cache(self):
        """Test clearing policy cache."""
        self.manager.load_policy("balanced")
        self.assertGreater(len(self.manager.policies), 0)
        self.manager.clear_cache()
        self.assertEqual(len(self.manager.policies), 0)

    def test_11_list_available_profiles(self):
        """Test listing available profiles."""
        profiles = self.manager.list_available_profiles()
        self.assertIn("strict", profiles)
        self.assertIn("balanced", profiles)
        self.assertIn("permissive", profiles)

    def test_12_get_policy_info(self):
        """Test retrieving policy information."""
        info = self.manager.get_policy_info("balanced")
        self.assertIsNotNone(info)
        self.assertIn("version", info)
        self.assertIn("max_autonomy_level", info)
        self.assertIn("profiles", info)
        self.assertEqual(info["max_autonomy_level"], 3)

    def test_13_policy_hash_calculation(self):
        """Test policy hash is calculated correctly."""
        success, policy, _ = self.manager.load_policy("balanced")
        self.assertTrue(success)
        self.assertIsNotNone(policy.policy_hash)
        self.assertEqual(len(policy.policy_hash), 64)  # SHA-256 is 64 hex chars

    def test_14_load_from_json_file(self):
        """Test loading policy from JSON file."""
        # Create test policy file
        policy_dict = {
            "version": "1.0",
            "metadata": {
                "version": "1.0",
                "created_by": "Test",
                "description": "Test policy",
            },
            "profiles": {
                "test": {
                    "utilitarian": 0.3,
                    "deontological": 0.3,
                    "virtue": 0.2,
                    "care": 0.2,
                }
            },
            "constraints": {
                "max_autonomy_level": 2,
                "require_verification": True,
                "max_code_generation_size": 5000,
            },
        }
        policy_file = Path(self.temp_dir) / "test.aetherra-policy"
        with open(policy_file, "w") as f:
            json.dump(policy_dict, f)

        # Load from file manually
        success, policy, msg = self.manager._load_from_file(str(policy_file))
        self.assertTrue(success)
        self.assertIsNotNone(policy)
        self.assertEqual(policy.constraints.max_autonomy_level, 2)

    def test_15_operation_validation_strict_mode(self):
        """Test operation validation in strict mode."""
        # Strict mode should reject large code
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=500
        )
        self.assertFalse(is_allowed)

        # But small code should be allowed
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=100
        )
        self.assertTrue(is_allowed)


class TestPolicyCaching(unittest.TestCase):
    """Test policy caching behavior."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PolicyManager(cache_ttl=3600)

    def tearDown(self):
        """Clean up."""
        self.manager.clear_cache()

    def test_01_cache_hit(self):
        """Test cache hit returns same instance."""
        self.manager.load_policy("balanced")
        policy1 = self.manager.policies["balanced"]
        success, policy2, _ = self.manager.load_policy("balanced")
        self.assertIs(policy1, policy2)

    def test_02_force_refresh_reloads(self):
        """Test force_refresh bypasses cache."""
        success, policy1, _ = self.manager.load_policy("balanced")
        success, policy2, _ = self.manager.load_policy("balanced", force_refresh=True)
        # New instance after refresh
        self.assertIsNot(policy1, policy2)

    def test_03_multiple_profiles_cached(self):
        """Test multiple profiles can be cached independently."""
        self.manager.load_policy("strict")
        self.manager.load_policy("balanced")
        self.manager.load_policy("permissive")
        self.assertEqual(len(self.manager.policies), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
