#!/usr/bin/env python3
"""
Comprehensive Test Suite for Lyrixa Modular System
Tests all components, imports, and functionality before full launch.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test all critical imports"""
    print("🧪 Testing Critical Imports...")

    # Test basic Python modules
    try:
        import asyncio

        print("  ✅ asyncio")
    except ImportError as e:
        print(f"  ❌ asyncio: {e}")

    # Test PySide6
    try:
        from PySide6.QtWidgets import QApplication

        print("  ✅ PySide6.QtWidgets")
    except ImportError as e:
        print(f"  ❌ PySide6.QtWidgets: {e}")

    # Test utils
    try:
        from utils.logging_utils import log

        print("  ✅ utils.logging_utils")
    except ImportError as e:
        print(f"  ❌ utils.logging_utils: {e}")

    try:
        from utils.launch_utils import run_self_improvement_api

        print("  ✅ utils.launch_utils")
    except ImportError as e:
        print(f"  ❌ utils.launch_utils: {e}")

    # Test agents
    try:
        from lyrixa.agents.core_agent import LyrixaAI

        print("  ✅ lyrixa.agents.core_agent")
    except ImportError as e:
        print(f"  ❌ lyrixa.agents.core_agent: {e}")

    try:
        from lyrixa.agents.goal_agent import GoalAgent

        print("  ✅ lyrixa.agents.goal_agent")
    except ImportError as e:
        print(f"  ❌ lyrixa.agents.goal_agent: {e}")

    # Test GUI
    try:
        from lyrixa.gui.gui_window import LyrixaWindow

        print("  ✅ lyrixa.gui.gui_window")
    except ImportError as e:
        print(f"  ❌ lyrixa.gui.gui_window: {e}")

    # Test intelligence
    try:
        from lyrixa.intelligence import LyrixaIntelligenceStack

        print("  ✅ lyrixa.intelligence")
    except ImportError as e:
        print(f"  ❌ lyrixa.intelligence: {e}")

    # Test core components
    try:
        from core.memory_manager import MemoryManager

        print("  ✅ core.memory_manager")
    except ImportError as e:
        print(f"  ❌ core.memory_manager: {e}")

    try:
        from core.plugin_manager import PluginManager

        print("  ✅ core.plugin_manager")
    except ImportError as e:
        print(f"  ❌ core.plugin_manager: {e}")

    try:
        from core.prompt_engine import PromptEngine

        print("  ✅ core.prompt_engine")
    except ImportError as e:
        print(f"  ❌ core.prompt_engine: {e}")

    try:
        from core.multi_llm_manager import MultiLLMManager

        print("  ✅ core.multi_llm_manager")
    except ImportError as e:
        print(f"  ❌ core.multi_llm_manager: {e}")

    try:
        from core.aether_runtime import AetherRuntime

        print("  ✅ core.aether_runtime")
    except ImportError as e:
        print(f"  ❌ core.aether_runtime: {e}")


def test_agent_system():
    """Test the modular agent system"""
    print("\n🤖 Testing Agent System...")

    try:
        from lyrixa.agents.agent_base import AgentBase, AgentResponse
        from lyrixa.agents.core_agent import LyrixaAI
        from lyrixa.agents.escalation_agent import EscalationAgent
        from lyrixa.agents.goal_agent import GoalAgent
        from lyrixa.agents.plugin_agent import PluginAgent
        from lyrixa.agents.reflection_agent import ReflectionAgent
        from lyrixa.agents.self_evaluation_agent import SelfEvaluationAgent

        print("  ✅ All agent imports successful")

        # Test agent instantiation with mock dependencies
        class MockMemory:
            async def store_memory(self, data):
                pass

        class MockPromptEngine:
            pass

        class MockLLMManager:
            pass

        mock_memory = MockMemory()
        mock_prompt = MockPromptEngine()
        mock_llm = MockLLMManager()

        # Test individual agents
        agents_to_test = [
            ("GoalAgent", GoalAgent),
            ("PluginAgent", PluginAgent),
            ("ReflectionAgent", ReflectionAgent),
            ("EscalationAgent", EscalationAgent),
            ("SelfEvaluationAgent", SelfEvaluationAgent),
        ]

        for agent_name, agent_class in agents_to_test:
            try:
                agent = agent_class(mock_memory, mock_prompt, mock_llm)
                print(f"    ✅ {agent_name} instantiated")
            except Exception as e:
                print(f"    ❌ {agent_name} failed: {e}")

        # Test main LyrixaAI coordination agent
        try:

            class MockRuntime:
                pass

            lyrixa = LyrixaAI(MockRuntime(), mock_memory, mock_prompt, mock_llm)
            print("    ✅ LyrixaAI coordination agent instantiated")
        except Exception as e:
            print(f"    ❌ LyrixaAI failed: {e}")

    except Exception as e:
        print(f"  ❌ Agent system test failed: {e}")
        traceback.print_exc()


