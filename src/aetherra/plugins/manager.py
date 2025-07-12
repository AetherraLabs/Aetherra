#!/usr/bin/env python3
"""
🔌 Aetherra Plugin Registry System
Advanced plugin management with registry integration for AI-consciousness programming.

This is the enhanced plugin system that integrates with the central Aetherra
Plugin Registry, enabling discovery, installation, and management of community
AI-consciousness modules.

License: GPL-3.0
"""

import json
import logging
import os
import shutil
import sys
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

try:
    import semantic_version
except ImportError:
    # Fallback for version comparison
    semantic_version = None

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PluginManifest:
    """Enhanced plugin manifest structure"""

    name: str
    version: str
    description: str
    author: str
    category: str = "general"
    license: str = "MIT"
    aetherra_version: str = ">=3.0.0"
    dependencies: Dict[str, Any] = field(default_factory=dict)
    entry_point: str = "plugin.aether"
    exports: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    repository: Optional[str] = None
    documentation: Optional[str] = None
    homepage: Optional[str] = None
    bug_reports: Optional[str] = None
    security_permissions: List[str] = field(default_factory=list)
    compatibility: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    ai_consciousness_version: str = ">=1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        """Create PluginManifest from dictionary"""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            category=data.get("category", "general"),
            author=data["author"],
            license=data.get("license", "MIT"),
            aetherra_version=data.get("aetherra_version", ">=3.0.0"),
            dependencies=data.get("dependencies", {}),
            entry_point=data.get("entry_point", "plugin.aether"),
            exports=data.get("exports", {}),
            keywords=data.get("keywords", []),
            repository=data.get("repository"),
            documentation=data.get("documentation"),
            homepage=data.get("homepage"),
            bug_reports=data.get("bug_reports"),
            security_permissions=data.get("security_permissions", []),
            compatibility=data.get("compatibility", {}),
            tags=data.get("tags", []),
            ai_consciousness_version=data.get("ai_consciousness_version", ">=1.0.0"),
            metadata=data.get("metadata", {}),
        )


class PluginManager:
    """Enhanced plugin manager with registry integration."""

    # Required plugin metadata
    name = "manager"
    description = "Plugin manager for Aetherra plugin system"
    input_schema = {
        "type": "object",
        "properties": {"input": {"type": "string", "description": "Input data"}},
        "required": ["input"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Processing result"},
            "status": {"type": "string", "description": "Operation status"},
        },
    }
    created_by = "Plugin System Auto-Fixer"


@dataclass
class PluginInfo:
    """Plugin information with installation status"""

    manifest: PluginManifest
    installed: bool = False
    loaded: bool = False
    path: Optional[Path] = None
    download_count: int = 0
    rating: float = 0.0
    last_updated: Optional[datetime] = None


class PluginRegistryClient:
    """Client for interacting with AetherraCode Plugin Registry"""

    def __init__(self, registry_url: str = "http://localhost:3001/api/v1"):
        self.registry_url = registry_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "AetherraCode-Plugin-Manager/3.0.0",
                "Accept": "application/json",
            }
        )

    def health_check(self) -> bool:
        """Check if registry is available"""
        try:
            response = self.session.get(f"{self.registry_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate plugin: {e}")
            return False

    def search_plugins(
        self,
        query: str = "",
        category: str = "",
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search for plugins in the registry"""
        params = {"q": query, "category": category, "limit": limit, "offset": offset}

        if tags:
            params["tags"] = ",".join(tags)

        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}

        response = self.session.get(
            f"{self.registry_url}/plugins/search", params=params
        )
        response.raise_for_status()
        return response.json()

    def get_plugin_info(self, name: str) -> PluginInfo:
        """Get detailed information about a specific plugin"""
        response = self.session.get(f"{self.registry_url}/plugins/{name}")
        response.raise_for_status()
        data = response.json()

        manifest = PluginManifest.from_dict(data["manifest"])

        return PluginInfo(
            manifest=manifest,
            download_count=data.get("download_count", 0),
            rating=data.get("rating", 0.0),
            last_updated=datetime.fromisoformat(data["last_updated"])
            if data.get("last_updated")
            else None,
        )

    def get_plugin_versions(self, name: str) -> List[str]:
        """Get available versions for a plugin"""
        response = self.session.get(f"{self.registry_url}/plugins/{name}/versions")
        response.raise_for_status()
        return response.json().get("versions", [])

    def download_plugin(self, name: str, version: str = "latest") -> bytes:
        """Download plugin package from registry"""
        url = f"{self.registry_url}/plugins/{name}/download"
        params = {}
        if version != "latest":
            params["version"] = version

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def get_categories(self) -> List[str]:
        """Get available plugin categories"""
        response = self.session.get(f"{self.registry_url}/categories")
        response.raise_for_status()
        return response.json().get("categories", [])

    def get_popular_plugins(self, limit: int = 20) -> List[PluginInfo]:
        """Get most popular plugins"""
        response = self.session.get(
            f"{self.registry_url}/plugins/popular", params={"limit": limit}
        )
        response.raise_for_status()

        plugins = []
        for data in response.json().get("plugins", []):
            manifest = PluginManifest.from_dict(data["manifest"])
            plugins.append(
                PluginInfo(
                    manifest=manifest,
                    download_count=data.get("download_count", 0),
                    rating=data.get("rating", 0.0),
                )
            )

        return plugins


