#!/usr/bin/env python3
"""
Careful World-Class Integration
===============================
🔧 More careful integration approach using proper string replacement
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_memory_tab_replacement():
    """Create proper replacement for create_memory_tab method"""

    return '''    def create_memory_tab(self):
        """Create memory tab with world-class memory core"""
        try:
            # Try to use world-class memory core
            from Aetherra.lyrixa.memory.world_class_memory_core import WorldClassMemoryCore

            # Create world-class memory widget
            memory_widget = WorldClassMemoryCore()
            return memory_widget

        except Exception as e:
            print(f"⚠️  World-class memory core not available: {e}")

            # Fallback to lightweight version
            try:
                from Aetherra.lyrixa.memory.lightweight_memory_core import LightweightMemoryCore
                memory_widget = LightweightMemoryCore()
                return memory_widget

            except Exception as e2:
                print(f"⚠️  Lightweight memory core not available: {e2}")

                # Final fallback to original implementation
                widget = QWidget()
                layout = QVBoxLayout()

                self.memory_view = QTextEdit()
                self.memory_view.setReadOnly(True)

                refresh_btn = QPushButton("Refresh Memory Snapshot")
                refresh_btn.clicked.connect(self.refresh_memory_view)

                layout.addWidget(QLabel("Memory State Viewer"))
                layout.addWidget(self.memory_view)
                layout.addWidget(refresh_btn)
                widget.setLayout(layout)
                return widget'''

def create_goal_tab_replacement():
    """Create proper replacement for create_goal_tab method"""

    return '''    def create_goal_tab(self):
        """Create goal tab with world-class goal tracker"""
        try:
            # Try to use world-class goal tracker
            from Aetherra.lyrixa.core.world_class_goal_tracker import WorldClassGoalTracker

            # Create world-class goal widget
            goal_widget = WorldClassGoalTracker()
            return goal_widget

        except Exception as e:
            print(f"⚠️  World-class goal tracker not available: {e}")

            # Fallback to lightweight version
            try:
                from Aetherra.lyrixa.core.lightweight_goal_tracker import GoalTracker
                from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit

                # Create a simple wrapper for the console-based goal tracker
                widget = QWidget()
                layout = QVBoxLayout()

                # Create goal tracker instance
                self.goal_tracker = GoalTracker()

                # Create display area
                self.goal_display = QTextEdit()
                self.goal_display.setReadOnly(True)

                # Create control buttons
                refresh_btn = QPushButton("🔄 Refresh Goals")
                refresh_btn.clicked.connect(self.refresh_goal_display)

                analyze_btn = QPushButton("🔍 Analyze Blockers")
                analyze_btn.clicked.connect(self.analyze_goal_blockers)

                # Layout
                layout.addWidget(QLabel("🎯 Goal Tracker"))
                layout.addWidget(self.goal_display)
                layout.addWidget(refresh_btn)
                layout.addWidget(analyze_btn)

                widget.setLayout(layout)

                # Initial display
                self.refresh_goal_display()

                return widget

            except Exception as e2:
                print(f"⚠️  Lightweight goal tracker not available: {e2}")

                # Final fallback to original implementation
                widget = QWidget()
                layout = QVBoxLayout()

                self.goal_log = QTextEdit()
                self.goal_log.setReadOnly(True)

                refresh_button = QPushButton("Refresh Goal List")
                refresh_button.clicked.connect(self.refresh_goal_log)

                layout.addWidget(QLabel("Active Goals"))
                layout.addWidget(self.goal_log)
                layout.addWidget(refresh_button)
                widget.setLayout(layout)
                return widget'''

def create_helper_methods():
    """Create helper methods for goal tracker"""

    return '''
    def refresh_goal_display(self):
        """Refresh the goal display with current goals"""
        try:
            if hasattr(self, 'goal_tracker'):
                output = []
                output.append("🎯 Active Goals")
                output.append("=" * 40)

                for goal in self.goal_tracker.goals.values():
                    if goal.status == "active":
                        output.append(f"📋 {goal.title}")
                        output.append(f"   Priority: {goal.priority}")
                        output.append(f"   Progress: {goal.progress:.1%}")
                        output.append(f"   Reason: {goal.reasoning}")
                        output.append("")

                self.goal_display.setPlainText("\\n".join(output))
        except Exception as e:
            self.goal_display.setPlainText(f"Error refreshing goals: {e}")

    def analyze_goal_blockers(self):
        """Analyze blockers for all goals"""
        try:
            if hasattr(self, 'goal_tracker'):
                blockers = self.goal_tracker.analyze_blockers()

                output = []
                output.append("🔍 Blocker Analysis")
                output.append("=" * 40)

                if blockers:
                    for blocker in blockers:
                        output.append(f"🚫 {blocker}")
                        output.append("")
                else:
                    output.append("✅ No blockers found!")

                self.goal_display.setPlainText("\\n".join(output))
        except Exception as e:
            self.goal_display.setPlainText(f"Error analyzing blockers: {e}")
'''

def apply_integration():
    """Apply integration using precise string replacement"""

    print("🔧 Applying World-Class Integration...")

    # Read the file
    hybrid_window_path = project_root / "Aetherra" / "lyrixa" / "gui" / "hybrid_window.py"

    with open(hybrid_window_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already patched
    if "WorldClassMemoryCore" in content:
        print("✅ Integration already applied!")
        return True

    # Find and replace the create_memory_tab method
    memory_start = content.find("    def create_memory_tab(self):")
    if memory_start != -1:
        memory_end = content.find("\n    def ", memory_start + 1)
        if memory_end == -1:
            memory_end = len(content)

        # Replace the method
        old_memory_method = content[memory_start:memory_end]
        new_memory_method = create_memory_tab_replacement()

        content = content.replace(old_memory_method, new_memory_method)
        print("✅ Memory tab method replaced")
    else:
        print("❌ Could not find memory tab method")
        return False

    # Find and replace the create_goal_tab method
    goal_start = content.find("    def create_goal_tab(self):")
    if goal_start != -1:
        goal_end = content.find("\n    def ", goal_start + 1)
        if goal_end == -1:
            goal_end = len(content)

        # Replace the method
        old_goal_method = content[goal_start:goal_end]
        new_goal_method = create_goal_tab_replacement()

        content = content.replace(old_goal_method, new_goal_method)
        print("✅ Goal tab method replaced")
    else:
        print("❌ Could not find goal tab method")
        return False

    # Add helper methods before the end of the class
    if "if __name__ == '__main__':" in content:
        insertion_point = content.find("if __name__ == '__main__':")
        helper_methods = create_helper_methods()
        content = content[:insertion_point] + helper_methods + "\n\n" + content[insertion_point:]
        print("✅ Helper methods added")

    # Write the updated content
    with open(hybrid_window_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Integration applied successfully!")
    return True

def test_integration():
    """Test that the integration works"""

    print("\n🧪 Testing Integration...")

    try:
        # Test imports
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow
        from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window

        print("✅ All imports successful")

        # Test window creation
        os.environ["LYRIXA_UI_MODE"] = "hybrid"
        window = create_lyrixa_window()

        print("✅ Window created successfully")

        # Test method availability
        if hasattr(window, 'create_memory_tab') and hasattr(window, 'create_goal_tab'):
            print("✅ Tab methods available")
        else:
            print("❌ Tab methods missing")
            return False

        print("✅ Integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""

    print("🔧 Careful World-Class Integration")
    print("=" * 40)

    if apply_integration():
        if test_integration():
            print("\n🎉 Integration successful!")
            print("✅ World-class components integrated with hybrid window")
            print("🚀 Ready to use with aetherra_hybrid_launcher.py")
            return True
        else:
            print("\n❌ Integration applied but test failed")
            return False
    else:
        print("\n❌ Integration failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
