#!/usr/bin/env python3
"""
Simple Phase 4 Plugin System Test
=================================
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lyrixa.core.plugins import LyrixaPlugin, LyrixaPluginManager
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class TestPlugin(LyrixaPlugin):
    def __init__(self):
        super().__init__()
        self.name = "TestPlugin"
        self.description = "Test plugin for data analysis"
        self.capabilities = ["analyze", "process"]

    async def initialize(self, lyrixa_context):
        return True

    async def execute(self, command, params=None):
        return {"success": True, "command": command}

    async def cleanup(self):
        return True


async def main():
    print("Phase 4 Plugin System Test")
    print("=" * 30)

    # Create manager
    manager = LyrixaPluginManager()
    manager.plugin_registry["TestPlugin"] = TestPlugin
    manager.plugin_info["TestPlugin"] = TestPlugin().get_info()

    # Initialize
    await manager.initialize({"workspace": "."})
    print("Plugin manager initialized")

    # Test semantic discovery
    result = await manager.suggest_plugins_for_goal("analyze my data")
    print(f"Plugin suggestion: {result}")

    # Test execution
    exec_result = await manager.execute_plugin("TestPlugin", "analyze")
    print(f"Execution result: {exec_result['success']}")

    # Test state memory
    manager.set_plugin_state("TestPlugin", "test_key", "test_value")
    value = manager.get_plugin_state("TestPlugin", "test_key")
    print(f"State memory test: {value}")

    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
