#!/usr/bin/env python3
"""
Phase 4 Plugin System Demo
=========================

A simple demonstration of the new semantic discovery and state memory features.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lyrixa.core.plugins import LyrixaPlugin, LyrixaPluginManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class DemoAnalysisPlugin(LyrixaPlugin):
    """Demo plugin for code analysis"""

    def __init__(self):
        super().__init__()
        self.name = "CodeAnalysisPlugin"
        self.description = (
            "Analyzes code quality, finds bugs, and suggests improvements"
        )
        self.category = "development"
        self.capabilities = [
            "analyze_code",
            "find_bugs",
            "code_review",
            "quality_metrics",
        ]
        self.author = "Lyrixa Team"
        self.version = "2.1.0"

    async def initialize(self, lyrixa_context):
        print(f"[TOOL] {self.name} initialized")
        return True

    async def execute(self, command, params=None):
        if command == "analyze_code":
            return {"status": "success", "bugs_found": 3, "quality_score": 85}
        elif command == "find_bugs":
            return {"status": "success", "critical_bugs": 1, "warnings": 5}
        else:
            return {"error": "Unknown command"}

    async def cleanup(self):
        return True


class DemoDataPlugin(LyrixaPlugin):
    """Demo plugin for data processing"""

    def __init__(self):
        super().__init__()
        self.name = "DataProcessorPlugin"
        self.description = (
            "Processes and transforms data files, generates reports and visualizations"
        )
        self.category = "data"
        self.capabilities = [
            "process_data",
            "generate_reports",
            "data_visualization",
            "file_analysis",
        ]
        self.author = "Lyrixa Team"
        self.version = "1.5.0"

    async def initialize(self, lyrixa_context):
        print(f"[TOOL] {self.name} initialized")
        return True

    async def execute(self, command, params=None):
        if command == "process_data":
            return {"status": "success", "files_processed": 12, "output_format": "CSV"}
        elif command == "generate_reports":
            return {"status": "success", "report_type": "summary", "pages": 5}
        else:
            return {"error": "Unknown command"}

    async def cleanup(self):
        return True


async def demo_semantic_discovery():
    """Demonstrate semantic plugin discovery"""
    print("🔍 SEMANTIC PLUGIN DISCOVERY DEMO")
    print("=" * 50)

    # Create plugin manager
    plugin_manager = LyrixaPluginManager()

    # Register demo plugins
    plugin_manager.plugin_registry["CodeAnalysisPlugin"] = DemoAnalysisPlugin
    plugin_manager.plugin_registry["DataProcessorPlugin"] = DemoDataPlugin

    # Create plugin info
    plugin_manager.plugin_info["CodeAnalysisPlugin"] = DemoAnalysisPlugin().get_info()
    plugin_manager.plugin_info["DataProcessorPlugin"] = DemoDataPlugin().get_info()

    # Initialize
    await plugin_manager.initialize({"workspace_path": "."})

    print("\n📋 Available plugins:")
    for name, info in plugin_manager.plugin_info.items():
        print(f"  • {name}: {info.description}")

    # Test semantic discovery with various user goals
    test_goals = [
        "I want to analyze my Python code for bugs",
        "Help me process my data files",
        "Generate a report from my CSV data",
        "Find issues in my JavaScript code",
        "Visualize my sales data",
        "Review my code quality",
    ]

    print("\n🎯 Testing semantic discovery with user goals:")
    for goal in test_goals:
        print(f"\n   User: '{goal}'")
        suggestion = await plugin_manager.suggest_plugins_for_goal(goal)
        print(f"   Lyrixa: {suggestion}")

    return plugin_manager


async def demo_state_memory(plugin_manager):
    """Demonstrate plugin state memory"""
    print("\n💾 PLUGIN STATE MEMORY DEMO")
    print("=" * 50)

    # Execute some plugin commands
    print("\n🚀 Executing plugin commands...")

    result1 = await plugin_manager.execute_plugin(
        "CodeAnalysisPlugin", "analyze_code", {"file": "main.py", "strict_mode": True}
    )
    print(f"   📊 Code analysis result: {result1['result']}")

    result2 = await plugin_manager.execute_plugin(
        "DataProcessorPlugin",
        "process_data",
        {"files": ["data.csv", "users.json"], "format": "parquet"},
    )
    print(f"   📊 Data processing result: {result2['result']}")

    # Show plugin insights
    print("\n🧠 Plugin insights:")

    for plugin_name in ["CodeAnalysisPlugin", "DataProcessorPlugin"]:
        insights = plugin_manager.get_plugin_insights(plugin_name)
        print(f"\n   {plugin_name}:")
        print(f"     • Interactions: {insights['total_interactions']}")
        print(f"     • Success rate: {insights['success_rate']:.2%}")

        suggestions = plugin_manager.suggest_plugin_optimizations(plugin_name)
        if suggestions:
            print(f"     • Suggestions: {suggestions[0]}")


async def main():
    """Main demo function"""
    print("🚀 PHASE 4 PLUGIN SYSTEM DEMO")
    print("🎯 Semantic Discovery & State Memory")
    print("=" * 60)

    try:
        plugin_manager = await demo_semantic_discovery()
        await demo_state_memory(plugin_manager)

        print("\n✨ Demo completed successfully!")
        print("\n📈 Key Features Demonstrated:")
        print("  ✅ Natural language plugin discovery")
        print("  ✅ Intelligent plugin suggestions")
        print("  ✅ Persistent state memory")
        print("  ✅ Performance tracking")
        print("  ✅ Usage insights and optimization")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
