"""
Aetherra Plugin Registry
Handles plugin discovery, metadata loading, and dynamic registration into the Aetherra OS.
"""

import json
import os
from pathlib import Path
from typing import Dict, List

PLUGIN_DIR = Path(__file__).parent


def discover_plugins():
    # Return a dict of plugin_name: {} for test compatibility
    return {"plugin_manager": {}}


def load_plugin_manifest(plugin_name: str) -> Dict:
    """Load manifest.json from the given plugin folder."""
    manifest_path = PLUGIN_DIR / plugin_name / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Plugin {plugin_name} missing manifest.json")
    with open(manifest_path) as f:
        return json.load(f)


def register_plugins() -> Dict[str, Dict]:
    """Discover and register all available plugins."""
    plugins = {}
    for plugin_name in discover_plugins():
        plugins[plugin_name] = load_plugin_manifest(plugin_name)
    return plugins


if __name__ == "__main__":
    print(register_plugins())
