#!/usr/bin/env python3
"""
🐛 DEBUG CONSOLE TEST
====================

Test the debug console functionality to ensure it's working properly.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_debug_console():
    """Test debug console functionality"""
    print("🐛 Testing Lyrixa Debug Console...")

    try:
        # Test import
        from lyrixa.core.debug_console import (
            CognitiveState,
            DebugLevel,
            LyrixaDebugConsole,
        )

        print("✅ Debug console imports successful")

        # Test initialization
        debug = LyrixaDebugConsole(DebugLevel.DETAILED)
        print("✅ Debug console initialized")

        # Test cognitive state change
        debug.set_cognitive_state(CognitiveState.ANALYZING, "Testing debug console")
        print("✅ Cognitive state change works")

        # Test perception capture
        perception_id = debug.capture_perception(
            user_input="Test input for debug console",
            context_window={"test": True},
            memory_context=[{"type": "test_memory"}],
            current_goals=["test_goal"],
            system_state={"debug_test": True},
        )
        print(f"✅ Perception captured: {perception_id}")

        # Test thought process
        thought_id = debug.start_thought_process(
            input_analysis={"intent": "testing", "confidence": 0.9},
            initial_reasoning="Testing debug console thought tracking",
        )
        print(f"✅ Thought process started: {thought_id}")

        # Test reasoning steps
        debug.add_reasoning_step(thought_id, "Step 1: Analyze test input", 0.85)
        debug.add_reasoning_step(thought_id, "Step 2: Generate test response", 0.90)
        print("✅ Reasoning steps added")

        # Test decision matrix
        options = [
            {"name": "option_a", "quality": 0.8, "speed": 0.6, "accuracy": 0.9},
            {"name": "option_b", "quality": 0.6, "speed": 0.9, "accuracy": 0.7},
            {"name": "option_c", "quality": 0.9, "speed": 0.5, "accuracy": 0.95},
        ]
        criteria = {"quality": 0.4, "speed": 0.3, "accuracy": 0.3}

        decision_matrix = debug.evaluate_decision_matrix(thought_id, options, criteria)
        print(f"✅ Decision matrix evaluated: {decision_matrix.final_rankings[0]}")

        # Test finalize decision
        debug.finalize_decision(thought_id, "option_c", 150.5)
        print("✅ Decision finalized")

        # Test current state
        state = debug.show_current_state()
        print(f"✅ Current state retrieved: {state['cognitive_state']}")

        # Test thought analysis
        analysis = debug.get_thought_analysis(thought_id)
        print(f"✅ Thought analysis: {len(analysis['reasoning_steps'])} steps")

        # Test export
        filepath = debug.export_debug_session("debug_test_export.json")
        print(f"✅ Debug session exported to: {filepath}")

        # Test CLI widget
        print("\n🖥️ Testing CLI debug widget...")
        from lyrixa.gui.debug_console_widget import create_debug_widget

        widget = create_debug_widget(debug)
        print("✅ Debug widget created")

        if hasattr(widget, "show_status"):
            widget.show_status()
            print("✅ CLI debug status displayed")

        if hasattr(widget, "show_latest_thought"):
            widget.show_latest_thought()
            print("✅ Latest thought displayed")

        print("\n🎉 All debug console tests passed!")
        return True

    except Exception as e:
        print(f"❌ Debug console test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_debug_console()
    sys.exit(0 if success else 1)
