#!/usr/bin/env python3
"""
🧪 DIRECT PLUGIN CHAINING TEST
==============================

Direct test of plugin chaining without semantic discovery dependency.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from lyrixa.core.plugin_chainer import ChainExecutionMode, ChainNode, PluginChainer
    from lyrixa.core.plugins import LyrixaPlugin, LyrixaPluginManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class SimpleDataPlugin(LyrixaPlugin):
    def __init__(self):
        super().__init__()
        self.name = "SimpleDataPlugin"
        self.description = "Generates simple test data"
        self.category = "data"
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
    def __init__(self):
        super().__init__()
        self.name = "SimpleProcessorPlugin"
        self.description = "Processes simple data"
        self.category = "processing"
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


async def test_direct_chaining():
    """Test plugin chaining directly without semantic discovery"""
    print("🧪 Testing Direct Plugin Chaining...")

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
    print(f"✅ Loaded plugins: {list(manager.loaded_plugins.keys())}")

    # Test chaining capabilities
    data_plugin = manager.loaded_plugins["SimpleDataPlugin"]
    processor_plugin = manager.loaded_plugins["SimpleProcessorPlugin"]

    print(
        f"📊 Data plugin can chain with processor: {data_plugin.can_chain_with(processor_plugin)}"
    )

    # Create a simple chain manually
    chainer = PluginChainer(manager)

    # Build nodes manually for testing
    nodes = []

    # Data plugin node
    data_node = ChainNode(
        plugin_name="SimpleDataPlugin",
        plugin_instance=data_plugin,
        inputs={},
        outputs={},
        dependencies=[],
    )
    nodes.append(data_node)

    # Processor plugin node
    processor_node = ChainNode(
        plugin_name="SimpleProcessorPlugin",
        plugin_instance=processor_plugin,
        inputs={},
        outputs={},
        dependencies=["SimpleDataPlugin"],
    )
    nodes.append(processor_node)

    # Create chain
    from lyrixa.core.plugin_chainer import PluginChain

    chain = PluginChain(
        chain_id="test_chain_1",
        nodes=nodes,
        execution_mode=ChainExecutionMode.SEQUENTIAL,
        metadata={"goal": "test direct chaining"},
        created_at="2025-07-06",
    )

    print(f"🏗️  Built chain with {len(chain.nodes)} nodes")

    # Execute the chain
    print("🚀 Executing chain...")
    result = await chainer.run_chain(chain)

    print(f"✅ Chain execution result: {result}")

    # Verify the result contains what we expect
    if "processed_data" in result and result["processed_data"] == [2, 4, 6, 8, 10]:
        print("🎉 Chain output is correct!")
        await manager.cleanup()
        return True
    else:
        print("❌ Chain output is incorrect!")
        await manager.cleanup()
        return False


async def test_chainer_building():
    """Test the automatic chain building functionality"""
    print("\n🧪 Testing Automatic Chain Building...")

    manager = LyrixaPluginManager("test_plugins")
    manager.plugin_registry.update(
        {
            "SimpleDataPlugin": SimpleDataPlugin,
            "SimpleProcessorPlugin": SimpleProcessorPlugin,
        }
    )

    await manager.initialize({"test_mode": True})

    # Add plugin info
    for plugin_name, plugin_class in manager.plugin_registry.items():
        if plugin_name.startswith("Simple"):
            instance = plugin_class()
            info = instance.get_info()
            info.file_path = "test"
            info.enabled = True
            manager.plugin_info[plugin_name] = info

    await manager._load_enabled_plugins()

    # Test the high-level API
    chain_info = await manager.build_plugin_chain(
        goal="process data",
        available_plugins=["SimpleDataPlugin", "SimpleProcessorPlugin"],
    )

    if chain_info:
        print(f"✅ Auto-built chain: {chain_info['plugins']}")

        result = await manager.execute_plugin_chain(chain_info["chain_id"])

        if result.get("success"):
            print("✅ Auto-chain execution successful!")
            print(f"   Result: {result['result']}")
            await manager.cleanup()
            return True
        else:
            print(f"❌ Auto-chain execution failed: {result}")
    else:
        print("❌ Failed to auto-build chain")

    await manager.cleanup()
    return False


async def run_tests():
    """Run all direct chaining tests"""
    print("🚀 DIRECT PLUGIN CHAINING TEST SUITE")
    print("=" * 50)

    tests = [
        ("Direct Chain Execution", test_direct_chaining),
        ("Automatic Chain Building", test_chainer_building),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            print(f"\n📋 Running: {test_name}")
            result = await test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results[test_name] = f"❌ ERROR: {e}"

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    for test_name, result in results.items():
        print(f"   {test_name}: {result}")

    passed = sum(1 for r in results.values() if "✅" in r)
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test suite error: {e}")
        sys.exit(1)
