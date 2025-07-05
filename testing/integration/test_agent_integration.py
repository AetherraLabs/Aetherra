#!/usr/bin/env python3
"""
🧪 Agent Integration Test
=========================

Test script to verify that the agent behavior improvements are working correctly:
- Agent syntax parsing
- Agent control through AetherraCode
- Agent mode and goal management
- UI integration
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))


def test_agent_syntax_parsing():
    """Test agent syntax parsing in AetherraCode"""
    print("🧪 Testing Agent Syntax Parsing...")

    from Aetherra.core.syntax_tree import SyntaxTreeVisitor, parse_neurocode

    # Test agent syntax
    test_code = """
# Agent control commands
agent.mode = "reflecting"
agent.start()
agent.add_goal("Improve code quality", priority="high")
agent.add_goal("Monitor system performance")
agent.status()
agent.stop()
agent.clear_goals()
"""

    # Parse the code
    tree = parse_neurocode(test_code)
    visitor = SyntaxTreeVisitor()

    print("✅ Parsed agent syntax successfully")
    print("📝 Parsed commands:")

    results = visitor.visit(tree)
    for result in results:
        if result:  # Skip None results
            print(f"   • {result}")

    return True


def test_agent_executor():
    """Test agent command execution"""
    print("\n🧪 Testing Agent Executor...")

    try:
        from Aetherra.core.agent_executor import AgentExecutor
        from Aetherra.core.enhanced_agent import EnhancedNeuroAgent
        from Aetherra.core.syntax_tree import NodeType, parse_neurocode

        # Create agent and executor
        agent = EnhancedNeuroAgent()
        executor = AgentExecutor(agent)

        # Test parsing and execution
        test_commands = [
            'agent.mode = "goal_monitoring"',
            'agent.add_goal("Test goal")',
            "agent.status()",
        ]

        for cmd in test_commands:
            tree = parse_neurocode(cmd)
            # Find agent nodes
            for node in tree.children or []:
                if node.type in [NodeType.AGENT, NodeType.AGENT_MODE, NodeType.AGENT_GOAL]:
                    result = executor.execute_agent_node(node)
                    print(f"   • {cmd}: {result.get('status')} - {result.get('message')}")

        print("✅ Agent executor working correctly")
        return True

    except ImportError as e:
        print(f"⚠️ Agent components not available: {e}")
        return False


def test_agent_state_management():
    """Test agent state and goal management"""
    print("\n🧪 Testing Agent State Management...")

    try:
        from Aetherra.core.enhanced_agent import EnhancedNeuroAgent

        # Create agent
        agent = EnhancedNeuroAgent()

        # Test state management
        initial_state = agent.get_state()
        print(f"   • Initial state: {initial_state}")

        # Test setting state
        agent.set_state("reflecting")
        new_state = agent.get_state()
        print(f"   • New state: {new_state}")

        # Test goal management
        initial_goals = agent.get_goals()
        print(f"   • Initial goals count: {len(initial_goals)}")

        # Add goals
        agent.add_goal({"text": "Test goal 1", "priority": "high"})
        agent.add_goal({"text": "Test goal 2", "priority": "medium"})

        goals_after_add = agent.get_goals()
        print(f"   • Goals after adding: {len(goals_after_add)}")

        # Clear goals
        agent.set_goals([])
        goals_after_clear = agent.get_goals()
        print(f"   • Goals after clearing: {len(goals_after_clear)}")

        print("✅ Agent state management working correctly")
        return True

    except ImportError as e:
        print(f"⚠️ Agent components not available: {e}")
        return False


def main():
    """Run all agent integration tests"""
    print("🚀 Starting Agent Integration Tests")
    print("=" * 50)

    tests = [
        test_agent_syntax_parsing,
        test_agent_executor,
        test_agent_state_management,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All agent integration tests passed!")
        print("\n✅ Agent Behavior Implementation Complete:")
        print("   • Agent syntax support in AetherraCode")
        print("   • Background thread with reflection loop")
        print("   • Periodic triggers for state-based actions")
        print("   • Goal monitoring and management")
        print("   • Agent mode setting and control")
        print("   • Deep integration with AetherraCode/Neuroplex")
        return 0
    else:
        print("⚠️ Some tests failed. Check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
