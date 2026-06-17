"""
Policy Manager - Load and validate ethical/safety policies.

Manages ethical frameworks and safety constraints for autonomous operations.
Supports multiple profiles (strict, balanced, permissive) with schema validation.

Features:
  - Load policies from file system or environment variables
  - Support predefined profiles with ethical weights
  - JSON schema validation
  - In-memory caching with TTL
  - Environment variable overrides
  - Safety constraint validation

Example:
    >>> manager = PolicyManager()
    >>> weights = manager.get_ethics_weights("balanced")
    >>> is_allowed = manager.validate_operation("code_generation")
"""

import hashlib
import json
import logging
import math
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)


@dataclass
class EthicsProfile:
    """Ethical decision-making profile with weighted frameworks."""

    utilitarian: float = 0.25
    """Maximize overall good/benefit (0.0-1.0)"""
    deontological: float = 0.25
    """Follow principles/rules (0.0-1.0)"""
    virtue: float = 0.25
    """Cultivate virtues/character (0.0-1.0)"""
    care: float = 0.25
    """Prioritize relationships/empathy (0.0-1.0)"""

    def __post_init__(self):
        """Validate that weights are finite, positive values."""
        weights = [self.utilitarian, self.deontological, self.virtue, self.care]
        if not all(isinstance(weight, (int, float)) for weight in weights):
            raise ValueError("Ethics weights must be numeric")
        if not all(math.isfinite(float(weight)) for weight in weights):
            raise ValueError("Ethics weights must be finite")
        if any(float(weight) <= 0 for weight in weights):
            raise ValueError("Ethics weights must be positive and non-zero")

    def normalize(self):
        """Normalize weights to sum to 1.0."""
        total = sum([self.utilitarian, self.deontological, self.virtue, self.care])
        if total > 0:
            self.utilitarian /= total
            self.deontological /= total
            self.virtue /= total
            self.care /= total


@dataclass
class SafetyConstraints:
    """Safety constraints for autonomous operations."""

    max_autonomy_level: int = 3
    """Maximum autonomy level allowed (1-5, where 5 is unrestricted)"""
    require_verification: bool = True
    """Require signature verification for all operations"""
    audit_trail: bool = True
    """Log all operations to audit trail"""
    max_code_generation_size: int = 10000
    """Maximum lines of code to generate"""
    disallowed_operations: List[str] = field(
        default_factory=lambda: [
            "rm -rf",
            "format C:",
            "dd if=/dev/zero",
            ":/format",
        ]
    )
    """Operations explicitly disallowed"""
    sandboxing: bool = True
    """Run generated code in sandbox"""
    rollback_on_failure: bool = True
    """Automatically rollback changes on test failure"""


@dataclass
class PolicyMetadata:
    """Policy file metadata."""

    version: str = "1.0"
    """Policy format version"""
    created_by: str = "Aetherra Labs"
    """Policy creator"""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """Creation timestamp"""
    effective_date: str = field(default_factory=lambda: datetime.now().isoformat())
    """When this policy becomes effective"""
    description: str = "Default policy"
    """Policy description"""


