#!/usr/bin/env python3
"""
Test modular integration - check what's currently working
"""

def test_modular_components():
    print("🔍 Testing Modular Component Integration...")

    # Test 1: Plugin Manager
    try:
        from Aetherra.lyrixa.plugins.enhanced_plugin_manager import PluginManager
        plugin_manager = PluginManager()
        plugins = plugin_manager.discover_plugins()
        print(f"✅ Plugin Manager: {len(plugins)} plugins discovered")
        for plugin in plugins[:3]:  # Show first 3
            print(f"   - {plugin}")
    except Exception as e:
        print(f"❌ Plugin Manager: {e}")

    # Test 2: Self-Improvement Dashboard API
    try:
        import Aetherra.lyrixa.self_improvement_dashboard_api as dashboard_api
        print("✅ Self-Improvement Dashboard API: Available")
    except Exception as e:
        print(f"❌ Self-Improvement Dashboard API: {e}")

    # Test 3: AetherHub
    try:
        from pathlib import Path
        hub_path = Path(__file__).parent.parent.parent / "aetherra_hub"
        if hub_path.exists():
            files = [f.name for f in hub_path.iterdir() if f.is_file()]
            print(f"✅ AetherHub: Found {len(files)} hub files")
        else:
            print("❌ AetherHub: Directory not found")
    except Exception as e:
        print(f"❌ AetherHub: {e}")

    # Test 4: Core Launcher Components
    try:
        from Aetherra.core.multi_llm_manager import MultiLLMManager
        from Aetherra.core.memory_manager import MemoryManager
        from Aetherra.core.plugin_manager import PluginManager as CorePluginManager
        print("✅ Core Components: MultiLLM, Memory, Core Plugin Manager available")
    except Exception as e:
        print(f"❌ Core Components: {e}")

    # Test 5: Intelligence Stack (current working version)
    try:
        from Aetherra.lyrixa.intelligence import LyrixaIntelligenceStack
        stack = LyrixaIntelligenceStack(".")
        metrics = stack.get_real_time_metrics()
        print(f"✅ Intelligence Stack: Working, performance {metrics['performance_score']:.1%}")
    except Exception as e:
        print(f"❌ Intelligence Stack: {e}")

if __name__ == "__main__":
    test_modular_components()
