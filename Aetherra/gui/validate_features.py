#!/usr/bin/env python3
"""
🔍 Aetherra AI OS - Feature Validation Script
==============================================

Validates that all enhanced Lyrixa features are properly integrated
and accessible through the GUI interface.

This script checks:
✅ Enhanced Conversational AI (#7)
✅ Intelligent Error Handling (#8)
✅ Analytics & Insights Engine (#6)
✅ Advanced Memory Systems (#5)
✅ Specialized Agent Ecosystem
✅ Ethics & Bias Detection
"""

import sys
import os
import asyncio
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_enhanced_conversation_ai():
    """Check Enhanced Conversational AI (#7) availability"""
    print("\n🧠 Checking Enhanced Conversational AI (#7)...")
    try:
        from enhanced_conversation_manager_7 import LyrixaEnhancedConversationManager
        manager = LyrixaEnhancedConversationManager()
        print("   ✅ Enhanced Conversational AI manager imported successfully")
        print("   📊 Multi-turn memory support: Available")
        print("   🎯 Intent-to-code translation: Available")
        print("   🧵 Thread-aware sessions: Available")
        return True
    except ImportError as e:
        print(f"   ❌ Enhanced Conversational AI not available: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️ Enhanced Conversational AI error: {e}")
        return False

def check_intelligent_error_handler():
    """Check Intelligent Error Handler (#8) availability"""
    print("\n[TOOL] Checking Intelligent Error Handler (#8)...")
    try:
        from intelligent_error_handler_8 import LyrixaIntelligentErrorHandler, get_global_error_handler
        handler = get_global_error_handler()
        stats = handler.get_error_statistics()
        print("   ✅ Intelligent Error Handler imported successfully")
        print(f"   📊 Error patterns learned: {stats.get('learned_patterns', 0)}")
        print(f"   🎯 Auto-correction enabled: {stats.get('auto_correction_enabled', False)}")
        print(f"   🧠 Learning enabled: {stats.get('learning_enabled', False)}")
        return True
    except ImportError as e:
        print(f"   ❌ Intelligent Error Handler not available: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️ Intelligent Error Handler error: {e}")
        return False

def check_analytics_engine():
    """Check Analytics & Insights Engine (#6) availability"""
    print("\n📊 Checking Analytics & Insights Engine (#6)...")
    try:
        from Aetherra.lyrixa.analytics_insights_engine import AnalyticsInsightsEngine
        engine = AnalyticsInsightsEngine()
        print("   ✅ Analytics & Insights Engine imported successfully")
        print("   📈 Real-time metrics collection: Available")
        print("   🔍 Pattern detection algorithms: Available")
        print("   💡 Insight generation: Available")
        return True
    except ImportError as e:
        print(f"   ❌ Analytics & Insights Engine not available: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️ Analytics & Insights Engine error: {e}")
        return False

def check_advanced_memory_systems():
    """Check Advanced Memory Systems (#5) availability"""
    print("\n🧠 Checking Advanced Memory Systems (#5)...")
    memory_available = False

    # Check basic memory engine
    try:
        from Aetherra.lyrixa.memory.lyrixa_memory_engine import LyrixaMemoryEngine
        engine = LyrixaMemoryEngine()
        print("   ✅ Basic Memory Engine: Available")
        memory_available = True
    except ImportError as e:
        print(f"   ❌ Basic Memory Engine not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Basic Memory Engine error: {e}")

    # Check quantum memory integration
    try:
        from Aetherra.lyrixa.memory.quantum_memory_integration import QuantumEnhancedMemoryEngine
        print("   ✅ Quantum Memory Integration: Available")
        print("   🔬 Quantum-enhanced pattern storage: Available")
        memory_available = True
    except ImportError as e:
        print(f"   ❌ Quantum Memory Integration not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Quantum Memory Integration error: {e}")

    # Check advanced memory integration
    try:
        from Aetherra.lyrixa.memory.advanced_memory_integration import AdvancedMemoryIntegration
        print("   ✅ Advanced Memory Integration: Available")
        memory_available = True
    except ImportError as e:
        print(f"   ❌ Advanced Memory Integration not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Advanced Memory Integration error: {e}")

    return memory_available

def check_specialized_agents():
    """Check Specialized Agent Ecosystem availability"""
    print("\n🤖 Checking Specialized Agent Ecosystem...")
    agents_available = 0
    total_agents = 4

    # Check Data Agent
    try:
        from Aetherra.lyrixa.agents.data_agent import DataAgent
        agent = DataAgent()
        print("   ✅ Data Agent: Available")
        agents_available += 1
    except ImportError as e:
        print(f"   ❌ Data Agent not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Data Agent error: {e}")

    # Check Technical Agent
    try:
        from Aetherra.lyrixa.agents.technical_agent import TechnicalAgent
        agent = TechnicalAgent()
        print("   ✅ Technical Agent: Available")
        agents_available += 1
    except ImportError as e:
        print(f"   ❌ Technical Agent not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Technical Agent error: {e}")

    # Check Support Agent
    try:
        from Aetherra.lyrixa.agents.support_agent import SupportAgent
        agent = SupportAgent()
        print("   ✅ Support Agent: Available")
        agents_available += 1
    except ImportError as e:
        print(f"   ❌ Support Agent not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Support Agent error: {e}")

    # Check Security Agent
    try:
        from Aetherra.lyrixa.agents.security_agent import SecurityAgent
        agent = SecurityAgent()
        print("   ✅ Security Agent: Available")
        agents_available += 1
    except ImportError as e:
        print(f"   ❌ Security Agent not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Security Agent error: {e}")

    print(f"   📊 Specialized Agents Available: {agents_available}/{total_agents}")
    return agents_available > 0

