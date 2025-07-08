"""
🐛🔍 LYRIXA DEBUG CONSOLE GUI WIDGET
===================================

GUI widget for the Lyrixa Debug Console providing real-time introspection into:
- What Lyrixa sees (perception and input analysis)
- What she's thinking (reasoning process and cognitive state)
- Why she picks suggestions or plans (decision matrix and scoring)

This widget integrates with the main GUI to provide developer transparency.
"""

import logging
from datetime import datetime
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check Qt availability first
QT_AVAILABLE = False
try:
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
    QT_AVAILABLE = True
except ImportError:
    # Fallback classes for headless mode
    class MockWidget:
        def __init__(self, *args, **kwargs):
            pass
            
        def setLayout(self, layout):
            pass
            
        def setWindowTitle(self, title):
            pass
            
        def setMinimumSize(self, width, height):
            pass
            
        def show(self):
            pass
            
        def hide(self):
            pass
            
        def update(self):
            pass
            
        def setStyleSheet(self, style):
            pass
            
        def addTab(self, widget, title):
            pass
            
        def setFrameStyle(self, style):
            pass
            
        def addWidget(self, widget):
            pass
            
        def addLayout(self, layout):
            pass
            
        def setText(self, text):
            pass
            
        def text(self):
            return ""
            
        def setPlainText(self, text):
            pass
            
        def toPlainText(self):
            return ""
            
        def append(self, text):
            pass
            
        def clear(self):
            pass
            
        def setReadOnly(self, readonly):
            pass
            
        def clicked(self):
            return self
            
        def connect(self, func):
            pass
            
        def timeout(self):
            return self
            
        def start(self, interval):
            pass
            
        def stop(self):
            pass
            
        def setValue(self, value):
            pass
            
        def setRange(self, min_val, max_val):
            pass
            
        def setFont(self, font):
            pass
            
        def setAlignment(self, alignment):
            pass
            
        def setPointSize(self, size):
            pass
            
        def setBold(self, bold):
            pass
            
        def addItem(self, item):
            pass
            
        def currentText(self):
            return ""
            
        def setCurrentText(self, text):
            pass
            
        def moveCursor(self, cursor):
            pass
            
        def insertPlainText(self, text):
            pass
    
    # Mock all Qt classes
    QWidget = MockWidget
    QTimer = MockWidget
    QFont = MockWidget
    QTextCursor = MockWidget
    QComboBox = MockWidget
    QFrame = MockWidget
    QGroupBox = MockWidget
    QHBoxLayout = MockWidget
    QLabel = MockWidget
    QProgressBar = MockWidget
    QPushButton = MockWidget
    QTabWidget = MockWidget
    QTextEdit = MockWidget
    QVBoxLayout = MockWidget
    
    # Mock constants
    class MockFrame:
        Box = 1
    
    QFrame.Box = 1


