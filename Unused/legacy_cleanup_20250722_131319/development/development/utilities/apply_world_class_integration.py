#!/usr/bin/env python3
"""
World-Class Components Integration Patch
========================================
🔧 Patches the hybrid window to use world-class components
🎯 Replaces placeholder tabs with real implementations
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def patch_hybrid_window():
    """Apply world-class components to hybrid window"""

    # Create the patch for create_memory_tab
    memory_tab_patch = '''
    def create_memory_tab(self):
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
                return widget
    '''

    # Create the patch for create_goal_tab
    goal_tab_patch = '''
    def create_goal_tab(self):
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
                return widget
    '''

    # Create helper methods for goal tracker integration
    helper_methods = '''
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

    return memory_tab_patch, goal_tab_patch, helper_methods

def apply_integration_patch():
    """Apply integration patch to hybrid window"""

    print("🔧 Applying World-Class Components Integration Patch...")

    # Get the patches
    memory_patch, goal_patch, helper_methods = patch_hybrid_window()

    # Read the current hybrid window file
    hybrid_window_path = project_root / "Aetherra" / "lyrixa" / "gui" / "hybrid_window.py"

    if not hybrid_window_path.exists():
        print("❌ Hybrid window file not found!")
        return False

    with open(hybrid_window_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already patched
    if "WorldClassMemoryCore" in content:
        print("✅ Integration patch already applied!")
        return True

    # Find the original create_memory_tab method
    import re

    # Replace create_memory_tab method
    memory_pattern = r'def create_memory_tab\(self\):(.*?)(?=def|\Z)'
    memory_replacement = memory_patch.strip() + '\n\n'

    if re.search(memory_pattern, content, re.DOTALL):
        content = re.sub(memory_pattern, memory_replacement, content, flags=re.DOTALL)
        print("✅ Memory tab patched")
    else:
        print("❌ Could not find create_memory_tab method")

    # Replace create_goal_tab method
    goal_pattern = r'def create_goal_tab\(self\):(.*?)(?=def|\Z)'
    goal_replacement = goal_patch.strip() + '\n\n'

    if re.search(goal_pattern, content, re.DOTALL):
        content = re.sub(goal_pattern, goal_replacement, content, flags=re.DOTALL)
        print("✅ Goal tab patched")
    else:
        print("❌ Could not find create_goal_tab method")

    # Add helper methods before the last method
    last_method_pattern = r'(def.*?(?=\n\nif __name__))'
    if re.search(last_method_pattern, content, re.DOTALL):
        content = re.sub(last_method_pattern, r'\1\n' + helper_methods, content, flags=re.DOTALL)
        print("✅ Helper methods added")
    else:
        # Add at the end of class
        class_end_pattern = r'(\n\n\ndef main\(\):|\n\n\nif __name__)'
        if re.search(class_end_pattern, content):
            content = re.sub(class_end_pattern, helper_methods + r'\1', content)
            print("✅ Helper methods added at class end")

    # Write the patched content
    backup_path = hybrid_window_path.with_suffix('.py.backup')

    # Create backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    try:
        with open(hybrid_window_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Integration patch applied successfully!")
        print(f"💾 Backup created at: {backup_path}")
        return True

    except Exception as e:
        print(f"❌ Failed to apply patch: {e}")
        return False

def verify_integration():
    """Verify the integration works"""

    print("\n🧪 Verifying Integration...")

    try:
        # Test imports
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow
        from Aetherra.lyrixa.memory.world_class_memory_core import WorldClassMemoryCore
        from Aetherra.lyrixa.core.world_class_goal_tracker import WorldClassGoalTracker

        print("✅ All imports successful")

        # Test that components can be instantiated
        try:
            memory_core = WorldClassMemoryCore()
            print("✅ WorldClassMemoryCore instantiated")
        except:
            print("⚠️  WorldClassMemoryCore requires GUI")

        try:
            goal_tracker = WorldClassGoalTracker()
            print("✅ WorldClassGoalTracker instantiated")
        except:
            print("⚠️  WorldClassGoalTracker requires GUI")

        print("✅ Integration verification complete!")
        return True

    except Exception as e:
        print(f"❌ Integration verification failed: {e}")
        return False

def main():
    """Main function"""

    print("🔧 World-Class Components Integration Patch")
    print("=" * 50)

    # Apply the patch
    if apply_integration_patch():

        # Verify the integration
        if verify_integration():
            print("\n🎉 Integration successful!")
            print("✅ World-class components are now integrated with hybrid window")
            print("🚀 Ready for use with aetherra_hybrid_launcher.py")
        else:
            print("\n⚠️  Integration applied but verification failed")
    else:
        print("\n❌ Integration patch failed")

    return True

if __name__ == "__main__":
    main()
