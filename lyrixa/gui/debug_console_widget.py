"""
🐛🔍 LYRIXA DEBUG CONSOLE GUI WIDGET
===================================

GUI widget for the Lyrixa Debug Console providing real-time introspection into:
- What Lyrixa sees (perception and input analysis)
- What she's thinking (reasoning process and cognitive state)
- Why she picks suggestions or plans (decision matrix and scoring)

This widget integrates with the main GUI to provide developer transparency.
"""

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
    class QWidget:
        def __init__(self):
            pass

    class QTimer:
        def __init__(self):
            pass


"""
🐛🔍 LYRIXA DEBUG CONSOLE GUI WIDGET
===================================

GUI widget for the Lyrixa Debug Console providing real-time introspection into:
- What Lyrixa sees (perception and input analysis)
- What she's thinking (reasoning process and cognitive state)
- Why she picks suggestions or plans (decision matrix and scoring)

This widget integrates with the main GUI to provide developer transparency.
"""

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
    QT_AVAILABLE = False


if QT_AVAILABLE:

    class DebugConsoleWidget(QWidget):
        """
        🐛🔍 Debug Console Widget

        Real-time debug visualization showing:
        - Cognitive state indicator
        - Thought process viewer
        - Perception timeline
        - Decision matrix analysis
        - Performance metrics
        """

        def __init__(self, debug_console=None):
            super().__init__()
            self.debug_console = debug_console
            self.update_timer = None
            self.init_ui()
            self.setup_auto_update()

        def init_ui(self):
            """Initialize the user interface"""
            self.setWindowTitle("🐛 Lyrixa Debug Console")
            self.setMinimumSize(1000, 700)

            # Main layout
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)

            # Header with controls
            header_layout = QHBoxLayout()

            # Title
            title_label = QLabel("🐛🔍 Lyrixa Debug Console")
            title_font = QFont()
            title_font.setPointSize(14)
            title_font.setBold(True)
            title_label.setFont(title_font)
            header_layout.addWidget(title_label)

            header_layout.addStretch()

            # Debug level selector
            self.debug_level_combo = QComboBox()
            self.debug_level_combo.addItems(
                ["MINIMAL", "STANDARD", "DETAILED", "VERBOSE", "TRACE"]
            )
            self.debug_level_combo.currentTextChanged.connect(self.change_debug_level)
            header_layout.addWidget(QLabel("Debug Level:"))
            header_layout.addWidget(self.debug_level_combo)

            # Export button
            self.export_btn = QPushButton("📁 Export Session")
            self.export_btn.clicked.connect(self.export_debug_session)
            header_layout.addWidget(self.export_btn)

            # Clear button
            self.clear_btn = QPushButton("🗑️ Clear History")
            self.clear_btn.clicked.connect(self.clear_debug_history)
            header_layout.addWidget(self.clear_btn)

            main_layout.addLayout(header_layout)

            # Status bar
            self.status_frame = QFrame()
            self.status_frame.setFrameStyle(QFrame.Box)
            status_layout = QHBoxLayout()

            self.cognitive_state_label = QLabel("😴 IDLE")
            self.cognitive_state_label.setStyleSheet(
                "font-weight: bold; color: #2E86AB;"
            )
            status_layout.addWidget(QLabel("Cognitive State:"))
            status_layout.addWidget(self.cognitive_state_label)

            status_layout.addStretch()

            self.performance_label = QLabel(
                "Decisions: 0 | Avg Time: 0ms | Confidence: 0.00"
            )
            status_layout.addWidget(self.performance_label)

            self.status_frame.setLayout(status_layout)
            main_layout.addWidget(self.status_frame)

            # Main content tabs
            self.tab_widget = QTabWidget()
            main_layout.addWidget(self.tab_widget)

            # Create tabs
            self.create_perception_tab()
            self.create_thoughts_tab()
            self.create_decisions_tab()
            self.create_performance_tab()

        def create_perception_tab(self):
            """Create the perception analysis tab"""
            tab = QWidget()
            layout = QVBoxLayout()

            # Current perception
            current_group = QGroupBox("👁️ Current Perception")
            current_layout = QVBoxLayout()

            self.current_input_label = QLabel("No input detected")
            self.current_input_label.setWordWrap(True)
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
            self.perception_history_text.setMaximumHeight(200)
            history_layout.addWidget(self.perception_history_text)

            history_group.setLayout(history_layout)
            layout.addWidget(history_group)

            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "👁️ Perception")

        def create_thoughts_tab(self):
            """Create the thought process analysis tab"""
            tab = QWidget()
            layout = QVBoxLayout()

            # Current thought process
            current_group = QGroupBox("🧠 Current Thought Process")
            current_layout = QVBoxLayout()

            self.current_thought_label = QLabel("No active thought process")
            current_layout.addWidget(self.current_thought_label)

            self.reasoning_text = QTextEdit()
            self.reasoning_text.setReadOnly(True)
            self.reasoning_text.setMaximumHeight(150)
            current_layout.addWidget(QLabel("Reasoning Steps:"))
            current_layout.addWidget(self.reasoning_text)

            current_group.setLayout(current_layout)
            layout.addWidget(current_group)

            # Thought history
            history_group = QGroupBox("📚 Thought History")
            history_layout = QVBoxLayout()

            self.thought_history_text = QTextEdit()
            self.thought_history_text.setReadOnly(True)
            history_layout.addWidget(self.thought_history_text)

            history_group.setLayout(history_layout)
            layout.addWidget(history_group)

            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "🧠 Thoughts")

        def create_decisions_tab(self):
            """Create the decision analysis tab"""
            tab = QWidget()
            layout = QVBoxLayout()

            # Decision matrix
            matrix_group = QGroupBox("⚖️ Decision Matrix")
            matrix_layout = QVBoxLayout()

            self.decision_matrix_text = QTextEdit()
            self.decision_matrix_text.setReadOnly(True)
            matrix_layout.addWidget(self.decision_matrix_text)

            matrix_group.setLayout(matrix_layout)
            layout.addWidget(matrix_group)

            # Recent decisions
            recent_group = QGroupBox("📋 Recent Decisions")
            recent_layout = QVBoxLayout()

            self.recent_decisions_text = QTextEdit()
            self.recent_decisions_text.setReadOnly(True)
            recent_layout.addWidget(self.recent_decisions_text)

            recent_group.setLayout(recent_layout)
            layout.addWidget(recent_group)

            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "⚖️ Decisions")

        def create_performance_tab(self):
            """Create the performance metrics tab"""
            tab = QWidget()
            layout = QVBoxLayout()

            # Performance metrics
            metrics_group = QGroupBox("📊 Performance Metrics")
            metrics_layout = QVBoxLayout()

            # Decision timing
            timing_layout = QHBoxLayout()
            timing_layout.addWidget(QLabel("Avg Decision Time:"))
            self.timing_progress = QProgressBar()
            self.timing_progress.setRange(0, 1000)  # 0-1000ms
            self.timing_label = QLabel("0ms")
            timing_layout.addWidget(self.timing_progress)
            timing_layout.addWidget(self.timing_label)
            metrics_layout.addLayout(timing_layout)

            # Confidence trends
            confidence_layout = QHBoxLayout()
            confidence_layout.addWidget(QLabel("Avg Confidence:"))
            self.confidence_progress = QProgressBar()
            self.confidence_progress.setRange(0, 100)
            self.confidence_label = QLabel("0.00")
            confidence_layout.addWidget(self.confidence_progress)
            confidence_layout.addWidget(self.confidence_label)
            metrics_layout.addLayout(confidence_layout)

            metrics_group.setLayout(metrics_layout)
            layout.addWidget(metrics_group)

            # Performance logs
            logs_group = QGroupBox("📈 Performance Logs")
            logs_layout = QVBoxLayout()

            self.performance_text = QTextEdit()
            self.performance_text.setReadOnly(True)
            logs_layout.addWidget(self.performance_text)

            logs_group.setLayout(logs_layout)
            layout.addWidget(logs_group)

            tab.setLayout(layout)
            self.tab_widget.addTab(tab, "📊 Performance")

        def setup_auto_update(self):
            """Setup automatic updates from debug console"""
            if self.debug_console:
                self.update_timer = QTimer()
                self.update_timer.timeout.connect(self.update_display)
                self.update_timer.start(1000)  # Update every second

        def update_display(self):
            """Update all display elements with latest debug data"""
            if not self.debug_console:
                return

            try:
                # Update cognitive state
                state = self.debug_console.current_cognitive_state
                state_emoji = {
                    "idle": "😴",
                    "analyzing": "🔍",
                    "reasoning": "🧠",
                    "deciding": "⚖️",
                    "executing": "⚡",
                    "learning": "📚",
                    "reflecting": "💭",
                }

                emoji = state_emoji.get(state.value, "🤖")
                self.cognitive_state_label.setText(f"{emoji} {state.value.upper()}")

                # Update performance metrics
                debug_state = self.debug_console.show_current_state()
                perf_text = f"Decisions: {debug_state['recent_decision_count']} | "
                perf_text += f"Avg Time: {debug_state['avg_decision_time']:.1f}ms | "
                perf_text += f"Confidence: {debug_state['avg_confidence']:.2f}"
                self.performance_label.setText(perf_text)

                # Update timing progress bar
                timing = min(1000, max(0, debug_state["avg_decision_time"]))
                self.timing_progress.setValue(int(timing))
                self.timing_label.setText(f"{debug_state['avg_decision_time']:.1f}ms")

                # Update confidence progress bar
                confidence = int(debug_state["avg_confidence"] * 100)
                self.confidence_progress.setValue(confidence)
                self.confidence_label.setText(f"{debug_state['avg_confidence']:.2f}")

                # Update current perception
                if self.debug_console.perception_history:
                    latest_perception = self.debug_console.perception_history[-1]

                    # Truncate long inputs
                    input_text = latest_perception.user_input
                    if len(input_text) > 100:
                        input_text = input_text[:100] + "..."
                    self.current_input_label.setText(input_text)

                    # Show attention focus
                    focus_text = ", ".join(latest_perception.attention_focus)
                    self.attention_focus_label.setText(focus_text)

                    # Show context info
                    memory_count = len(latest_perception.memory_context)
                    goals_count = len(latest_perception.current_goals)
                    self.context_info_label.setText(
                        f"Memory: {memory_count} | Goals: {goals_count}"
                    )

                # Update current thought process
                if self.debug_console.thought_history:
                    latest_thought = self.debug_console.thought_history[-1]

                    if latest_thought.final_decision:
                        self.current_thought_label.setText(
                            f"✅ Completed: {latest_thought.final_decision}"
                        )
                    else:
                        self.current_thought_label.setText(
                            f"🔄 Active: {latest_thought.thought_id}"
                        )

                    # Show reasoning steps
                    reasoning_text = ""
                    for i, step in enumerate(latest_thought.reasoning_steps, 1):
                        reasoning_text += f"{i}. {step}\n"
                    self.reasoning_text.setPlainText(reasoning_text)

                # Update thought history
                self.update_thought_history()

                # Update decision matrix if available
                self.update_decision_matrix()

                # Update performance logs
                self.update_performance_logs()

            except Exception as e:
                print(f"Debug widget update error: {e}")

        def update_thought_history(self):
            """Update thought history display"""
            if not self.debug_console.thought_history:
                return

            history_text = ""
            for thought in self.debug_console.thought_history[-10:]:  # Show last 10
                timestamp = thought.timestamp.strftime("%H:%M:%S")
                status = "✅" if thought.final_decision else "🔄"
                history_text += f"{status} [{timestamp}] {thought.thought_id}\n"

                if thought.final_decision:
                    history_text += f"    Decision: {thought.final_decision}\n"

                if thought.confidence_scores:
                    avg_conf = sum(thought.confidence_scores.values()) / len(
                        thought.confidence_scores
                    )
                    history_text += f"    Confidence: {avg_conf:.2f}\n"

                history_text += "\n"

            self.thought_history_text.setPlainText(history_text)

            # Auto-scroll to bottom
            cursor = self.thought_history_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.thought_history_text.setTextCursor(cursor)

        def update_decision_matrix(self):
            """Update decision matrix display"""
            if not self.debug_console.thought_history:
                return

            # Find latest thought with decision factors
            matrix_text = ""
            for thought in reversed(self.debug_console.thought_history):
                if (
                    thought.decision_factors
                    and "decision_matrix" in thought.decision_factors
                ):
                    matrix_data = thought.decision_factors["decision_matrix"]

                    matrix_text += f"🎯 Latest Decision Matrix ({thought.timestamp.strftime('%H:%M:%S')})\n\n"

                    if "final_rankings" in matrix_data:
                        matrix_text += "Rankings:\n"
                        for i, (option, score) in enumerate(
                            matrix_data["final_rankings"][:5]
                        ):
                            emoji = (
                                "🥇"
                                if i == 0
                                else "🥈"
                                if i == 1
                                else "🥉"
                                if i == 2
                                else "📋"
                            )
                            matrix_text += f"  {emoji} {option}: {score:.2f}\n"

                    if "reasoning" in matrix_data:
                        matrix_text += f"\nReasoning: {matrix_data['reasoning']}\n"

                    if "confidence" in matrix_data:
                        matrix_text += f"Confidence: {matrix_data['confidence']:.2f}\n"

                    break

            if not matrix_text:
                matrix_text = "No decision matrix data available yet."

            self.decision_matrix_text.setPlainText(matrix_text)

        def update_performance_logs(self):
            """Update performance logs display"""
            log_text = ""

            # Recent performance data
            if self.debug_console.decision_timings:
                recent_timings = self.debug_console.decision_timings[-10:]
                log_text += f"Recent Decision Timings (last {len(recent_timings)}):\n"
                for i, timing in enumerate(recent_timings):
                    log_text += f"  {i + 1}. {timing:.1f}ms\n"
                log_text += "\n"

            if self.debug_console.confidence_trends:
                recent_confidence = self.debug_console.confidence_trends[-10:]
                log_text += (
                    f"Recent Confidence Trends (last {len(recent_confidence)}):\n"
                )
                for i, conf in enumerate(recent_confidence):
                    log_text += f"  {i + 1}. {conf:.2f}\n"
                log_text += "\n"

            # Performance summary
            if (
                self.debug_console.decision_timings
                and self.debug_console.confidence_trends
            ):
                import numpy as np

                avg_timing = np.mean(self.debug_console.decision_timings)
                avg_confidence = np.mean(self.debug_console.confidence_trends)

                log_text += "Overall Performance:\n"
                log_text += f"  Average Decision Time: {avg_timing:.1f}ms\n"
                log_text += f"  Average Confidence: {avg_confidence:.2f}\n"
                log_text += (
                    f"  Total Decisions: {len(self.debug_console.decision_timings)}\n"
                )

            if not log_text:
                log_text = "No performance data available yet."

            self.performance_text.setPlainText(log_text)

        def change_debug_level(self, level_name):
            """Change debug level"""
            if self.debug_console:
                try:
                    from lyrixa.core.debug_console import DebugLevel

                    level = DebugLevel[level_name]
                    self.debug_console.toggle_debug_level(level)
                    print(f"🐛 Debug level changed to: {level.name}")
                except KeyError:
                    print(f"🐛 Invalid debug level: {level_name}")

        def export_debug_session(self):
            """Export debug session to file"""
            if self.debug_console:
                filepath = self.debug_console.export_debug_session()
                print(f"🐛 Debug session exported to: {filepath}")

        def clear_debug_history(self):
            """Clear debug history"""
            if self.debug_console:
                self.debug_console.thought_history.clear()
                self.debug_console.perception_history.clear()
                self.debug_console.decision_timings.clear()
                self.debug_console.confidence_trends.clear()
                print("🐛 Debug history cleared")

        def set_debug_console(self, debug_console):
            """Set the debug console instance"""
            self.debug_console = debug_console
            if hasattr(self, "update_timer") and self.update_timer:
                if not self.update_timer.isActive():
                    self.update_timer.start(1000)