class PluginSecurityManager:
    """Handle plugin security validation and sandboxing"""

    GPL_COMPATIBLE_LICENSES = [
        "GPL-3.0",
        "GPL-3.0-or-later",
        "GPL-2.0",
        "GPL-2.0-or-later",
        "LGPL-3.0",
        "LGPL-3.0-or-later",
        "LGPL-2.1",
        "LGPL-2.1-or-later",
        "BSD-3-Clause",
        "BSD-2-Clause",
        "MIT",
        "Apache-2.0",
        "MPL-2.0",
        "ISC",
        "X11",
        "Public-Domain",
    ]

    DANGEROUS_PERMISSIONS = [
        "system_access",
        "network_unrestricted",
        "file_system_write",
        "process_execution",
        "registry_modification",
    ]

    def validate_license(self, license_name: str) -> bool:
        """Check if license is GPL-3.0 compatible"""
        return license_name in self.GPL_COMPATIBLE_LICENSES

    def validate_permissions(self, permissions: List[str]) -> Dict[str, bool]:
        """Validate plugin security permissions"""
        validation = {}
        for permission in permissions:
            validation[permission] = {
                "allowed": permission not in self.DANGEROUS_PERMISSIONS,
                "requires_approval": permission in self.DANGEROUS_PERMISSIONS,
                "description": self._get_permission_description(permission),
            }
        return validation

    def scan_plugin_code(self, plugin_path: Path) -> Dict[str, Any]:
        """Basic security scan of plugin code"""
        security_report = {"threats_found": [], "warnings": [], "safe": True}

        # Scan AetherraCode files for potentially dangerous patterns
        for aetherra_file in plugin_path.glob("**/*.aether"):
            content = aetherra_file.read_text()

            dangerous_patterns = [
                "system_execute",
                "file_delete",
                "network_raw",
                "memory_direct",
                "process_kill",
                "registry_write",
            ]

            for pattern in dangerous_patterns:
                if pattern in content:
                    security_report["threats_found"].append(
                        {
                            "file": str(aetherra_file.relative_to(plugin_path)),
                            "pattern": pattern,
                            "severity": "high",
                        }
                    )
                    security_report["safe"] = False

        return security_report

    def _get_permission_description(self, permission: str) -> str:
        """Get human-readable description of permission"""
        descriptions = {
            "system_access": "Access to system-level functions and APIs",
            "network_unrestricted": "Unrestricted network access to any host",
            "file_system_write": "Write access to file system outside plugin directory",
            "process_execution": "Ability to execute external processes",
            "registry_modification": "Modify system registry or configuration",
        }
        return descriptions.get(permission, f"Permission: {permission}")


