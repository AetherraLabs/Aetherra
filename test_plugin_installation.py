#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Plugin Installation Test Script
Tests the plugin installation workflow for Lyrixa Basic
"""

import asyncio
import json
import logging
import shutil
import urllib.request
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PluginInstaller:
    """Handles plugin installation for Lyrixa Basic"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.lyrixa_plugins_dir = self.project_root / "Aetherra" / "lyrixa" / "plugins"
        self.lyrixa_plugins_dir.mkdir(parents=True, exist_ok=True)

    async def install_plugin_from_hub(self, plugin_name: str) -> bool:
        """Install a plugin from the Aetherra Hub"""
        try:
            logger.info(f"📦 Installing plugin: {plugin_name}")

            # 1. Get plugin info from Hub
            response = urllib.request.urlopen("http://localhost:3001/api/plugins")
            plugins_data = json.loads(response.read())

            # Find the plugin
            plugin_info = None
            for plugin in plugins_data.get("plugins", []):
                if plugin.get("name") == plugin_name:
                    plugin_info = plugin
                    break

            if not plugin_info:
                logger.error(f"❌ Plugin '{plugin_name}' not found in Hub")
                return False

            logger.info(
                f"✅ Found plugin: {plugin_info.get('description', 'No description')}"
            )

            # 2. Copy/install the plugin
            if "local_path" in plugin_info:
                # This is a local plugin - copy it to Lyrixa's plugin directory
                source_path = Path(plugin_info["local_path"])

                if source_path.is_file():
                    # Single file plugin
                    dest_path = self.lyrixa_plugins_dir / source_path.name
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"📄 Copied plugin file to: {dest_path}")

                elif source_path.is_dir():
                    # Directory plugin
                    dest_path = self.lyrixa_plugins_dir / plugin_name
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path)
                    logger.info(f"📁 Copied plugin directory to: {dest_path}")

                else:
                    logger.error(f"❌ Plugin source path doesn't exist: {source_path}")
                    return False

            else:
                logger.error(
                    f"❌ No installation method available for plugin: {plugin_name}"
                )
                return False

            # 3. Create installation record
            install_record = {
                "name": plugin_name,
                "version": plugin_info.get("version", "1.0.0"),
                "description": plugin_info.get("description", ""),
                "installed_at": plugin_info.get("registered_at", ""),
                "source": "hub",
                "category": plugin_info.get("category", "utility"),
            }

            # Save to installed plugins registry
            registry_file = self.lyrixa_plugins_dir / "installed_plugins.json"
            registry = {}
            if registry_file.exists():
                with open(registry_file, encoding="utf-8") as f:
                    registry = json.load(f)

            registry[plugin_name] = install_record

            with open(registry_file, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Plugin '{plugin_name}' installed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Plugin installation failed: {e}")
            return False

    async def list_installed_plugins(self):
        """List all installed plugins"""
        registry_file = self.lyrixa_plugins_dir / "installed_plugins.json"

        if not registry_file.exists():
            logger.info("📋 No plugins installed yet")
            return []

        with open(registry_file, encoding="utf-8") as f:
            registry = json.load(f)

        logger.info(f"📋 Installed Plugins ({len(registry)}):")
        for name, info in registry.items():
            logger.info(
                f"  • {name} v{info.get('version', '?')} - {info.get('description', 'No description')}"
            )

        return list(registry.keys())


async def test_plugin_installation():
    """Test the plugin installation workflow"""
    installer = PluginInstaller()

    print("🧪 Testing Plugin Installation Workflow")
    print("=" * 50)

    # 1. Show current installed plugins
    print("\n1. Current installed plugins:")
    await installer.list_installed_plugins()

    # 2. Install a test plugin
    print("\n2. Installing 'advanced-memory-system' plugin:")
    success = await installer.install_plugin_from_hub("advanced-memory-system")

    if success:
        print("\n3. Updated installed plugins:")
        await installer.list_installed_plugins()
    else:
        print("❌ Installation failed!")

    return success


if __name__ == "__main__":
    asyncio.run(test_plugin_installation())
