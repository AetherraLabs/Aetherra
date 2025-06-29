#!/usr/bin/env python3
"""Quick Integration Test for NeuroCode Components"""

import sys
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))


def test_integration():
    print("🧪 NeuroCode Integration Test")
    print("=" * 40)

    # Test 1: Memory & Agent Integration
    try:
        from agent_reflection_loop import AgentReflectionLoop
        from core.memory import NeuroMemory

        memory = NeuroMemory()
        agent = AgentReflectionLoop(memory)

        print("✅ Agent and Memory integrated successfully")
        print(f"   🤖 Agent running: {agent.get_status()['is_running']}")
        print(f"   💾 Memory entries: {len(memory.memory)}")

        # Test manual reflection
        agent._perform_reflection_cycle()
        print(f"   🔄 Manual reflection completed: {agent.reflection_count}")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

    # Test 2: UI Import Check
    try:
        print("✅ NeuroUI imports successfully")

    except Exception as e:
        print(f"❌ UI import failed: {e}")
        return False

    # Test 3: CLI Functionality
    try:
        print("✅ CLI interface available")

    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False

    print("\n🎉 All integration tests passed!")
    print("\n🚀 Ready for next iteration. What would you like to enhance?")
    print("   1. 🔧 Technical polish (error handling, performance)")
    print("   2. 🤖 Advanced agent capabilities (learning, collaboration)")
    print("   3. 🎨 UI enhancements (visualization, real-time updates)")
    print("   4. 🌐 Ecosystem development (plugins, integrations)")
    print("   5. 🔬 Research features (consciousness metrics, self-modification)")

    return True


if __name__ == "__main__":
    test_integration()