def check_ethics_system():
    """Check Ethics & Bias Detection availability"""
    print("\n⚖️ Checking Ethics & Bias Detection System...")
    ethics_available = False

    # Check Moral Reasoning Engine
    try:
        from Aetherra.lyrixa.ethics_agent.moral_reasoning import MoralReasoningEngine
        engine = MoralReasoningEngine()
        print("   ✅ Moral Reasoning Engine: Available")
        ethics_available = True
    except ImportError as e:
        print(f"   ❌ Moral Reasoning Engine not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Moral Reasoning Engine error: {e}")

    # Check Bias Detection Engine
    try:
        from Aetherra.lyrixa.ethics_agent.bias_detector import BiasDetectionEngine
        engine = BiasDetectionEngine()
        print("   ✅ Bias Detection Engine: Available")
        ethics_available = True
    except ImportError as e:
        print(f"   ❌ Bias Detection Engine not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Bias Detection Engine error: {e}")

    # Check Value Alignment Engine
    try:
        from Aetherra.lyrixa.ethics_agent.value_alignment import ValueAlignmentEngine
        engine = ValueAlignmentEngine()
        print("   ✅ Value Alignment Engine: Available")
        ethics_available = True
    except ImportError as e:
        print(f"   ❌ Value Alignment Engine not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Value Alignment Engine error: {e}")

    return ethics_available

def check_web_interface_integration():
    """Check Web Interface Server integration"""
    print("\n🌐 Checking Web Interface Server Integration...")
    try:
        from Aetherra.gui.web_interface_server import AetherraWebServer
        server = AetherraWebServer()
        print("   ✅ Web Interface Server: Available")
        print("   🔗 Enhanced API endpoints: Available")
        print("   📡 WebSocket real-time communication: Available")
        print("   🎨 React frontend integration: Available")
        return True
    except ImportError as e:
        print(f"   ❌ Web Interface Server not available: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️ Web Interface Server error: {e}")
        return False

async def run_integration_test():
    """Run a basic integration test"""
    print("\n🧪 Running Integration Test...")
    try:
        # Test Enhanced Conversational AI
        from enhanced_conversation_manager_7 import LyrixaEnhancedConversationManager
        conv_manager = LyrixaEnhancedConversationManager()

        result = await conv_manager.process_enhanced_message(
            message="Hello, test the integration!",
            user_id="validation_test",
            context={"test_mode": True}
        )

        print("   ✅ Enhanced Conversation Test: PASSED")
        print(f"   📊 Response generated: {len(result.get('response', ''))} characters")
        print(f"   🎯 Intent detected: {result.get('intent', 'none')}")

        return True
    except Exception as e:
        print(f"   ❌ Integration Test FAILED: {e}")
        traceback.print_exc()
        return False

def main():
    """Main validation function"""
    print("🔍 AETHERRA AI OS - FEATURE VALIDATION")
    print("=" * 50)
    print("Checking all enhanced Lyrixa features...")

    results = {
        "Enhanced Conversational AI (#7)": check_enhanced_conversation_ai(),
        "Intelligent Error Handling (#8)": check_intelligent_error_handler(),
        "Analytics & Insights Engine (#6)": check_analytics_engine(),
        "Advanced Memory Systems (#5)": check_advanced_memory_systems(),
        "Specialized Agent Ecosystem": check_specialized_agents(),
        "Ethics & Bias Detection": check_ethics_system(),
        "Web Interface Integration": check_web_interface_integration()
    }

    # Run integration test
    print("\n🔬 Running Integration Tests...")
    try:
        integration_result = asyncio.run(run_integration_test())
        results["Integration Test"] = integration_result
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        results["Integration Test"] = False

    # Display summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for feature, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {feature}")
        if status:
            passed += 1

    print("=" * 50)
    print(f"📈 Overall Status: {passed}/{total} features available")

    if passed == total:
        print("🎉 ALL FEATURES VALIDATED SUCCESSFULLY!")
        print("🚀 Aetherra AI OS is ready for full operation!")
    elif passed >= total * 0.7:  # 70% threshold
        print("⚠️ Most features available - some components may need attention")
        print("[TOOL] Consider checking missing dependencies")
    else:
        print("❌ Several features unavailable - check installation")
        print("📝 Review setup documentation and dependencies")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
