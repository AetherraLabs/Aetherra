#!/usr/bin/env python3
"""
[TOOL] LYRIXA PLUGIN SYSTEM - COMPLETE REBUILD
=========================================

This is the REAL plugin system that Lyrixa needs.
- Install/uninstall plugins from within Lyrixa UI
- Create plugins within the app
- Load plugins within the app
- Plugin discovery and management
- Full UI integration

NO MORE SCATTERED CODE - THIS IS THE ONE TRUE SYSTEM
"""

import importlib.util
import json
import os
import shutil
import sys
import traceback
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import Lyrixa components
try:
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem

    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

# Import safe file operations
try:
    from safe_file_operations import safe_write_file

    SAFE_WRITE_AVAILABLE = True
except ImportError:
    SAFE_WRITE_AVAILABLE = False

    def safe_write_file(path, content, encoding="utf-8"):
        """Fallback to regular file writing"""
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return True


class PluginManifest:
    """Plugin manifest for metadata and requirements"""

    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name", "Unknown Plugin")
        self.version = data.get("version", "1.0.0")
        self.description = data.get("description", "No description")
        self.author = data.get("author", "Unknown")
        self.capabilities = data.get("capabilities", [])
        self.dependencies = data.get("dependencies", [])
        self.entry_point = data.get("entry_point", "main.py")
        self.ui_components = data.get("ui_components", [])
        self.permissions = data.get("permissions", [])


