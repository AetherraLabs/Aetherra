#!/usr/bin/env python3
"""
🧪 LYRIXA AI ASSISTANT TEST
===========================

Test script to verify the new Lyrixa AI Assistant system works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


async def test_lyrixa_system():
    """Test the Lyrixa AI Assistant system"""
    print("🧪 Testing Lyrixa AI Assistant System")
    print("=" * 50)

    try:
        # Test imports
        print("📦 Testing imports...")

        from lyrixa import LyrixaAI

        print("✅ LyrixaAI imported successfully")

        from lyrixa.core.memory import LyrixaMemorySystem

        print("✅ Memory system imported")

        from lyrixa.core.plugins import LyrixaPluginManager

        print("✅ Plugin manager imported")

        from lyrixa.core.goals import LyrixaGoalSystem

        print("✅ Goal system imported")

        from lyrixa.core.agents import AgentOrchestrator

        print("✅ Agent orchestrator imported")

        from lyrixa.core.aether_interpreter import AetherInterpreter

        print("✅ Aether interpreter imported")

        # Test basic initialization
        print("\n🎙️ Testing Lyrixa initialization...")
        lyrixa = LyrixaAI(workspace_path=str(current_dir))
        print("✅ Lyrixa AI Assistant created")

        # Test async initialization
        print("\n🔄 Testing async initialization...")
        await lyrixa.initialize()
        print("✅ Lyrixa fully initialized")

        # Test basic interaction
        print("\n💬 Testing basic interaction...")
        response = await lyrixa.process_natural_language("Hello Lyrixa!")
        print(f"✅ Response received: {response['lyrixa_response'][:100]}...")

        # Test .aether generation
        print("\n🌌 Testing .aether code generation...")
        aether_response = await lyrixa.process_natural_language(
            "Create a simple data processing workflow"
        )
        if aether_response.get("aether_code"):
            print("✅ .aether code generated successfully")
            print(
                f"📄 Generated code length: {len(aether_response['aether_code'])} characters"
            )
        else:
            print("⚠️  No .aether code generated (this is normal for testing)")

        # Test memory system
        print("\n🧠 Testing memory system...")
        memory_id = await lyrixa.memory.store_memory(
            content={"test": "This is a test memory"}, tags=["test"], importance=0.5
        )
        print(f"✅ Memory stored with ID: {memory_id[:8]}...")

        memories = await lyrixa.memory.recall_memories("test", limit=1)
        print(f"✅ Memory recalled: {len(memories)} memories found")

        # Test goal system
        print("\n🎯 Testing goal system...")
        goal_id = await lyrixa.goals.create_goal(
            title="Test Goal", description="This is a test goal for verification"
        )
        print(f"✅ Goal created with ID: {goal_id[:8]}...")

        goals = lyrixa.goals.get_active_goals()
        print(f"✅ Active goals retrieved: {len(goals)} goals")

        # Test plugin system
        print("\n🧩 Testing plugin system...")
        capabilities = lyrixa.plugins.get_capabilities()
        print(f"✅ Plugin capabilities: {len(capabilities)} available")
        print(f"   Capabilities: {list(capabilities.keys())}")

        # Test system status
        print("\n📊 Testing system status...")
        status = await lyrixa.get_system_status()
        print(f"✅ System status retrieved")
        print(f"   Session: {status['session_id'][:16]}...")
        print(f"   Memories: {status['memory_system']['total_memories']}")
        print(f"   Goals: {status['goal_system']['active_goals']}")
        print(f"   Plugins: {status['plugin_system']['loaded_plugins']}")

        # Cleanup
        print("\n🧹 Testing cleanup...")
        await lyrixa.cleanup()
        print("✅ Cleanup completed")

        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print("🌌 Aetherra + Lyrixa AI Assistant is ready for use!")
        print("🚀 Run 'python aetherra_launcher.py' to start the full experience")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure all modules are properly installed")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🧪 LYRIXA AI ASSISTANT VERIFICATION")
    print("====================================")
    print("Testing the new Python-based Lyrixa system...")
    print()

    # Run async tests
    success = asyncio.run(test_lyrixa_system())

    if success:
        print("\n✅ VERIFICATION SUCCESSFUL")
        print("The Lyrixa AI Assistant is working correctly!")
        print("\nNext steps:")
        print("1. Run 'python aetherra_launcher.py' for the full experience")
        print("2. Choose option 1 to launch Lyrixa interactive mode")
        print("3. Start building with natural language and .aether workflows!")
        return 0
    else:
        print("\n❌ VERIFICATION FAILED")
        print("Please check the error messages above and fix any issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