else:
    # Non-Qt fallback for headless environments
    class DebugConsoleWidget:
        """Headless debug console for CLI environments"""

        def __init__(self, debug_console=None):
            self.debug_console = debug_console
            print("🐛 Debug Console: Running in headless mode")

        def show_status(self):
            """Show debug status in CLI"""
            if self.debug_console:
                state = self.debug_console.show_current_state()
                print(f"""
🐛 **DEBUG CONSOLE STATUS**
Cognitive State: {state["cognitive_state"]}
Debug Level: {state["debug_level"]}
Recent Decisions: {state["recent_decision_count"]}
Avg Decision Time: {state["avg_decision_time"]:.1f}ms
Avg Confidence: {state["avg_confidence"]:.2f}
""")

        def show_latest_thought(self):
            """Show latest thought process"""
            if self.debug_console:
                analysis = self.debug_console.get_thought_analysis()
                if "error" not in analysis:
                    print(f"""
🧠 **LATEST THOUGHT PROCESS**
ID: {analysis["thought_id"]}
Duration: {analysis["execution_time_ms"]:.1f}ms
Reasoning Steps: {len(analysis["reasoning_steps"])}

**Reasoning Process:**""")
                    for i, step in enumerate(analysis["reasoning_steps"], 1):
                        print(f"   {i}. {step}")

                    if analysis["final_decision"]:
                        print(f"\n✅ Final Decision: {analysis['final_decision']}")

        def set_debug_console(self, debug_console):
            """Set the debug console instance"""
            self.debug_console = debug_console


# Factory function to create appropriate debug widget
def create_debug_widget(debug_console=None):
    """Create debug widget based on environment"""
    if QT_AVAILABLE:
        return DebugConsoleWidget(debug_console)
    else:
        return DebugConsoleWidget(debug_console)
