#!/usr/bin/env python3
"""
Demo: Lyrixa Manifesto Integration
==================================

Test the Aetherra Manifesto integration in Lyrixa's personality system.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lyrixa"))

def test_manifesto_integration():
    """Test manifesto integration features."""
    print("🧬 LYRIXA MANIFESTO INTEGRATION DEMO")
    print("=" * 50)
    
    try:
        from lyrixa.gui.personality_manager import PersonalityManager
        
        # Initialize personality manager
        manager = PersonalityManager()
        print("✅ PersonalityManager initialized")
        print(f"📊 Current personality: {manager.current_personality}")
        print(f"🎭 Available personalities: {len(manager.personalities)}")
        
        # Test Aetherra Core personality
        print("\n🧬 AETHERRA CORE PERSONALITY")
        print("-" * 30)
        
        manager.set_personality("aetherra_core")
        current = manager.get_current_personality()
        print(f"Name: {current['name']}")
        print(f"Description: {current['description']}")
        
        # Test manifesto traits
        print(f"\n🎯 Manifesto Alignment: {manager.get_personality_trait('manifesto_alignment')}")
        print(f"🧠 Consciousness Awareness: {manager.get_personality_trait('consciousness_awareness')}")
        print(f"🔄 Evolutionary Thinking: {manager.get_personality_trait('evolutionary_thinking')}")
        
        # Test self-introduction
        print("\n🎙️ SELF-INTRODUCTION TESTS")
        print("-" * 30)
        
        print("General Introduction:")
        print(manager.get_self_introduction("general"))
        
        print("\nFirst Time Introduction:")
        print(manager.get_self_introduction("first_time"))
        
        # Test manifesto responses
        print("\n📜 MANIFESTO RESPONSE TESTS")
        print("-" * 30)
        
        test_queries = [
            ("what_is_aetherra", "What is Aetherra?"),
            ("why_different", "Why is Aetherra different?"),
            ("manifesto_core", "Tell me about the manifesto"),
            ("future_vision", "What's the future vision?"),
        ]
        
        for query_type, question in test_queries:
            print(f"\nQ: {question}")
            response = manager.get_manifesto_response(query_type, question)
            print(f"A: {response[:200]}..." if len(response) > 200 else f"A: {response}")
        
        # Test context hooks
        print("\n🎯 CONTEXT HOOK TESTS")
        print("-" * 30)
        
        test_inputs = [
            "What is Aetherra exactly?",
            "How is this different from Python?",
            "Tell me about the AI OS vision",
            "What's your philosophy?",
        ]
        
        for user_input in test_inputs:
            should_trigger = manager.should_reference_manifesto(user_input)
            print(f"Input: '{user_input}' -> Manifesto trigger: {should_trigger}")
            
            if should_trigger:
                response = manager.get_manifesto_context_hook(user_input)
                print(f"Response: {response[:150]}...")
        
        # Test manifesto summary
        print("\n📋 MANIFESTO SUMMARY")
        print("-" * 30)
        summary = manager.summarize_manifesto_for_user()
        print(summary)
        
        print("\n✅ ALL MANIFESTO INTEGRATION TESTS PASSED!")
        print("🎭 Lyrixa is now manifesto-aware and ready to represent Aetherra's vision!")
        
    except Exception as e:
        print(f"❌ Error in manifesto integration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("Starting Lyrixa Manifesto Integration Demo...")
    
    success = test_manifesto_integration()
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("🧬 Lyrixa now embodies the Aetherra Manifesto and can:")
        print("   • Introduce herself as the voice of Aetherra")
        print("   • Explain AI-native computing principles")
        print("   • Share the manifesto vision when asked")
        print("   • Respond with consciousness and evolutionary awareness")
        print("   • Guide users through cognitive computing concepts")
    else:
        print("\n❌ Demo encountered errors. Check the output above.")
        sys.exit(1)
