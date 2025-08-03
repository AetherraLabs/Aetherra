#!/usr/bin/env python3
"""
🔌 Aetherra Plugin Discovery Service
====================================
Automatically discovers and registers local plugins with the Aetherra Hub.

This service scans the Aetherra/plugins directory and makes local plugins
visible in the Hub marketplace interface.
"""

import json
import os
import asyncio
import logging
import importlib.util
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)

@dataclass
class PluginMetadata:
    """Plugin metadata structure."""
    name: str
    version: str
    description: str
    author: str
    category: str = "utility"
    license: str = "GPL-3.0"
    aetherra_version: str = ">=3.0.0"
    dependencies: Optional[Dict[str, str]] = None
    keywords: Optional[List[str]] = None
    entry_point: Optional[str] = None
    exports: Optional[Dict[str, str]] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None
    homepage: Optional[str] = None
    local_path: Optional[str] = None
    plugin_type: str = "local"  # local, hub, system

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = {}
        if self.keywords is None:
            self.keywords = []
        if self.exports is None:
            self.exports = {}


class AetherraPluginDiscovery:
    """
    🔍 Plugin Discovery Service

    Discovers and catalogs local plugins, making them available to the Hub.
    """

    def __init__(self, plugins_dir: Optional[str] = None):
        self.plugins_dir = plugins_dir or "Aetherra/plugins"
        self.plugins_dir = Path(self.plugins_dir).absolute()
        self.discovered_plugins: Dict[str, PluginMetadata] = {}
        self.hub_url = "http://localhost:3001"

    async def discover_all_plugins(self) -> Dict[str, PluginMetadata]:
        """Discover all plugins in the plugins directory."""
        logger.info("🔍 Starting plugin discovery...")

        if not self.plugins_dir.exists():
            logger.warning(f"[WARN] Plugins directory not found: {self.plugins_dir}")
            return {}

        # Discover different types of plugins
        await self._discover_aetherplug_plugins()
        await self._discover_python_plugins()
        await self._discover_sample_plugins()

        logger.info(f"[OK] Discovered {len(self.discovered_plugins)} plugins")
        return self.discovered_plugins

    async def _discover_aetherplug_plugins(self):
        """Discover .aetherplug format plugins."""
        logger.info("🔍 Scanning for .aetherplug plugins...")

        # Look for aetherra-plugin.json files
        for plugin_json in self.plugins_dir.rglob("aetherra-plugin.json"):
            try:
                await self._process_aetherplug_manifest(plugin_json)
            except Exception as e:
                logger.error(f"❌ Error processing {plugin_json}: {e}")

    async def _process_aetherplug_manifest(self, manifest_path: Path):
        """Process an aetherra-plugin.json manifest file."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            plugin_dir = manifest_path.parent

            metadata = PluginMetadata(
                name=manifest.get("name", plugin_dir.name),
                version=manifest.get("version", "1.0.0"),
                description=manifest.get("description", "No description provided"),
                author=manifest.get("author", "Unknown"),
                category=manifest.get("category", "utility"),
                license=manifest.get("license", "GPL-3.0"),
                aetherra_version=manifest.get("aetherra_version", ">=3.0.0"),
                dependencies=manifest.get("dependencies", {}),
                keywords=manifest.get("keywords", []),
                entry_point=manifest.get("entry_point"),
                exports=manifest.get("exports", {}),
                repository=manifest.get("repository"),
                documentation=manifest.get("documentation"),
                homepage=manifest.get("homepage"),
                local_path=str(plugin_dir),
                plugin_type="aetherplug"
            )

            self.discovered_plugins[metadata.name] = metadata
            logger.info(f"[OK] Discovered .aetherplug: {metadata.name} v{metadata.version}")

        except Exception as e:
            logger.error(f"❌ Error processing manifest {manifest_path}: {e}")

    async def _discover_python_plugins(self):
        """Discover Python-based plugins."""
        logger.info("🔍 Scanning for Python plugins...")

        # Look for Python files that appear to be plugins
        for py_file in self.plugins_dir.rglob("*.py"):
            if py_file.name.startswith("__") or py_file.name in ["setup.py", "conftest.py"]:
                continue

            try:
                await self._analyze_python_plugin(py_file)
            except Exception as e:
                logger.error(f"❌ Error analyzing {py_file}: {e}")

    async def _analyze_python_plugin(self, py_file: Path):
        """Analyze a Python file to determine if it's a plugin."""
        try:
            # Read the file to look for plugin indicators
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for plugin class or plugin_data
            if "class " in content and ("Plugin" in content or "plugin" in content.lower()):
                await self._extract_python_plugin_metadata(py_file, content)
            elif "plugin_data" in content:
                await self._extract_plugin_data_metadata(py_file, content)

        except Exception as e:
            logger.error(f"❌ Error reading {py_file}: {e}")

    async def _extract_python_plugin_metadata(self, py_file: Path, content: str):
        """Extract metadata from a Python plugin class."""
        try:
            # Try to import the module and extract metadata
            spec = importlib.util.spec_from_file_location("plugin_module", py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, 'name') and hasattr(attr, 'description'):
                        metadata = PluginMetadata(
                            name=getattr(attr, 'name', py_file.stem),
                            version=getattr(attr, 'version', '1.0.0'),
                            description=getattr(attr, 'description', 'No description'),
                            author=getattr(attr, 'created_by', getattr(attr, 'author', 'Unknown')),
                            category=getattr(attr, 'category', 'utility'),
                            local_path=str(py_file),
                            plugin_type="python",
                            keywords=['python', 'local']
                        )

                        self.discovered_plugins[metadata.name] = metadata
                        logger.info(f"[OK] Discovered Python plugin: {metadata.name}")
                        break

        except Exception as e:
            logger.error(f"❌ Error importing {py_file}: {e}")

    async def _extract_plugin_data_metadata(self, py_file: Path, content: str):
        """Extract metadata from plugin_data dictionary."""
        try:
            # Try to import and get plugin_data
            spec = importlib.util.spec_from_file_location("plugin_module", py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'plugin_data'):
                    data = module.plugin_data
                    metadata = PluginMetadata(
                        name=data.get('name', py_file.stem),
                        version=data.get('version', '1.0.0'),
                        description=data.get('description', 'No description'),
                        author=data.get('author', 'Unknown'),
                        category=data.get('category', 'utility'),
                        local_path=str(py_file),
                        plugin_type="python",
                        keywords=['python', 'local']
                    )

                    self.discovered_plugins[metadata.name] = metadata
                    logger.info(f"[OK] Discovered plugin_data: {metadata.name}")

        except Exception as e:
            logger.error(f"❌ Error extracting plugin_data from {py_file}: {e}")

    async def _discover_sample_plugins(self):
        """Discover sample plugins specifically."""
        logger.info("🔍 Scanning for sample plugins...")

        # Look for files matching sample_plugin_*.py pattern
        for sample_file in self.plugins_dir.glob("sample_plugin_*.py"):
            try:
                await self._process_sample_plugin(sample_file)
            except Exception as e:
                logger.error(f"❌ Error processing sample plugin {sample_file}: {e}")

    async def _process_sample_plugin(self, sample_file: Path):
        """Process a sample plugin file."""
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract basic info from the sample plugin
            plugin_num = sample_file.stem.split('_')[-1]

            metadata = PluginMetadata(
                name=f"sample_plugin_{plugin_num}",
                version="1.0.0",
                description=f"Sample plugin {plugin_num} for testing and demonstration",
                author="Aetherra Development Team",
                category="sample",
                local_path=str(sample_file),
                plugin_type="sample",
                keywords=['sample', 'demo', 'testing']
            )

            self.discovered_plugins[metadata.name] = metadata
            logger.info(f"[OK] Discovered sample plugin: {metadata.name}")

        except Exception as e:
            logger.error(f"❌ Error processing sample plugin {sample_file}: {e}")

    async def register_with_hub(self, plugin_metadata: PluginMetadata) -> bool:
        """Register a plugin with the Aetherra Hub."""
        try:
            # Convert metadata to Hub format
            hub_plugin = {
                "name": plugin_metadata.name,
                "version": plugin_metadata.version,
                "description": plugin_metadata.description,
                "author": plugin_metadata.author,
                "category": plugin_metadata.category,
                "license": plugin_metadata.license,
                "aetherra_version": plugin_metadata.aetherra_version,
                "dependencies": plugin_metadata.dependencies,
                "keywords": plugin_metadata.keywords,
                "local_path": plugin_metadata.local_path,
                "plugin_type": plugin_metadata.plugin_type,
                "featured": plugin_metadata.plugin_type == "aetherplug",  # Feature .aetherplug plugins
                "downloads": 0,
                "rating": 5.0 if plugin_metadata.plugin_type == "aetherplug" else 4.5,
                "created_at": "2025-08-02T14:00:00Z",
                "updated_at": "2025-08-02T14:00:00Z"
            }

            # Try to register with Hub API
            try:
                response = requests.post(
                    f"{self.hub_url}/api/v1/plugins",
                    json=hub_plugin,
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    logger.info(f"[OK] Registered {plugin_metadata.name} with Hub")
                    return True
                else:
                    logger.warning(f"[WARN] Hub registration failed for {plugin_metadata.name}: {response.status_code}")
            except requests.exceptions.RequestException:
                logger.warning(f"[WARN] Hub not available for {plugin_metadata.name} registration")

            return False

        except Exception as e:
            logger.error(f"❌ Error registering {plugin_metadata.name} with Hub: {e}")
            return False

    async def sync_all_with_hub(self):
        """Sync all discovered plugins with the Hub."""
        logger.info("🔄 Syncing all plugins with Aetherra Hub...")

        await self.discover_all_plugins()

        success_count = 0
        for plugin_name, metadata in self.discovered_plugins.items():
            if await self.register_with_hub(metadata):
                success_count += 1

        logger.info(f"[OK] Successfully synced {success_count}/{len(self.discovered_plugins)} plugins with Hub")
        return success_count

    def get_plugin_summary(self) -> Dict[str, Any]:
        """Get a summary of discovered plugins."""
        by_type = {}
        by_category = {}

        for plugin in self.discovered_plugins.values():
            # Count by type
            by_type[plugin.plugin_type] = by_type.get(plugin.plugin_type, 0) + 1

            # Count by category
            by_category[plugin.category] = by_category.get(plugin.category, 0) + 1

        return {
            "total_plugins": len(self.discovered_plugins),
            "by_type": by_type,
            "by_category": by_category,
            "plugin_names": list(self.discovered_plugins.keys())
        }


async def main():
    """Main function for testing plugin discovery."""
    logging.basicConfig(level=logging.INFO)

    discovery = AetherraPluginDiscovery()
    await discovery.discover_all_plugins()

    summary = discovery.get_plugin_summary()
    print(f"\n🔍 Plugin Discovery Summary:")
    print(f"Total plugins: {summary['total_plugins']}")
    print(f"By type: {summary['by_type']}")
    print(f"By category: {summary['by_category']}")
    print(f"Plugin names: {summary['plugin_names']}")

    # Try to sync with Hub
    await discovery.sync_all_with_hub()


if __name__ == "__main__":
    asyncio.run(main())