async def test_agent_functionality():
    """Test agent functionality"""
    print("\n⚙️ Testing Agent Functionality...")

    try:
        from lyrixa.agents.goal_agent import GoalAgent
        from lyrixa.agents.plugin_agent import PluginAgent

        class MockMemory:
            async def store_memory(self, data):
                print(f"    📝 Memory stored: {data.get('type', 'unknown')}")

        class MockPromptEngine:
            pass

        class MockLLMManager:
            pass

        mock_memory = MockMemory()
        mock_prompt = MockPromptEngine()
        mock_llm = MockLLMManager()

        # Test GoalAgent
        print("  Testing GoalAgent...")
        goal_agent = GoalAgent(mock_memory, mock_prompt, mock_llm)
        response = await goal_agent.process_input(
            "Create a new goal to test the system"
        )
        print(f"    ✅ Goal response: {response.content[:50]}...")

        # Test PluginAgent
        print("  Testing PluginAgent...")
        plugin_agent = PluginAgent(mock_memory, mock_prompt, mock_llm)
        response = await plugin_agent.process_input("Find plugins for file management")
        print(f"    ✅ Plugin response: {response.content[:50]}...")

        print("  ✅ Agent functionality tests passed")

    except Exception as e:
        print(f"  ❌ Agent functionality test failed: {e}")
        traceback.print_exc()


def test_gui_components():
    """Test GUI components without launching full interface"""
    print("\n🖥️ Testing GUI Components...")

    try:
        from PySide6.QtWidgets import QApplication

        from lyrixa.gui.gui_window import LyrixaWindow

        # Initialize QApplication for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Test window creation
        window = LyrixaWindow()
        print("  ✅ LyrixaWindow created successfully")

        # Test window methods
        window.add_diagnostics_tab()
        print("  ✅ Diagnostics tab added")

        window.update_dashboard_metrics()
        print("  ✅ Dashboard metrics updated")

        # Don't show the window, just test creation
        print("  ✅ GUI components test passed")

    except Exception as e:
        print(f"  ❌ GUI components test failed: {e}")
        traceback.print_exc()


def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing File Structure...")

    base_path = Path(__file__).parent.parent
    required_files = [
        "lyrixa/agents/__init__.py",
        "lyrixa/agents/agent_base.py",
        "lyrixa/agents/core_agent.py",
        "lyrixa/agents/goal_agent.py",
        "lyrixa/agents/plugin_agent.py",
        "lyrixa/agents/reflection_agent.py",
        "lyrixa/agents/escalation_agent.py",
        "lyrixa/agents/self_evaluation_agent.py",
        "lyrixa/gui/gui_window.py",
        "lyrixa/intelligence/__init__.py",
        "utils/launch_utils.py",
        "utils/logging_utils.py",
        "utils/__init__.py",
    ]

    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")


def test_core_dependencies():
    """Test core system dependencies"""
    print("\n🔧 Testing Core Dependencies...")

    # Check if core modules exist
    core_modules = [
        "core/memory_manager.py",
        "core/plugin_manager.py",
        "core/prompt_engine.py",
        "core/multi_llm_manager.py",
    ]

    base_path = Path(__file__).parent.parent

    for module in core_modules:
        module_path = base_path / module
        if module_path.exists():
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module} - MISSING")

    # Check for runtime
    runtime_paths = [
        "runtime/aether_runtime.py",
        "core/aether_runtime.py",  # Alternative location
    ]

    runtime_found = False
    for runtime_path in runtime_paths:
        if (base_path / runtime_path).exists():
            print(f"  ✅ {runtime_path}")
            runtime_found = True
            break

    if not runtime_found:
        print(f"  ❌ aether_runtime.py - NOT FOUND in expected locations")


async def run_comprehensive_tests():
    """Run all tests"""
    print("🧬" + "=" * 60 + "🧬")
    print("🚀     Lyrixa Modular System Test Suite     🚀")
    print("🧬" + "=" * 60 + "🧬")

    test_file_structure()
    test_imports()
    test_core_dependencies()
    test_agent_system()
    await test_agent_functionality()
    test_gui_components()

    print("\n" + "=" * 60)
    print("🎯 Test Suite Complete!")
    print("If you see mostly ✅ marks above, the system is ready to launch.")
    print("If you see ❌ marks, those issues need to be resolved first.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
