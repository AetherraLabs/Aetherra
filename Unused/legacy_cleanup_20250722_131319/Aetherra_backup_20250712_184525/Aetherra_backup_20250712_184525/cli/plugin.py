#!/usr/bin/env python3
"""
🔌 AetherraCode Plugin CLI
Command-line interface for the AetherraCode Plugin Registry System.

This provides an easy-to-use command-line interface for managing AetherraCode plugins,
integrating with the enhanced plugin management system.

Usage:
    aetherra plugin <command> [options]

Commands:
    install <name>          Install a plugin from registry
    uninstall <name>        Uninstall a plugin
    list                    List installed plugins
    search [query]          Search plugin registry
    info <name>             Get plugin information
    update [name]           Update plugin(s)
    popular                 Show popular plugins
    categories              List plugin categories

License: GPL-3.0
"""

import sys
from pathlib import Path

# Add core directory to path for imports
core_dir = Path(__file__).parent.parent / "core"
sys.path.insert(0, str(core_dir))

try:
    from enhanced_plugin_manager import EnhancedPluginManager
except ImportError:
    print("❌ Error: Could not import AetherraCode plugin management system")
    print("   Make sure you're running this from the AetherraCode project directory")
    sys.exit(1)


def format_plugin_list(plugins, detailed=False):
    """Format plugin list for display"""
    if not plugins:
        return "No plugins found."

    output = []
    output.append(f"\n🔌 AetherraCode Plugins ({len(plugins)}):")
    output.append("=" * 70)

    for plugin in plugins:
        # Status icon
        if hasattr(plugin, "installed") and plugin.installed:
            status = "✅ Installed"
            if hasattr(plugin, "loaded") and plugin.loaded:
                status += " & Loaded"
        else:
            status = "[DISC] Available"

        # Rating stars
        rating_stars = ""
        if hasattr(plugin, "rating") and plugin.rating > 0:
            rating_stars = "⭐" * int(plugin.rating)

        # Basic info
        output.append(
            f"{status} {plugin.manifest.name} v{plugin.manifest.version} ({plugin.manifest.category})"
        )
        output.append(f"    {plugin.manifest.description}")

        if detailed:
            output.append(
                f"    Author: {plugin.manifest.author} | License: {plugin.manifest.license}"
            )

            if hasattr(plugin, "download_count") and plugin.download_count > 0:
                output.append(
                    f"    Downloads: {plugin.download_count:,} | Rating: {rating_stars}"
                )

            if plugin.manifest.keywords:
                output.append(f"    Keywords: {', '.join(plugin.manifest.keywords)}")

            if hasattr(plugin, "path") and plugin.path:
                output.append(f"    Path: {plugin.path}")

        output.append("")

    return "\n".join(output)


def format_plugin_info(plugin):
    """Format detailed plugin information"""
    output = []

    if hasattr(plugin, "installed") and plugin.installed:
        output.append(f"\n📋 Installed Plugin: {plugin.manifest.name}")
    else:
        output.append(f"\n📋 Registry Plugin: {plugin.manifest.name}")

    output.append("=" * 70)
    output.append(f"Version: {plugin.manifest.version}")
    output.append(f"Category: {plugin.manifest.category}")
    output.append(f"Author: {plugin.manifest.author}")
    output.append(f"License: {plugin.manifest.license}")
    output.append(f"Description: {plugin.manifest.description}")

    if hasattr(plugin, "rating") and plugin.rating > 0:
        rating_stars = "⭐" * int(plugin.rating)
        output.append(f"Rating: {rating_stars} ({plugin.rating:.1f})")

    if hasattr(plugin, "download_count") and plugin.download_count > 0:
        output.append(f"Downloads: {plugin.download_count:,}")

    if plugin.manifest.repository:
        output.append(f"Repository: {plugin.manifest.repository}")

    if plugin.manifest.documentation:
        output.append(f"Documentation: {plugin.manifest.documentation}")

    if plugin.manifest.homepage:
        output.append(f"Homepage: {plugin.manifest.homepage}")

    if plugin.manifest.keywords:
        output.append(f"Keywords: {', '.join(plugin.manifest.keywords)}")

    if plugin.manifest.dependencies:
        output.append(f"Dependencies: {', '.join(plugin.manifest.dependencies.keys())}")

    if plugin.manifest.security_permissions:
        output.append(f"Permissions: {', '.join(plugin.manifest.security_permissions)}")

    if hasattr(plugin, "installed"):
        if plugin.installed:
            output.append("Installed: ✅ Yes")
            if hasattr(plugin, "path") and plugin.path:
                output.append(f"Path: {plugin.path}")
            if hasattr(plugin, "loaded"):
                output.append(f"Loaded: {'✅ Yes' if plugin.loaded else '⚪ No'}")
        else:
            output.append("Installed: ❌ No")

    return "\n".join(output)