class EnhancedPluginManager:
    """Enhanced plugin manager with registry integration"""

    def __init__(
        self, plugins_dir: Optional[str] = None, registry_url: Optional[str] = None
    ):
        # Setup directories
        if plugins_dir is None:
            home = Path.home()
            self.plugins_dir = home / ".aethercode" / "plugins"
        else:
            self.plugins_dir = Path(plugins_dir)

        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.plugins_dir / ".cache"
        self.cache_dir.mkdir(exist_ok=True)

        # Initialize components
        self.registry = (
            PluginRegistryClient(registry_url)
            if registry_url
            else PluginRegistryClient()
        )
        self.security = PluginSecurityManager()
        self.loaded_plugins: Dict[str, Any] = {}

        # Plugin metadata cache
        self._plugin_cache: Dict[str, PluginInfo] = {}
        self._load_plugin_cache()

        logger.info("🔌 Enhanced AetherraCode Plugin Manager initialized")
        logger.info(f"📁 Plugins directory: {self.plugins_dir}")
        logger.info(f"🌐 Registry: {self.registry.registry_url}")

    def install_plugin(
        self,
        name: str,
        version: str = "latest",
        force: bool = False,
        skip_security: bool = False,
    ) -> bool:
        """Install a plugin from the registry with enhanced validation"""
        try:
            logger.info(f"🔄 Installing plugin: {name} ({version})")

            # Check registry availability
            if not self.registry.health_check():
                logger.error("❌ Plugin registry is not available")
                return False

            # Check if plugin already installed
            plugin_dir = self.plugins_dir / name
            if plugin_dir.exists() and not force:
                logger.warning(
                    f"⚠️  Plugin {name} already installed. Use --force to reinstall."
                )
                return False

            # Get plugin information
            plugin_info = self.registry.get_plugin_info(name)

            # Security validation
            if not skip_security:
                if not self.security.validate_license(plugin_info.manifest.license):
                    logger.error(
                        f"❌ Plugin license '{plugin_info.manifest.license}' is not GPL-3.0 compatible"
                    )
                    return False

                permissions = self.security.validate_permissions(
                    plugin_info.manifest.security_permissions
                )
                dangerous_perms = [
                    p
                    for p, v in permissions.items()
                    if isinstance(v, dict) and v.get("requires_approval", False)
                ]
                if dangerous_perms:
                    logger.warning(
                        f"⚠️  Plugin requests dangerous permissions: {dangerous_perms}"
                    )
                    if not self._prompt_user_approval(
                        f"Allow dangerous permissions for {name}?"
                    ):
                        return False

            # Download and extract plugin
            plugin_data = self.registry.download_plugin(name, version)

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Save and extract archive
                archive_path = temp_path / f"{name}.tar.gz"
                with open(archive_path, "wb") as f:
                    f.write(plugin_data)

                extract_dir = temp_path / "extracted"
                extract_dir.mkdir()

                # Extract based on file type
                if archive_path.suffix == ".gz":
                    with tarfile.open(archive_path, "r:gz") as tar:
                        tar.extractall(extract_dir)
                else:
                    with zipfile.ZipFile(archive_path, "r") as zip_file:
                        zip_file.extractall(extract_dir)

                # Find plugin root (handle nested directories)
                plugin_root = self._find_plugin_root(extract_dir)
                if not plugin_root:
                    raise ValueError("Could not find plugin root directory")

                # Validate plugin structure
                manifest_path = plugin_root / "aetherra-plugin.json"
                if not manifest_path.exists():
                    raise ValueError("Plugin manifest not found")

                manifest = self._parse_manifest(manifest_path)

                # Security scan
                if not skip_security:
                    security_report = self.security.scan_plugin_code(plugin_root)
                    if not security_report["safe"]:
                        logger.error(f"❌ Security threats found in plugin {name}")
                        for threat in security_report["threats_found"]:
                            logger.error(
                                f"   {threat['file']}: {threat['pattern']} ({threat['severity']})"
                            )
                        return False

                # Remove existing installation if force
                if plugin_dir.exists():
                    shutil.rmtree(plugin_dir)

                # Install plugin
                shutil.copytree(plugin_root, plugin_dir)

                # Update cache
                plugin_info.installed = True
                plugin_info.path = plugin_dir
                self._plugin_cache[name] = plugin_info
                self._save_plugin_cache()

                logger.info(
                    f"✅ Plugin installed successfully: {name} v{manifest.version}"
                )
                return True

        except Exception as e:
            logger.error(f"❌ Failed to install plugin {name}: {e}")
            return False

    def uninstall_plugin(self, name: str) -> bool:
        """Uninstall a plugin with cleanup"""
        try:
            plugin_dir = self.plugins_dir / name

            if not plugin_dir.exists():
                logger.warning(f"⚠️  Plugin {name} not found")
                return False

            # Cleanup loaded plugin
            if name in self.loaded_plugins:
                self._cleanup_plugin(name)
                del self.loaded_plugins[name]

            # Remove plugin directory
            shutil.rmtree(plugin_dir)

            # Update cache
            if name in self._plugin_cache:
                self._plugin_cache[name].installed = False
                self._plugin_cache[name].path = None

            self._save_plugin_cache()
            logger.info(f"✅ Plugin uninstalled: {name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to uninstall plugin {name}: {e}")
            return False

    def list_installed_plugins(self) -> List[PluginInfo]:
        """List all installed plugins with detailed information"""
        plugins = []

        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
                manifest_path = plugin_dir / "aetherra-plugin.json"
                if manifest_path.exists():
                    try:
                        manifest = self._parse_manifest(manifest_path)

                        plugin_info = PluginInfo(
                            manifest=manifest,
                            installed=True,
                            loaded=manifest.name in self.loaded_plugins,
                            path=plugin_dir,
                        )

                        # Add cached information if available
                        if manifest.name in self._plugin_cache:
                            cached = self._plugin_cache[manifest.name]
                            plugin_info.download_count = cached.download_count
                            plugin_info.rating = cached.rating
                            plugin_info.last_updated = cached.last_updated

                        plugins.append(plugin_info)

                    except Exception as e:
                        logger.warning(f"⚠️  Invalid plugin in {plugin_dir}: {e}")

        return sorted(plugins, key=lambda p: p.manifest.name)

    def search_registry(
        self, query: str = "", category: str = "", tags: Optional[List[str]] = None
    ) -> List[PluginInfo]:
        """Search the plugin registry with caching"""
        try:
            results = self.registry.search_plugins(query, category, tags)
            plugins = []

            for data in results.get("plugins", []):
                manifest = PluginManifest.from_dict(data["manifest"])

                plugin_info = PluginInfo(
                    manifest=manifest,
                    download_count=data.get("download_count", 0),
                    rating=data.get("rating", 0.0),
                    last_updated=datetime.fromisoformat(data["last_updated"])
                    if data.get("last_updated")
                    else None,
                )

                # Check if installed locally
                local_path = self.plugins_dir / manifest.name
                plugin_info.installed = local_path.exists()
                if plugin_info.installed:
                    plugin_info.path = local_path
                    plugin_info.loaded = manifest.name in self.loaded_plugins

                plugins.append(plugin_info)

                # Update cache
                self._plugin_cache[manifest.name] = plugin_info

            self._save_plugin_cache()
            return plugins

        except Exception as e:
            logger.error(f"❌ Registry search failed: {e}")
            return []

    def get_popular_plugins(self, limit: int = 20) -> List[PluginInfo]:
        """Get popular plugins from registry"""
        try:
            return self.registry.get_popular_plugins(limit)
        except Exception as e:
            logger.error(f"❌ Failed to get popular plugins: {e}")
            return []

    def update_plugin(self, name: str) -> bool:
        """Update a plugin to latest version"""
        try:
            if name not in self._plugin_cache or not self._plugin_cache[name].installed:
                logger.error(f"❌ Plugin {name} is not installed")
                return False

            current_version = self._plugin_cache[name].manifest.version

            # Get latest version from registry
            plugin_info = self.registry.get_plugin_info(name)
            latest_version = plugin_info.manifest.version

            # Compare versions using semantic versioning if available
            if semantic_version is not None:
                try:
                    if semantic_version.Version(
                        current_version
                    ) >= semantic_version.Version(latest_version):
                        logger.info(
                            f"✅ Plugin {name} is already up to date (v{current_version})"
                        )
                        return True
                except Exception:
                    # Fallback to string comparison if semantic versioning fails
                    if current_version == latest_version:
                        logger.info(
                            f"✅ Plugin {name} is already up to date (v{current_version})"
                        )
                        return True
            else:
                # Simple string comparison fallback
                if current_version == latest_version:
                    logger.info(
                        f"✅ Plugin {name} is already up to date (v{current_version})"
                    )
                    return True

            logger.info(
                f"🔄 Updating {name} from v{current_version} to v{latest_version}"
            )
            return self.install_plugin(name, latest_version, force=True)

        except Exception as e:
            logger.error(f"❌ Failed to update plugin {name}: {e}")
            return False

    def _parse_manifest(self, manifest_path: Path) -> PluginManifest:
        """Parse and validate plugin manifest"""
        with open(manifest_path) as f:
            data = json.load(f)

        required_fields = [
            "name",
            "version",
            "description",
            "category",
            "author",
            "license",
        ]
        for required_field in required_fields:
            if required_field not in data:
                raise ValueError(
                    f"Missing required field in manifest: {required_field}"
                )

        return PluginManifest.from_dict(data)

    def _find_plugin_root(self, extract_dir: Path) -> Optional[Path]:
        """Find the root directory of extracted plugin"""
        # Look for manifest file
        for root, _dirs, files in os.walk(extract_dir):
            if "aetherra-plugin.json" in files:
                return Path(root)
        return None

    def _load_plugin_cache(self) -> None:
        """Load plugin cache from disk"""
        cache_file = self.cache_dir / "plugin_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cache_data = json.load(f)

                for name, data in cache_data.items():
                    manifest = PluginManifest.from_dict(data["manifest"])
                    self._plugin_cache[name] = PluginInfo(
                        manifest=manifest,
                        installed=data.get("installed", False),
                        download_count=data.get("download_count", 0),
                        rating=data.get("rating", 0.0),
                        last_updated=datetime.fromisoformat(data["last_updated"])
                        if data.get("last_updated")
                        else None,
                    )
            except Exception as e:
                logger.warning(f"⚠️  Failed to load plugin cache: {e}")

    def _save_plugin_cache(self) -> None:
        """Save plugin cache to disk"""
        cache_file = self.cache_dir / "plugin_cache.json"
        cache_data = {}

        for name, info in self._plugin_cache.items():
            cache_data[name] = {
                "manifest": {
                    "name": info.manifest.name,
                    "version": info.manifest.version,
                    "description": info.manifest.description,
                    "category": info.manifest.category,
                    "author": info.manifest.author,
                    "license": info.manifest.license,
                    "keywords": info.manifest.keywords,
                },
                "installed": info.installed,
                "download_count": info.download_count,
                "rating": info.rating,
                "last_updated": info.last_updated.isoformat()
                if info.last_updated
                else None,
            }

        try:
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️  Failed to save plugin cache: {e}")

    def _prompt_user_approval(self, message: str) -> bool:
        """Prompt user for approval (simplified for CLI)"""
        try:
            response = input(f"{message} (y/N): ").lower().strip()
            return response in ["y", "yes"]
        except KeyboardInterrupt:
            return False

    def _cleanup_plugin(self, name: str) -> None:
        """Cleanup plugin before unloading"""
        if name in self.loaded_plugins:
            logger.info(f"🧹 Cleaning up plugin: {name}")
            # In real implementation, this would call plugin cleanup functions


