#!/usr/bin/env python3
"""Quick test for LiveThinkingPane add_thought_process method"""

import sys

sys.path.insert(0, "lyrixa")

try:
    from datetime import datetime

    from PySide6.QtWidgets import QApplication

    from lyrixa.gui.intelligence_layer import LiveThinkingPane, ThoughtProcess

    # Create QApplication
    app = QApplication.instance() or QApplication([])

    # Test LiveThinkingPane
    thinking_pane = LiveThinkingPane()
    print("✅ LiveThinkingPane created")

    # Test adding thought process
    test_thought = ThoughtProcess(
        id="test_001",
        description="Testing thought process method",
        confidence=0.75,
        context={"test": True},
        suggestions=["This is a test"],
        timestamp=datetime.now(),
    )

    thinking_pane.add_thought_process(test_thought)
    print("✅ add_thought_process method works correctly")

    print("\n✅ LiveThinkingPane method fixed successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