def cmd_install(args, manager):
    """Handle plugin installation"""
    if len(args) < 1:
        print("❌ Error: Plugin name required")
        print(
            "Usage: aetherra plugin install <name> [--version=VERSION] [--force] [--skip-security]"
        )
        return 1

    name = args[0]
    version = "latest"
    force = False
    skip_security = False

    # Parse options
    for arg in args[1:]:
        if arg.startswith("--version="):
            version = arg.split("=", 1)[1]
        elif arg == "--force":
            force = True
        elif arg == "--skip-security":
            skip_security = True
        else:
            print(f"❌ Unknown option: {arg}")
            return 1

    print(f"🔄 Installing plugin: {name} ({version})")
    success = manager.install_plugin(
        name, version, force=force, skip_security=skip_security
    )

    if success:
        print(f"✅ Successfully installed {name}")
        return 0
    else:
        print(f"❌ Failed to install {name}")
        return 1


def cmd_uninstall(args, manager):
    """Handle plugin uninstallation"""
    if len(args) < 1:
        print("❌ Error: Plugin name required")
        print("Usage: aetherra plugin uninstall <name>")
        return 1

    name = args[0]
    print(f"🗑️ Uninstalling plugin: {name}")
    success = manager.uninstall_plugin(name)

    if success:
        print(f"✅ Successfully uninstalled {name}")
        return 0
    else:
        print(f"❌ Failed to uninstall {name}")
        return 1


def cmd_list(args, manager):
    """Handle plugin listing"""
    detailed = "--detailed" in args or "-d" in args

    plugins = manager.list_installed_plugins()
    print(format_plugin_list(plugins, detailed=detailed))

    if not plugins:
        print("\n💡 Tip: Use 'aetherra plugin search' to discover plugins")

    return 0


def cmd_search(args, manager):
    """Handle plugin search"""
    query = ""
    category = ""
    tags = None

    # Parse arguments
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--category="):
            category = arg.split("=", 1)[1]
        elif arg.startswith("--tags="):
            tags = arg.split("=", 1)[1].split(",")
        elif not arg.startswith("--"):
            query = " ".join(args[i:])  # Remaining args are query
            break
        i += 1

    try:
        plugins = manager.search_registry(query, category, tags)
        print(format_plugin_list(plugins))

        if not plugins:
            print("💡 Try different search terms or browse categories")
        else:
            print("\n💡 Use 'aetherra plugin install <name>' to install a plugin")

        return 0

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return 1


def cmd_info(args, manager):
    """Handle plugin info"""
    if len(args) < 1:
        print("❌ Error: Plugin name required")
        print("Usage: aetherra plugin info <name>")
        return 1

    name = args[0]

    try:
        # Check if installed locally first
        installed_plugins = {
            p.manifest.name: p for p in manager.list_installed_plugins()
        }

        if name in installed_plugins:
            plugin = installed_plugins[name]
        else:
            plugin = manager.registry.get_plugin_info(name)

        print(format_plugin_info(plugin))
        return 0

    except Exception as e:
        print(f"❌ Failed to get plugin info: {e}")
        return 1


def cmd_update(args, manager):
    """Handle plugin updates"""
    if len(args) == 0:
        # Update all plugins
        plugins = manager.list_installed_plugins()
        if not plugins:
            print("No plugins installed to update")
            return 0

        updated = 0
        failed = 0

        for plugin in plugins:
            print(f"🔄 Checking {plugin.manifest.name}...")
            try:
                if manager.update_plugin(plugin.manifest.name):
                    updated += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Failed to update {plugin.manifest.name}: {e}")
                failed += 1

        print("\n📊 Update Summary:")
        print(f"✅ Updated: {updated} plugins")
        if failed > 0:
            print(f"❌ Failed: {failed} plugins")

        return 0 if failed == 0 else 1

    else:
        # Update specific plugin
        name = args[0]
        print(f"🔄 Updating plugin: {name}")
        success = manager.update_plugin(name)

        if success:
            print(f"✅ Successfully updated {name}")
            return 0
        else:
            print(f"❌ Failed to update {name}")
            return 1


