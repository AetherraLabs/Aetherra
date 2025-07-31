"""
Simplified Configuration Manager for Lyrixa AI Assistant
Compatible with the Plugin-Driven UI System
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """User preference settings."""

    language: str = "en"
    theme: str = "light"
    font_family: str = "Arial"
    font_size: int = 10
    enable_notifications: bool = True
    auto_dismiss_time: int = 10
    play_sounds: bool = False
    enable_telemetry: bool = False
    share_anonymous_data: bool = False


@dataclass
class AnticipationSettings:
    """Anticipation engine configuration."""

    pattern_detection_sensitivity: float = 0.7
    minimum_pattern_occurrences: int = 3
    pattern_confidence_threshold: float = 0.8
    context_window_size: int = 30
    activity_weight: float = 1.0
    time_weight: float = 0.8
    location_weight: float = 0.6
    suggestion_diversity: float = 0.5
    max_concurrent_suggestions: int = 5
    suggestion_cooldown: int = 5


@dataclass
class SystemConfiguration:
    """System-level configuration."""

    max_memory_usage: int = 512
    cache_size: int = 100
    log_level: str = "INFO"
    backup_frequency: int = 24
    data_retention_days: int = 30


class SimpleConfigurationManager:
    """
    Simplified configuration manager that works without Qt dependencies.
    Compatible with the Plugin-Driven UI System.
    """

    def __init__(self):
        """Initialize the configuration manager."""
        self.user_preferences = UserPreferences()
        self.anticipation_settings = AnticipationSettings()
        self.system_configuration = SystemConfiguration()

        # Configuration file path
        self.config_file = Path.home() / "Documents" / "Lyrixa" / "config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.load_configuration()
        logger.info("Simple Configuration Manager initialized successfully")

    def load_configuration(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    data = json.load(f)

                # Load user preferences
                if "user_preferences" in data:
                    pref_data = data["user_preferences"]
                    for key, value in pref_data.items():
                        if hasattr(self.user_preferences, key):
                            setattr(self.user_preferences, key, value)

                # Load anticipation settings
                if "anticipation_settings" in data:
                    ant_data = data["anticipation_settings"]
                    for key, value in ant_data.items():
                        if hasattr(self.anticipation_settings, key):
                            setattr(self.anticipation_settings, key, value)

                # Load system configuration
                if "system_configuration" in data:
                    sys_data = data["system_configuration"]
                    for key, value in sys_data.items():
                        if hasattr(self.system_configuration, key):
                            setattr(self.system_configuration, key, value)

                logger.info("Configuration loaded successfully")
            else:
                logger.info("No existing configuration found, using defaults")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

    def save_configuration(self):
        """Save configuration to file."""
        try:
            config_data = {
                "user_preferences": asdict(self.user_preferences),
                "anticipation_settings": asdict(self.anticipation_settings),
                "system_configuration": asdict(self.system_configuration),
            }

            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)

            logger.info("Configuration saved successfully")

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get_preferences(self) -> UserPreferences:
        """Get current user preferences."""
        return self.user_preferences

    def get_anticipation_settings(self) -> AnticipationSettings:
        """Get current anticipation settings."""
        return self.anticipation_settings

    def get_system_configuration(self) -> SystemConfiguration:
        """Get current system configuration."""
        return self.system_configuration

    def update_preference(self, key: str, value):
        """Update a specific user preference."""
        if hasattr(self.user_preferences, key):
            setattr(self.user_preferences, key, value)
            self.save_configuration()
            logger.info(f"Updated preference {key} to {value}")
        else:
            logger.warning(f"Unknown preference key: {key}")

    def update_anticipation_setting(self, key: str, value):
        """Update a specific anticipation setting."""
        if hasattr(self.anticipation_settings, key):
            setattr(self.anticipation_settings, key, value)
            self.save_configuration()
            logger.info(f"Updated anticipation setting {key} to {value}")
        else:
            logger.warning(f"Unknown anticipation setting key: {key}")

    def update_system_setting(self, key: str, value):
        """Update a specific system setting."""
        if hasattr(self.system_configuration, key):
            setattr(self.system_configuration, key, value)
            self.save_configuration()
            logger.info(f"Updated system setting {key} to {value}")
        else:
            logger.warning(f"Unknown system setting key: {key}")

    def export_configuration(self, filepath: str):
        """Export configuration to a specified file."""
        try:
            config_data = {
                "user_preferences": asdict(self.user_preferences),
                "anticipation_settings": asdict(self.anticipation_settings),
                "system_configuration": asdict(self.system_configuration),
            }

            with open(filepath, "w") as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Configuration exported to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False

    def import_configuration(self, filepath: str):
        """Import configuration from a specified file."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Import user preferences
            if "user_preferences" in data:
                pref_data = data["user_preferences"]
                for key, value in pref_data.items():
                    if hasattr(self.user_preferences, key):
                        setattr(self.user_preferences, key, value)

            # Import anticipation settings
            if "anticipation_settings" in data:
                ant_data = data["anticipation_settings"]
                for key, value in ant_data.items():
                    if hasattr(self.anticipation_settings, key):
                        setattr(self.anticipation_settings, key, value)

            # Import system configuration
            if "system_configuration" in data:
                sys_data = data["system_configuration"]
                for key, value in sys_data.items():
                    if hasattr(self.system_configuration, key):
                        setattr(self.system_configuration, key, value)

            self.save_configuration()
            logger.info(f"Configuration imported from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False

    def reset_to_defaults(self):
        """Reset all configuration to default values."""
        self.user_preferences = UserPreferences()
        self.anticipation_settings = AnticipationSettings()
        self.system_configuration = SystemConfiguration()
        self.save_configuration()
        logger.info("Configuration reset to defaults")

    def get_configuration_summary(self) -> dict:
        """Get a summary of current configuration."""
        return {
            "user_preferences": asdict(self.user_preferences),
            "anticipation_settings": asdict(self.anticipation_settings),
            "system_configuration": asdict(self.system_configuration),
        }


# Create a global instance for easy access
config_manager = SimpleConfigurationManager()


# Example usage
if __name__ == "__main__":
    # Test the configuration manager
    print("Testing Simple Configuration Manager")

    # Print current configuration
    print("Current configuration:")
    print(json.dumps(config_manager.get_configuration_summary(), indent=2))

    # Update some preferences
    config_manager.update_preference("theme", "dark")
    config_manager.update_preference("font_size", 12)

    # Update anticipation settings
    config_manager.update_anticipation_setting("pattern_detection_sensitivity", 0.8)

    print("\nUpdated configuration:")
    print(json.dumps(config_manager.get_configuration_summary(), indent=2))


# Backward compatibility alias
ConfigurationManager = SimpleConfigurationManager