@dataclass
class Policy:
    """Complete policy definition."""

    metadata: PolicyMetadata
    profiles: Dict[str, EthicsProfile]
    constraints: SafetyConstraints
    policy_hash: str = ""
    loaded_at: datetime = field(default_factory=datetime.now)

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of policy content."""
        content = json.dumps(asdict(self), sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def is_expired(self, ttl_seconds: int = 3600) -> bool:
        """Check if policy cache has expired."""
        age = datetime.now() - self.loaded_at
        return age > timedelta(seconds=ttl_seconds)


class PolicyValidator:
    """Validates policies against schema and semantic rules."""

    # JSON Schema for policy files
    POLICY_SCHEMA = {
        "type": "object",
        "required": ["version", "metadata", "profiles", "constraints"],
        "properties": {
            "version": {"type": "string"},
            "metadata": {
                "type": "object",
                "properties": {
                    "version": {"type": "string"},
                    "created_by": {"type": "string"},
                    "created_at": {"type": "string"},
                    "effective_date": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
            "profiles": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "utilitarian": {"type": "number", "minimum": 0, "maximum": 1},
                        "deontological": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                        },
                        "virtue": {"type": "number", "minimum": 0, "maximum": 1},
                        "care": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                },
            },
            "constraints": {
                "type": "object",
                "properties": {
                    "max_autonomy_level": {"type": "integer", "minimum": 1, "maximum": 5},
                    "require_verification": {"type": "boolean"},
                    "audit_trail": {"type": "boolean"},
                    "max_code_generation_size": {"type": "integer", "minimum": 100},
                    "disallowed_operations": {"type": "array", "items": {"type": "string"}},
                    "sandboxing": {"type": "boolean"},
                    "rollback_on_failure": {"type": "boolean"},
                },
            },
        },
    }

    @staticmethod
    def validate_schema(policy_dict: dict) -> Tuple[bool, List[str]]:
        """
        Validate policy against JSON schema.

        Args:
            policy_dict: Policy dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required top-level keys
        required = ["version", "metadata", "profiles", "constraints"]
        for key in required:
            if key not in policy_dict:
                errors.append(f"Missing required key: {key}")

        # Validate metadata
        if "metadata" in policy_dict:
            metadata = policy_dict["metadata"]
            if not isinstance(metadata, dict):
                errors.append("metadata must be a dictionary")
            else:
                if "version" not in metadata:
                    errors.append("metadata.version is required")
                if "created_by" not in metadata:
                    errors.append("metadata.created_by is required")

        # Validate profiles
        if "profiles" in policy_dict:
            profiles = policy_dict["profiles"]
            if not isinstance(profiles, dict):
                errors.append("profiles must be a dictionary")
            else:
                for profile_name, profile_data in profiles.items():
                    if not isinstance(profile_data, dict):
                        errors.append(f"Profile '{profile_name}' must be a dictionary")
                        continue

                    # Check ethics weights
                    weights = [
                        profile_data.get("utilitarian", 0),
                        profile_data.get("deontological", 0),
                        profile_data.get("virtue", 0),
                        profile_data.get("care", 0),
                    ]
                    total = sum(weights)
                    if not (0.99 <= total <= 1.01):
                        errors.append(f"Profile '{profile_name}' weights sum to {total}, not 1.0")

                    # Check weight ranges
                    for weight_name, weight_val in [
                        ("utilitarian", profile_data.get("utilitarian")),
                        ("deontological", profile_data.get("deontological")),
                        ("virtue", profile_data.get("virtue")),
                        ("care", profile_data.get("care")),
                    ]:
                        if weight_val is not None:
                            if not isinstance(weight_val, (int, float)):
                                errors.append(
                                    f"Profile '{profile_name}.{weight_name}' must be numeric"
                                )
                            elif not (0 < weight_val <= 1):
                                errors.append(
                                    f"Profile '{profile_name}.{weight_name}' must be greater than 0 and at most 1"
                                )

        # Validate constraints
        if "constraints" in policy_dict:
            constraints = policy_dict["constraints"]
            if not isinstance(constraints, dict):
                errors.append("constraints must be a dictionary")
            else:
                # Check autonomy level
                if "max_autonomy_level" in constraints:
                    level = constraints["max_autonomy_level"]
                    if not isinstance(level, int) or not (1 <= level <= 5):
                        errors.append("constraints.max_autonomy_level must be between 1 and 5")

                # Check code size limit
                if "max_code_generation_size" in constraints:
                    size = constraints["max_code_generation_size"]
                    if not isinstance(size, int) or size < 100:
                        errors.append("constraints.max_code_generation_size must be >= 100")

                # Check boolean fields
                for bool_field in [
                    "require_verification",
                    "audit_trail",
                    "sandboxing",
                    "rollback_on_failure",
                ]:
                    if bool_field in constraints:
                        val = constraints[bool_field]
                        if not isinstance(val, bool):
                            errors.append(f"constraints.{bool_field} must be boolean")

        return len(errors) == 0, errors

    @staticmethod
    def validate_semantic(policy: Policy) -> Tuple[bool, List[str]]:
        """
        Semantic validation of policy beyond schema.

        Args:
            policy: Policy object to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate that profiles have valid EthicsProfile weights
        for profile_name, profile in policy.profiles.items():
            try:
                # Test that profile can be created
                _ = EthicsProfile(
                    utilitarian=profile.utilitarian,
                    deontological=profile.deontological,
                    virtue=profile.virtue,
                    care=profile.care,
                )
            except ValueError as e:
                errors.append(f"Profile '{profile_name}': {str(e)}")

        return len(errors) == 0, errors


class PolicyManager:
    """Manage and load ethical/safety policies for autonomous operations."""

    # Predefined policy profiles (as dictionaries for validation)
    PREDEFINED_PROFILES = {
        "strict": {
            "version": "1.0",
            "metadata": {
                "version": "1.0",
                "created_by": "Aetherra Labs",
                "description": "Strict policy: maximum safety and verification",
            },
            "profiles": {
                "strict": {
                    "utilitarian": 0.1,
                    "deontological": 0.7,
                    "virtue": 0.1,
                    "care": 0.1,
                }
            },
            "constraints": {
                "max_autonomy_level": 1,
                "require_verification": True,
                "audit_trail": True,
                "max_code_generation_size": 100,
                "sandboxing": True,
                "rollback_on_failure": True,
            },
        },
        "balanced": {
            "version": "1.0",
            "metadata": {
                "version": "1.0",
                "created_by": "Aetherra Labs",
                "description": "Balanced policy: moderate safety and autonomy",
            },
            "profiles": {
                "balanced": {
                    "utilitarian": 0.25,
                    "deontological": 0.25,
                    "virtue": 0.25,
                    "care": 0.25,
                }
            },
            "constraints": {
                "max_autonomy_level": 3,
                "require_verification": True,
                "audit_trail": True,
                "max_code_generation_size": 10000,
                "sandboxing": True,
                "rollback_on_failure": True,
            },
        },
        "permissive": {
            "version": "1.0",
            "metadata": {
                "version": "1.0",
                "created_by": "Aetherra Labs",
                "description": "Permissive policy: higher autonomy, lower restrictions",
            },
            "profiles": {
                "permissive": {
                    "utilitarian": 0.6,
                    "deontological": 0.1,
                    "virtue": 0.15,
                    "care": 0.15,
                }
            },
            "constraints": {
                "max_autonomy_level": 4,
                "require_verification": False,
                "audit_trail": True,
                "max_code_generation_size": 50000,
                "sandboxing": False,
                "rollback_on_failure": False,
            },
        },
    }

    def __init__(
        self,
        policy_dir: Optional[str] = None,
        cache_ttl: int = 3600,
    ):
        """
        Initialize PolicyManager.

        Args:
            policy_dir: Custom policy directory (overrides search paths)
            cache_ttl: Cache time-to-live in seconds
        """
        self.policy_dir = policy_dir or self._find_policy_dir()
        self.cache_ttl = cache_ttl
        self.policies: Dict[str, Policy] = {}
        self.validator = PolicyValidator()
        logger.info(f"PolicyManager initialized with policy_dir: {self.policy_dir}")

    def _find_policy_dir(self) -> str:
        """
        Find policy directory from multiple search paths.

        Search order:
          1. AETHERRA_POLICY_DIR environment variable
          2. ./policies/ (relative to current directory)
          3. ~/.aetherra/policies/ (user home directory)
          4. Return default even if not found

        Returns:
            Path to policy directory
        """
        # Check environment variable
        env_dir = os.getenv("AETHERRA_POLICY_DIR")
        if env_dir and os.path.isdir(env_dir):
            logger.debug(f"Found policy dir from AETHERRA_POLICY_DIR: {env_dir}")
            return env_dir

        # Check local policies directory
        local_dir = "./policies"
        if os.path.isdir(local_dir):
            logger.debug(f"Found policy dir at {local_dir}")
            return local_dir

        # Check user home directory
        home_dir = Path.home() / ".aetherra" / "policies"
        if home_dir.is_dir():
            logger.debug(f"Found policy dir in home: {home_dir}")
            return str(home_dir)

        # Return default
        default_dir = "./policies"
        logger.debug(f"Using default policy dir: {default_dir}")
        return default_dir

    def load_policy(
        self,
        profile: str = "balanced",
        force_refresh: bool = False,
    ) -> Tuple[bool, Optional[Policy], str]:
        """
        Load policy by profile name.

        Tries in this order:
          1. Predefined profiles (strict, balanced, permissive)
          2. File system (./policies/<profile>.aetherra-policy)
          3. Environment variable override (AETHERRA_POLICY_<PROFILE>)

        Args:
            profile: Profile name (e.g., "balanced")
            force_refresh: Ignore cache and reload from disk

        Returns:
            Tuple of (success, Policy or None, message)
        """
        if profile in self.policies and not force_refresh:
            policy = self.policies[profile]
            if not policy.is_expired(self.cache_ttl):
                logger.debug(f"Using cached policy: {profile}")
                return True, policy, f"Loaded from cache: {profile}"

        # Try predefined profiles first
        if profile in self.PREDEFINED_PROFILES:
            policy_dict = self.PREDEFINED_PROFILES[profile]
            is_valid, errors = self.validator.validate_schema(policy_dict)
            if not is_valid:
                msg = f"Predefined policy '{profile}' failed validation: {errors}"
                logger.error(msg)
                return False, None, msg

            policy = self._dict_to_policy(policy_dict)
            self.policies[profile] = policy
            logger.info(f"Loaded predefined policy: {profile}")
            return True, policy, f"Loaded predefined policy: {profile}"

        # Try loading from file system
        policy_file = Path(self.policy_dir) / f"{profile}.aetherra-policy"
        if policy_file.exists():
            success, policy, msg = self._load_from_file(str(policy_file))
            if success and policy:
                self.policies[profile] = policy
            return success, policy, msg

        # Try environment variable override
        env_var = f"AETHERRA_POLICY_{profile.upper()}"
        env_path = os.getenv(env_var)
        if env_path and os.path.isfile(env_path):
            success, policy, msg = self._load_from_file(env_path)
            if success and policy:
                self.policies[profile] = policy
            return success, policy, msg

        msg = f"Policy not found: {profile}"
        logger.warning(msg)
        return False, None, msg

    def _load_from_file(self, file_path: str) -> Tuple[bool, Optional[Policy], str]:
        """
        Load policy from file (YAML or JSON).

        Args:
            file_path: Path to policy file

        Returns:
            Tuple of (success, Policy or None, message)
        """
        try:
            with open(file_path) as f:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    policy_dict = yaml.safe_load(f)
                else:
                    policy_dict = json.load(f)

            if not isinstance(policy_dict, dict):
                return False, None, "Policy file must contain a dictionary"

            # Validate schema
            is_valid, errors = self.validator.validate_schema(policy_dict)
            if not is_valid:
                return False, None, f"Schema validation failed: {errors}"

            # Convert to Policy object
            policy = self._dict_to_policy(policy_dict)

            # Validate semantic rules
            is_valid, errors = self.validator.validate_semantic(policy)
            if not is_valid:
                return False, None, f"Semantic validation failed: {errors}"

            logger.info(f"Loaded policy from file: {file_path}")
            return True, policy, f"Loaded from {file_path}"

        except json.JSONDecodeError as e:
            return False, None, f"JSON parse error: {str(e)}"
        except yaml.YAMLError as e:
            return False, None, f"YAML parse error: {str(e)}"
        except Exception as e:
            logger.error(f"Error loading policy from {file_path}: {e}")
            return False, None, f"Error loading policy: {str(e)}"

    def _dict_to_policy(self, policy_dict: dict) -> Policy:
        """
        Convert dictionary to Policy object.

        Args:
            policy_dict: Policy dictionary

        Returns:
            Policy object
        """
        # Build metadata
        metadata_dict = policy_dict.get("metadata", {})
        metadata = PolicyMetadata(
            version=metadata_dict.get("version", "1.0"),
            created_by=metadata_dict.get("created_by", "Unknown"),
            created_at=metadata_dict.get("created_at", datetime.now().isoformat()),
            effective_date=metadata_dict.get("effective_date", datetime.now().isoformat()),
            description=metadata_dict.get("description", "Policy loaded from file"),
        )

        # Build profiles
        profiles = {}
        for profile_name, profile_dict in policy_dict.get("profiles", {}).items():
            profiles[profile_name] = EthicsProfile(
                utilitarian=profile_dict.get("utilitarian", 0.25),
                deontological=profile_dict.get("deontological", 0.25),
                virtue=profile_dict.get("virtue", 0.25),
                care=profile_dict.get("care", 0.25),
            )

        # Build constraints
        constraints_dict = policy_dict.get("constraints", {})
        constraints = SafetyConstraints(
            max_autonomy_level=constraints_dict.get("max_autonomy_level", 3),
            require_verification=constraints_dict.get("require_verification", True),
            audit_trail=constraints_dict.get("audit_trail", True),
            max_code_generation_size=constraints_dict.get("max_code_generation_size", 10000),
            disallowed_operations=constraints_dict.get(
                "disallowed_operations",
                [
                    "rm -rf",
                    "format C:",
                    "dd if=/dev/zero",
                    ":/format",
                ],
            ),
            sandboxing=constraints_dict.get("sandboxing", True),
            rollback_on_failure=constraints_dict.get("rollback_on_failure", True),
        )

        policy = Policy(
            metadata=metadata,
            profiles=profiles,
            constraints=constraints,
        )
        policy.policy_hash = policy.calculate_hash()
        return policy

    def get_ethics_weights(
        self,
        profile: str = "balanced",
    ) -> Dict[str, float]:
        """
        Get ethics framework weights for a profile.

        Args:
            profile: Profile name (e.g., "balanced")

        Returns:
            Dictionary of ethics weights: {utilitarian, deontological, virtue, care}
        """
        success, policy, _ = self.load_policy(profile)
        if not success or not policy:
            logger.warning(f"Failed to load policy {profile}, using defaults")
            return asdict(EthicsProfile())

        if profile not in policy.profiles:
            logger.warning(
                f"Profile '{profile}' not in policy (available: {list(policy.profiles.keys())})"
            )
            # Return first available profile
            first_profile = next(iter(policy.profiles.values()))
            return asdict(first_profile)

        ethics = policy.profiles[profile]
        return asdict(ethics)

    def validate_operation(
        self,
        operation: str,
        profile: str = "balanced",
        code_size: int = 0,
    ) -> Tuple[bool, str]:
        """
        Validate if operation is allowed by policy.

        Args:
            operation: Operation to validate (e.g., "code_generation")
            profile: Policy profile to check against
            code_size: Size of code in lines (for code generation)

        Returns:
            Tuple of (is_allowed, reason)
        """
        success, policy, _ = self.load_policy(profile)
        if not success or not policy:
            logger.warning(f"Policy {profile} not found, operation denied")
            return False, f"Policy '{profile}' not found"

        constraints = policy.constraints

        # Check if operation is in disallowed list
        if operation in constraints.disallowed_operations:
            return (
                False,
                f"Operation '{operation}' is explicitly disallowed by policy",
            )

        # For code generation, check size limit
        if operation == "code_generation":
            if code_size > constraints.max_code_generation_size:
                return (
                    False,
                    f"Code generation exceeds policy limit "
                    f"({code_size} > {constraints.max_code_generation_size} lines)",
                )

        return True, f"Operation '{operation}' is allowed"

    def clear_cache(self):
        """Clear all cached policies."""
        self.policies.clear()
        logger.info("Policy cache cleared")

    def list_available_profiles(self, profile: str = None) -> List[str]:
        """
        List available profiles in a policy.

        Args:
            profile: Policy name to check (loads if needed)

        Returns:
            List of profile names
        """
        if profile:
            success, policy, _ = self.load_policy(profile)
            if success and policy:
                return list(policy.profiles.keys())
        # Return predefined profile names
        return ["strict", "balanced", "permissive"]

    def get_policy_info(self, profile: str = "balanced") -> Optional[Dict]:
        """
        Get information about a loaded policy.

        Args:
            profile: Profile name

        Returns:
            Dictionary with policy metadata and constraints
        """
        success, policy, _ = self.load_policy(profile)
        if not success or not policy:
            return None

        return {
            "version": policy.metadata.version,
            "created_by": policy.metadata.created_by,
            "description": policy.metadata.description,
            "profiles": list(policy.profiles.keys()),
            "max_autonomy_level": policy.constraints.max_autonomy_level,
            "require_verification": policy.constraints.require_verification,
            "audit_trail": policy.constraints.audit_trail,
            "max_code_generation_size": policy.constraints.max_code_generation_size,
            "sandboxing": policy.constraints.sandboxing,
            "cached": True,
            "loaded_at": policy.loaded_at.isoformat(),
        }