# CLI Interface for enhanced plugin management
def main():
    """Enhanced CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AetherraCode Enhanced Plugin Manager",
        epilog="Use 'aetherra plugin <command> --help' for command-specific help",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a plugin")
    install_parser.add_argument("name", help="Plugin name")
    install_parser.add_argument("--version", default="latest", help="Plugin version")
    install_parser.add_argument(
        "--force", action="store_true", help="Force reinstallation"
    )
    install_parser.add_argument(
        "--skip-security", action="store_true", help="Skip security validation"
    )

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a plugin")
    uninstall_parser.add_argument("name", help="Plugin name")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a plugin")
    update_parser.add_argument(
        "name", nargs="?", help="Plugin name (update all if not specified)"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List installed plugins")
    list_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed information"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search plugin registry")
    search_parser.add_argument("query", nargs="?", default="", help="Search query")
    search_parser.add_argument("--category", help="Plugin category")
    search_parser.add_argument("--tags", help="Comma-separated tags")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get plugin information")
    info_parser.add_argument("name", help="Plugin name")

    # Popular command
    popular_parser = subparsers.add_parser("popular", help="Show popular plugins")
    popular_parser.add_argument(
        "--limit", type=int, default=20, help="Number of plugins to show"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = EnhancedPluginManager()

    # Execute commands
    if args.command == "install":
        success = manager.install_plugin(
            args.name, args.version, force=args.force, skip_security=args.skip_security
        )
        sys.exit(0 if success else 1)

    elif args.command == "uninstall":
        success = manager.uninstall_plugin(args.name)
        sys.exit(0 if success else 1)

    elif args.command == "update":
        if args.name:
            success = manager.update_plugin(args.name)
            sys.exit(0 if success else 1)
        else:
            # Update all plugins
            plugins = manager.list_installed_plugins()
            updated = 0
            for plugin in plugins:
                if manager.update_plugin(plugin.manifest.name):
                    updated += 1
            print(f"✅ Updated {updated} plugins")

    elif args.command == "list":
        plugins = manager.list_installed_plugins()
        if plugins:
            print(f"\n🔌 Installed AetherraCode Plugins ({len(plugins)}):")
            print("=" * 60)

            for plugin in plugins:
                status = "🟢 Loaded" if plugin.loaded else "⚪ Available"
                rating_stars = "⭐" * int(plugin.rating) if plugin.rating > 0 else ""

                print(
                    f"{status} {plugin.manifest.name} v{plugin.manifest.version} ({plugin.manifest.category})"
                )
                print(f"    {plugin.manifest.description}")

                if args.detailed:
                    print(
                        f"    Author: {plugin.manifest.author} | License: {plugin.manifest.license}"
                    )
                    if plugin.download_count:
                        print(
                            f"    Downloads: {plugin.download_count:,} | Rating: {rating_stars}"
                        )
                    if plugin.manifest.keywords:
                        print(f"    Keywords: {', '.join(plugin.manifest.keywords)}")
                print()
        else:
            print(
                "No plugins installed. Use 'aetherra plugin search' to discover plugins."
            )

    elif args.command == "search":
        tags = args.tags.split(",") if args.tags else None
        results = manager.search_registry(args.query, args.category, tags)

        if results:
            print(f"\n🔍 Plugin Registry Search Results ({len(results)} found):")
            print("=" * 70)

            for plugin in results:
                status_icon = "📦"
                if plugin.installed:
                    status_icon = "✅ Installed"

                rating_stars = "⭐" * int(plugin.rating) if plugin.rating > 0 else ""

                print(
                    f"{status_icon} {plugin.manifest.name} v{plugin.manifest.version} ({plugin.manifest.category})"
                )
                print(f"    {plugin.manifest.description}")
                print(
                    f"    Author: {plugin.manifest.author} | Downloads: {plugin.download_count:,} | {rating_stars}"
                )
                if plugin.manifest.keywords:
                    print(f"    Keywords: {', '.join(plugin.manifest.keywords)}")
                print()
        else:
            print("No plugins found matching your search criteria.")

    elif args.command == "popular":
        plugins = manager.get_popular_plugins(args.limit)

        if plugins:
            print(f"\n🌟 Most Popular AetherraCode Plugins (Top {len(plugins)}):")
            print("=" * 60)

            for i, plugin in enumerate(plugins, 1):
                rating_stars = "⭐" * int(plugin.rating)
                print(f"{i:2d}. {plugin.manifest.name} v{plugin.manifest.version}")
                print(f"     {plugin.manifest.description}")
                print(
                    f"     Downloads: {plugin.download_count:,} | Rating: {rating_stars}"
                )
                print()

    elif args.command == "info":
        try:
            # Check if plugin is installed locally first
            installed_plugins = {
                p.manifest.name: p for p in manager.list_installed_plugins()
            }

            if args.name in installed_plugins:
                plugin = installed_plugins[args.name]
                print(f"\n📋 Installed Plugin: {plugin.manifest.name}")
            else:
                plugin = manager.registry.get_plugin_info(args.name)
                print(f"\n📋 Registry Plugin: {plugin.manifest.name}")

            print("=" * 60)
            print(f"Version: {plugin.manifest.version}")
            print(f"Category: {plugin.manifest.category}")
            print(f"Author: {plugin.manifest.author}")
            print(f"License: {plugin.manifest.license}")
            print(f"Description: {plugin.manifest.description}")

            if plugin.rating > 0:
                rating_stars = "⭐" * int(plugin.rating)
                print(f"Rating: {rating_stars} ({plugin.rating:.1f})")

            if plugin.download_count > 0:
                print(f"Downloads: {plugin.download_count:,}")

            if plugin.manifest.repository:
                print(f"Repository: {plugin.manifest.repository}")

            if plugin.manifest.documentation:
                print(f"Documentation: {plugin.manifest.documentation}")

            if plugin.manifest.keywords:
                print(f"Keywords: {', '.join(plugin.manifest.keywords)}")

            if plugin.manifest.dependencies:
                print(f"Dependencies: {', '.join(plugin.manifest.dependencies.keys())}")

            if plugin.installed:
                print(f"Installed: ✅ Yes (Path: {plugin.path})")
                print(f"Loaded: {'✅ Yes' if plugin.loaded else '⚪ No'}")
            else:
                print("Installed: ❌ No")

        except Exception as e:
            print(f"❌ Failed to get plugin info: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
