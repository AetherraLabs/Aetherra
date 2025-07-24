# Aetherra Script Registry Loader
# Auto-loads script registry during Lyrixa initialization

import json
import os
from typing import Any, Dict, Optional


class ScriptRegistryLoader:
    def __init__(self, registry_path: str = "Aetherra/scripts/script_registry.json"):
        self.registry_path = registry_path
        self.registry = None
        self.loaded = False

    def load_script_registry(self) -> Dict[str, Any]:
        """Load the script registry from file"""
        try:
            if not os.path.exists(self.registry_path):
                print(f"❌ Script registry not found at {self.registry_path}")
                return {}

            with open(self.registry_path, "r", encoding="utf-8") as f:
                registry = json.load(f)

            print(
                f"✅ Script registry loaded successfully: {registry['registry_info']['name']}"
            )
            print(
                f"📊 Total scripts: {registry['execution_statistics']['total_scripts']}"
            )

            # Store in memory for quick access
            self.registry = registry
            self.loaded = True

            return registry

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse script registry: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading script registry: {e}")
            return {}

    def get_registry(self) -> Optional[Dict[str, Any]]:
        """Get the loaded registry, load if not already loaded"""
        if not self.loaded:
            return self.load_script_registry()
        return self.registry

    def get_scripts_by_category(self, category: str) -> Dict[str, Any]:
        """Get all scripts in a specific category"""
        if not self.loaded:
            self.load_script_registry()

        if not self.registry:
            return {}

        scripts = {}
        for script_name, script_data in self.registry.get("scripts", {}).items():
            if script_data.get("category") == category:
                scripts[script_name] = script_data

        return scripts

    def get_script_metadata(self, script_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific script"""
        if not self.loaded:
            self.load_script_registry()

        if not self.registry:
            return None

        return self.registry.get("scripts", {}).get(script_name)

    def get_categories(self) -> Dict[str, Any]:
        """Get all available categories"""
        if not self.loaded:
            self.load_script_registry()

        if not self.registry:
            return {}

        return self.registry.get("categories", {})


# Initialize global registry loader
script_registry_loader = ScriptRegistryLoader()
