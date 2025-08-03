#!/usr/bin/env python3
"""
⚙️ Aetherra Configuration Loader
================================

Centralized configuration management for the Aetherra AI Operating System.
Handles loading, validation, and management of system configurations.

This module provides:
- JSON configuration file loading
- Environment variable integration
- Configuration validation and defaults
- Dynamic configuration updates
- Configuration hierarchy management
- Secure credential handling

Author: Aetherra Labs
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""

    pass


class AetherraConfigLoader:
    """
    🔧 Configuration loader and manager for Aetherra OS
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = (
            Path(config_path) if config_path else self._find_config_file()
        )
        self.config_data = {}
        self.environment_overrides = {}
        self.default_config = self._get_default_config()

        # Configuration cache
        self._cache = {}
        self._cache_valid = False

        # Load configuration on initialization
        self._load_configuration()

    def _find_config_file(self) -> Path:
        """Find the configuration file in standard locations"""
        # List of possible config file locations (in order of preference)
        possible_paths = [
            Path.cwd() / "config.json",
            Path.cwd() / "Aetherra" / "config.json",
            Path.cwd() / "aetherra_config.json",
            Path(__file__).parent.parent.parent / "config.json",
            Path.home() / ".aetherra" / "config.json",
            Path("/etc/aetherra/config.json") if sys.platform != "win32" else None,
        ]

        # Filter out None values
        possible_paths = [path for path in possible_paths if path is not None]

        # Find the first existing config file
        for config_path in possible_paths:
            if config_path.exists():
                logger.info(f"📁 Found config file: {config_path}")
                return config_path

        # Default to config.json in current directory
        default_path = Path.cwd() / "config.json"
        logger.info(f"📁 Using default config path: {default_path}")
        return default_path

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "system": {
                "name": "Aetherra AI Operating System",
                "version": "1.0.0",
                "mode": "production",
                "debug": False,
                "log_level": "INFO",
            },
            "gui_enabled": False,
            "web_interface": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 8686,
                "ssl_enabled": False,
            },
            "memory_systems": {
                "quantum": {
                    "enabled": True,
                    "max_capacity": "1GB",
                    "compression_enabled": True,
                },
                "core": {"enabled": True, "persistence": True, "backup_enabled": True},
                "concepts": {
                    "enabled": True,
                    "clustering": True,
                    "max_concepts": 10000,
                },
                "episodic": {
                    "enabled": True,
                    "timeline_tracking": True,
                    "retention_days": 365,
                },
            },
            "plugins": {
                "enabled": True,
                "auto_discovery": True,
                "plugin_directories": [
                    "plugins/",
                    "Aetherra/plugins/",
                    "lyrixa_plugins/",
                ],
                "max_plugins": 100,
                "security_check": True,
            },
            "aetherra_engine": {
                "enabled": True,
                "processing_threads": 4,
                "max_concurrent_tasks": 10,
            },
            "scheduler": {
                "enabled": True,
                "background_tasks": True,
                "max_scheduled_tasks": 50,
            },
            "hub": {
                "enabled": True,
                "url": "http://localhost:3001",
                "auto_sync": True,
                "sync_interval": 300,
            },
            "aether_scripts": {
                "enabled": True,
                "auto_execute": ["system_logger", "daily_reflector"],
                "script_timeout": 300,
            },
            "file_watcher": {
                "enabled": True,
                "analysis_interval": 30,
                "batch_size": 10,
                "auto_relocate": False,
                "auto_optimize": False,
                "monitored_directories": ["."],
                "enable_aether_triggers": True,
            },
            "lyrixa_intelligence": {
                "default_provider": "openai",
                "fallback_providers": ["anthropic", "local"],
                "max_context_length": 8000,
                "temperature": 0.7,
                "memory_integration": True,
                "emotional_modeling": True,
                "learning_enabled": True,
                "max_response_length": 2000,
                "save_learning_on_shutdown": True,
            },
            "ai_providers": {
                "openai": {
                    "enabled": True,
                    "model": "gpt-4",
                    "api_key": "",  # Set via environment variable
                    "timeout": 30,
                },
                "anthropic": {
                    "enabled": True,
                    "model": "claude-3-sonnet-20240229",
                    "api_key": "",  # Set via environment variable
                    "timeout": 30,
                },
                "local": {"enabled": False, "model_path": "", "gpu_enabled": True},
            },
            "logging": {
                "level": "INFO",
                "file": "aetherra_os.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "console_output": True,
            },
            "security": {
                "api_keys_encrypted": False,
                "require_authentication": False,
                "allowed_hosts": ["localhost", "127.0.0.1"],
                "max_request_rate": 100,
            },
            "performance": {
                "cache_enabled": True,
                "cache_size": "100MB",
                "parallel_processing": True,
                "memory_optimization": True,
            },
        }

    def _load_configuration(self):
        """Load configuration from file and environment"""
        try:
            # Start with default configuration
            self.config_data = self.default_config.copy()

            # Load from file if it exists
            if self.config_path.exists():
                self._load_from_file()
            else:
                logger.warning(f"⚠️ Config file not found: {self.config_path}")
                logger.info("📝 Using default configuration")

            # Apply environment variable overrides
            self._load_environment_overrides()

            # Validate configuration
            self._validate_configuration()

            # Mark cache as invalid
            self._cache_valid = False

            logger.info("✅ Configuration loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise ConfigurationError(f"Configuration loading failed: {e}")

    def _load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                file_config = json.load(f)

            # Deep merge with default configuration
            self.config_data = self._deep_merge(self.config_data, file_config)

            logger.info(f"📄 Loaded configuration from {self.config_path}")

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in config file: {e}")
            raise ConfigurationError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            logger.error(f"❌ Error reading config file: {e}")
            raise ConfigurationError(f"Error reading config file: {e}")

    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables"""
        env_prefix = "AETHERRA_"

        # Map environment variables to config paths
        env_mappings = {
            "AETHERRA_DEBUG": "system.debug",
            "AETHERRA_LOG_LEVEL": "logging.level",
            "AETHERRA_GUI_ENABLED": "gui_enabled",
            "AETHERRA_WEB_PORT": "web_interface.port",
            "AETHERRA_WEB_HOST": "web_interface.host",
            "AETHERRA_HUB_URL": "hub.url",
            "AETHERRA_HUB_ENABLED": "hub.enabled",
            "OPENAI_API_KEY": "ai_providers.openai.api_key",
            "ANTHROPIC_API_KEY": "ai_providers.anthropic.api_key",
            "AETHERRA_MEMORY_QUANTUM_ENABLED": "memory_systems.quantum.enabled",
            "AETHERRA_PLUGINS_ENABLED": "plugins.enabled",
            "AETHERRA_INTELLIGENCE_PROVIDER": "lyrixa_intelligence.default_provider",
        }

        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(env_value)
                self._set_nested_config(config_path, converted_value)
                logger.debug(
                    f"🌍 Environment override: {config_path} = {converted_value}"
                )

    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        # Boolean conversion
        if value.lower() in ("true", "1", "yes", "on"):
            return True
        elif value.lower() in ("false", "0", "no", "off"):
            return False

        # Number conversion
        try:
            # Try integer first
            if "." not in value:
                return int(value)
            else:
                return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _set_nested_config(self, path: str, value: Any):
        """Set a nested configuration value using dot notation"""
        keys = path.split(".")
        current = self.config_data

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final value
        current[keys[-1]] = value

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _validate_configuration(self):
        """Validate the loaded configuration"""
        errors = []

        # Validate required fields
        required_fields = [
            "system.name",
            "system.version",
            "web_interface.host",
            "web_interface.port",
        ]

        for field in required_fields:
            if not self._get_nested_value(field):
                errors.append(f"Required field missing: {field}")

        # Validate data types and ranges
        validations = [
            ("web_interface.port", int, lambda x: 1 <= x <= 65535),
            ("plugins.max_plugins", int, lambda x: x > 0),
            ("aetherra_engine.processing_threads", int, lambda x: 1 <= x <= 32),
            (
                "lyrixa_intelligence.temperature",
                (int, float),
                lambda x: 0.0 <= x <= 2.0,
            ),
            ("file_watcher.analysis_interval", int, lambda x: x > 0),
        ]

        for field, expected_type, validator in validations:
            value = self._get_nested_value(field)
            if value is not None:
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Invalid type for {field}: expected {expected_type.__name__}"
                    )
                elif not validator(value):
                    errors.append(f"Invalid value for {field}: {value}")

        # Log warnings for any validation errors
        if errors:
            for error in errors:
                logger.warning(f"⚠️ Configuration validation: {error}")

    def _get_nested_value(self, path: str) -> Any:
        """Get a nested configuration value using dot notation"""
        keys = path.split(".")
        current = self.config_data

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None

    def load_config(self) -> Dict[str, Any]:
        """Public method to get the complete configuration"""
        if not self._cache_valid:
            self._cache = self.config_data.copy()
            self._cache_valid = True

        return self._cache

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with optional default"""
        try:
            value = self._get_nested_value(key)
            return value if value is not None else default
        except Exception:
            return default

    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value"""
        try:
            self._set_nested_config(key, value)
            self._cache_valid = False  # Invalidate cache
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set config value {key}: {e}")
            return False

    def reload(self) -> bool:
        """Reload configuration from file"""
        try:
            self._load_configuration()
            logger.info("🔄 Configuration reloaded")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to reload configuration: {e}")
            return False

    def save(self, backup: bool = True) -> bool:
        """Save current configuration to file"""
        try:
            # Create backup if requested
            if backup and self.config_path.exists():
                backup_path = self.config_path.with_suffix(".json.backup")
                backup_path.write_text(self.config_path.read_text())
                logger.info(f"💾 Created config backup: {backup_path}")

            # Save configuration
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Configuration saved to {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            return False

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a complete configuration section"""
        return self.get(section, {})

    def update_section(self, section: str, updates: Dict[str, Any]) -> bool:
        """Update a configuration section with new values"""
        try:
            current_section = self.get_section(section)
            updated_section = self._deep_merge(current_section, updates)
            return self.set(section, updated_section)
        except Exception as e:
            logger.error(f"❌ Failed to update section {section}: {e}")
            return False

    def get_ai_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get AI provider specific configuration"""
        return self.get(f"ai_providers.{provider}", {})

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return bool(self.get(f"{feature}.enabled", False))

    def get_memory_config(self, memory_type: str) -> Dict[str, Any]:
        """Get memory system specific configuration"""
        return self.get(f"memory_systems.{memory_type}", {})

    def get_plugin_directories(self) -> List[str]:
        """Get list of plugin directories"""
        return self.get("plugins.plugin_directories", [])

    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get_section("logging")

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.get_section("security")

    def get_status(self) -> Dict[str, Any]:
        """Get configuration loader status"""
        return {
            "config_file": str(self.config_path),
            "config_exists": self.config_path.exists(),
            "config_size": self.config_path.stat().st_size
            if self.config_path.exists()
            else 0,
            "sections": list(self.config_data.keys()),
            "environment_overrides": len(self.environment_overrides),
            "cache_valid": self._cache_valid,
            "last_modified": self.config_path.stat().st_mtime
            if self.config_path.exists()
            else None,
        }


# Global configuration loader instance
_config_loader = None


def get_config_loader(config_path: Optional[str] = None) -> AetherraConfigLoader:
    """Get the global configuration loader instance"""
    global _config_loader

    if _config_loader is None or config_path is not None:
        _config_loader = AetherraConfigLoader(config_path)

    return _config_loader


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to load configuration"""
    loader = get_config_loader(config_path)
    return loader.load_config()


def get_config(key: str, default: Any = None) -> Any:
    """Convenience function to get a configuration value"""
    loader = get_config_loader()
    return loader.get(key, default)


def set_config(key: str, value: Any) -> bool:
    """Convenience function to set a configuration value"""
    loader = get_config_loader()
    return loader.set(key, value)


def reload_config() -> bool:
    """Convenience function to reload configuration"""
    loader = get_config_loader()
    return loader.reload()


def save_config() -> bool:
    """Convenience function to save configuration"""
    loader = get_config_loader()
    return loader.save()


if __name__ == "__main__":
    # Test the configuration loader
    print("⚙️ Testing Aetherra Configuration Loader...")

    try:
        # Test loading
        config = load_config()
        print(f"✅ Configuration loaded: {len(config)} sections")

        # Test getting values
        system_name = get_config("system.name")
        print(f"System name: {system_name}")

        # Test status
        loader = get_config_loader()
        status = loader.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