class DebugConsoleWidget(QWidget):
    """
    🐛🔍 Advanced Debug Console Widget
    
    Provides comprehensive debugging and introspection capabilities for Lyrixa.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.debug_data = {}
        self.update_timer = QTimer()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the debug console UI."""
        try:
            if QT_AVAILABLE:
                self.setWindowTitle("🐛 Lyrixa Debug Console")
                self.setMinimumSize(1000, 700)
                
            # Main layout
            main_layout = QVBoxLayout()
            
            # Header
            header_layout = QHBoxLayout()
            
            # Title
            title_label = QLabel("🐛🔍 Lyrixa Debug Console")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            header_layout.addWidget(title_label)
            
            # Debug level selector
            self.debug_level_combo = QComboBox()
            self.debug_level_combo.addItem("🔍 All")
            self.debug_level_combo.addItem("⚠️ Warning")
            self.debug_level_combo.addItem("❌ Error")
            header_layout.addWidget(QLabel("Debug Level:"))
            header_layout.addWidget(self.debug_level_combo)
            
            # Export button
            self.export_btn = QPushButton("📁 Export Session")
            if QT_AVAILABLE:
                self.export_btn.clicked.connect(self.export_debug_session)
            header_layout.addWidget(self.export_btn)
            
            # Clear button
            self.clear_btn = QPushButton("🗑️ Clear History")
            if QT_AVAILABLE:
                self.clear_btn.clicked.connect(self.clear_debug_history)
            header_layout.addWidget(self.clear_btn)
            
            main_layout.addLayout(header_layout)
            
            # Status frame
            self.status_frame = QFrame()
            if QT_AVAILABLE:
                self.status_frame.setFrameStyle(QFrame.Box)
            status_layout = QHBoxLayout()
            
            self.cognitive_state_label = QLabel("😴 IDLE")
            self.cognitive_state_label.setStyleSheet(
                "font-weight: bold; color: #666; padding: 5px;"
            )
            status_layout.addWidget(QLabel("Cognitive State:"))
            status_layout.addWidget(self.cognitive_state_label)
            
            # Performance metrics
            self.performance_label = QLabel(
                "🧠 Memory: 0MB | 🚀 Speed: 0ms | 🎯 Accuracy: 0%"
            )
            status_layout.addWidget(self.performance_label)
            
            self.status_frame.setLayout(status_layout)
            main_layout.addWidget(self.status_frame)
            
            # Tab widget for different debug views
            self.tab_widget = QTabWidget()
            
            # Create tabs
            self.create_perception_tab()
            self.create_reasoning_tab()
            self.create_decision_tab()
            self.create_performance_tab()
            
            main_layout.addWidget(self.tab_widget)
            
            self.setLayout(main_layout)
            
            # Setup timer for updates
            if QT_AVAILABLE:
                self.update_timer.timeout.connect(self.update_display)
                self.update_timer.start(1000)  # Update every second
                
        except Exception as e:
            logger.error(f"Error setting up debug console UI: {e}")
            
    def create_perception_tab(self):
        """Create the perception analysis tab."""
        try:
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Current perception
            current_group = QGroupBox("👁️ Current Perception")
            current_layout = QVBoxLayout()
            
            self.current_input_label = QLabel("No input detected")
            self.current_input_label.setStyleSheet("font-family: monospace; padding: 5px;")
            current_layout.addWidget(QLabel("User Input:"))
            current_layout.addWidget(self.current_input_label)
            
            self.attention_focus_label = QLabel("No focus areas")
            current_layout.addWidget(QLabel("Attention Focus:"))
            current_layout.addWidget(self.attention_focus_label)
            
            self.context_info_label = QLabel("Memory: 0 | Goals: 0")
            current_layout.addWidget(QLabel("Context:"))
            current_layout.addWidget(self.context_info_label)
            
            current_group.setLayout(current_layout)
            layout.addWidget(current_group)
            
            # Perception history
            history_group = QGroupBox("📊 Perception History")
            history_layout = QVBoxLayout()
            
            self.perception_history_text = QTextEdit()
            self.perception_history_text.setReadOnly(True)
            self.perception_history_text.setStyleSheet(
                "font-family: monospace; font-size: 10px; background-color: #f0f0f0;"
            )
            history_layout.addWidget(self.perception_history_text)
            
            history_group.setLayout(history_layout)
            layout.addWidget(history_group)
            
            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "👁️ Perception")
            
        except Exception as e:
            logger.error(f"Error creating perception tab: {e}")
            
    def create_reasoning_tab(self):
        """Create the reasoning process tab."""
        try:
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Current thought process
            current_group = QGroupBox("🧠 Current Thought Process")
            current_layout = QVBoxLayout()
            
            self.current_thought_label = QLabel("No active thought process")
            current_layout.addWidget(self.current_thought_label)
            
            self.reasoning_text = QTextEdit()
            self.reasoning_text.setReadOnly(True)
            self.reasoning_text.setStyleSheet("font-family: monospace; font-size: 10px;")
            current_layout.addWidget(QLabel("Reasoning Steps:"))
            current_layout.addWidget(self.reasoning_text)
            
            current_group.setLayout(current_layout)
            layout.addWidget(current_group)
            
            # Reasoning history
            history_group = QGroupBox("📚 Thought History")
            history_layout = QVBoxLayout()
            
            self.reasoning_history_text = QTextEdit()
            self.reasoning_history_text.setReadOnly(True)
            self.reasoning_history_text.setStyleSheet(
                "font-family: monospace; font-size: 10px; background-color: #f0f0f0;"
            )
            history_layout.addWidget(self.reasoning_history_text)
            
            history_group.setLayout(history_layout)
            layout.addWidget(history_group)
            
            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "🧠 Reasoning")
            
        except Exception as e:
            logger.error(f"Error creating reasoning tab: {e}")
            
    def create_decision_tab(self):
        """Create the decision matrix tab."""
        try:
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Decision matrix
            decision_group = QGroupBox("⚖️ Decision Matrix")
            decision_layout = QVBoxLayout()
            
            self.decision_matrix_text = QTextEdit()
            self.decision_matrix_text.setReadOnly(True)
            self.decision_matrix_text.setStyleSheet("font-family: monospace; font-size: 10px;")
            decision_layout.addWidget(self.decision_matrix_text)
            
            decision_group.setLayout(decision_layout)
            layout.addWidget(decision_group)
            
            # Suggestion scoring
            scoring_group = QGroupBox("📊 Suggestion Scoring")
            scoring_layout = QVBoxLayout()
            
            self.scoring_text = QTextEdit()
            self.scoring_text.setReadOnly(True)
            self.scoring_text.setStyleSheet("font-family: monospace; font-size: 10px;")
            scoring_layout.addWidget(self.scoring_text)
            
            scoring_group.setLayout(scoring_layout)
            layout.addWidget(scoring_group)
            
            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "⚖️ Decisions")
            
        except Exception as e:
            logger.error(f"Error creating decision tab: {e}")
            
    def create_performance_tab(self):
        """Create the performance monitoring tab."""
        try:
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Performance metrics
            metrics_group = QGroupBox("📈 Performance Metrics")
            metrics_layout = QVBoxLayout()
            
            # Memory usage
            memory_layout = QHBoxLayout()
            memory_layout.addWidget(QLabel("Memory Usage:"))
            self.memory_progress = QProgressBar()
            self.memory_progress.setRange(0, 100)
            memory_layout.addWidget(self.memory_progress)
            metrics_layout.addLayout(memory_layout)
            
            # Processing speed
            speed_layout = QHBoxLayout()
            speed_layout.addWidget(QLabel("Processing Speed:"))
            self.speed_label = QLabel("0ms")
            speed_layout.addWidget(self.speed_label)
            metrics_layout.addLayout(speed_layout)
            
            # Accuracy
            accuracy_layout = QHBoxLayout()
            accuracy_layout.addWidget(QLabel("Accuracy:"))
            self.accuracy_progress = QProgressBar()
            self.accuracy_progress.setRange(0, 100)
            accuracy_layout.addWidget(self.accuracy_progress)
            metrics_layout.addLayout(accuracy_layout)
            
            metrics_group.setLayout(metrics_layout)
            layout.addWidget(metrics_group)
            
            # Performance history
            history_group = QGroupBox("📊 Performance History")
            history_layout = QVBoxLayout()
            
            self.performance_history_text = QTextEdit()
            self.performance_history_text.setReadOnly(True)
            self.performance_history_text.setStyleSheet(
                "font-family: monospace; font-size: 10px; background-color: #f0f0f0;"
            )
            history_layout.addWidget(self.performance_history_text)
            
            history_group.setLayout(history_layout)
            layout.addWidget(history_group)
            
            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "📈 Performance")
            
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
            states = ["😴 IDLE", "🤔 THINKING", "💡 PROCESSING", "🎯 FOCUSED", "⚡ ACTIVE"]
            import random
            current_state = random.choice(states)
            self.cognitive_state_label.setText(current_state)
            
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
            self.performance_label.setText(
                f"🧠 Memory: {memory_mb}MB | 🚀 Speed: {speed_ms}ms | 🎯 Accuracy: {accuracy_pct}%"
            )
            
            # Update progress bars
            self.memory_progress.setValue(min(100, memory_mb // 2))
            self.speed_label.setText(f"{speed_ms}ms")
            self.accuracy_progress.setValue(accuracy_pct)
            
            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            history_entry = f"[{timestamp}] Memory: {memory_mb}MB, Speed: {speed_ms}ms, Accuracy: {accuracy_pct}%\n"
            self.performance_history_text.append(history_entry)
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
            
    def update_perception_data(self):
        """Update perception data display."""
        try:
            # Sample perception data
            self.current_input_label.setText("User typing: 'How can I improve my workflow?'")
            self.attention_focus_label.setText("Keywords: workflow, improve, productivity")
            self.context_info_label.setText("Memory: 5 conversations | Goals: 2 active")
            
            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            history_entry = f"[{timestamp}] Input detected: workflow improvement query\n"
            self.perception_history_text.append(history_entry)
            
        except Exception as e:
            logger.error(f"Error updating perception data: {e}")
            
    def update_reasoning_data(self):
        """Update reasoning data display."""
        try:
            # Sample reasoning data
            self.current_thought_label.setText("Analyzing workflow optimization strategies...")
            
            reasoning_steps = [
                "1. Identify current workflow inefficiencies",
                "2. Analyze user's work patterns",
                "3. Generate optimization suggestions",
                "4. Prioritize by impact and effort"
            ]
            
            self.reasoning_text.setPlainText("\n".join(reasoning_steps))
            
            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            history_entry = f"[{timestamp}] Reasoning: Workflow optimization analysis\n"
            self.reasoning_history_text.append(history_entry)
            
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
                "4. Break scheduling (Score: 6.8)"
            ]
            
            self.decision_matrix_text.setPlainText("\n".join(decision_matrix))
            
            # Sample scoring
            scoring_data = [
                "Suggestion Scoring:",
                "- Relevance: 9/10",
                "- Feasibility: 8/10",
                "- Impact: 8/10",
                "- User preference: 7/10",
                "Final Score: 8.0/10"
            ]
            
            self.scoring_text.setPlainText("\n".join(scoring_data))
            
        except Exception as e:
            logger.error(f"Error updating decision data: {e}")
            
    def log_debug_event(self, event_type: str, data: Dict):
        """Log a debug event."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.debug_data[timestamp] = {
                "type": event_type,
                "data": data
            }
            
            logger.debug(f"Debug event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"Error logging debug event: {e}")
            
    def export_debug_session(self):
        """Export the current debug session."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lyrixa_debug_session_{timestamp}.json"
            
            import json
            with open(filename, 'w') as f:
                json.dump(self.debug_data, f, indent=2)
                
            logger.info(f"Debug session exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting debug session: {e}")
            
    def clear_debug_history(self):
        """Clear the debug history."""
        try:
            self.debug_data.clear()
            
            # Clear all text widgets
            self.perception_history_text.clear()
            self.reasoning_history_text.clear()
            self.performance_history_text.clear()
            
            logger.info("Debug history cleared")
            
        except Exception as e:
            logger.error(f"Error clearing debug history: {e}")
            
    def closeEvent(self, event):
        """Handle close event."""
        try:
            if QT_AVAILABLE:
                self.update_timer.stop()
            event.accept()
        except Exception as e:
            logger.error(f"Error during close event: {e}")
            event.accept()


def main():
    """Main function for testing the debug console."""
    if QT_AVAILABLE:
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        console = DebugConsoleWidget()
        console.show()
        
        return app.exec()
    else:
        print("Qt not available - running in mock mode")
        console = DebugConsoleWidget()
        console.update_display()
        print("Debug console initialized successfully in mock mode")
        return 0


if __name__ == "__main__":
    main()
