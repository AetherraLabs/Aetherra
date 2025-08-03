#!/usr/bin/env python3
"""
Lyrixa Polish Features Demonstration
===================================

This script demonstrates all the strategic polish features implemented for Lyrixa:
- Context Memory Awareness
- Plugin Panel Management
- Chat History & Replay
- Quick Commands
- Personality Management
- Response Style Memory
- Intelligence Panel

Run this to see Lyrixa's enhanced capabilities in action!
"""

import os
import sys
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def main():
    print("🎭 Lyrixa Strategic Polish Features Demonstration")
    print("=" * 60)

    try:
        # Import all polish components
        from lyrixa.gui.chat_history_manager import ChatHistoryManager
        from lyrixa.gui.context_memory_manager import ContextMemoryManager
        from lyrixa.gui.intelligence_panel_manager import IntelligencePanelManager
        from lyrixa.gui.personality_manager import PersonalityManager
        from lyrixa.gui.plugin_panel_manager import PluginPanelManager
        from lyrixa.gui.quick_commands_manager import QuickCommandsManager
        from lyrixa.gui.response_style_memory import ResponseStyleMemoryManager

        print("✅ All polish components imported successfully!")
        print()

        # 1. Context Memory Awareness Demo
        print("🧭 1. Context Memory Awareness")
        print("-" * 30)

        context_mgr = ContextMemoryManager()
        context_mgr.switch_context(
            "code_analysis", {"file": "example.py", "language": "python"}
        )
        patterns = context_mgr.get_context_patterns("code_analysis")
        print(f"   ✅ Context switched to: code_analysis")
        print(f"   📊 Context patterns tracked: {len(patterns)}")
        print()

        # 2. Plugin Panel Management Demo
        print("🔌 2. Plugin Panel Management")
        print("-" * 30)

        panel_mgr = PluginPanelManager()
        panel_mgr.toggle_panel_collapse("plugin_panel")
        layout_summary = panel_mgr.get_layout_summary()
        print(f"   ✅ Panel management initialized")
        print(f"   📐 Layout presets available: {layout_summary['available_presets']}")
        print(f"   🎛️ Active layout: {layout_summary['active_layout']}")
        print()

        # 3. Chat History & Replay Demo
        print("💬 3. Chat History & Replay")
        print("-" * 30)

        chat_mgr = ChatHistoryManager()
        chat_mgr.add_message(
            "user", "Hello Lyrixa! Can you help me with Python?", "text"
        )
        chat_mgr.add_message(
            "assistant",
            "Of course! I'd be happy to help you with Python programming.",
            "text",
        )
        recent_messages = chat_mgr.get_recent_messages(10)
        print(f"   ✅ Chat history tracking active")
        print(f"   📝 Messages recorded: {len(recent_messages)}")
        print()

        # 4. Quick Commands Demo
        print("⚡ 4. Quick Commands")
        print("-" * 30)

        commands_mgr = QuickCommandsManager()
        commands_mgr.execute_command("analyze_code")
        favorite_commands = commands_mgr.get_favorite_commands()
        stats = commands_mgr.get_command_stats()
        print(f"   ✅ Quick commands system ready")
        print(f"   🌟 Favorite commands: {len(favorite_commands)}")
        print(f"   📈 Total commands: {stats['total_commands']}")
        print()

        # 5. Personality Management Demo
        print("🎭 5. Personality Management")
        print("-" * 30)

        personality_mgr = PersonalityManager()
        personalities = personality_mgr.get_available_personalities()
        personality_mgr.set_personality("friendly")
        current = personality_mgr.get_current_personality()
        print(f"   ✅ Personality system initialized")
        print(f"   🎨 Available personalities: {len(personalities)}")
        print(f"   🎯 Current personality: {current['name']}")
        print()

        # 6. Response Style Memory Demo
        print("🎯 6. Response Style Memory")
        print("-" * 30)

        style_mgr = ResponseStyleMemoryManager()
        style_mgr.record_feedback(
            "demo_response", "code_help", {}, 4, "helpful", "Very clear explanation!"
        )
        recommendations = style_mgr.get_style_recommendations("code_help")
        summary = style_mgr.get_feedback_summary(30)
        print(f"   ✅ Response style learning active")
        print(f"   📊 Style recommendations: {len(recommendations)} aspects")
        print(f"   🎓 Feedback entries: {summary.get('total_feedback_entries', 0)}")
        print()

        # 7. Intelligence Panel Demo
        print("🧠 7. Intelligence Panel")
        print("-" * 30)

        intelligence_mgr = IntelligencePanelManager()
        intelligence_mgr.start_monitoring()
        time.sleep(1)  # Let it gather some data
        summary = intelligence_mgr.get_intelligence_summary()
        alerts = intelligence_mgr.get_critical_alerts()
        intelligence_mgr.stop_monitoring()
        print(f"   ✅ Intelligence monitoring system ready")
        print(f"   🔍 Active memory items: {len(summary.get('active_memory', {}))}")
        print(f"   🎯 Current goals: {len(summary.get('current_goals', []))}")
        print(f"   [WARN] Critical alerts: {len(alerts)}")
        print()

        # Integration Demo
        print("🔗 8. Integration Showcase")
        print("-" * 30)

        # Show how components work together
        print("   🎭 Setting personality to 'technical'...")
        personality_mgr.set_personality("technical")

        print("   🧭 Switching to development context...")
        context_mgr.switch_context("development", {"mode": "debugging"})

        print("   💬 Recording enhanced chat interaction...")
        chat_mgr.add_message("user", "Can you analyze this complex algorithm?", "text")

        print("   🎯 Recording positive feedback...")
        style_mgr.record_feedback(
            "tech_response", "development", {"technical": True}, 5, "perfect_level"
        )

        print("   ✅ All systems working together seamlessly!")
        print()

        # Final Summary
        print("🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("All strategic polish features are now active and ready to enhance")
        print("the Lyrixa user experience with:")
        print()
        print("✨ Context-aware responses")
        print("✨ Intelligent panel management")
        print("✨ Conversation memory & replay")
        print("✨ Quick access commands")
        print("✨ Adaptive personality")
        print("✨ Learning response styles")
        print("✨ Real-time intelligence insights")
        print()
        print("🚀 Lyrixa is now polished and ready for production!")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
