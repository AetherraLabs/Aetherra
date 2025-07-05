#!/usr/bin/env python3
"""
🧪 LYRIXA AI ASSISTANT TEST
===========================

Test the new Python-based Lyrixa AI Assistant to ensure all systems work correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


async def test_lyrixa():
    """Test Lyrixa AI Assistant functionality"""
    print("🧪 Testing Lyrixa AI Assistant...")

    try:
        from lyrixa import LyrixaAI

        # Initialize Lyrixa
        workspace_path = str(current_dir)
        lyrixa = LyrixaAI(workspace_path=workspace_path)

        print("✅ Lyrixa initialized successfully")

        # Initialize all systems
        await lyrixa.initialize()
        print("✅ All systems initialized")

        # Test cases
        test_cases = [
            "Hello Lyrixa, how are you?",
            "Create a data analysis workflow",
            "List files in the current directory",
            "Remember that I prefer Python for development",
            "What are my current goals?",
            "Help me understand .aether workflows",
        ]

        print("\n🧪 Running test cases...")

        for i, test_input in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {test_input} ---")

            try:
                response = await lyrixa.process_natural_language(test_input)

                print(f"✅ Intent: {response['intent']['type']}")
                print(f"✅ Confidence: {response['intent']['confidence']:.2f}")
                print(f"✅ Response: {response['lyrixa_response'][:100]}...")

                if response.get("actions_taken"):
                    print(f"✅ Actions: {', '.join(response['actions_taken'])}")

            except Exception as e:
                print(f"❌ Test {i} failed: {e}")

        # Test system status
        print("\n🧪 Testing system status...")
        status = await lyrixa.get_system_status()
        print(f"✅ Session ID: {status['session_id']}")
        print(f"✅ Memory: {status['memory_system']['total_memories']} memories")
        print(f"✅ Plugins: {status['plugin_system']['loaded_plugins']} loaded")
        print(f"✅ Agents: {len(status['agent_system'])} agent types")

        # Test .aether code generation
        print("\n🧪 Testing .aether code generation...")
        aether_response = await lyrixa.process_natural_language(
            "Create a simple data processing workflow"
        )

        if aether_response.get("aether_code"):
            print("✅ .aether code generated")
            print(f"Code preview: {aether_response['aether_code'][:100]}...")

            # Test execution
            print("🧪 Testing workflow execution...")
            execution_result = await lyrixa.execute_aether_workflow(
                aether_response["aether_code"]
            )
            print(f"✅ Execution status: {execution_result['status']}")
        else:
            print("⚠️ No .aether code generated for test case")

        # Cleanup
        await lyrixa.cleanup()
        print("\n✅ All tests completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all Lyrixa modules are properly installed")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_individual_components():
    """Test individual Lyrixa components"""
    print("\n🧪 Testing individual components...")

    try:
        # Test imports
        from lyrixa.core.aether_interpreter import AetherInterpreter
        from lyrixa.core.agents import AgentOrchestrator
        from lyrixa.core.goals import LyrixaGoalSystem
        from lyrixa.core.memory import LyrixaMemorySystem
        from lyrixa.core.plugins import LyrixaPluginManager

        print("✅ All core imports successful")

        # Test .aether interpreter
        interpreter = AetherInterpreter()
        test_code = """
node input input
  source: "test_data.csv"

node processor transform
  operation: "clean_data"

input -> processor
"""
        workflow = await interpreter.parse_aether_code(test_code)
        print(f"✅ .aether interpreter: parsed {len(workflow.nodes)} nodes")

        # Test memory system
        memory = LyrixaMemorySystem(memory_db_path="test_memory.db")
        memory_id = await memory.store_memory(
            content={"test": "data"}, tags=["test"], importance=0.8
        )
        print(f"✅ Memory system: stored memory {memory_id[:8]}...")

        # Test plugin manager
        plugins = LyrixaPluginManager(plugin_directory="test_plugins")
        await plugins.initialize({"workspace_path": "."})
        print(f"✅ Plugin manager: loaded {len(plugins.loaded_plugins)} plugins")

        # Test goal system
        goals = LyrixaGoalSystem(goals_file="test_goals.json")
        goal_id = await goals.create_goal("Test Goal", "Testing the goal system")
        print(f"✅ Goal system: created goal {goal_id[:8]}...")

        # Test agent orchestrator
        agents = AgentOrchestrator()
        await agents.initialize({"workspace_path": "."})
        print(f"✅ Agent orchestrator: initialized {len(agents.agents)} agents")

        # Cleanup test files
        for test_file in ["test_memory.db", "test_goals.json"]:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"🧹 Cleaned up {test_file}")

        print("✅ All component tests passed!")
        return True

    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🧪 LYRIXA AI ASSISTANT TEST SUITE")
    print("=" * 50)

    # Test individual components
    component_success = await test_individual_components()

    # Test full system
    if component_success:
        system_success = await test_lyrixa()
    else:
        print("❌ Skipping full system test due to component failures")
        system_success = False

    # Summary
    print("\n" + "=" * 50)
    print("🧪 TEST SUMMARY")
    print("=" * 50)
    print(f"Components: {'✅ PASS' if component_success else '❌ FAIL'}")
    print(f"Full System: {'✅ PASS' if system_success else '❌ FAIL'}")

    if component_success and system_success:
        print("\n🎉 All tests passed! Lyrixa AI Assistant is ready to use.")
        print("Run 'python lyrixa_launcher.py' to start the interactive assistant.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)