def cmd_popular(args, manager):
    """Handle popular plugins"""
    limit = 20

    # Parse limit
    for arg in args:
        if arg.startswith("--limit="):
            try:
                limit = int(arg.split("=", 1)[1])
            except ValueError:
                print("❌ Invalid limit value")
                return 1

    try:
        plugins = manager.get_popular_plugins(limit)

        if plugins:
            print(f"\n🌟 Most Popular AetherraCode Plugins (Top {len(plugins)}):")
            print("=" * 70)

            for i, plugin in enumerate(plugins, 1):
                rating_stars = "⭐" * int(plugin.rating) if plugin.rating > 0 else ""
                print(f"{i:2d}. {plugin.manifest.name} v{plugin.manifest.version}")
                print(f"     {plugin.manifest.description}")
                print(
                    f"     Downloads: {plugin.download_count:,} | Rating: {rating_stars}"
                )
                print()
        else:
            print("No popular plugins found")

        return 0

    except Exception as e:
        print(f"❌ Failed to get popular plugins: {e}")
        return 1


def cmd_categories(args, manager):
    """Handle categories listing"""
    try:
        categories = manager.registry.get_categories()

        print("\n📂 Available Plugin Categories:")
        print("=" * 40)

        for category in sorted(categories):
            print(f"📁 {category}")

        print(
            "\n💡 Use 'aetherra plugin search --category=<name>' to browse a category"
        )
        return 0

    except Exception as e:
        print(f"❌ Failed to get categories: {e}")
        return 1


def show_help():
    """Show help information"""
    help_text = """
🔌 AetherraCode Plugin Manager

Usage:
    aetherra plugin <command> [options]

Commands:
    install <name>              Install a plugin from registry
        --version=VERSION       Specify plugin version (default: latest)
        --force                 Force reinstallation
        --skip-security         Skip security validation (not recommended)

    uninstall <name>            Uninstall a plugin

    list                        List installed plugins
        --detailed, -d          Show detailed information

    search [query]              Search plugin registry
        --category=NAME         Filter by category
        --tags=TAG1,TAG2        Filter by tags

    info <name>                 Get detailed plugin information

    update [name]               Update plugin(s) to latest version
                                (updates all if no name specified)

    popular                     Show popular plugins
        --limit=N               Number of plugins to show (default: 20)

    categories                  List available plugin categories

    help                        Show this help message

Examples:
    aetherra plugin search memory
    aetherra plugin install advanced-memory-system
    aetherra plugin info advanced-memory-system
    aetherra plugin list --detailed
    aetherra plugin update

Plugin Registry: https://registry.aethercode.org
Documentation: https://docs.aethercode.org/plugins
"""
    print(help_text)


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "help" or command == "--help" or command == "-h":
        show_help()
        return 0

    # Initialize plugin manager
    try:
        manager = EnhancedPluginManager()
    except Exception as e:
        print(f"❌ Failed to initialize plugin manager: {e}")
        return 1

    # Route to command handlers
    commands = {
        "install": cmd_install,
        "uninstall": cmd_uninstall,
        "remove": cmd_uninstall,  # Alias
        "list": cmd_list,
        "ls": cmd_list,  # Alias
        "search": cmd_search,
        "find": cmd_search,  # Alias
        "info": cmd_info,
        "show": cmd_info,  # Alias
        "update": cmd_update,
        "upgrade": cmd_update,  # Alias
        "popular": cmd_popular,
        "categories": cmd_categories,
        "cats": cmd_categories,  # Alias
    }

    if command not in commands:
        print(f"❌ Unknown command: {command}")
        print("Use 'aetherra plugin help' for available commands")
        return 1

    try:
        return commands[command](args, manager)
    except KeyboardInterrupt:
        print("\n[WARN] Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