class PluginInstance:
    """Running instance of a plugin"""

    def __init__(self, manifest: PluginManifest, plugin_path: Path):
        self.manifest = manifest
        self.plugin_path = plugin_path
        self.loaded = False
        self.active = False
        self.module = None
        self.last_error = None
        self.execution_count = 0

    def load(self):
        """Load the plugin module"""
        try:
            # Add plugin path to Python path
            sys.path.insert(0, str(self.plugin_path))

            # Import the main module
            spec = importlib.util.spec_from_file_location(
                self.manifest.name, self.plugin_path / self.manifest.entry_point
            )

            if spec and spec.loader:
                self.module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.module)
                self.loaded = True
                self.last_error = None
                return True
            else:
                self.last_error = "Failed to load module spec"
                return False

        except Exception as e:
            self.last_error = str(e)
            return False

    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a plugin command"""
        if not self.loaded or not self.module:
            return {"error": "Plugin not loaded"}

        try:
            # Look for execute function in plugin
            if hasattr(self.module, "execute"):
                self.execution_count += 1
                result = self.module.execute(command, **kwargs)
                return {"success": True, "result": result}
            else:
                return {"error": "Plugin has no execute function"}

        except Exception as e:
            return {"error": f"Plugin execution failed: {str(e)}"}


class LyrixaPluginSystem:
    """
    The ONE TRUE plugin system for Lyrixa

    This system provides:
    - Plugin installation/uninstallation from UI
    - Plugin creation tools within Lyrixa
    - Plugin discovery and management
    - Real-time plugin loading/unloading
    - Plugin communication with Lyrixa core
    """

    def __init__(self, lyrixa_instance=None):
        self.lyrixa = lyrixa_instance
        self.plugins_dir = Path("lyrixa_plugins")
        self.plugins_dir.mkdir(exist_ok=True)

        # Plugin registry
        self.installed_plugins: Dict[str, PluginInstance] = {}
        self.active_plugins: Dict[str, PluginInstance] = {}
        self.plugin_registry_file = self.plugins_dir / "registry.json"

        # Load existing plugins
        self._load_plugin_registry()
        self._discover_plugins()

        print("🔌 Lyrixa Plugin System Initialized")
        print(f"   📁 Plugin directory: {self.plugins_dir}")
        print(f"   🔍 Found {len(self.installed_plugins)} installed plugins")

    def _load_plugin_registry(self):
        """Load plugin registry from disk"""
        if self.plugin_registry_file.exists():
            try:
                with open(self.plugin_registry_file, "r") as f:
                    data = json.load(f)
                    print(
                        f"📋 Loaded plugin registry with {len(data.get('plugins', []))} entries"
                    )
            except Exception as e:
                print(f"[WARN] Failed to load plugin registry: {e}")

    def _save_plugin_registry(self):
        """Save plugin registry to disk using safe file operations"""
        registry_data = {
            "plugins": [],
            "last_updated": datetime.now().isoformat(),
            "lyrixa_version": "2.0.0",
        }

        for name, plugin in self.installed_plugins.items():
            registry_data["plugins"].append(
                {
                    "name": name,
                    "version": plugin.manifest.version,
                    "description": plugin.manifest.description,
                    "author": plugin.manifest.author,
                    "installed_at": datetime.now().isoformat(),
                    "active": plugin.active,
                    "execution_count": plugin.execution_count,
                }
            )

        registry_content = json.dumps(registry_data, indent=2)

        # Use safe file writing to prevent corruption
        if SAFE_WRITE_AVAILABLE:
            success = safe_write_file(str(self.plugin_registry_file), registry_content)
            if not success:
                print(
                    f"[WARN] Failed to safely write plugin registry, falling back to normal write"
                )
                with open(self.plugin_registry_file, "w") as f:
                    f.write(registry_content)
        else:
            with open(self.plugin_registry_file, "w") as f:
                f.write(registry_content)

    def _discover_plugins(self):
        """Discover plugins in the plugins directory"""
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
                manifest_file = plugin_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, "r") as f:
                            manifest_data = json.load(f)

                        manifest = PluginManifest(manifest_data)
                        plugin_instance = PluginInstance(manifest, plugin_dir)

                        self.installed_plugins[manifest.name] = plugin_instance
                        print(
                            f"   🔍 Discovered plugin: {manifest.name} v{manifest.version}"
                        )

                    except Exception as e:
                        print(f"   ❌ Failed to load plugin {plugin_dir.name}: {e}")

    def install_plugin(self, plugin_source: str) -> Dict[str, Any]:
        """
        Install a plugin from various sources

        Args:
            plugin_source: Can be:
                - Path to a .zip file
                - Path to a directory
                - URL to download from
                - Plugin name from repository
        """
        try:
            if plugin_source.endswith(".zip"):
                return self._install_from_zip(plugin_source)
            elif os.path.isdir(plugin_source):
                return self._install_from_directory(plugin_source)
            elif plugin_source.startswith("http"):
                return self._install_from_url(plugin_source)
            else:
                return self._install_from_repository(plugin_source)

        except Exception as e:
            return {"success": False, "error": f"Installation failed: {str(e)}"}

    def _install_from_zip(self, zip_path: str) -> Dict[str, Any]:
        """Install plugin from ZIP file"""
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Extract to temporary directory first
                temp_dir = self.plugins_dir / "temp_install"
                temp_dir.mkdir(exist_ok=True)

                zip_ref.extractall(temp_dir)

                # Look for manifest file
                manifest_file = None
                for root, dirs, files in os.walk(temp_dir):
                    if "manifest.json" in files:
                        manifest_file = Path(root) / "manifest.json"
                        break

                if not manifest_file:
                    shutil.rmtree(temp_dir)
                    return {
                        "success": False,
                        "error": "No manifest.json found in plugin",
                    }

                # Load manifest and validate
                with open(manifest_file, "r") as f:
                    manifest_data = json.load(f)

                manifest = PluginManifest(manifest_data)

                # Check if plugin already exists
                if manifest.name in self.installed_plugins:
                    shutil.rmtree(temp_dir)
                    return {
                        "success": False,
                        "error": f"Plugin {manifest.name} already installed",
                    }

                # Move to final location
                final_dir = self.plugins_dir / manifest.name
                if final_dir.exists():
                    shutil.rmtree(final_dir)

                shutil.move(str(manifest_file.parent), str(final_dir))
                shutil.rmtree(temp_dir)

                # Create plugin instance
                plugin_instance = PluginInstance(manifest, final_dir)
                self.installed_plugins[manifest.name] = plugin_instance

                # Save registry
                self._save_plugin_registry()

                # Log to memory if available
                if MEMORY_AVAILABLE and self.lyrixa:
                    self.lyrixa.memory.remember(
                        f"Installed plugin: {manifest.name} v{manifest.version}",
                        tags=["plugin", "installation", "system"],
                        category="plugins",
                    )

                return {
                    "success": True,
                    "message": f"Successfully installed {manifest.name} v{manifest.version}",
                    "plugin_name": manifest.name,
                }

        except Exception as e:
            return {"success": False, "error": f"ZIP installation failed: {str(e)}"}

    def _install_from_directory(self, dir_path: str) -> Dict[str, Any]:
        """Install plugin from directory"""
        try:
            source_dir = Path(dir_path)
            manifest_file = source_dir / "manifest.json"

            if not manifest_file.exists():
                return {"success": False, "error": "No manifest.json found"}

            with open(manifest_file, "r") as f:
                manifest_data = json.load(f)

            manifest = PluginManifest(manifest_data)

            if manifest.name in self.installed_plugins:
                return {
                    "success": False,
                    "error": f"Plugin {manifest.name} already installed",
                }

            # Copy to plugins directory
            dest_dir = self.plugins_dir / manifest.name
            if dest_dir.exists():
                shutil.rmtree(dest_dir)

            shutil.copytree(source_dir, dest_dir)

            # Create plugin instance
            plugin_instance = PluginInstance(manifest, dest_dir)
            self.installed_plugins[manifest.name] = plugin_instance

            self._save_plugin_registry()

            return {
                "success": True,
                "message": f"Successfully installed {manifest.name} v{manifest.version}",
                "plugin_name": manifest.name,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Directory installation failed: {str(e)}",
            }

    def uninstall_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Uninstall a plugin"""
        try:
            if plugin_name not in self.installed_plugins:
                return {"success": False, "error": f"Plugin {plugin_name} not found"}

            plugin = self.installed_plugins[plugin_name]

            # Deactivate if active
            if plugin_name in self.active_plugins:
                self.deactivate_plugin(plugin_name)

            # Remove plugin directory
            if plugin.plugin_path.exists():
                shutil.rmtree(plugin.plugin_path)

            # Remove from registry
            del self.installed_plugins[plugin_name]
            self._save_plugin_registry()

            # Log to memory
            if MEMORY_AVAILABLE and self.lyrixa:
                self.lyrixa.memory.remember(
                    f"Uninstalled plugin: {plugin_name}",
                    tags=["plugin", "uninstallation", "system"],
                    category="plugins",
                )

            return {
                "success": True,
                "message": f"Successfully uninstalled {plugin_name}",
            }

        except Exception as e:
            return {"success": False, "error": f"Uninstallation failed: {str(e)}"}

    def activate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Activate a plugin"""
        try:
            if plugin_name not in self.installed_plugins:
                return {
                    "success": False,
                    "error": f"Plugin {plugin_name} not installed",
                }

            plugin = self.installed_plugins[plugin_name]

            if not plugin.loaded:
                if not plugin.load():
                    return {
                        "success": False,
                        "error": f"Failed to load plugin: {plugin.last_error}",
                    }

            plugin.active = True
            self.active_plugins[plugin_name] = plugin

            # Log activation
            if MEMORY_AVAILABLE and self.lyrixa:
                self.lyrixa.memory.remember(
                    f"Activated plugin: {plugin_name}",
                    tags=["plugin", "activation", "system"],
                    category="plugins",
                )

            return {"success": True, "message": f"Successfully activated {plugin_name}"}

        except Exception as e:
            return {"success": False, "error": f"Activation failed: {str(e)}"}

    def deactivate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Deactivate a plugin"""
        try:
            if plugin_name not in self.active_plugins:
                return {"success": False, "error": f"Plugin {plugin_name} not active"}

            plugin = self.active_plugins[plugin_name]
            plugin.active = False

            del self.active_plugins[plugin_name]

            return {
                "success": True,
                "message": f"Successfully deactivated {plugin_name}",
            }

        except Exception as e:
            return {"success": False, "error": f"Deactivation failed: {str(e)}"}

    def execute_plugin(
        self, plugin_name: str, command: str, **kwargs
    ) -> Dict[str, Any]:
        """Execute a command in an active plugin"""
        if plugin_name not in self.active_plugins:
            return {"success": False, "error": f"Plugin {plugin_name} not active"}

        plugin = self.active_plugins[plugin_name]
        return plugin.execute(command, **kwargs)

    def list_plugins(self) -> Dict[str, Any]:
        """List all plugins with their status"""
        plugins_info = {
            "installed": [],
            "active": [],
            "total_installed": len(self.installed_plugins),
            "total_active": len(self.active_plugins),
        }

        for name, plugin in self.installed_plugins.items():
            plugin_info = {
                "name": name,
                "version": plugin.manifest.version,
                "description": plugin.manifest.description,
                "author": plugin.manifest.author,
                "active": plugin.active,
                "loaded": plugin.loaded,
                "execution_count": plugin.execution_count,
                "capabilities": plugin.manifest.capabilities,
            }

            if plugin.last_error:
                plugin_info["last_error"] = plugin.last_error

            plugins_info["installed"].append(plugin_info)

            if plugin.active:
                plugins_info["active"].append(plugin_info)

        return plugins_info

    def create_plugin_template(
        self, plugin_name: str, description: str = "", overwrite: bool = False
    ) -> Dict[str, Any]:
        """Create a new plugin template"""
        try:
            plugin_dir = self.plugins_dir / plugin_name

            if plugin_dir.exists():
                if not overwrite:
                    # Suggest alternative names
                    alternatives = []
                    for i in range(1, 6):
                        alt_name = f"{plugin_name}_{i}"
                        if not (self.plugins_dir / alt_name).exists():
                            alternatives.append(alt_name)

                    return {
                        "success": False,
                        "error": f"Plugin directory '{plugin_name}' already exists",
                        "suggestions": {
                            "overwrite": "Use overwrite=True to replace existing plugin",
                            "alternatives": alternatives[:3],
                            "action_needed": "Choose a different name or set overwrite=True",
                        },
                    }
                else:
                    # Remove existing directory
                    shutil.rmtree(plugin_dir)
                    print(f"🗑️ Removed existing plugin directory: {plugin_name}")

            plugin_dir.mkdir()

            # Create manifest.json safely
            manifest_data = {
                "name": plugin_name,
                "version": "1.0.0",
                "description": description or f"A Lyrixa plugin: {plugin_name}",
                "author": "Lyrixa User",
                "capabilities": ["custom_command"],
                "dependencies": [],
                "entry_point": "main.py",
                "ui_components": [],
                "permissions": ["lyrixa_core"],
            }

            manifest_content = json.dumps(manifest_data, indent=2)
            manifest_file = plugin_dir / "manifest.json"

            if SAFE_WRITE_AVAILABLE:
                safe_write_file(str(manifest_file), manifest_content)
            else:
                with open(manifest_file, "w") as f:
                    f.write(manifest_content)

            # Create main.py template
            main_py_content = f'''#!/usr/bin/env python3
"""
{plugin_name} - Lyrixa Plugin
{description}

Auto-generated by Lyrixa Plugin System
"""

def execute(command, **kwargs):
    """
    Main plugin execution function

    Args:
        command (str): The command to execute
        **kwargs: Additional arguments

    Returns:
        dict: Result of the command execution
    """

    if command == "hello":
        return {{
            "message": "Hello from {plugin_name}!",
            "plugin": "{plugin_name}",
            "status": "active"
        }}

    elif command == "info":
        return {{
            "name": "{plugin_name}",
            "description": "{description}",
            "capabilities": ["hello", "info"],
            "version": "1.0.0"
        }}

    else:
        return {{
            "error": f"Unknown command: {{command}}",
            "available_commands": ["hello", "info"]
        }}


def initialize():
    """Called when plugin is activated"""
    print(f"🔌 {plugin_name} plugin initialized")
    return True


def cleanup():
    """Called when plugin is deactivated"""
    print(f"🔌 {plugin_name} plugin cleaned up")
    return True


# Plugin metadata (optional)
PLUGIN_INFO = {{
    "name": "{plugin_name}",
    "friendly_name": "{plugin_name.replace("_", " ").title()}",
    "category": "utility",
    "tags": ["custom", "utility", "lyrixa"]
}}
'''

            # Create main.py template safely
            if SAFE_WRITE_AVAILABLE:
                safe_write_file(
                    str(plugin_dir / "main.py"), main_py_content, encoding="utf-8"
                )
            else:
                with open(plugin_dir / "main.py", "w", encoding="utf-8") as f:
                    f.write(main_py_content)

            # Create README.md content
            readme_content = f"""# {plugin_name}

{description}

## Usage

This plugin provides the following commands:

- `hello` - Returns a greeting message
- `info` - Returns plugin information

## Development

This plugin was created using the Lyrixa Plugin System template.

To modify this plugin:

1. Edit `main.py` to add your custom functionality
2. Update `manifest.json` if you add new capabilities or dependencies
3. Test your plugin using the Lyrixa Plugin Manager

## Installation

This plugin is automatically available in Lyrixa once created.

## License

Created with Lyrixa Plugin System
"""

            # Create README.md safely
            if SAFE_WRITE_AVAILABLE:
                safe_write_file(
                    str(plugin_dir / "README.md"), readme_content, encoding="utf-8"
                )
            else:
                with open(plugin_dir / "README.md", "w", encoding="utf-8") as f:
                    f.write(readme_content)

            return {
                "success": True,
                "message": f"Plugin template created: {plugin_name}",
                "plugin_path": str(plugin_dir),
                "files_created": ["manifest.json", "main.py", "README.md"],
            }

        except Exception as e:
            return {"success": False, "error": f"Template creation failed: {str(e)}"}

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a plugin"""
        if plugin_name not in self.installed_plugins:
            return None

        plugin = self.installed_plugins[plugin_name]

        return {
            "name": plugin.manifest.name,
            "version": plugin.manifest.version,
            "description": plugin.manifest.description,
            "author": plugin.manifest.author,
            "capabilities": plugin.manifest.capabilities,
            "dependencies": plugin.manifest.dependencies,
            "ui_components": plugin.manifest.ui_components,
            "permissions": plugin.manifest.permissions,
            "status": {
                "installed": True,
                "loaded": plugin.loaded,
                "active": plugin.active,
                "execution_count": plugin.execution_count,
                "last_error": plugin.last_error,
            },
            "path": str(plugin.plugin_path),
        }

    def search_plugins(self, query: str) -> List[Dict[str, Any]]:
        """Search plugins by name, description, or capabilities"""
        results = []
        query_lower = query.lower()

        for name, plugin in self.installed_plugins.items():
            if (
                query_lower in name.lower()
                or query_lower in plugin.manifest.description.lower()
                or any(
                    query_lower in cap.lower() for cap in plugin.manifest.capabilities
                )
            ):
                results.append(self.get_plugin_info(name))

        return results


# Global instance
plugin_system = None


def get_plugin_system(lyrixa_instance=None):
    """Get the global plugin system instance"""
    global plugin_system
    if plugin_system is None:
        plugin_system = LyrixaPluginSystem(lyrixa_instance)
    return plugin_system


if __name__ == "__main__":
    # Demo the plugin system with enhanced features
    print("🔌 LYRIXA PLUGIN SYSTEM DEMO")
    print("=" * 50)

    # Initialize plugin system
    ps = LyrixaPluginSystem()

    # Test 1: Try creating a plugin that might already exist
    print("\n📝 Test 1: Creating plugin (may already exist)...")
    result = ps.create_plugin_template("hello_world", "A simple hello world plugin")
    if not result["success"]:
        print(f"❌ {result['error']}")
        if "suggestions" in result:
            print("💡 Suggestions:")
            print(f"   - {result['suggestions']['overwrite']}")
            print(f"   - Alternative names: {result['suggestions']['alternatives']}")

            # Try with an alternative name
            if result["suggestions"]["alternatives"]:
                alt_name = result["suggestions"]["alternatives"][0]
                print(f"\n🔄 Trying alternative name: {alt_name}")
                result = ps.create_plugin_template(
                    alt_name, "A simple hello world plugin"
                )
                if result["success"]:
                    print(f"✅ Successfully created plugin: {alt_name}")
    else:
        print(f"✅ Plugin created: {result}")

    # Test 2: Create with overwrite
    print("\n📝 Test 2: Creating plugin with overwrite...")
    result = ps.create_plugin_template(
        "hello_world", "An updated hello world plugin", overwrite=True
    )
    if result["success"]:
        print("✅ Successfully created/updated plugin: hello_world")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

    # Rediscover plugins
    ps._discover_plugins()

    # List all plugins
    plugins_info = ps.list_plugins()
    print(f"\n📋 Found {plugins_info['total_installed']} plugins:")
    for plugin_info in plugins_info["installed"]:
        plugin_name = plugin_info["name"]
        description = plugin_info["description"]
        print(f"  - {plugin_name}: {description}")

    # Test activation and execution
    if "hello_world" in ps.installed_plugins:
        print("\n⚡ Activating hello_world plugin...")
        result = ps.activate_plugin("hello_world")
        print(f"Activation: {result}")

        if result["success"]:
            # Execute plugin command
            print("\n🚀 Executing hello command...")
            result = ps.execute_plugin("hello_world", "hello")
            print(f"Execution result: {result}")

            # Get plugin info
            info = ps.get_plugin_info("hello_world")
            if info:
                print("\nℹ️ Plugin status:")
                print(f"   - Active: {info['status']['active']}")
                print(f"   - Execution count: {info['status']['execution_count']}")

    print("\n🎉 Plugin System Demo Complete!")
    print("=" * 50)
