#!/usr/bin/env python3
"""
🧠 MINIMAL LYRIXA GUI
====================

Minimal GUI to test basic Lyrixa functionality without complex components.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🚀 Starting minimal Lyrixa GUI...")

# Test basic imports first
try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    print("✅ PySide6 imports successful")
except ImportError as e:
    print(f"❌ PySide6 error: {e}")
    sys.exit(1)


class MinimalLyrixaGUI(QMainWindow):
    """Minimal GUI for testing."""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("🧠 Lyrixa AI Assistant - Minimal Test")
        self.setGeometry(300, 300, 600, 400)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout
        layout = QVBoxLayout(main_widget)

        # Title
        title = QLabel("🧠 Lyrixa AI Assistant")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Status
        self.status_label = QLabel("[TOOL] Starting up...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Test buttons
        self.test1_button = QPushButton("🧪 Test Basic Import")
        self.test1_button.clicked.connect(self.test_basic_import)
        layout.addWidget(self.test1_button)

        self.test2_button = QPushButton("🧠 Test Memory (Safe)")
        self.test2_button.clicked.connect(self.test_memory_safe)
        layout.addWidget(self.test2_button)

        self.test3_button = QPushButton("💬 Test Conversation (Safe)")
        self.test3_button.clicked.connect(self.test_conversation_safe)
        layout.addWidget(self.test3_button)

        # Knowledge test
        self.test_knowledge_button = QPushButton("🧠 Test Knowledge Responder")
        self.test_knowledge_button.clicked.connect(self.test_knowledge_responder)
        layout.addWidget(self.test_knowledge_button)

        # Results area
        self.results_label = QLabel("Click buttons to test functionality")
        self.results_label.setAlignment(Qt.AlignCenter)
        self.results_label.setStyleSheet(
            "padding: 20px; background-color: #f0f0f0; border-radius: 5px;"
        )
        layout.addWidget(self.results_label)

    def setup_timer(self):
        """Set up a timer to update status."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ready_status)
        self.timer.setSingleShot(True)
        self.timer.start(1000)  # 1 second delay

    def update_ready_status(self):
        """Update status to ready."""
        self.status_label.setText("🟢 Ready for testing")

    def update_results(self, message):
        """Update the results label."""
        self.results_label.setText(message)

    def test_basic_import(self):
        """Test basic imports."""
        try:
            self.update_results("🧪 Testing basic imports...")

            # Test core imports
            import asyncio
            import json
            from pathlib import Path

            self.update_results("✅ Basic imports successful!")

        except Exception as e:
            self.update_results(f"❌ Basic import test failed: {e}")

    def test_memory_safe(self):
        """Test memory system safely."""
        try:
            self.update_results("🧠 Testing memory system (safe mode)...")

            # Try to import without initializing
            from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem

            self.update_results("✅ Memory system import successful!")

        except Exception as e:
            self.update_results(f"❌ Memory system test failed: {e}")

    def test_conversation_safe(self):
        """Test conversation engine safely."""
        try:
            self.update_results("💬 Testing conversation engine (safe mode)...")

            # Try to import without initializing
            from lyrixa.core.conversation import LyrixaConversationalEngine

            self.update_results("✅ Conversation engine import successful!")

        except Exception as e:
            self.update_results(f"❌ Conversation engine test failed: {e}")

    def test_knowledge_responder(self):
        """Test knowledge responder."""
        try:
            self.update_results("🧠 Testing knowledge responder...")

            # Import and test basic functionality
            from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
            from lyrixa.core.project_knowledge_responder import (
                ProjectKnowledgeResponder,
            )

            # Create memory system (this might take a moment)
            self.update_results("🔄 Initializing memory system...")
            memory = AdvancedMemorySystem()

            # Create knowledge responder
            responder = ProjectKnowledgeResponder(memory)

            # Test query detection
            test_query = "What is Aetherra?"
            is_factual = responder.is_factual_or_project_query(test_query)

            self.update_results(
                f"✅ Knowledge responder working! Query '{test_query}' detected as factual: {is_factual}"
            )

        except Exception as e:
            self.update_results(f"❌ Knowledge responder test failed: {e}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Create and show the GUI
    gui = MinimalLyrixaGUI()
    gui.show()

    print("👆 Minimal GUI window opened")
    print("🧪 Use the test buttons to check Lyrixa functionality")

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
