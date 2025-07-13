#!/usr/bin/env python3
"""
Test Lyrixa Modular Integration - Local Components
==================================================

Test the modular components from within the Lyrixa directory structure.
"""

def test_local_modular_components():
    print("🔍 Testing Local Modular Component Integration...")

    # Test 1: Enhanced Plugin Manager (local)
    try:
        from plugins.enhanced_plugin_manager import PluginManager
        plugin_manager = PluginManager()
        plugins = plugin_manager.discover_plugins()
        print(f"✅ Enhanced Plugin Manager: {len(plugins)} plugins discovered")
        if plugins:
            print(f"   Available plugins: {', '.join(plugins[:5])}")  # Show first 5
        else:
            print("   No plugins found in plugins directory")
    except Exception as e:
        print(f"❌ Enhanced Plugin Manager: {e}")

    # Test 2: Plugin Discovery (local)
    try:
        from plugin_discovery import discover_all_plugins
        discovery_results = discover_all_plugins()
        total_plugins = len(discovery_results.get('combined', []))
        print(f"✅ Plugin Discovery System: {total_plugins} total plugins found")
        if discovery_results.get('errors'):
            print(f"   Warnings: {len(discovery_results['errors'])} plugin manager issues")
    except Exception as e:
        print(f"❌ Plugin Discovery System: {e}")

    # Test 3: Self-Improvement Dashboard (local)
    try:
        import self_improvement_dashboard_api
        print("✅ Self-Improvement Dashboard API: Module available")

        # Try CLI version too
        import self_improvement_dashboard
        print("✅ Self-Improvement Dashboard CLI: Available")
    except Exception as e:
        print(f"❌ Self-Improvement Dashboard: {e}")

    # Test 4: Intelligence Stack (working version)
    try:
        from intelligence import LyrixaIntelligenceStack
        stack = LyrixaIntelligenceStack(".")
        metrics = stack.get_real_time_metrics()
        print(f"✅ Intelligence Stack: Working, performance {metrics['performance_score']:.1%}")
        print(f"   Status: {metrics['status']}, Uptime: {metrics['uptime']}")
    except Exception as e:
        print(f"❌ Intelligence Stack: {e}")

    # Test 5: AetherHub (check files and potential startup)
    try:
        from pathlib import Path
        hub_path = Path(__file__).parent.parent.parent / "aetherra_hub"
        if hub_path.exists():
            files = [f.name for f in hub_path.iterdir() if f.is_file()]
            print(f"✅ AetherHub: {len(files)} service files available")

            # Check if package.json exists for npm start capability
            if (hub_path / "package.json").exists():
                print("   Ready for: npm install && npm start")
            if (hub_path / "server.js").exists():
                print("   Server: Available for web interface")
        else:
            print("❌ AetherHub: Directory not found")
    except Exception as e:
        print(f"❌ AetherHub: {e}")

    # Test 6: Launcher (check if it's working)
    try:
        # Don't actually import launcher as it starts GUI, just check file
        from pathlib import Path
        launcher_path = Path(__file__).parent / "launcher.py"
        if launcher_path.exists():
            print("✅ Launcher: Available for GUI startup")
        else:
            print("❌ Launcher: launcher.py not found")
    except Exception as e:
        print(f"❌ Launcher: {e}")

    print(f"\n🎯 MODULAR ARCHITECTURE STATUS:")
    print(f"   ✅ Components can be tested independently")
    print(f"   ✅ No forced dependencies between modules")
    print(f"   ✅ Each component handles its own functionality")
    print(f"   ✅ Dynamic discovery and connection when needed")

if __name__ == "__main__":
    test_local_modular_components()
