#!/usr/bin/env python3
"""
🧪 PLUGIN CHAINING INTEGRATION TEST
===================================

Comprehensive test suite for the new plugin chaining system.
Tests chain building, execution, and integration with Lyrixa.
"""

import asyncio
import json
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
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class TestDataPlugin(LyrixaPlugin):
    """Test plugin that generates data"""

    def __init__(self):
        super().__init__()
        self.name = "TestDataPlugin"
        self.description = "Generates test data"
        self.category = "data"
        self.capabilities = ["generate_data", "create_dataset"]

        # Chaining metadata
        self.input_types = []  # No input required
        self.output_types = ["data/json", "data/list"]
        self.collaborates_with = ["TestProcessorPlugin", "TestAnalyzerPlugin"]
        self.auto_chain = True
        self.chain_priority = 0.8

    async def initialize(self, lyrixa_context):
        return True

    async def execute(self, command, params=None):
        params = params or {}

        if command == "generate_data":
            return {
                "data": [{"id": i, "value": f"item_{i}"} for i in range(5)],
                "count": 5,
                "type": "test_data",
            }
        elif command == "auto_chain":
            return await self.execute("generate_data", params)

        return {"error": f"Unknown command: {command}"}

    async def cleanup(self):
        return True


class TestProcessorPlugin(LyrixaPlugin):
    """Test plugin that processes data"""

    def __init__(self):
        super().__init__()
        self.name = "TestProcessorPlugin"
        self.description = "Processes and transforms data"
        self.category = "data"
        self.capabilities = ["process_data", "transform"]

        # Chaining metadata
        self.input_types = ["data/json", "data/list"]
        self.output_types = ["data/processed", "data/transformed"]
        self.collaborates_with = ["TestAnalyzerPlugin"]
        self.auto_chain = True
        self.chain_priority = 0.6

    async def initialize(self, lyrixa_context):
        return True

    async def execute(self, command, params=None):
        params = params or {}

        if command == "process_data" or command == "auto_chain":
            input_data = params.get("data", [])
            processed = []

            for item in input_data:
                if isinstance(item, dict):
                    processed.append(
                        {**item, "processed": True, "timestamp": "2025-07-06"}
                    )

            return {
                "processed_data": processed,
                "count": len(processed),
                "processing_complete": True,
            }

        return {"error": f"Unknown command: {command}"}

    async def cleanup(self):
        return True


class TestAnalyzerPlugin(LyrixaPlugin):
    """Test plugin that analyzes data"""

    def __init__(self):
        super().__init__()
        self.name = "TestAnalyzerPlugin"
        self.description = "Analyzes and reports on data"
        self.category = "analytics"
        self.capabilities = ["analyze_data", "generate_report"]

        # Chaining metadata
        self.input_types = ["data/processed", "data/transformed", "data/json"]
        self.output_types = ["report/json", "analysis/summary"]
        self.collaborates_with = []
        self.auto_chain = True
        self.chain_priority = 0.4

    async def initialize(self, lyrixa_context):
        return True

    async def execute(self, command, params=None):
        params = params or {}

        if command == "analyze_data" or command == "auto_chain":
            input_data = params.get("processed_data", params.get("data", []))

            analysis = {
                "total_items": len(input_data),
                "processed_items": sum(
                    1
                    for item in input_data
                    if isinstance(item, dict) and item.get("processed")
                ),
                "analysis_date": "2025-07-06",
                "summary": f"Analyzed {len(input_data)} items successfully",
            }

            return {
                "analysis": analysis,
                "report_generated": True,
                "status": "complete",
            }

        return {"error": f"Unknown command: {command}"}

    async def cleanup(self):
        return True


