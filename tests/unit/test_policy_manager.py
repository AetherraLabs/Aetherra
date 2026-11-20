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

# Standard library imports
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.system.policy_manager import (
    EthicsProfile,
    PolicyManager,
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
        assert profile.utilitarian == 0.25
        assert profile.deontological == 0.25
        assert profile.virtue == 0.25
        assert profile.care == 0.25

    def test_02_invalid_weights_sum(self):
        """Test that zero weights are rejected even when the sum is 1.0."""
        with pytest.raises(
            ValueError, match="Ethics weights must be positive and non-zero"
        ):
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
        assert round(abs(total - 1.0), 2) == 0


class TestSafetyConstraints(unittest.TestCase):
    """Test SafetyConstraints dataclass."""

    def test_01_default_constraints(self):
        """Test default safety constraints."""
        constraints = SafetyConstraints()
        assert constraints.max_autonomy_level == 3
        assert constraints.require_verification
        assert constraints.audit_trail

    def test_02_custom_constraints(self):
        """Test custom safety constraints."""
        constraints = SafetyConstraints(
            max_autonomy_level=5,
            require_verification=False,
            max_code_generation_size=50000,
        )
        assert constraints.max_autonomy_level == 5
        assert not constraints.require_verification
        assert constraints.max_code_generation_size == 50000

    def test_03_disallowed_operations(self):
        """Test disallowed operations list."""
        constraints = SafetyConstraints()
        assert "rm -rf" in constraints.disallowed_operations
        assert "format C:" in constraints.disallowed_operations


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
        assert is_valid, f"Valid policy failed: {errors}"
        assert len(errors) == 0

    def test_02_missing_required_fields(self):
        """Test validation catches missing required fields."""
        invalid_policy = {
            "version": "1.0",
            "metadata": {"version": "1.0"},
            # Missing profiles and constraints
        }
        is_valid, errors = self.validator.validate_schema(invalid_policy)
        assert not is_valid
        assert any("profiles" in e for e in errors)

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
        assert not is_valid

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
        assert not is_valid

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
        assert not is_valid


class TestPolicyManager(unittest.TestCase):
    """Test PolicyManager loading and validation."""

    def setUp(self):
        """Set up manager and temporary directory for testing."""
        self.manager = PolicyManager()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        # Standard library imports
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.manager.clear_cache()

    def test_01_predefined_strict_profile(self):
        """Test loading predefined strict profile."""
        success, policy, msg = self.manager.load_policy("strict")
        assert success
        assert policy is not None
        assert policy.constraints.max_autonomy_level == 1
        assert policy.constraints.require_verification

    def test_02_predefined_balanced_profile(self):
        """Test loading predefined balanced profile."""
        success, policy, msg = self.manager.load_policy("balanced")
        assert success
        assert policy is not None
        assert policy.constraints.max_autonomy_level == 3

    def test_03_predefined_permissive_profile(self):
        """Test loading predefined permissive profile."""
        success, policy, msg = self.manager.load_policy("permissive")
        assert success
        assert policy is not None
        assert policy.constraints.max_autonomy_level == 4
        assert not policy.constraints.require_verification

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
        assert round(abs(total - 1.0), 2) == 0

    def test_05_validate_allowed_operation(self):
        """Test validating allowed operation."""
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "balanced", code_size=100
        )
        assert is_allowed

    def test_06_validate_disallowed_operation(self):
        """Test validating explicitly disallowed operation."""
        is_allowed, reason = self.manager.validate_operation("rm -rf", "balanced")
        assert not is_allowed
        assert "disallowed" in reason

    def test_07_validate_oversized_code(self):
        """Test validation rejects code exceeding size limit."""
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=2000
        )
        assert not is_allowed
        assert "exceeds" in reason

    def test_08_policy_caching(self):
        """Test that policies are cached."""
        success1, policy1, _ = self.manager.load_policy("balanced")
        success2, policy2, _ = self.manager.load_policy("balanced")
        assert success1
        assert success2
        # Same object reference indicates caching
        assert policy1 is policy2

    def test_09_cache_expiration(self):
        """Test cache TTL expiration."""
        manager = PolicyManager(cache_ttl=1)  # 1 second TTL
        # Load policy
        success, policy, _ = manager.load_policy("balanced")
        assert success
        # Check it's cached
        assert "balanced" in manager.policies
        # Simulate expiration
        manager.policies["balanced"].loaded_at = datetime.now() - timedelta(seconds=2)
        # Load again (should reload)
        success, policy2, msg = manager.load_policy("balanced", force_refresh=False)
        assert "loaded" in msg.lower()

    def test_10_clear_cache(self):
        """Test clearing policy cache."""
        self.manager.load_policy("balanced")
        assert len(self.manager.policies) > 0
        self.manager.clear_cache()
        assert len(self.manager.policies) == 0

    def test_11_list_available_profiles(self):
        """Test listing available profiles."""
        profiles = self.manager.list_available_profiles()
        assert "strict" in profiles
        assert "balanced" in profiles
        assert "permissive" in profiles

    def test_12_get_policy_info(self):
        """Test retrieving policy information."""
        info = self.manager.get_policy_info("balanced")
        assert info is not None
        assert "version" in info
        assert "max_autonomy_level" in info
        assert "profiles" in info
        assert info["max_autonomy_level"] == 3

    def test_13_policy_hash_calculation(self):
        """Test policy hash is calculated correctly."""
        success, policy, _ = self.manager.load_policy("balanced")
        assert success
        assert policy.policy_hash is not None
        assert len(policy.policy_hash) == 64  # SHA-256 is 64 hex chars

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
        assert success
        assert policy is not None
        assert policy.constraints.max_autonomy_level == 2

    def test_15_operation_validation_strict_mode(self):
        """Test operation validation in strict mode."""
        # Strict mode should reject large code
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=500
        )
        assert not is_allowed

        # But small code should be allowed
        is_allowed, reason = self.manager.validate_operation(
            "code_generation", "strict", code_size=100
        )
        assert is_allowed


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
        assert policy1 is policy2

    def test_02_force_refresh_reloads(self):
        """Test force_refresh bypasses cache."""
        success, policy1, _ = self.manager.load_policy("balanced")
        success, policy2, _ = self.manager.load_policy("balanced", force_refresh=True)
        # New instance after refresh
        assert policy1 is not policy2

    def test_03_multiple_profiles_cached(self):
        """Test multiple profiles can be cached independently."""
        self.manager.load_policy("strict")
        self.manager.load_policy("balanced")
        self.manager.load_policy("permissive")
        assert len(self.manager.policies) == 3


if __name__ == "__main__":
    unittest.main(verbosity=2)
