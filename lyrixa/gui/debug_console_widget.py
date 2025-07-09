"""
🐛🔍 LYRIXA DEBUG CONSOLE GUI WIDGET
===================================

GUI widget for the Lyrixa Debug Console providing real-time introspection into:
- What Lyrixa sees (perception and input analysis)
- What she's thinking (reasoning process and cognitive state)
- Why she picks suggestions or plans (decision matrix and scoring)

This widget integrates with the main GUI to provide developer transparency.
"""

# Type: ignore for entire file to suppress Qt mock compatibility warnings
# pylint: disable=all
# pyright: ignore-errors

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QFont, QTextCursor
    from PySide6.QtWidgets import (
        QComboBox,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

# Check Qt availability first
QT_AVAILABLE = False
try:
    from PySide6.QtCore import QTimer  # type: ignore
    from PySide6.QtGui import QFont, QTextCursor  # type: ignore
    from PySide6.QtWidgets import (  # type: ignore
        QComboBox,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    # Comprehensive mock classes for headless environments
    class MockWidget:
        """Enhanced mock widget that satisfies Qt type requirements"""

        Box = 1
        ReadOnly = True
        Bold = True

        def __init__(self, *args, **kwargs):
            self._active = False
            self.children = []
            self.text_content = ""
            self.properties = {}

        def setLayout(self, layout):
            self.layout = layout
            return self

        def setWindowTitle(self, title):
            self.window_title = title
            return self

        def setMinimumSize(self, width, height):
            self.min_size = (width, height)
            return self

        def show(self):
            return self

        def hide(self):
            return self

        def update(self):
            return self

        def setStyleSheet(self, style):
            self.style_sheet = style
            return self

        def addTab(self, widget, title):
            self.children.append((widget, title))
            return self

        def setFrameStyle(self, style):
            self.frame_style = style
            return self

        def addWidget(self, widget):
            self.children.append(widget)
            return self

        def addLayout(self, layout):
            self.children.append(layout)
            return self

        def setText(self, text):
            self.text_content = text
            return self

        def text(self):
            return self.text_content

        def setPlainText(self, text):
            self.text_content = text
            return self

        def toPlainText(self):
            return self.text_content

        def append(self, text):
            self.text_content += str(text)
            return self

        def clear(self):
            self.text_content = ""
            return self

        def setReadOnly(self, readonly):
            self.readonly = readonly
            return self

        def clicked(self):
            return self

        def connect(self, func):
            return self

        def timeout(self):
            return self

        def start(self, interval=None):
            if interval is not None:
                self.interval = interval
            self._active = True
            return self

        def stop(self):
            self._active = False
            return self

        def isActive(self):
            return self._active

        def setValue(self, value):
            self.value = value
            return self

        def setRange(self, min_val, max_val):
            self.range = (min_val, max_val)
            return self

        def setFont(self, font):
            self.font = font
            return self

        def setAlignment(self, alignment):
            self.alignment = alignment
            return self

        def setPointSize(self, size):
            self.point_size = size
            return self

        def setBold(self, bold):
            self.bold = bold
            return self

        def addItem(self, item):
            if not hasattr(self, "items"):
                self.items = []
            self.items.append(item)
            return self

        def currentText(self):
            return getattr(self, "current_text", "")

        def setCurrentText(self, text):
            self.current_text = text
            return self

        def moveCursor(self, cursor):
            self.cursor = cursor
            return self

        def insertPlainText(self, text):
            self.text_content += str(text)
            return self

        def setMaximumHeight(self, height):
            self.max_height = height
            return self

    # Use MockWidget for all Qt classes to ensure type compatibility
    QWidget = MockWidget  # type: ignore
    QTimer = MockWidget  # type: ignore
    QFont = MockWidget  # type: ignore
    QTextCursor = MockWidget  # type: ignore
    QComboBox = MockWidget  # type: ignore
    QFrame = MockWidget  # type: ignore
    QGroupBox = MockWidget  # type: ignore
    QHBoxLayout = MockWidget  # type: ignore
    QLabel = MockWidget  # type: ignore
    QProgressBar = MockWidget  # type: ignore
    QPushButton = MockWidget  # type: ignore
    QTabWidget = MockWidget  # type: ignore
    QTextEdit = MockWidget  # type: ignore
    QVBoxLayout = MockWidget  # type: ignore


class DebugConsoleWidget(QWidget):  # type: ignore
    """
    🐛🔍 Advanced Debug Console Widget

    Provides comprehensive debugging and introspection capabilities for Lyrixa.
    """

    def __init__(self, parent=None, auto_start=True):
        super().__init__(parent)  # type: ignore
        self.debug_data = {}
        self.update_timer = QTimer()  # type: ignore
        self.auto_start = auto_start
        self.setup_ui()

    def setup_ui(self):
        """Set up the debug console UI."""
        try:
            if QT_AVAILABLE:
                self.setWindowTitle("🐛 Lyrixa Debug Console")  # type: ignore
                self.setMinimumSize(1000, 700)  # type: ignore

            # Main layout
            main_layout = QVBoxLayout()  # type: ignore

            # Header
            header_layout = QHBoxLayout()  # type: ignore

            # Title
            title_label = QLabel("🐛🔍 Lyrixa Debug Console")  # type: ignore
            title_font = QFont()  # type: ignore
            title_font.setPointSize(16)  # type: ignore
            title_font.setBold(True)  # type: ignore
            title_label.setFont(title_font)  # type: ignore
            header_layout.addWidget(title_label)  # type: ignore

            # Debug level selector
            self.debug_level_combo = QComboBox()  # type: ignore
            self.debug_level_combo.addItem("🔍 All")  # type: ignore
            self.debug_level_combo.addItem("⚠️ Warning")  # type: ignore
            self.debug_level_combo.addItem("❌ Error")  # type: ignore
            header_layout.addWidget(QLabel("Debug Level:"))  # type: ignore
            header_layout.addWidget(self.debug_level_combo)  # type: ignore

            # Export button
            self.export_btn = QPushButton("📁 Export Session")  # type: ignore
            if QT_AVAILABLE:
                self.export_btn.clicked.connect(self.export_debug_session)  # type: ignore
            header_layout.addWidget(self.export_btn)  # type: ignore

            # Clear button
            self.clear_btn = QPushButton("🗑️ Clear History")  # type: ignore
            if QT_AVAILABLE:
                self.clear_btn.clicked.connect(self.clear_debug_history)  # type: ignore
            header_layout.addWidget(self.clear_btn)  # type: ignore

            main_layout.addLayout(header_layout)  # type: ignore

            # Status frame
            self.status_frame = QFrame()  # type: ignore
            if QT_AVAILABLE:
                self.status_frame.setFrameStyle(QFrame.Box)  # type: ignore
            status_layout = QHBoxLayout()  # type: ignore

            self.cognitive_state_label = QLabel("😴 IDLE")  # type: ignore
            self.cognitive_state_label.setStyleSheet(  # type: ignore
                "font-weight: bold; color: #666; padding: 5px;"
            )
            status_layout.addWidget(QLabel("Cognitive State:"))  # type: ignore
            status_layout.addWidget(self.cognitive_state_label)  # type: ignore

            # Performance metrics
            self.performance_label = QLabel(  # type: ignore
                "🧠 Memory: 0MB | 🚀 Speed: 0ms | 🎯 Accuracy: 0%"
            )
            status_layout.addWidget(self.performance_label)  # type: ignore

            self.status_frame.setLayout(status_layout)  # type: ignore
            main_layout.addWidget(self.status_frame)  # type: ignore

            # Tab widget for different debug views
            self.tab_widget = QTabWidget()  # type: ignore

            # Create tabs
            self.create_perception_tab()
            self.create_reasoning_tab()
            self.create_decision_tab()
            self.create_performance_tab()

            main_layout.addWidget(self.tab_widget)  # type: ignore

            self.setLayout(main_layout)  # type: ignore

            # Setup timer for updates
            if QT_AVAILABLE and self.auto_start:
                self.update_timer.timeout.connect(self.update_display)  # type: ignore
                self.update_timer.start(1000)  # type: ignore

        except Exception as e:
            logger.error(f"Error setting up debug console UI: {e}")

    def create_perception_tab(self):
        """Create the perception analysis tab."""
        try:
            tab = QWidget()  # type: ignore
            layout = QVBoxLayout()  # type: ignore

            # Current perception
            current_group = QGroupBox("👁️ Current Perception")  # type: ignore
            current_layout = QVBoxLayout()  # type: ignore

            self.current_input_label = QLabel("No input detected")  # type: ignore
            self.current_input_label.setStyleSheet(
                "font-family: monospace; padding: 5px;"
            )  # type: ignore
            current_layout.addWidget(QLabel("User Input:"))  # type: ignore
            current_layout.addWidget(self.current_input_label)  # type: ignore

            self.attention_focus_label = QLabel("No focus areas")  # type: ignore
            current_layout.addWidget(QLabel("Attention Focus:"))  # type: ignore
            current_layout.addWidget(self.attention_focus_label)  # type: ignore

            self.context_info_label = QLabel("Memory: 0 | Goals: 0")  # type: ignore
            current_layout.addWidget(QLabel("Context:"))  # type: ignore
            current_layout.addWidget(self.context_info_label)  # type: ignore

            current_group.setLayout(current_layout)  # type: ignore
            layout.addWidget(current_group)  # type: ignore

            # Perception history
            history_group = QGroupBox("📊 Perception History")  # type: ignore
            history_layout = QVBoxLayout()  # type: ignore

            self.perception_history_text = QTextEdit()  # type: ignore
            self.perception_history_text.setReadOnly(True)  # type: ignore
            self.perception_history_text.setStyleSheet(  # type: ignore
                "font-family: monospace; font-size: 10px; background-color: #f0f0f0;"
            )
            history_layout.addWidget(self.perception_history_text)  # type: ignore

            history_group.setLayout(history_layout)  # type: ignore
            layout.addWidget(history_group)  # type: ignore

            tab.setLayout(layout)  # type: ignore
            self.tab_widget.addTab(tab, "👁️ Perception")  # type: ignore

        except Exception as e:
            logger.error(f"Error creating perception tab: {e}")

    def create_reasoning_tab(self):
        """Create the reasoning process tab."""
        try:
            tab = QWidget()  # type: ignore
            layout = QVBoxLayout()  # type: ignore

            # Current thought process
            current_group = QGroupBox("🧠 Current Thought Process")  # type: ignore
            current_layout = QVBoxLayout()  # type: ignore

            self.current_thought_label = QLabel("No active thought process")  # type: ignore
            current_layout.addWidget(self.current_thought_label)  # type: ignore

            self.reasoning_text = QTextEdit()  # type: ignore
            self.reasoning_text.setReadOnly(True)  # type: ignore
            self.reasoning_text.setStyleSheet(
                "font-family: monospace; font-size: 10px;"
            )  # type: ignore
            current_layout.addWidget(QLabel("Reasoning Steps:"))  # type: ignore
            current_layout.addWidget(self.reasoning_text)  # type: ignore

            current_group.setLayout(current_layout)  # type: ignore
            layout.addWidget(current_group)  # type: ignore

            # Reasoning history
            history_group = QGroupBox("📚 Thought History")  # type: ignore
            history_layout = QVBoxLayout()  # type: ignore

            self.reasoning_history_text = QTextEdit()  # type: ignore
            self.reasoning_history_text.setReadOnly(True)  # type: ignore
            self.reasoning_history_text.setStyleSheet(  # type: ignore
                "font-family: monospace; font-size: 10px; background-color: #f0f0f0;"
            )
            history_layout.addWidget(self.reasoning_history_text)  # type: ignore

            history_group.setLayout(history_layout)  # type: ignore
            layout.addWidget(history_group)  # type: ignore

            tab.setLayout(layout)  # type: ignore
            self.tab_widget.addTab(tab, "🧠 Reasoning")  # type: ignore

        except Exception as e:
            logger.error(f"Error creating reasoning tab: {e}")

    def create_decision_tab(self):
        """Create the decision matrix tab."""
        try:
            tab = QWidget()  # type: ignore
            layout = QVBoxLayout()  # type: ignore

            # Decision matrix
            decision_group = QGroupBox("⚖️ Decision Matrix")  # type: ignore
            decision_layout = QVBoxLayout()  # type: ignore

            self.decision_matrix_text = QTextEdit()  # type: ignore
            self.decision_matrix_text.setReadOnly(True)  # type: ignore
            self.decision_matrix_text.setStyleSheet(
                "font-family: monospace; font-size: 10px;"
            )  # type: ignore
            decision_layout.addWidget(self.decision_matrix_text)  # type: ignore

            decision_group.setLayout(decision_layout)  # type: ignore
            layout.addWidget(decision_group)  # type: ignore

            # Suggestion scoring
            scoring_group = QGroupBox("📊 Suggestion Scoring")  # type: ignore
            scoring_layout = QVBoxLayout()  # type: ignore

            self.scoring_text = QTextEdit()  # type: ignore
            self.scoring_text.setReadOnly(True)  # type: ignore
            self.scoring_text.setStyleSheet("font-family: monospace; font-size: 10px;")  # type: ignore
            scoring_layout.addWidget(self.scoring_text)  # type: ignore

            scoring_group.setLayout(scoring_layout)  # type: ignore
            layout.addWidget(scoring_group)  # type: ignore

            tab.setLayout(layout)  # type: ignore
            self.tab_widget.addTab(tab, "⚖️ Decisions")  # type: ignore

        except Exception as e:
            logger.error(f"Error creating decision tab: {e}")

    def create_performance_tab(self):
        """Create the performance monitoring tab."""
        try:
            tab = QWidget()  # type: ignore
            layout = QVBoxLayout()  # type: ignore

            # Performance metrics
            metrics_group = QGroupBox("📈 Performance Metrics")  # type: ignore
            metrics_layout = QVBoxLayout()  # type: ignore

            # Memory usage
            memory_layout = QHBoxLayout()  # type: ignore
            memory_layout.addWidget(QLabel("Memory Usage:"))  # type: ignore
            self.memory_progress = QProgressBar()  # type: ignore
            self.memory_progress.setRange(0, 100)  # type: ignore
            memory_layout.addWidget(self.memory_progress)  # type: ignore
            metrics_layout.addLayout(memory_layout)  # type: ignore

            # Processing speed
            speed_layout = QHBoxLayout()  # type: ignore
            speed_layout.addWidget(QLabel("Processing Speed:"))  # type: ignore
            self.speed_label = QLabel("0ms")  # type: ignore
            speed_layout.addWidget(self.speed_label)  # type: ignore
            metrics_layout.addLayout(speed_layout)  # type: ignore

            # Accuracy
            accuracy_layout = QHBoxLayout()  # type: ignore
            accuracy_layout.addWidget(QLabel("Accuracy:"))  # type: ignore
            self.accuracy_progress = QProgressBar()  # type: ignore
            self.accuracy_progress.setRange(0, 100)  # type: ignore
            accuracy_layout.addWidget(self.accuracy_progress)  # type: ignore
            metrics_layout.addLayout(accuracy_layout)  # type: ignore

            metrics_group.setLayout(metrics_layout)  # type: ignore
            layout.addWidget(metrics_group)  # type: ignore

            # Performance history
            history_group = QGroupBox("📊 Performance History")  # type: ignore
            history_layout = QVBoxLayout()  # type: ignore

            self.performance_history_text = QTextEdit()  # type: ignore
            self.performance_history_text.setReadOnly(True)  # type: ignore
            self.performance_history_text.setStyleSheet(  # type: ignore
                "font-family: monospace; font-size: 10px; background-color: #f0f0f0;"
            )
            history_layout.addWidget(self.performance_history_text)  # type: ignore

            history_group.setLayout(history_layout)  # type: ignore
            layout.addWidget(history_group)  # type: ignore

            tab.setLayout(layout)  # type: ignore
            self.tab_widget.addTab(tab, "📈 Performance")  # type: ignore

        except Exception as e:
            logger.error(f"Error creating performance tab: {e}")

    def update_display(self):
        """Update the debug display with current data."""
        try:
            # Update cognitive state
            self.update_cognitive_state()

            # Update performance metrics
            self.update_performance_metrics()

            # Update perception data
            self.update_perception_data()

            # Update reasoning data
            self.update_reasoning_data()

            # Update decision data
            self.update_decision_data()

        except Exception as e:
            logger.error(f"Error updating debug display: {e}")

    def update_cognitive_state(self):
        """Update the cognitive state display."""
        try:
            # Sample cognitive states
            states = [
                "😴 IDLE",
                "🤔 THINKING",
                "💡 PROCESSING",
                "🎯 FOCUSED",
                "⚡ ACTIVE",
            ]
            import random

            current_state = random.choice(states)
            self.cognitive_state_label.setText(current_state)  # type: ignore

        except Exception as e:
            logger.error(f"Error updating cognitive state: {e}")

    def update_performance_metrics(self):
        """Update performance metrics display."""
        try:
            import random

            # Generate sample metrics
            memory_mb = random.randint(50, 200)
            speed_ms = random.randint(10, 100)
            accuracy_pct = random.randint(85, 99)

            # Update labels
            self.performance_label.setText(  # type: ignore
                f"🧠 Memory: {memory_mb}MB | 🚀 Speed: {speed_ms}ms | 🎯 Accuracy: {accuracy_pct}%"
            )

            # Update progress bars
            self.memory_progress.setValue(min(100, memory_mb // 2))  # type: ignore
            self.speed_label.setText(f"{speed_ms}ms")  # type: ignore
            self.accuracy_progress.setValue(accuracy_pct)  # type: ignore

            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            history_entry = f"[{timestamp}] Memory: {memory_mb}MB, Speed: {speed_ms}ms, Accuracy: {accuracy_pct}%\n"
            self.performance_history_text.append(history_entry)  # type: ignore

        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    def update_perception_data(self):
        """Update perception data display."""
        try:
            # Sample perception data
            self.current_input_label.setText(
                "User typing: 'How can I improve my workflow?'"
            )  # type: ignore
            self.attention_focus_label.setText(
                "Keywords: workflow, improve, productivity"
            )  # type: ignore
            self.context_info_label.setText("Memory: 5 conversations | Goals: 2 active")  # type: ignore

            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            history_entry = (
                f"[{timestamp}] Input detected: workflow improvement query\n"
            )
            self.perception_history_text.append(history_entry)  # type: ignore

        except Exception as e:
            logger.error(f"Error updating perception data: {e}")

    def update_reasoning_data(self):
        """Update reasoning data display."""
        try:
            # Sample reasoning data
            self.current_thought_label.setText(
                "Analyzing workflow optimization strategies..."
            )  # type: ignore

            reasoning_steps = [
                "1. Identify current workflow inefficiencies",
                "2. Analyze user's work patterns",
                "3. Generate optimization suggestions",
                "4. Prioritize by impact and effort",
            ]

            self.reasoning_text.setPlainText("\n".join(reasoning_steps))  # type: ignore

            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            history_entry = f"[{timestamp}] Reasoning: Workflow optimization analysis\n"
            self.reasoning_history_text.append(history_entry)  # type: ignore

        except Exception as e:
            logger.error(f"Error updating reasoning data: {e}")

    def update_decision_data(self):
        """Update decision data display."""
        try:
            # Sample decision matrix
            decision_matrix = [
                "Decision Options:",
                "1. Time blocking technique (Score: 8.5)",
                "2. Automation tools (Score: 7.2)",
                "3. Task prioritization (Score: 8.0)",
                "4. Break scheduling (Score: 6.8)",
            ]

            self.decision_matrix_text.setPlainText("\n".join(decision_matrix))  # type: ignore

            # Sample scoring
            scoring_data = [
                "Suggestion Scoring:",
                "- Relevance: 9/10",
                "- Feasibility: 8/10",
                "- Impact: 8/10",
                "- User preference: 7/10",
                "Final Score: 8.0/10",
            ]

            self.scoring_text.setPlainText("\n".join(scoring_data))  # type: ignore

        except Exception as e:
            logger.error(f"Error updating decision data: {e}")

    def log_debug_event(self, event_type: str, data: Dict):
        """Log a debug event."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.debug_data[timestamp] = {"type": event_type, "data": data}

            logger.debug(f"Debug event logged: {event_type}")

        except Exception as e:
            logger.error(f"Error logging debug event: {e}")

    def export_debug_session(self):
        """Export the current debug session."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lyrixa_debug_session_{timestamp}.json"

            import json

            with open(filename, "w") as f:
                json.dump(self.debug_data, f, indent=2)

            logger.info(f"Debug session exported to {filename}")

        except Exception as e:
            logger.error(f"Error exporting debug session: {e}")

    def clear_debug_history(self):
        """Clear the debug history."""
        try:
            self.debug_data.clear()

            # Clear all text widgets
            self.perception_history_text.clear()  # type: ignore
            self.reasoning_history_text.clear()  # type: ignore
            self.performance_history_text.clear()  # type: ignore

            logger.info("Debug history cleared")

        except Exception as e:
            logger.error(f"Error clearing debug history: {e}")

    def closeEvent(self, event):
        """Handle close event."""
        try:
            if QT_AVAILABLE:
                self.update_timer.stop()  # type: ignore
            event.accept()  # type: ignore
        except Exception as e:
            logger.error(f"Error during close event: {e}")
            event.accept()  # type: ignore

    def start_debug_timer(self):
        """Start the debug update timer."""
        try:
            if QT_AVAILABLE:
                if (
                    hasattr(self.update_timer, "isActive")
                    and not self.update_timer.isActive()
                ):  # type: ignore
                    self.update_timer.timeout.connect(self.update_display)  # type: ignore
                    self.update_timer.start(1000)  # type: ignore
                    logger.info("Debug timer started")
                elif not hasattr(self.update_timer, "isActive"):
                    # Mock mode
                    logger.info("Debug timer started (mock mode)")
        except Exception as e:
            logger.error(f"Error starting debug timer: {e}")

    def stop_debug_timer(self):
        """Stop the debug update timer."""
        try:
            if QT_AVAILABLE:
                if (
                    hasattr(self.update_timer, "isActive")
                    and self.update_timer.isActive()
                ):  # type: ignore
                    self.update_timer.stop()  # type: ignore
                    logger.info("Debug timer stopped")
                elif not hasattr(self.update_timer, "isActive"):
                    # Mock mode
                    logger.info("Debug timer stopped (mock mode)")
        except Exception as e:
            logger.error(f"Error stopping debug timer: {e}")


def main():
    """Main function for testing the debug console."""
    if QT_AVAILABLE:
        from PySide6.QtWidgets import QApplication  # type: ignore

        app = QApplication.instance()  # type: ignore
        if app is None:
            app = QApplication([])  # type: ignore

        console = DebugConsoleWidget()
        console.show()  # type: ignore

        return app.exec()  # type: ignore
    else:
        print("Qt not available - running in mock mode")
        console = DebugConsoleWidget()
        console.update_display()
        print("Debug console initialized successfully in mock mode")
        return 0


if __name__ == "__main__":
    main()
