#!/usr/bin/env python3
"""
🏪 Aetherra Hub Integration
===========================

Handles integration between Aetherra OS and the Aetherra Hub (Plugin Marketplace).
Provides seamless plugin discovery, installation, and management.

This module enables:
- Real-time plugin discovery from the Hub
- Automatic plugin installation and updates
- Plugin metadata synchronization
- Hub marketplace browsing and search
- Featured plugin recommendations

Author: Aetherra Labs
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
import requests

# Add Aetherra to path
sys.path.insert(0, "Aetherra")

from aetherra_core.config import config_loader

logger = logging.getLogger(__name__)


class AetherraHubClient:
    """
    🌐 Client for communicating with the Aetherra Hub API
    """

    def __init__(self, hub_url: str = "http://localhost:3001", api_version: str = "v1"):
        self.hub_url = hub_url.rstrip("/")
        self.api_base = f"{self.hub_url}/api/{api_version}"
        self.session = None
        self.connected = False

        # Configuration
        self.config = config_loader.load_config()
        self.timeout = 30
        self.retry_attempts = 3

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self):
        """Establish connection to the Hub"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

            # Test connection
            await self.health_check()
            self.connected = True
            logger.info(f"✅ Connected to Aetherra Hub at {self.hub_url}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to Aetherra Hub: {e}")
            self.connected = False

    async def disconnect(self):
        """Close connection to the Hub"""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False

    async def health_check(self) -> Dict[str, Any]:
        """Check Hub health status"""
        try:
            async with self.session.get(f"{self.api_base}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Hub health check failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Hub health check failed: {e}")
            raise

    async def search_plugins(
        self, query: str = "", filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Search for plugins in the Hub"""
        if not self.connected:
            await self.connect()

        try:
            params = {"q": query}
            if filters:
                params.update(filters)

            async with self.session.get(
                f"{self.api_base}/plugins/search", params=params
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    logger.info(
                        f"🔍 Found {results.get('total', 0)} plugins matching '{query}'"
                    )
                    return results
                else:
                    logger.error(f"❌ Plugin search failed: {response.status}")
                    return {
                        "plugins": [],
                        "total": 0,
                        "error": f"HTTP {response.status}",
                    }

        except Exception as e:
            logger.error(f"❌ Plugin search error: {e}")
            return {"plugins": [], "total": 0, "error": str(e)}

    async def get_featured_plugins(self) -> List[Dict[str, Any]]:
        """Get featured plugins from the Hub"""
        if not self.connected:
            await self.connect()

        try:
            async with self.session.get(
                f"{self.api_base}/plugins/featured"
            ) as response:
                if response.status == 200:
                    featured = await response.json()
                    logger.info(f"⭐ Retrieved {len(featured)} featured plugins")
                    return featured
                else:
                    logger.error(
                        f"❌ Featured plugins request failed: {response.status}"
                    )
                    return []

        except Exception as e:
            logger.error(f"❌ Featured plugins error: {e}")
            return []

    async def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific plugin"""
        if not self.connected:
            await self.connect()

        try:
            async with self.session.get(
                f"{self.api_base}/plugins/{plugin_id}"
            ) as response:
                if response.status == 200:
                    details = await response.json()
                    logger.info(f"📦 Retrieved details for plugin '{plugin_id}'")
                    return details
                elif response.status == 404:
                    logger.warning(f"⚠️ Plugin '{plugin_id}' not found in Hub")
                    return None
                else:
                    logger.error(f"❌ Plugin details request failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"❌ Plugin details error: {e}")
            return None

    async def download_plugin(
        self, plugin_id: str, version: str = "latest"
    ) -> Optional[bytes]:
        """Download a plugin package from the Hub"""
        if not self.connected:
            await self.connect()

        try:
            download_url = f"{self.api_base}/plugins/{plugin_id}/download"
            if version != "latest":
                download_url += f"?version={version}"

            async with self.session.get(download_url) as response:
                if response.status == 200:
                    content = await response.read()
                    logger.info(
                        f"📥 Downloaded plugin '{plugin_id}' ({len(content)} bytes)"
                    )
                    return content
                else:
                    logger.error(f"❌ Plugin download failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"❌ Plugin download error: {e}")
            return None

    async def get_plugin_categories(self) -> List[str]:
        """Get available plugin categories"""
        if not self.connected:
            await self.connect()

        try:
            async with self.session.get(
                f"{self.api_base}/plugins/categories"
            ) as response:
                if response.status == 200:
                    categories = await response.json()
                    return categories.get("categories", [])
                else:
                    return [
                        "ai",
                        "automation",
                        "utility",
                        "interface",
                        "memory",
                        "analysis",
                    ]

        except Exception as e:
            logger.warning(f"⚠️ Failed to get categories, using defaults: {e}")
            return ["ai", "automation", "utility", "interface", "memory", "analysis"]


class AetherraHubIntegration:
    """
    🔗 Main integration class for Aetherra Hub functionality
    """

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or os.getcwd())
        self.config = config_loader.load_config()

        # Hub configuration
        hub_config = self.config.get("hub", {})
        self.hub_url = hub_config.get("url", "http://localhost:3001")
        self.enabled = hub_config.get("enabled", True)

        # Plugin directories
        self.plugin_dirs = [
            self.project_root / "plugins",
            self.project_root / "Aetherra" / "plugins",
            self.project_root / "lyrixa_plugins",
        ]

        # Hub client
        self.client = AetherraHubClient(self.hub_url)

        # Local plugin registry
        self.local_plugins = {}
        self.hub_plugins_cache = {}
        self.last_sync_time = None

    async def initialize(self):
        """Initialize the Hub integration"""
        if not self.enabled:
            logger.info("ℹ️ Aetherra Hub integration disabled")
            return False

        try:
            logger.info("🏪 Initializing Aetherra Hub integration...")

            # Connect to Hub
            await self.client.connect()

            # Scan local plugins
            await self.scan_local_plugins()

            # Initial sync with Hub
            await self.sync_with_hub()

            logger.info("✅ Aetherra Hub integration initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Hub integration: {e}")
            return False

    async def scan_local_plugins(self):
        """Scan for locally installed plugins"""
        logger.info("🔍 Scanning local plugins...")

        self.local_plugins = {}

        for plugin_dir in self.plugin_dirs:
            if plugin_dir.exists():
                await self._scan_directory(plugin_dir)

        logger.info(f"📦 Found {len(self.local_plugins)} local plugins")

    async def _scan_directory(self, directory: Path):
        """Scan a specific directory for plugins"""
        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix == ".aetherplugin":
                    await self._process_plugin_file(item)
                elif item.is_dir() and (item / "manifest.json").exists():
                    await self._process_plugin_directory(item)

        except Exception as e:
            logger.warning(f"⚠️ Error scanning directory {directory}: {e}")

    async def _process_plugin_file(self, plugin_file: Path):
        """Process a .aetherplugin file"""
        try:
            # For .aetherplugin files, create basic metadata
            plugin_id = plugin_file.stem
            self.local_plugins[plugin_id] = {
                "id": plugin_id,
                "name": plugin_id.replace("_", " ").title(),
                "type": "aetherplugin",
                "path": str(plugin_file),
                "installed": True,
                "local": True,
            }

        except Exception as e:
            logger.warning(f"⚠️ Error processing plugin file {plugin_file}: {e}")

    async def _process_plugin_directory(self, plugin_dir: Path):
        """Process a plugin directory with manifest.json"""
        try:
            manifest_file = plugin_dir / "manifest.json"

            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            plugin_id = manifest.get("id", plugin_dir.name)
            self.local_plugins[plugin_id] = {
                **manifest,
                "path": str(plugin_dir),
                "installed": True,
                "local": True,
            }

        except Exception as e:
            logger.warning(f"⚠️ Error processing plugin directory {plugin_dir}: {e}")

    async def sync_with_hub(self):
        """Synchronize local plugin registry with Hub"""
        if not self.client.connected:
            return

        try:
            logger.info("🔄 Synchronizing with Aetherra Hub...")

            # Get featured plugins for caching
            featured = await self.client.get_featured_plugins()

            # Cache featured plugins
            for plugin in featured:
                plugin_id = plugin.get("id")
                if plugin_id:
                    self.hub_plugins_cache[plugin_id] = plugin

            # Get categories
            categories = await self.client.get_plugin_categories()

            self.last_sync_time = datetime.now()
            logger.info(f"✅ Sync complete: {len(featured)} featured plugins cached")

        except Exception as e:
            logger.error(f"❌ Hub sync failed: {e}")

    async def search_hub_plugins(
        self, query: str = "", category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for plugins in the Hub"""
        filters = {}
        if category:
            filters["category"] = category

        return await self.client.search_plugins(query, filters)

    async def get_featured_plugins(self) -> List[Dict[str, Any]]:
        """Get featured plugins (from cache or Hub)"""
        if self.hub_plugins_cache:
            featured = [
                p for p in self.hub_plugins_cache.values() if p.get("featured", False)
            ]
            if featured:
                return featured

        # Fallback to live request
        return await self.client.get_featured_plugins()

    async def install_plugin_from_hub(
        self, plugin_id: str, version: str = "latest"
    ) -> Dict[str, Any]:
        """Install a plugin from the Hub"""
        try:
            logger.info(f"📥 Installing plugin '{plugin_id}' from Hub...")

            # Get plugin details
            details = await self.client.get_plugin_details(plugin_id)
            if not details:
                return {"success": False, "error": "Plugin not found in Hub"}

            # Download plugin
            content = await self.client.download_plugin(plugin_id, version)
            if not content:
                return {"success": False, "error": "Failed to download plugin"}

            # Determine installation directory
            install_dir = self.plugin_dirs[0]  # Use first plugin directory
            install_dir.mkdir(parents=True, exist_ok=True)

            # Install based on plugin type
            plugin_type = details.get("type", "unknown")

            if plugin_type == "aetherplugin":
                # Install as .aetherplugin file
                plugin_file = install_dir / f"{plugin_id}.aetherplugin"
                with open(plugin_file, "wb") as f:
                    f.write(content)

            else:
                # Install as directory with extracted content
                plugin_dir = install_dir / plugin_id
                plugin_dir.mkdir(exist_ok=True)

                # For now, just save as a package file
                package_file = plugin_dir / "package.zip"
                with open(package_file, "wb") as f:
                    f.write(content)

                # Create manifest
                manifest = {
                    "id": plugin_id,
                    "name": details.get("name", plugin_id),
                    "version": details.get("version", version),
                    "description": details.get("description", ""),
                    "installed_from_hub": True,
                    "hub_id": plugin_id,
                }

                with open(plugin_dir / "manifest.json", "w") as f:
                    json.dump(manifest, f, indent=2)

            # Update local registry
            await self.scan_local_plugins()

            logger.info(f"✅ Plugin '{plugin_id}' installed successfully")
            return {"success": True, "plugin_id": plugin_id, "version": version}

        except Exception as e:
            logger.error(f"❌ Plugin installation failed: {e}")
            return {"success": False, "error": str(e)}

    async def uninstall_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Uninstall a locally installed plugin"""
        try:
            if plugin_id not in self.local_plugins:
                return {"success": False, "error": "Plugin not found locally"}

            plugin_info = self.local_plugins[plugin_id]
            plugin_path = Path(plugin_info["path"])

            # Remove plugin files
            if plugin_path.is_file():
                plugin_path.unlink()
            elif plugin_path.is_dir():
                import shutil

                shutil.rmtree(plugin_path)

            # Update local registry
            del self.local_plugins[plugin_id]

            logger.info(f"🗑️ Plugin '{plugin_id}' uninstalled successfully")
            return {"success": True, "plugin_id": plugin_id}

        except Exception as e:
            logger.error(f"❌ Plugin uninstallation failed: {e}")
            return {"success": False, "error": str(e)}

    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for plugin updates"""
        updates_available = []

        try:
            for plugin_id, plugin_info in self.local_plugins.items():
                if plugin_info.get("installed_from_hub", False):
                    # Check Hub for newer version
                    hub_details = await self.client.get_plugin_details(plugin_id)
                    if hub_details:
                        local_version = plugin_info.get("version", "0.0.0")
                        hub_version = hub_details.get("version", "0.0.0")

                        # Simple version comparison (could be improved)
                        if hub_version != local_version:
                            updates_available.append(
                                {
                                    "plugin_id": plugin_id,
                                    "local_version": local_version,
                                    "hub_version": hub_version,
                                    "details": hub_details,
                                }
                            )

        except Exception as e:
            logger.error(f"❌ Update check failed: {e}")

        return updates_available

    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "enabled": self.enabled,
            "connected": self.client.connected if self.client else False,
            "hub_url": self.hub_url,
            "local_plugins": len(self.local_plugins),
            "hub_plugins_cached": len(self.hub_plugins_cache),
            "last_sync": self.last_sync_time.isoformat()
            if self.last_sync_time
            else None,
        }

    async def shutdown(self):
        """Cleanup and shutdown integration"""
        logger.info("🛑 Shutting down Aetherra Hub integration...")

        if self.client:
            await self.client.disconnect()

        logger.info("✅ Hub integration shutdown complete")


# Convenience functions for easy integration
async def get_hub_integration(
    project_root: Optional[str] = None,
) -> AetherraHubIntegration:
    """Get an initialized Hub integration instance"""
    integration = AetherraHubIntegration(project_root)
    await integration.initialize()
    return integration


async def search_plugins(
    query: str = "", category: Optional[str] = None
) -> Dict[str, Any]:
    """Quick plugin search function"""
    async with AetherraHubClient() as client:
        filters = {"category": category} if category else {}
        return await client.search_plugins(query, filters)


async def install_plugin(plugin_id: str, version: str = "latest") -> Dict[str, Any]:
    """Quick plugin installation function"""
    integration = await get_hub_integration()
    try:
        return await integration.install_plugin_from_hub(plugin_id, version)
    finally:
        await integration.shutdown()


if __name__ == "__main__":
    # Test the integration
    async def test_integration():
        integration = AetherraHubIntegration()

        try:
            success = await integration.initialize()
            if success:
                status = integration.get_status()
                print(f"Hub Integration Status: {json.dumps(status, indent=2)}")

                # Test search
                results = await integration.search_hub_plugins("memory")
                print(
                    f"Search results: {len(results.get('plugins', []))} plugins found"
                )

        finally:
            await integration.shutdown()

    asyncio.run(test_integration())
