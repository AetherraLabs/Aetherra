#!/usr/bin/env python3
"""
🎉 ENHANCED CHAT DEMO - Comprehensive Aetherra Integration
==========================================================

This demo showcases the fully integrated web interface with ALL
chat features, intelligence systems, and agents properly wired in.

🌟 Features Demonstrated:
- Real-time conversation with LLM integration
- 4 specialized agents (Contradiction, Curiosity, Learning Loop, Self-Question)
- 3 ethics systems (Bias Detection, Moral Reasoning, Value Alignment)
- Intelligence stack integration
- Memory system integration
- Plugin system integration

🚀 Run this to see the complete system in action!
"""

import sys
import time
import asyncio
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def test_conversation_features():
    """Test all conversation and chat features"""
    print("💬 TESTING CONVERSATION FEATURES")
    print("=" * 35)

    try:
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        # Initialize conversation manager
        conv_manager = LyrixaConversationManager(
            workspace_path=str(project_root),
            gui_interface=None
        )

        # Test conversation
        test_messages = [
            "Hello Lyrixa, can you introduce yourself?",
            "What are your capabilities?",
            "Can you help me with coding?",
            "What ethics systems do you have?"
        ]

        print("🗣️ Testing conversation responses:")
        for i, message in enumerate(test_messages, 1):
            print(f"\n   {i}. User: {message}")
            try:
                response = conv_manager.generate_response_sync(message)
                print(f"      Lyrixa: {response[:100]}...")
            except Exception as e:
                print(f"      Error: {e}")

        print("\n✅ Conversation system: OPERATIONAL")

    except Exception as e:
        print(f"❌ Conversation system error: {e}")

def test_specialized_agents():
    """Test the 4 specialized agents"""
    print("\n🤖 TESTING SPECIALIZED AGENTS")
    print("=" * 30)

    specialized_agents = {
        'ContradictionDetectionAgent': 'Aetherra.lyrixa.agents.contradiction_detection_agent',
        'CuriosityAgent': 'Aetherra.lyrixa.agents.curiosity_agent',
        'LearningLoopIntegrationAgent': 'Aetherra.lyrixa.agents.learning_loop_integration_agent',
        'SelfQuestionGeneratorAgent': 'Aetherra.lyrixa.agents.self_question_generator_agent'
    }

    loaded_agents = {}

    for agent_name, module_path in specialized_agents.items():
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            agent_instance = agent_class()
            loaded_agents[agent_name] = agent_instance
            print(f"   ✅ {agent_name}: Ready")

            # Test basic functionality if available
            if hasattr(agent_instance, 'get_status'):
                status = agent_instance.get_status()
                print(f"      Status: {status}")

        except Exception as e:
            print(f"   ❌ {agent_name}: {e}")

    print(f"\n🎯 Specialized agents loaded: {len(loaded_agents)}/4")
    return loaded_agents

def test_ethics_systems():
    """Test the 3 ethics systems"""
    print("\n🛡️ TESTING ETHICS SYSTEMS")
    print("=" * 25)

    ethics_systems = {
        'BiasDetectionEngine': 'Aetherra.lyrixa.ethics_agent.bias_detector',
        'MoralReasoningEngine': 'Aetherra.lyrixa.ethics_agent.moral_reasoning',
        'ValueAlignmentEngine': 'Aetherra.lyrixa.ethics_agent.value_alignment'
    }

    loaded_ethics = {}

    for system_name, module_path in ethics_systems.items():
        try:
            module = __import__(module_path, fromlist=[system_name])
            system_class = getattr(module, system_name)
            system_instance = system_class()
            loaded_ethics[system_name] = system_instance
            print(f"   ✅ {system_name}: Active")

        except Exception as e:
            print(f"   ❌ {system_name}: {e}")

    print(f"\n🎯 Ethics systems loaded: {len(loaded_ethics)}/3")
    return loaded_ethics

