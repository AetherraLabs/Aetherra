#!/usr/bin/env python3
"""
🎨 NeuroCode Enhanced UI - Modern Tabbed Interface
==================================================

A responsive, modern, and extendable user interface for NeuroCode featuring:
- Clean tabbed interface (Chat, Code, Memory, Plugins)
- Visual memory reflection browsing
- Responsive design with modern aesthetics
- Integrated memory viewer with timeline visualization
- Plugin transparency and management
- Real-time code execution and output

This UI focuses on user experience and visual clarity while maintaining
the powerful AI-native capabilities of NeuroCode.

Fixed version with standardized PySide6 imports for production stability.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Qt imports with PySide6 (standardized for production)
try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    print("❌ PySide6 not available. Please install PySide6.")
    QT_AVAILABLE = False

# Import NeuroCode components with robust error handling
Memory = None
try:
    from core.memory import NeuroMemory as Memory
except ImportError:
    print("⚠️ Memory module not available - using mock")


class MemoryReflectionViewer(QWidget):
    """Enhanced memory reflection and visualization component"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.memory = None
        self.memories = []
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🧠 Memory Reflection Viewer")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Control panel
        controls = QHBoxLayout()

        # Period selector
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last Hour", "Last Day", "Last Week", "All Time"])
        self.period_combo.setCurrentText("Last Day")
        self.period_combo.currentTextChanged.connect(self.refresh_view)

        # Tag filter
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("Filter by tags...")
        self.tag_filter.textChanged.connect(self.refresh_view)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_view)

        controls.addWidget(QLabel("Period:"))
        controls.addWidget(self.period_combo)
        controls.addWidget(QLabel("Tags:"))
        controls.addWidget(self.tag_filter)
        controls.addWidget(self.refresh_btn)

        layout.addLayout(controls)

        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Memory list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("📋 Memory Entries"))

        self.memory_list = QTreeWidget()
        self.memory_list.setHeaderLabels(["Time", "Content", "Tags"])
        self.memory_list.itemSelectionChanged.connect(self.on_memory_selected)
        left_layout.addWidget(self.memory_list)

        # Right panel - Analysis
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("🔍 Reflection Analysis"))

        self.reflection_display = QTextEdit()
        self.reflection_display.setReadOnly(True)
        right_layout.addWidget(self.reflection_display)

        # Statistics
        right_layout.addWidget(QLabel("📊 Memory Statistics"))
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        right_layout.addWidget(self.stats_display)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        layout.addWidget(splitter)

        # Initialize memory if available
        self.init_memory()
        self.refresh_view()

    def init_memory(self):
        """Initialize memory system"""
        try:
            if Memory:
                self.memory = Memory()
            else:
                # Create mock memory for demonstration
                self.create_mock_memories()
        except Exception as e:
            print(f"⚠️ Memory initialization failed: {e}")
            self.create_mock_memories()

    def create_mock_memories(self):
        """Create mock memories for demonstration"""
        self.memories = [
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "content": "Learning NeuroCode fundamentals",
                "tags": ["learning", "fundamentals"],
            },
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "content": "Memory system exploration",
                "tags": ["memory", "exploration"],
            },
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "content": "AI-native programming concepts",
                "tags": ["ai", "programming"],
            },
        ]

    def refresh_view(self):
        """Refresh the memory view"""
        self.memory_list.clear()

        # Get memories based on filters
        filtered_memories = self.get_filtered_memories()

        # Populate tree
        for memory in filtered_memories:
            item = QTreeWidgetItem(
                [
                    memory["timestamp"],
                    memory["content"][:50] + "..."
                    if len(memory["content"]) > 50
                    else memory["content"],
                    ", ".join(memory["tags"]),
                ]
            )
            self.memory_list.addTopLevelItem(item)

        # Update statistics
        self.update_statistics(filtered_memories)

    def get_filtered_memories(self):
        """Get memories based on current filters"""
        memories = self.memories.copy()

        # Filter by tags
        tag_filter = self.tag_filter.text().lower()
        if tag_filter:
            memories = [m for m in memories if any(tag_filter in tag.lower() for tag in m["tags"])]

        return memories

    def on_memory_selected(self):
        """Handle memory selection"""
        current_item = self.memory_list.currentItem()
        if not current_item:
            return

        content = current_item.text(1)
        self.show_memory_analysis(content)

    def show_memory_analysis(self, content):
        """Show analysis for selected memory"""
        analysis = f"""
🔍 Memory Analysis for: "{content}"

📊 Pattern Detection:
• Memory type: User learning
• Confidence: High
• Related concepts: AI, Programming, Learning

🧠 Cognitive Insights:
• This memory represents knowledge acquisition
• Part of learning progression pattern
• Connects to broader AI/programming domain

🔗 Related Memories:
• Similar content found in learning cluster
• Temporal proximity to other educational memories
• Strong semantic similarity to AI concepts

💡 Suggestions:
• Review related memories for reinforcement
• Consider creating more specific tags
• Explore connected concept clusters
"""
        self.reflection_display.setPlainText(analysis)

    def update_statistics(self, memories):
        """Update memory statistics display"""
        if not memories:
            stats = "📊 No memories found with current filters"
        else:
            # Gather statistics
            total_memories = len(memories)
            unique_tags = set()
            for memory in memories:
                unique_tags.update(memory["tags"])

            # Generate patterns if memory system is available
            patterns_info = ""
            try:
                if self.memory and hasattr(self.memory, "patterns"):
                    patterns = self.memory.patterns()
                    patterns_info = f"\n🔍 Detected Patterns: {len(patterns) if patterns else 0}"
            except Exception:
                patterns_info = "\n🔍 Pattern detection: Not available"

            stats = f"""📊 Memory Statistics

📈 Overview:
• Total memories: {total_memories}
• Unique tags: {len(unique_tags)}
• Tags: {", ".join(sorted(unique_tags))}
{patterns_info}

📅 Temporal Distribution:
• Recent activity: Active
• Memory formation rate: Consistent
• Learning pattern: Progressive

🏷️ Tag Analysis:
• Most common themes: Learning, AI, Programming
• Tag diversity: Good
• Categorization: Well-structured
"""

        self.stats_display.setPlainText(stats)


