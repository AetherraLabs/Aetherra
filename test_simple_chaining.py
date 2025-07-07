#!/usr/bin/env python3
"""
🧪 SIMPLE PLUGIN CHAINING TEST
==============================

Simple test to verify the basic plugin chaining functionality works.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lyrixa.core.plugin_chainer import ChainExecutionMode
    from lyrixa.core.plugins import LyrixaPlugin, LyrixaPluginManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class SimpleDataPlugin(LyrixaPlugin):
    """Simple test plugin that generates data"""

    def __init__(self):
        super().__init__()
        self.name = "SimpleDataPlugin"
        self.description = "Generates simple test data"
        self.category = "data"

        # Chaining metadata
        self.input_types = []
        self.output_types = ["data/json"]
        self.auto_chain = True
        self.chain_priority = 0.8

    async def initialize(self, lyrixa_context):
        return True

    async def execute(self, command, params=None):
        return {"data": [1, 2, 3, 4, 5], "generated_by": "SimpleDataPlugin"}

    async def cleanup(self):
        return True


class SimpleProcessorPlugin(LyrixaPlugin):
    """Simple test plugin that processes data"""

    def __init__(self):
        super().__init__()
        self.name = "SimpleProcessorPlugin"
        self.description = "Processes simple data"
        self.category = "processing"

        # Chaining metadata
        self.input_types = ["data/json"]
        self.output_types = ["data/processed"]
        self.auto_chain = True
        self.chain_priority = 0.6

    async def initialize(self, lyrixa_context):
        return True

    async def execute(self, command, params=None):
        params = params or {}
        input_data = params.get("data", [])
        return {
            "processed_data": [x * 2 for x in input_data],
            "processed_by": "SimpleProcessorPlugin",
        }

    async def cleanup(self):
        return True


async def test_simple_chaining():
    """Test simple plugin chaining"""
    print("🧪 Testing Simple Plugin Chaining...")

    # Create plugin manager
    manager = LyrixaPluginManager("test_plugins")

    # Register test plugins
    manager.plugin_registry.update(
        {
            "SimpleDataPlugin": SimpleDataPlugin,
            "SimpleProcessorPlugin": SimpleProcessorPlugin,
        }
    )

    # Initialize
    await manager.initialize({"test_mode": True})

    # Add plugin info
    for plugin_name, plugin_class in manager.plugin_registry.items():
        if plugin_name.startswith("Simple"):
            instance = plugin_class()
            info = instance.get_info()
            info.file_path = "test"
            info.enabled = True
            manager.plugin_info[plugin_name] = info

    # Load test plugins
    await manager._load_enabled_plugins()

    print(
        f"✅ Loaded {len([p for p in manager.loaded_plugins if p.startswith('Simple')])} test plugins"
    )

    # Test chaining methods
    data_plugin = manager.loaded_plugins["SimpleDataPlugin"]
    processor_plugin = manager.loaded_plugins["SimpleProcessorPlugin"]

    print(f"📊 Data plugin I/O: {data_plugin.get_io_spec()}")
    print(f"⚙️  Processor plugin I/O: {processor_plugin.get_io_spec()}")
    print(f"🔗 Can chain? {data_plugin.can_chain_with(processor_plugin)}")

    # Test direct chain building
    if manager.plugin_chainer:
        print("\n🏗️  Building chain...")
        chain = await manager.plugin_chainer.build_chain(
            goal="process simple data",
            available_plugins=["SimpleDataPlugin", "SimpleProcessorPlugin"],
            execution_mode=ChainExecutionMode.SEQUENTIAL,
        )

        if chain:
            print(f"✅ Chain built: {[node.plugin_name for node in chain.nodes]}")

            # Execute chain
            print("🚀 Executing chain...")
            result = await manager.plugin_chainer.run_chain(chain)
            print(f"✅ Chain result: {result}")

            await manager.cleanup()
            return True
        else:
            print("❌ Failed to build chain")

    await manager.cleanup()
    return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_simple_chaining())
        if success:
            print("🎉 Simple chaining test passed!")
        else:
            print("❌ Simple chaining test failed!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)
