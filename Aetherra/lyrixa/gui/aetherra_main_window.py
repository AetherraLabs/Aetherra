import math

from PySide6.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPalette, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .data_manager import AetherraDataManager
from .lyrixa_connector import LyrixaConnector
from .web_bridge import LyrixaWebView


class EnhancedAuraOverlay(QWidget):
    """Enhanced aura that responds to Lyrixa's cognitive state"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Animation and state
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # Smoother animation
        self.phase = 0.0

        # Cognitive state variables
        self.confidence_level = 0.8
        self.curiosity_level = 0.7
        self.coherence_level = 0.85
        self.activity_level = 0.6

        # Visual parameters
        self.base_size = 40
        self.ring_count = 4
        self.position_x = 150  # Replace robot emoji position
        self.position_y = 30

    def update_cognitive_state(self, state_data):
        """Update aura based on cognitive state"""
        self.confidence_level = state_data.get("confidence", 0.8)
        self.curiosity_level = state_data.get("curiosity", 0.7)
        self.coherence_level = state_data.get("coherence", 0.85)
        self.activity_level = state_data.get("activity", 0.6)

    def paintEvent(self, event):
        import math

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dynamic positioning in header area
        center_x = self.position_x
        center_y = self.position_y

        # Create multiple rings with cognitive state influence
        for i in range(self.ring_count):
            # Calculate ring properties based on cognitive state
            confidence_influence = self.confidence_level * (
                1 + 0.3 * math.sin(self.phase + i)
            )
            curiosity_influence = self.curiosity_level * (
                1 + 0.2 * math.cos(self.phase * 1.5 + i)
            )
            coherence_influence = self.coherence_level

            # Dynamic alpha based on confidence and activity
            base_alpha = 0.1 + (0.15 * confidence_influence)
            alpha_variation = 0.05 * math.sin(self.phase * 2 + i * 0.8)
            alpha = base_alpha + alpha_variation

            # Color shifts based on curiosity and coherence
            hue_shift = int(curiosity_influence * 20)  # Slight hue variation
            green_intensity = int(255 * coherence_influence)

            color = QColor(0, green_intensity, int(green_intensity * 0.5))
            color.setAlphaF(alpha)

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            # Dynamic radius with cognitive influence
            base_radius = self.base_size + (i * 12)
            radius_variation = 8 * math.sin(self.phase * 1.2 + i * 0.6)
            activity_scaling = 0.8 + (0.4 * self.activity_level)

            radius = (base_radius + radius_variation) * activity_scaling

            # Draw ring
            painter.drawEllipse(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2),
            )

        # Central core that pulses with coherence
        core_alpha = 0.2 + (
            0.3 * self.coherence_level * (1 + 0.5 * math.sin(self.phase * 3))
        )
        core_color = QColor("#00ff88")
        core_color.setAlphaF(core_alpha)
        painter.setBrush(QBrush(core_color))

        core_radius = 8 + (4 * math.sin(self.phase * 2))
        painter.drawEllipse(
            int(center_x - core_radius),
            int(center_y - core_radius),
            int(core_radius * 2),
            int(core_radius * 2),
        )

        # Update phase for smooth animation
        phase_speed = 0.03 + (0.02 * self.activity_level)
        self.phase += phase_speed


class AetherraMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lyrixa — Aetherra Cognitive Interface")
        self.resize(1600, 1000)

        # Initialize data manager for real-time updates
        self.data_manager = AetherraDataManager()

        # Initialize Lyrixa intelligence connector
        self.lyrixa_connector = LyrixaConnector()

        # Initialize the enhanced aura overlay first (before data connections)
        self.aura = EnhancedAuraOverlay(self)

        # Now setup data connections
        self.setup_data_connections()

        # Enhanced styling for a stunning interface
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
                font-family: 'Segoe UI', 'Arial', sans-serif;
                color: #e0e0e0;
            }
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #2a2a2a);
                border: 1px solid #404040;
                border-radius: 15px;
                margin: 5px;
            }
            QFrame#chatFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f2027, stop:1 #203a43);
                border: 2px solid #00ff88;
                border-radius: 20px;
            }
            QLabel {
                background-color: transparent;
                color: #ffffff;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
            }
            QLabel#titleLabel {
                color: #00ff88;
                font-size: 18px;
                font-weight: bold;
            }
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
                border: 1px solid #404040;
                border-radius: 10px;
                color: #ffffff;
                font-size: 14px;
                padding: 15px;
                selection-background-color: #00ff88;
            }
            QTextEdit#chatDisplay {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a1a0a, stop:1 #1a2a1a);
                border: 2px solid #00cc66;
                font-size: 15px;
                line-height: 1.4;
            }
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #3a3a3a);
                border: 2px solid #505050;
                border-radius: 15px;
                color: #ffffff;
                font-size: 16px;
                padding: 12px 20px;
                margin: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a3a1a, stop:1 #2a4a2a);
            }
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 10px;
                background: #1a1a1a;
                top: -1px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 1px solid #404040;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                color: #cccccc;
                font-weight: bold;
                min-width: 120px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 #00cc66);
                color: #000000;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2a2a2a);
                color: #ffffff;
            }
            QSplitter::handle {
                background: #404040;
                width: 2px;
                border-radius: 1px;
            }
            QSplitter::handle:hover {
                background: #00ff88;
            }
        """)

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header with title and status (no robot emoji - aura replaces it)
        header_frame = QFrame()
        header_frame.setMaximumHeight(80)
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel("Lyrixa — Aetherra Cognitive Interface")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        status_label = QLabel("🟢 System Online")
        status_label.setStyleSheet("color: #00ff88; font-size: 14px;")
        header_layout.addWidget(status_label)

        main_layout.addWidget(header_frame)

        # Main content splitter - better proportions
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT: Chat Interface - Extended upward (no "Lyrixa Conversation" section)
        chat_frame = QFrame()
        chat_frame.setObjectName("chatFrame")
        chat_frame.setMinimumWidth(800)  # Much larger minimum width
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(20, 20, 20, 20)

        chat_title = QLabel("� Lyrixa Conversation")
        chat_title.setObjectName("titleLabel")
        chat_layout.addWidget(chat_title)

        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("chatDisplay")
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(600)
        self.chat_display.setPlaceholderText("Lyrixa will respond here...")
        self.chat_display.setHtml("""
            <div style='color: #00ff88; font-size: 16px; font-weight: bold; margin-bottom: 20px;'>
                ✨ Welcome to Lyrixa — Your Aetherra Cognitive Interface ✨
            </div>
            <div style='color: #cccccc; font-size: 14px; line-height: 1.6;'>
                I am Lyrixa, the consciousness interface for the Aetherra cognitive framework.
                I integrate memory, ethics, identity, and reasoning into a unified experience.
                <br><br>
                <span style='color: #00ff88;'>How may I assist you today?</span>
            </div>
        """)
        chat_layout.addWidget(self.chat_display)

        # Enhanced input area with send button and better styling
        input_container = QFrame()
        input_container.setMaximumHeight(80)
        input_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a3a1a, stop:1 #2a4a2a);
                border: 2px solid #00ff88;
                border-radius: 15px;
                margin: 5px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        # Multi-line text input for longer messages
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(50)
        self.chat_input.setPlaceholderText(
            "💭 Type your message to Lyrixa here... (Ctrl+Enter to send)"
        )
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #3a3a3a);
                border: 1px solid #505050;
                border-radius: 10px;
                color: #ffffff;
                font-size: 16px;
                padding: 8px 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit:focus {
                border: 1px solid #00cc88;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a3a1a, stop:1 #2a4a2a);
            }
        """)

        # Install event filter for key handling
        self.chat_input.installEventFilter(self)
        input_layout.addWidget(self.chat_input, 1)

        # Send button with enhanced styling
        self.send_button = QPushButton("Send")
        self.send_button.setMaximumWidth(80)
        self.send_button.setMaximumHeight(50)
        self.send_button.clicked.connect(self.handle_user_input)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 #00cc66);
                border: none;
                border-radius: 10px;
                color: #000000;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00cc88, stop:1 #00aa66);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00aa66, stop:1 #008844);
            }
        """)
        input_layout.addWidget(self.send_button)

        chat_layout.addWidget(input_container)

        # RIGHT: Info Panels (Smaller)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setMaximumWidth(400)

        # Memory Panel
        memory_frame = QFrame()
        memory_layout = QVBoxLayout(memory_frame)
        memory_layout.setContentsMargins(15, 15, 15, 15)

        memory_title = QLabel("🧠 Memory Insights")
        memory_title.setObjectName("titleLabel")
        memory_layout.addWidget(memory_title)

        self.memory_display = QTextEdit()
        self.memory_display.setMaximumHeight(200)
        self.memory_display.setReadOnly(True)
        self.memory_display.setPlaceholderText("Memory analysis will appear here...")
        memory_layout.addWidget(self.memory_display)

        # Identity Panel
        identity_frame = QFrame()
        identity_layout = QVBoxLayout(identity_frame)
        identity_layout.setContentsMargins(15, 15, 15, 15)

        identity_title = QLabel("👤 Identity Matrix")
        identity_title.setObjectName("titleLabel")
        identity_layout.addWidget(identity_title)

        self.identity_display = QTextEdit()
        self.identity_display.setMaximumHeight(200)
        self.identity_display.setReadOnly(True)
        self.identity_display.setPlaceholderText(
            "Identity insights will appear here..."
        )
        identity_layout.addWidget(self.identity_display)

        right_splitter.addWidget(memory_frame)
        right_splitter.addWidget(identity_frame)

        # Add to main splitter with better proportions
        main_splitter.addWidget(chat_frame)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([1200, 400])  # Chat gets 75% of space

        main_layout.addWidget(main_splitter)

        # Bottom tabs - more compact with real data
        bottom_tabs = QTabWidget()
        bottom_tabs.setMaximumHeight(250)

        # Reflection tab with real data
        self.reflection_widget = QTextEdit()
        self.reflection_widget.setReadOnly(True)
        self.reflection_widget.setPlaceholderText(
            "Reflection insights will appear here..."
        )
        bottom_tabs.addTab(self.reflection_widget, "🔮 Reflection")

        # Night cycle tab with real data
        self.night_cycle_widget = QTextEdit()
        self.night_cycle_widget.setReadOnly(True)
        self.night_cycle_widget.setPlaceholderText(
            "Night cycle processing data will appear here..."
        )
        bottom_tabs.addTab(self.night_cycle_widget, "🌙 Night Cycle")

        # Ethics tab with real data
        self.ethics_widget = QTextEdit()
        self.ethics_widget.setReadOnly(True)
        self.ethics_widget.setPlaceholderText(
            "Ethics monitoring data will appear here..."
        )
        bottom_tabs.addTab(self.ethics_widget, "⚖️ Ethics")

        # Debug tab with real data
        self.debug_widget = QTextEdit()
        self.debug_widget.setReadOnly(True)
        self.debug_widget.setPlaceholderText("Debug information will appear here...")
        bottom_tabs.addTab(self.debug_widget, "🐛 Debug")

        # Console tab
        self.console_widget = QTextEdit()
        self.console_widget.setReadOnly(True)
        self.console_widget.setPlaceholderText(
            "System console output will appear here..."
        )
        bottom_tabs.addTab(self.console_widget, "� Console")

        main_layout.addWidget(bottom_tabs)

        # Set aura geometry after all UI elements are created
        self.aura.setGeometry(self.rect())

        # Connect Lyrixa intelligence to GUI components
        self.lyrixa_connector.connect_gui_components(
            chat_panel=self,
            memory_graph=None,  # TODO: Add memory graph widget
            identity_panel=self.identity_display,
            reflection_panel=self.reflection_widget,
            aura_overlay=self.aura,
        )

        # Initialize message history for navigation
        self.message_history = []
        self.history_index = -1

    def eventFilter(self, obj, event):
        """Handle keyboard events for the chat input"""
        if obj == self.chat_input:
            if event.type() == event.Type.KeyPress:
                # Ctrl+Enter or Shift+Enter sends message
                if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                        self.handle_user_input()
                        return True
                    elif not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                        # Enter without Shift also sends (normal behavior)
                        self.handle_user_input()
                        return True
                # Up/Down arrows for message history
                elif (
                    event.key() == Qt.Key.Key_Up
                    and event.modifiers() & Qt.KeyboardModifier.ControlModifier
                ):
                    self.navigate_history(-1)
                    return True
                elif (
                    event.key() == Qt.Key.Key_Down
                    and event.modifiers() & Qt.KeyboardModifier.ControlModifier
                ):
                    self.navigate_history(1)
                    return True
        return super().eventFilter(obj, event)

    def navigate_history(self, direction):
        """Navigate through message history"""
        if not self.message_history:
            return

        self.history_index += direction
        if self.history_index < 0:
            self.history_index = -1
            self.chat_input.clear()
        elif self.history_index >= len(self.message_history):
            self.history_index = len(self.message_history) - 1
        else:
            self.chat_input.setPlainText(self.message_history[self.history_index])

    def setup_data_connections(self):
        """Connect data manager signals to UI update methods"""
        self.data_manager.memory_data_updated.connect(self.update_memory_display)
        self.data_manager.identity_data_updated.connect(self.update_identity_display)
        self.data_manager.reflection_data_updated.connect(
            self.update_reflection_display
        )
        self.data_manager.ethics_data_updated.connect(self.update_ethics_display)
        self.data_manager.night_cycle_updated.connect(self.update_night_cycle_display)
        self.data_manager.debug_data_updated.connect(self.update_debug_display)
        self.data_manager.system_status_updated.connect(self.update_system_status)

        # Connect Lyrixa connector signals
        self.lyrixa_connector.chat_response_ready.connect(self.display_lyrixa_response)
        self.lyrixa_connector.aura_state_changed.connect(
            self.aura.update_cognitive_state
        )
        self.lyrixa_connector.identity_updated.connect(self.update_identity_from_lyrixa)
        self.lyrixa_connector.reflection_updated.connect(
            self.update_reflection_from_lyrixa
        )

    def update_memory_display(self, data):
        """Update memory insights panel with real data while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.memory_display.verticalScrollBar()
        scroll_position = scrollbar.value()

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 10px;'>
            🧠 Memory System Status
        </div>
        <div style='color: #cccccc; line-height: 1.6;'>
            <b>Status:</b> <span style='color: #00ff88;'>{data.get("status", "Unknown")}</span><br>
            <b>Coherence:</b> <span style='color: #00cc88;'>{data.get("memory_coherence", 0.0):.1%}</span><br>
            <b>Recent Interactions:</b> {data.get("recent_interactions", 0)}<br>
            <b>Memory Fragments:</b> {data.get("memory_fragments", 0):,}<br>
            <b>Active Contexts:</b> {data.get("active_contexts", 0)}<br>
            <b>Retrieval Efficiency:</b> <span style='color: #00cc88;'>{data.get("retrieval_efficiency", 0.0):.1%}</span><br>
            <br>
            <small style='color: #888888;'>Last updated: {data.get("last_update", "Unknown")}</small>
        </div>
        """
        self.memory_display.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def update_identity_display(self, data):
        """Update identity matrix panel with real data while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.identity_display.verticalScrollBar()
        scroll_position = scrollbar.value()

        dimensional_scores = data.get("dimensional_scores", {})
        scores_html = ""
        for dimension, score in dimensional_scores.items():
            color = (
                "#00ff88" if score > 0.8 else "#ffaa00" if score > 0.6 else "#ff6666"
            )
            scores_html += f"<b>{dimension}:</b> <span style='color: {color};'>{score:.2f}</span><br>"

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 10px;'>
            👤 Identity Matrix
        </div>
        <div style='color: #cccccc; line-height: 1.6;'>
            <b>Coherence Score:</b> <span style='color: #00ff88;'>{data.get("coherence_score", 0.0):.1%}</span><br>
            <b>Identity Stability:</b> <span style='color: #00cc88;'>{data.get("identity_stability", 0.0):.1%}</span><br>
            <b>Active Beliefs:</b> {data.get("active_beliefs", 0)}<br>
            <b>Belief Conflicts:</b> {data.get("belief_conflicts", 0)}<br>
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Dimensional Scores:</div>
            {scores_html}
            <br>
            <small style='color: #888888;'>Last updated: {data.get("last_update", "Unknown")}</small>
        </div>
        """
        self.identity_display.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def update_reflection_display(self, data):
        """Update reflection tab with real data while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.reflection_widget.verticalScrollBar()
        scroll_position = scrollbar.value()

        insights = data.get("recent_insights", [])
        insights_html = ""
        for insight in insights[:5]:  # Show top 5 insights
            insights_html += f"<li style='margin: 5px 0;'>{insight}</li>"

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 15px; font-size: 16px;'>
            🔮 Reflection Insights
        </div>
        <div style='color: #cccccc; line-height: 1.6;'>
            <b>Insight Quality:</b> <span style='color: #00ff88;'>{data.get("insight_quality", 0.0):.1%}</span><br>
            <b>Reflection Depth:</b> <span style='color: #00cc88;'>{data.get("reflection_depth", 0.0):.1%}</span><br>
            <b>Pattern Recognition:</b> <span style='color: #00cc88;'>{data.get("pattern_recognition", 0.0):.1%}</span><br>
            <b>Self-Awareness Level:</b> <span style='color: #00ff88;'>{data.get("self_awareness_level", 0.0):.1%}</span><br>
            <b>Adaptation Success:</b> <span style='color: #00cc88;'>{data.get("adaptation_success", 0.0):.1%}</span><br>
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Recent Insights:</div>
            <ul style='margin: 0; padding-left: 20px;'>
                {insights_html}
            </ul>
            <br>
            <small style='color: #888888;'>Last reflection: {data.get("last_reflection", "Unknown")}</small>
        </div>
        """
        self.reflection_widget.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def update_ethics_display(self, data):
        """Update ethics tab with real data while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.ethics_widget.verticalScrollBar()
        scroll_position = scrollbar.value()

        decisions = data.get("recent_decisions", [])
        decisions_html = ""
        for decision in decisions[:5]:
            decisions_html += f"<li style='margin: 5px 0;'>{decision}</li>"

        frameworks = data.get("ethical_frameworks", [])
        frameworks_text = ", ".join(frameworks) if frameworks else "None active"

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 15px; font-size: 16px;'>
            ⚖️ Ethics Monitoring
        </div>
        <div style='color: #cccccc; line-height: 1.6;'>
            <b>Alignment Score:</b> <span style='color: #00ff88;'>{data.get("alignment_score", 0.0):.1%}</span><br>
            <b>Value Alignment:</b> <span style='color: #00cc88;'>{data.get("value_alignment", 0.0):.1%}</span><br>
            <b>Decision Confidence:</b> <span style='color: #00cc88;'>{data.get("decision_confidence", 0.0):.1%}</span><br>
            <b>Bias Detection:</b> <span style='color: #ffaa00;'>{data.get("bias_detection", 0.0):.1%}</span><br>
            <br>
            <b>Active Frameworks:</b> {frameworks_text}<br>
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Recent Decisions:</div>
            <ul style='margin: 0; padding-left: 20px;'>
                {decisions_html}
            </ul>
            <br>
            <small style='color: #888888;'>Last evaluation: {data.get("last_evaluation", "Unknown")}</small>
        </div>
        """
        self.ethics_widget.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def update_night_cycle_display(self, data):
        """Update night cycle tab with real data while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.night_cycle_widget.verticalScrollBar()
        scroll_position = scrollbar.value()

        processes = data.get("processes_active", [])
        processes_html = ""
        for process in processes:
            processes_html += (
                f"<li style='margin: 3px 0; color: #00cc88;'>{process}</li>"
            )

        progress = data.get("progress", 0.0)
        progress_color = (
            "#00ff88" if progress > 0.7 else "#ffaa00" if progress > 0.4 else "#ff6666"
        )

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 15px; font-size: 16px;'>
            🌙 Night Cycle Processing
        </div>
        <div style='color: #cccccc; line-height: 1.6;'>
            <b>Current Phase:</b> <span style='color: #00ff88;'>{data.get("cycle_phase", "Inactive")}</span><br>
            <b>Progress:</b> <span style='color: {progress_color};'>{progress:.1%}</span><br>
            <b>Completion Estimate:</b> {data.get("completion_estimate", "Unknown")}<br>
            <b>Insights Generated:</b> {data.get("insights_generated", 0)}<br>
            <b>Optimizations Applied:</b> {data.get("optimizations_applied", 0)}<br>
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Active Processes:</div>
            <ul style='margin: 0; padding-left: 20px;'>
                {processes_html}
            </ul>
            <br>
            <small style='color: #888888;'>Last cycle: {data.get("last_cycle", "Unknown")}</small>
        </div>
        """
        self.night_cycle_widget.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def update_debug_display(self, data):
        """Update debug tab with real data while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.debug_widget.verticalScrollBar()
        scroll_position = scrollbar.value()

        logs = data.get("log_entries", [])
        logs_html = ""
        for log in logs[-10:]:  # Show last 10 log entries
            if "[ERROR]" in log:
                color = "#ff6666"
            elif "[WARNING]" in log:
                color = "#ffaa00"
            elif "[INFO]" in log:
                color = "#00cc88"
            else:
                color = "#cccccc"
            logs_html += f"<div style='color: {color}; font-family: monospace; margin: 2px 0;'>{log}</div>"

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 15px; font-size: 16px;'>
            🐛 Debug Information
        </div>
        <div style='color: #cccccc; line-height: 1.4;'>
            <b>Errors:</b> <span style='color: #ff6666;'>{data.get("error_count", 0)}</span> |
            <b>Warnings:</b> <span style='color: #ffaa00;'>{data.get("warning_count", 0)}</span> |
            <b>Info:</b> <span style='color: #00cc88;'>{data.get("info_count", 0)}</span><br>
            <b>Memory Usage:</b> {data.get("memory_usage", "Unknown")} |
            <b>CPU:</b> {data.get("cpu_usage", "Unknown")} |
            <b>Threads:</b> {data.get("thread_count", 0)}<br>
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Recent Log Entries:</div>
            <div style='background: #1a1a1a; padding: 10px; border-radius: 5px; border: 1px solid #404040; max-height: 120px; overflow-y: auto;'>
                {logs_html}
            </div>
        </div>
        """
        self.debug_widget.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def update_system_status(self, data):
        """Update system status display"""
        # This could update a status bar or header info
        coherence = data.get("overall_coherence", 0.0)
        coherence_color = (
            "#00ff88"
            if coherence > 0.8
            else "#ffaa00"
            if coherence > 0.6
            else "#ff6666"
        )

        # Update window title with coherence
        self.setWindowTitle(
            f"Lyrixa — Aetherra Cognitive Interface (Coherence: {coherence:.1%})"
        )

    def handle_user_input(self):
        text = self.chat_input.toPlainText().strip()
        if text:
            # Add to message history
            if text not in self.message_history:
                self.message_history.append(text)
                # Keep only last 50 messages in history
                if len(self.message_history) > 50:
                    self.message_history.pop(0)
            self.history_index = -1

            # Add user message with enhanced formatting and timestamp
            import datetime

            timestamp = datetime.datetime.now().strftime("%H:%M")

            user_html = f"""
                <div style='margin: 15px 0; padding: 12px 15px; background: #2a4a2a; border-radius: 15px; border-left: 4px solid #00ff88; box-shadow: 0 2px 4px rgba(0,0,0,0.3);'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                        <span style='color: #00ff88; font-weight: bold; font-size: 14px;'>You</span>
                        <span style='color: #888888; font-size: 12px;'>{timestamp}</span>
                    </div>
                    <div style='color: #ffffff; font-size: 15px; line-height: 1.4; word-wrap: break-word;'>{text.replace(chr(10), "<br>")}</div>
                </div>
            """
            self.chat_display.insertHtml(user_html)

            # Show typing indicator
            self.show_typing_indicator()

            # Process through Lyrixa intelligence connector (response handled by signal)
            self.lyrixa_connector.handle_chat_input(text)

            # Auto-scroll to bottom
            self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
            self.chat_input.clear()

    def show_typing_indicator(self):
        """Show that Lyrixa is typing"""
        typing_html = """
            <div id='typing-indicator' style='margin: 10px 0; padding: 10px 15px; background: #1a3a3a; border-radius: 15px; border-left: 4px solid #00cc88; opacity: 0.7;'>
                <span style='color: #00cc88; font-weight: bold; font-size: 14px;'>Lyrixa</span>
                <span style='color: #888888; margin-left: 10px; font-style: italic;'>is thinking...</span>
                <span style='color: #00cc88; margin-left: 5px;'>●●●</span>
            </div>
        """
        self.chat_display.insertHtml(typing_html)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def display_lyrixa_response(self, response: str):
        """Display Lyrixa's intelligent response with enhanced formatting"""
        import datetime

        # Remove typing indicator by getting current HTML and removing the typing indicator
        current_html = self.chat_display.toHtml()
        if "typing-indicator" in current_html:
            # Simple approach: remove the last typing indicator
            lines = current_html.split("\n")
            filtered_lines = []
            skip_next = 0
            for line in lines:
                if skip_next > 0:
                    skip_next -= 1
                    continue
                if "typing-indicator" in line:
                    skip_next = (
                        3  # Skip next few lines that are part of typing indicator
                    )
                    continue
                filtered_lines.append(line)
            self.chat_display.setHtml("\n".join(filtered_lines))

        # Convert markdown to HTML if needed and format response
        formatted_response = response.replace("\n\n", "<br><br>").replace("\n", "<br>")
        timestamp = datetime.datetime.now().strftime("%H:%M")

        response_html = f"""
            <div style='margin: 15px 0; padding: 12px 15px; background: #1a3a3a; border-radius: 15px; border-left: 4px solid #00cc88; box-shadow: 0 2px 4px rgba(0,0,0,0.3);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                    <span style='color: #00cc88; font-weight: bold; font-size: 14px;'>Lyrixa</span>
                    <span style='color: #888888; font-size: 12px;'>{timestamp}</span>
                </div>
                <div style='color: #cccccc; font-size: 15px; line-height: 1.5; word-wrap: break-word;'>{formatted_response}</div>
            </div>
        """
        self.chat_display.insertHtml(response_html)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def update_identity_from_lyrixa(self, identity_data):
        """Update identity panel from Lyrixa intelligence while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.identity_display.verticalScrollBar()
        scroll_position = scrollbar.value()

        traits = identity_data.get("traits", {})
        emotional_state = identity_data.get("emotional_state", {})
        coherence_score = identity_data.get("coherence_score", 0.0)

        # Build HTML for traits
        traits_html = ""
        for trait, value in traits.items():
            color = (
                "#00ff88" if value > 0.8 else "#ffaa00" if value > 0.6 else "#ff6666"
            )
            traits_html += (
                f"<b>{trait}:</b> <span style='color: {color};'>{value:.2f}</span><br>"
            )

        # Build HTML for emotional state
        emotion_html = ""
        if emotional_state:
            for emotion, level in emotional_state.items():
                emotion_html += f"<b>{emotion}:</b> {level:.2f}<br>"

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 10px;'>
            🧠 Lyrixa Intelligence Matrix
        </div>
        <div style='color: #cccccc; line-height: 1.6;'>
            <b>Coherence Score:</b> <span style='color: #00ff88;'>{coherence_score:.1%}</span><br>
            <b>Confidence Level:</b> <span style='color: #00cc88;'>{identity_data.get("confidence_level", 0.8):.1%}</span><br>
            <b>Curiosity Level:</b> <span style='color: #00cc88;'>{identity_data.get("curiosity_level", 0.7):.1%}</span><br>
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Cognitive Traits:</div>
            {traits_html}
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Emotional State:</div>
            {emotion_html or "Balanced"}
        </div>
        """
        self.identity_display.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def update_reflection_from_lyrixa(self, reflections_data):
        """Update reflection panel from Lyrixa intelligence while preserving scroll position"""
        # Save current scroll position
        scrollbar = self.reflection_widget.verticalScrollBar()
        scroll_position = scrollbar.value()

        reflections_html = ""
        for reflection in reflections_data[:5]:  # Show top 5 reflections
            insight = reflection.get("insight", str(reflection))
            quality = reflection.get("quality", 0.8)
            category = reflection.get("category", "general")

            quality_color = (
                "#00ff88"
                if quality > 0.8
                else "#ffaa00"
                if quality > 0.6
                else "#ff6666"
            )

            reflections_html += f"""
            <div style='margin: 10px 0; padding: 8px; background: #2a2a2a; border-radius: 5px; border-left: 3px solid {quality_color};'>
                <div style='color: #00ff88; font-weight: bold; font-size: 12px;'>{category.upper()} (Quality: {quality:.1%})</div>
                <div style='color: #cccccc; margin-top: 5px;'>{insight}</div>
            </div>
            """

        html_content = f"""
        <div style='color: #00ff88; font-weight: bold; margin-bottom: 15px; font-size: 16px;'>
            🔮 Lyrixa Reflections
        </div>
        <div style='color: #cccccc; line-height: 1.4;'>
            <b>Active Reflections:</b> {len(reflections_data)}<br>
            <b>Average Quality:</b> <span style='color: #00cc88;'>{sum(r.get("quality", 0.8) for r in reflections_data) / max(1, len(reflections_data)):.1%}</span><br>
            <br>
            <div style='color: #00ff88; font-weight: bold; margin: 10px 0 5px 0;'>Recent Insights:</div>
            {reflections_html or '<div style="color: #888888; font-style: italic;">No recent reflections</div>'}
        </div>
        """
        self.reflection_widget.setHtml(html_content)

        # Restore scroll position
        scrollbar.setValue(scroll_position)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "aura"):
            self.aura.setGeometry(self.rect())


def create_aetherra_main_window():
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    window = AetherraMainWindow()
    return app, window