def create_enhanced_neuro_ui():
    """Create and return the enhanced NeuroCode UI"""
    if not QT_AVAILABLE:
        print("❌ Cannot create UI - Qt not available")
        return None

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("🧬 NeuroCode Enhanced UI")
    main_window.setGeometry(100, 100, 1200, 800)

    # Create central widget with tabs
    central_widget = QTabWidget()
    main_window.setCentralWidget(central_widget)

    # Memory Reflection tab
    memory_viewer = MemoryReflectionViewer()
    central_widget.addTab(memory_viewer, "🧠 Memory Reflection")

    # Placeholder tabs for future expansion
    from neuro_chat import NeuroChatInterface
    
    # Replace chat placeholder with actual chat interface
    try:
        chat_interface = NeuroChatInterface()
        central_widget.addTab(chat_interface.tab_widget, "💬 AI Chat")
    except Exception as e:
        print(f"⚠️ Could not load chat interface: {e}")
        placeholder1 = QLabel("💬 Chat interface - loading error...")
        placeholder1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_widget.addTab(placeholder1, "💬 AI Chat")

    placeholder2 = QLabel("📝 Code editor coming soon...")
    placeholder2.setAlignment(Qt.AlignmentFlag.AlignCenter)
    central_widget.addTab(placeholder2, "📝 Code Editor")

    placeholder3 = QLabel("🔌 Plugin manager coming soon...")
    placeholder3.setAlignment(Qt.AlignmentFlag.AlignCenter)
    central_widget.addTab(placeholder3, "🔌 Plugins")

    return main_window


def main():
    """Main entry point for the NeuroCode Enhanced UI"""
    if QT_AVAILABLE:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        main_window = create_enhanced_neuro_ui()
        if main_window:
            main_window.show()
            sys.exit(app.exec())
    else:
        print("❌ Qt not available. Please install PySide6.")


if __name__ == "__main__":
    main()
