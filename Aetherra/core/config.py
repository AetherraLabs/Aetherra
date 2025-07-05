"""
Aetherra Configuration
=====================

Global configuration settings and constants for the Aetherra platform.
"""

import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """Global configuration for Aetherra"""

    # Version information
    VERSION = "2.0.0"

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    PLUGINS_DIR = PROJECT_ROOT / "plugins"

    # Database settings
    DEFAULT_DB_PATH = "aetherra.db"
    MEMORY_DB_PATH = "memory.db"

    # AI/LLM settings
    DEFAULT_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7

    # Memory settings
    MAX_MEMORY_ENTRIES = 10000
    MEMORY_CLEANUP_THRESHOLD = 0.8

    # Plugin settings
    PLUGIN_TIMEOUT = 30.0  # seconds
    MAX_PLUGINS = 50

    # UI settings
    DEFAULT_THEME = "dark"
    WINDOW_SIZE = (1200, 800)

    # Performance settings
    ENABLE_CACHING = True
    CACHE_SIZE = 1000

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return getattr(cls, key.upper(), default)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set configuration value"""
        setattr(cls, key.upper(), value)

    @classmethod
    def from_env(cls, key: str, env_var: str, default: Any = None) -> Any:
        """Get configuration from environment variable"""
        value = os.getenv(env_var, default)
        if value is not None:
            cls.set(key, value)
        return cls.get(key)

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }


# Environment-based configuration loading
Config.from_env("default_model", "AETHERRA_MODEL", Config.DEFAULT_MODEL)
Config.from_env("max_tokens", "AETHERRA_MAX_TOKENS", Config.MAX_TOKENS)
Config.from_env("temperature", "AETHERRA_TEMPERATURE", Config.TEMPERATURE)

# Ensure data directories exist
Config.DATA_DIR.mkdir(exist_ok=True)
Config.PLUGINS_DIR.mkdir(exist_ok=True)