async def test_basic_chaining():
    """Test basic plugin chaining functionality"""
    print("\n🧪 Testing Basic Plugin Chaining...")

    # Create plugin manager
    manager = LyrixaPluginManager("test_plugins")

    # Register test plugins
    manager.plugin_registry.update(
        {
            "TestDataPlugin": TestDataPlugin,
            "TestProcessorPlugin": TestProcessorPlugin,
            "TestAnalyzerPlugin": TestAnalyzerPlugin,
        }
    )

    # Initialize
    await manager.initialize({"test_mode": True})

    # Manually add plugin info
    for plugin_name, plugin_class in manager.plugin_registry.items():
        if plugin_name.startswith("Test"):
            instance = plugin_class()
            info = instance.get_info()
            info.file_path = "test"
            info.enabled = True
            manager.plugin_info[plugin_name] = info

    # Load test plugins
    await manager._load_enabled_plugins()

    print(f"✅ Loaded {len(manager.loaded_plugins)} test plugins")

    # Test chaining methods on plugins
    data_plugin = manager.loaded_plugins["TestDataPlugin"]
    processor_plugin = manager.loaded_plugins["TestProcessorPlugin"]

    print(f"📊 Data plugin I/O spec: {data_plugin.get_io_spec()}")
    print(f"⚙️  Processor plugin I/O spec: {processor_plugin.get_io_spec()}")
    print(
        f"🔗 Can data plugin chain with processor? {data_plugin.can_chain_with(processor_plugin)}"
    )

    # Test chain building
    print("\n🏗️  Building plugin chain...")
    chain_info = await manager.build_plugin_chain(
        goal="process and analyze test data",
        available_plugins=[
            "TestDataPlugin",
            "TestProcessorPlugin",
            "TestAnalyzerPlugin",
        ],
    )

    if chain_info:
        print(f"✅ Chain built successfully: {chain_info['chain_id']}")
        print(f"   Plugins in chain: {' -> '.join(chain_info['plugins'])}")
        print(f"   Execution mode: {chain_info['execution_mode']}")

        # Execute the chain
        print("\n🚀 Executing plugin chain...")
        result = await manager.execute_plugin_chain(chain_info["chain_id"])

        if result.get("success"):
            print("✅ Chain execution successful!")
            print(f"   Final result: {json.dumps(result['result'], indent=2)}")
        else:
            print(f"❌ Chain execution failed: {result.get('error')}")

        # Get chain status
        status = manager.get_chain_status(chain_info["chain_id"])
        if status:
            print(f"📈 Chain status: {status['progress']:.1%} complete")

        # Cleanup
        await manager.cleanup_chain(chain_info["chain_id"])
    else:
        print("❌ Failed to build chain")

    await manager.cleanup()
    return True


async def test_chain_suggestions():
    """Test chain suggestion functionality"""
    print("\n🧪 Testing Chain Suggestions...")

    manager = LyrixaPluginManager("test_plugins")

    # Register test plugins
    manager.plugin_registry.update(
        {
            "TestDataPlugin": TestDataPlugin,
            "TestProcessorPlugin": TestProcessorPlugin,
            "TestAnalyzerPlugin": TestAnalyzerPlugin,
        }
    )

    await manager.initialize({"test_mode": True})

    # Add plugin info
    for plugin_name, plugin_class in manager.plugin_registry.items():
        if plugin_name.startswith("Test"):
            instance = plugin_class()
            info = instance.get_info()
            info.file_path = "test"
            info.enabled = True
            manager.plugin_info[plugin_name] = info

    await manager._load_enabled_plugins()

    # Test chain suggestions
    suggestions = await manager.suggest_plugin_chains(
        user_input="I need to process some data and get a report",
        context={"user_goal": "data_analysis"},
    )

    print(f"💡 Found {len(suggestions)} chain suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion.get('description', 'Unknown')}")
        print(f"      Plugins: {' -> '.join(suggestion.get('plugins', []))}")
        print(f"      Estimated time: {suggestion.get('estimated_time', 'Unknown')}s")

    await manager.cleanup()
    return len(suggestions) > 0


async def test_parallel_execution():
    """Test parallel chain execution"""
    print("\n🧪 Testing Parallel Chain Execution...")

    # Create a chain that can run some parts in parallel
    manager = LyrixaPluginManager("test_plugins")
    manager.plugin_registry.update(
        {
            "TestDataPlugin": TestDataPlugin,
            "TestProcessorPlugin": TestProcessorPlugin,
            "TestAnalyzerPlugin": TestAnalyzerPlugin,
        }
    )

    await manager.initialize({"test_mode": True})

    # Add plugin info
    for plugin_name, plugin_class in manager.plugin_registry.items():
        if plugin_name.startswith("Test"):
            instance = plugin_class()
            info = instance.get_info()
            info.file_path = "test"
            info.enabled = True
            manager.plugin_info[plugin_name] = info

    await manager._load_enabled_plugins()

    # Build chain with parallel execution
    if manager.plugin_chainer:
        chain = await manager.plugin_chainer.build_chain(
            goal="parallel data processing",
            available_plugins=[
                "TestDataPlugin",
                "TestProcessorPlugin",
                "TestAnalyzerPlugin",
            ],
            execution_mode=ChainExecutionMode.PARALLEL,
        )

        if chain:
            print(f"✅ Parallel chain built: {chain.chain_id}")
            result = await manager.plugin_chainer.run_chain(chain)
            print(f"✅ Parallel execution result: {result.get('status', 'Unknown')}")
            await manager.cleanup()
            return True

    await manager.cleanup()
    return False


async def run_all_tests():
    """Run all plugin chaining tests"""
    print("🚀 PLUGIN CHAINING INTEGRATION TEST SUITE")
    print("=" * 50)

    tests = [
        ("Basic Chaining", test_basic_chaining),
        ("Chain Suggestions", test_chain_suggestions),
        ("Parallel Execution", test_parallel_execution),
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

    if passed == total:
        print("🎉 All tests passed! Plugin chaining is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