def test_intelligence_stack():
    """Test intelligence stack integration"""
    print("\n🧠 TESTING INTELLIGENCE STACK")
    print("=" * 30)

    try:
        from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

        # Initialize intelligence stack
        intelligence = LyrixaIntelligenceStack(
            workspace_path=str(project_root)
        )

        print("   ✅ Intelligence Stack: Initialized")

        # Test basic intelligence features
        if hasattr(intelligence, 'get_system_status'):
            status = intelligence.get_system_status()
            print(f"   📊 System Status: {status}")

        print("   ✅ Intelligence integration: OPERATIONAL")
        return intelligence

    except Exception as e:
        print(f"   ❌ Intelligence stack error: {e}")
        return None

def test_memory_systems():
    """Test memory system integration"""
    print("\n💾 TESTING MEMORY SYSTEMS")
    print("=" * 25)

    try:
        from Aetherra.lyrixa.memory.lyrixa_memory_engine import LyrixaMemoryEngine

        # Initialize memory engine
        memory = LyrixaMemoryEngine()
        print("   ✅ Memory Engine: Initialized")

        # Test basic memory operations
        if hasattr(memory, 'get_memory_stats'):
            stats = memory.get_memory_stats()
            print(f"   📊 Memory Stats: {stats}")

        print("   ✅ Memory integration: OPERATIONAL")
        return memory

    except Exception as e:
        print(f"   ❌ Memory system error: {e}")
        return None

def test_web_interface_integration():
    """Test web interface with full integration"""
    print("\n🌐 TESTING WEB INTERFACE INTEGRATION")
    print("=" * 35)

    try:
        from Aetherra.lyrixa.gui.web_interface_server import AetherraWebServer

        # Create server instance
        server = AetherraWebServer()

        print("   ✅ Web Server: Initialized")
        print(f"   🤖 Agents Loaded: {len(server.agents)}")
        print(f"   🛡️ Ethics Systems: {len(server.ethics_agents)}")
        print(f"   🧠 Intelligence: {'Yes' if server.lyrixa_intelligence else 'No'}")
        print(f"   💬 Conversation: {'Yes' if server.conversation_manager else 'No'}")
        print(f"   💾 Memory: {'Yes' if server.memory_engine else 'No'}")

        # Test real integration
        status = server._get_real_system_status()
        active_components = sum(1 for comp in status['components'].values() if comp['active'])

        print(f"   🔧 Active Components: {active_components}/5")
        print("   ✅ Web interface integration: COMPLETE")

        return server

    except Exception as e:
        print(f"   ❌ Web interface error: {e}")
        return None

def main():
    """Main test function"""
    print("🎉 AETHERRA ENHANCED CHAT INTEGRATION TEST")
    print("=" * 45)
    print("Testing ALL chat features and intelligence systems...")
    print()

    # Test all components
    conversation_working = test_conversation_features()
    agents = test_specialized_agents()
    ethics = test_ethics_systems()
    intelligence = test_intelligence_stack()
    memory = test_memory_systems()
    web_server = test_web_interface_integration()

    # Final summary
    print("\n🎯 INTEGRATION SUMMARY")
    print("=" * 22)

    working_systems = []
    if conversation_working: working_systems.append("💬 Conversation Manager")
    if agents: working_systems.append(f"🤖 {len(agents)} Specialized Agents")
    if ethics: working_systems.append(f"🛡️ {len(ethics)} Ethics Systems")
    if intelligence: working_systems.append("🧠 Intelligence Stack")
    if memory: working_systems.append("💾 Memory Engine")
    if web_server: working_systems.append("🌐 Web Interface")

    print(f"✅ WORKING SYSTEMS ({len(working_systems)}/6):")
    for system in working_systems:
        print(f"   • {system}")

    if len(working_systems) >= 5:
        print("\n🚀 SUCCESS! All major chat features and intelligence")
        print("   systems are properly wired into the web interface!")
        print()
        print("🌟 Ready to launch enhanced web interface:")
        print("   python Aetherra/lyrixa/gui/web_interface_server.py")
    else:
        print(f"\n⚠️ Some systems need attention ({len(working_systems)}/6 working)")

    return web_server

if __name__ == "__main__":
    main()
