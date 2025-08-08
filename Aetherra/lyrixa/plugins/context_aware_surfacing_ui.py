"""
Context Aware Surfacing Plugin UI
Intelligent content recommendation and surfacing system
"""

import json
import sqlite3
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSlider,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ContextAwareSurfacingUI(QWidget):
    """Context Aware Surfacing Plugin UI for intelligent content recommendations."""

    def __init__(self):
        super().__init__()
        self.db_path = Path(__file__).parent.parent / "context_surfacing.db"
        self.init_database()
        self.setup_ui()
        self.apply_styling()
        self.load_context_data()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_recommendations)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds

    def init_database(self):
        """Initialize the context surfacing database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create contexts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contexts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        context_type TEXT NOT NULL,
                        context_data TEXT NOT NULL,
                        relevance_score REAL DEFAULT 0.5,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        active BOOLEAN DEFAULT 1
                    )
                """)

                # Create surfaced_content table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS surfaced_content (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id TEXT NOT NULL,
                        content_type TEXT NOT NULL,
                        content_data TEXT NOT NULL,
                        context_id INTEGER,
                        relevance_score REAL DEFAULT 0.5,
                        surfaced_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_interaction INTEGER DEFAULT 0,
                        FOREIGN KEY (context_id) REFERENCES contexts (id)
                    )
                """)

                conn.commit()

        except Exception as e:
            print(f"Database initialization error: {e}")

    def setup_ui(self):
        """Set up the context aware surfacing interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🎯 Context Aware Surfacing")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #ff6b6b; margin: 10px;"
        )
        layout.addWidget(title)

        # Create main tab widget
        self.tabs = QTabWidget()

        # Live Recommendations Tab
        self.tabs.addTab(self.create_live_recommendations(), "🔮 Live Recommendations")

        # Context Analysis Tab
        self.tabs.addTab(self.create_context_analysis(), "📊 Context Analysis")

        # Surfacing Rules Tab
        self.tabs.addTab(self.create_surfacing_rules(), "⚙️ Surfacing Rules")

        # Content Library Tab
        self.tabs.addTab(self.create_content_library(), "📚 Content Library")

        # Performance Tab
        self.tabs.addTab(self.create_performance_dashboard(), "📈 Performance")

        layout.addWidget(self.tabs)

    def create_live_recommendations(self):
        """Create the live recommendations interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Current context display
        context_group = QGroupBox("🎯 Current Context")
        context_layout = QVBoxLayout(context_group)

        self.current_context_display = QTextEdit()
        self.current_context_display.setReadOnly(True)
        self.current_context_display.setMaximumHeight(100)
        self.current_context_display.setPlainText("Analyzing current context...")
        context_layout.addWidget(self.current_context_display)

        # Context controls
        controls_layout = QHBoxLayout()
        refresh_context_btn = QPushButton("🔄 Refresh Context")
        clear_context_btn = QPushButton("🗑️ Clear Context")
        controls_layout.addWidget(refresh_context_btn)
        controls_layout.addWidget(clear_context_btn)
        context_layout.addLayout(controls_layout)

        layout.addWidget(context_group)

        # Recommendations display
        rec_group = QGroupBox("💡 Smart Recommendations")
        rec_layout = QVBoxLayout(rec_group)

        # Recommendation filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by:"))

        self.content_type_filter = QComboBox()
        self.content_type_filter.addItems(
            ["All Types", "Documents", "Conversations", "Code", "Web", "Notes"]
        )
        filter_layout.addWidget(self.content_type_filter)

        self.relevance_threshold = QSlider(Qt.Orientation.Horizontal)
        self.relevance_threshold.setRange(0, 100)
        self.relevance_threshold.setValue(30)
        filter_layout.addWidget(QLabel("Min Relevance:"))
        filter_layout.addWidget(self.relevance_threshold)

        rec_layout.addLayout(filter_layout)

        # Recommendations list
        self.recommendations_list = QListWidget()
        rec_layout.addWidget(self.recommendations_list)

        # Recommendation actions
        action_layout = QHBoxLayout()
        pin_btn = QPushButton("📌 Pin Selected")
        dismiss_btn = QPushButton("❌ Dismiss")
        feedback_btn = QPushButton("👍 Provide Feedback")
        action_layout.addWidget(pin_btn)
        action_layout.addWidget(dismiss_btn)
        action_layout.addWidget(feedback_btn)
        rec_layout.addLayout(action_layout)

        layout.addWidget(rec_group)

        # Connect signals
        refresh_context_btn.clicked.connect(self.refresh_context)
        clear_context_btn.clicked.connect(self.clear_context)
        self.content_type_filter.currentTextChanged.connect(self.filter_recommendations)
        self.relevance_threshold.valueChanged.connect(self.filter_recommendations)

        return widget

    def create_context_analysis(self):
        """Create the context analysis dashboard."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Context timeline
        timeline_group = QGroupBox("📅 Context Timeline")
        timeline_layout = QVBoxLayout(timeline_group)

        self.context_timeline = QTreeWidget()
        self.context_timeline.setHeaderLabels(
            ["Time", "Context Type", "Content", "Relevance"]
        )
        timeline_layout.addWidget(self.context_timeline)

        layout.addWidget(timeline_group)

        # Context patterns
        patterns_group = QGroupBox("🔍 Context Patterns")
        patterns_layout = QGridLayout(patterns_group)

        patterns_layout.addWidget(QLabel("Most Active Context Type:"), 0, 0)
        self.most_active_context = QLabel("Unknown")
        patterns_layout.addWidget(self.most_active_context, 0, 1)

        patterns_layout.addWidget(QLabel("Average Context Switch Rate:"), 1, 0)
        self.context_switch_rate = QLabel("0/hour")
        patterns_layout.addWidget(self.context_switch_rate, 1, 1)

        patterns_layout.addWidget(QLabel("Peak Activity Time:"), 2, 0)
        self.peak_activity_time = QLabel("Unknown")
        patterns_layout.addWidget(self.peak_activity_time, 2, 1)

        layout.addWidget(patterns_group)

        # Context heatmap
        heatmap_group = QGroupBox("🌡️ Context Relevance Heatmap")
        heatmap_layout = QVBoxLayout(heatmap_group)

        self.relevance_bars = {}
        for context_type in [
            "Work",
            "Personal",
            "Learning",
            "Entertainment",
            "Communication",
        ]:
            bar_layout = QHBoxLayout()
            bar_layout.addWidget(QLabel(f"{context_type}:"))

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            self.relevance_bars[context_type] = progress_bar

            bar_layout.addWidget(progress_bar)
            heatmap_layout.addLayout(bar_layout)

        layout.addWidget(heatmap_group)

        return widget

    def create_surfacing_rules(self):
        """Create the surfacing rules configuration interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Active rules
        rules_group = QGroupBox("📋 Active Surfacing Rules")
        rules_layout = QVBoxLayout(rules_group)

        self.rules_list = QListWidget()
        rules_layout.addWidget(self.rules_list)

        # Rule controls
        rule_controls = QHBoxLayout()
        add_rule_btn = QPushButton("➕ Add Rule")
        edit_rule_btn = QPushButton("✏️ Edit Selected")
        delete_rule_btn = QPushButton("🗑️ Delete Selected")

        rule_controls.addWidget(add_rule_btn)
        rule_controls.addWidget(edit_rule_btn)
        rule_controls.addWidget(delete_rule_btn)
        rules_layout.addLayout(rule_controls)

        layout.addWidget(rules_group)

        # Rule creation
        create_group = QGroupBox("🔧 Create New Rule")
        create_layout = QGridLayout(create_group)

        create_layout.addWidget(QLabel("Rule Name:"), 0, 0)
        self.rule_name_input = QLineEdit()
        create_layout.addWidget(self.rule_name_input, 0, 1)

        create_layout.addWidget(QLabel("Trigger Context:"), 1, 0)
        self.trigger_context_input = QLineEdit()
        self.trigger_context_input.setPlaceholderText(
            "e.g., 'coding', 'meeting', 'research'"
        )
        create_layout.addWidget(self.trigger_context_input, 1, 1)

        create_layout.addWidget(QLabel("Content Types:"), 2, 0)
        self.content_types_input = QLineEdit()
        self.content_types_input.setPlaceholderText("e.g., 'documents,code,notes'")
        create_layout.addWidget(self.content_types_input, 2, 1)

        create_layout.addWidget(QLabel("Min Relevance:"), 3, 0)
        self.min_relevance_slider = QSlider(Qt.Orientation.Horizontal)
        self.min_relevance_slider.setRange(0, 100)
        self.min_relevance_slider.setValue(50)
        create_layout.addWidget(self.min_relevance_slider, 3, 1)

        create_layout.addWidget(QLabel("Active:"), 4, 0)
        self.rule_active_checkbox = QCheckBox()
        self.rule_active_checkbox.setChecked(True)
        create_layout.addWidget(self.rule_active_checkbox, 4, 1)

        save_rule_btn = QPushButton("💾 Save Rule")
        create_layout.addWidget(save_rule_btn, 5, 0, 1, 2)

        layout.addWidget(create_group)

        # Connect signals
        save_rule_btn.clicked.connect(self.save_surfacing_rule)

        return widget

    def create_content_library(self):
        """Create the content library management interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Content sources
        sources_group = QGroupBox("📂 Content Sources")
        sources_layout = QVBoxLayout(sources_group)

        self.content_sources = QListWidget()
        sources_layout.addWidget(self.content_sources)

        # Source controls
        source_controls = QHBoxLayout()
        add_source_btn = QPushButton("➕ Add Source")
        scan_source_btn = QPushButton("🔍 Scan Sources")
        refresh_source_btn = QPushButton("🔄 Refresh")

        source_controls.addWidget(add_source_btn)
        source_controls.addWidget(scan_source_btn)
        source_controls.addWidget(refresh_source_btn)
        sources_layout.addLayout(source_controls)

        layout.addWidget(sources_group)

        # Content statistics
        stats_group = QGroupBox("📊 Content Statistics")
        stats_layout = QGridLayout(stats_group)

        stats_layout.addWidget(QLabel("Total Content Items:"), 0, 0)
        self.total_content_label = QLabel("0")
        stats_layout.addWidget(self.total_content_label, 0, 1)

        stats_layout.addWidget(QLabel("Indexed Content:"), 1, 0)
        self.indexed_content_label = QLabel("0")
        stats_layout.addWidget(self.indexed_content_label, 1, 1)

        stats_layout.addWidget(QLabel("Avg. Relevance Score:"), 2, 0)
        self.avg_relevance_label = QLabel("0.0")
        stats_layout.addWidget(self.avg_relevance_label, 2, 1)

        layout.addWidget(stats_group)

        # Recently surfaced content
        recent_group = QGroupBox("⏰ Recently Surfaced")
        recent_layout = QVBoxLayout(recent_group)

        self.recent_content = QListWidget()
        recent_layout.addWidget(self.recent_content)

        layout.addWidget(recent_group)

        return widget

    def create_performance_dashboard(self):
        """Create the performance monitoring dashboard."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Performance metrics
        metrics_group = QGroupBox("⚡ Performance Metrics")
        metrics_layout = QGridLayout(metrics_group)

        metrics_layout.addWidget(QLabel("Recommendations/Hour:"), 0, 0)
        self.recommendations_per_hour = QLabel("0")
        metrics_layout.addWidget(self.recommendations_per_hour, 0, 1)

        metrics_layout.addWidget(QLabel("User Interaction Rate:"), 1, 0)
        self.interaction_rate = QLabel("0%")
        metrics_layout.addWidget(self.interaction_rate, 1, 1)

        metrics_layout.addWidget(QLabel("Average Response Time:"), 2, 0)
        self.response_time = QLabel("0ms")
        metrics_layout.addWidget(self.response_time, 2, 1)

        metrics_layout.addWidget(QLabel("Context Accuracy:"), 3, 0)
        self.context_accuracy = QLabel("0%")
        metrics_layout.addWidget(self.context_accuracy, 3, 1)

        layout.addWidget(metrics_group)

        # Success rate visualization
        success_group = QGroupBox("📈 Success Rates")
        success_layout = QVBoxLayout(success_group)

        # Context detection success
        context_success_layout = QHBoxLayout()
        context_success_layout.addWidget(QLabel("Context Detection:"))
        self.context_detection_bar = QProgressBar()
        self.context_detection_bar.setRange(0, 100)
        context_success_layout.addWidget(self.context_detection_bar)
        success_layout.addLayout(context_success_layout)

        # Recommendation relevance
        relevance_success_layout = QHBoxLayout()
        relevance_success_layout.addWidget(QLabel("Recommendation Relevance:"))
        self.relevance_success_bar = QProgressBar()
        self.relevance_success_bar.setRange(0, 100)
        relevance_success_layout.addWidget(self.relevance_success_bar)
        success_layout.addLayout(relevance_success_layout)

        # User satisfaction
        satisfaction_layout = QHBoxLayout()
        satisfaction_layout.addWidget(QLabel("User Satisfaction:"))
        self.satisfaction_bar = QProgressBar()
        self.satisfaction_bar.setRange(0, 100)
        satisfaction_layout.addWidget(self.satisfaction_bar)
        success_layout.addLayout(satisfaction_layout)

        layout.addWidget(success_group)

        # System health
        health_group = QGroupBox("🏥 System Health")
        health_layout = QVBoxLayout(health_group)

        self.system_health_status = QLabel("System Status: Operational")
        self.last_update_status = QLabel("Last Update: Just now")
        self.error_count_status = QLabel("Errors (24h): 0")

        health_layout.addWidget(self.system_health_status)
        health_layout.addWidget(self.last_update_status)
        health_layout.addWidget(self.error_count_status)

        layout.addWidget(health_group)

        return widget

    def apply_styling(self):
        """Apply dark theme styling to the context surfacing interface."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ff6b6b;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ff6b6b;
            }
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid #666666;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #ff6b6b;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QLineEdit, QTextEdit {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #ff6b6b;
            }
            QListWidget, QTreeWidget {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                alternate-background-color: #404040;
            }
            QListWidget::item, QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #ff6b6b;
                color: white;
            }
            QListWidget::item:hover, QTreeWidget::item:hover {
                background-color: #505050;
            }
            QProgressBar {
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #ff6b6b;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #666666;
                height: 8px;
                background: #353535;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ff6b6b;
                border: 1px solid #666666;
                width: 18px;
                border-radius: 9px;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #666666;
                border-radius: 3px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #ff6b6b;
            }
        """)

    def load_context_data(self):
        """Load context data from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Load recent contexts
                cursor.execute("""
                    SELECT context_type, context_data, relevance_score, timestamp
                    FROM contexts
                    WHERE active = 1
                    ORDER BY timestamp DESC
                    LIMIT 50
                """)

                contexts = cursor.fetchall()
                self.populate_context_timeline(contexts)
                self.update_context_patterns()

        except Exception as e:
            print(f"Error loading context data: {e}")

    def populate_context_timeline(self, contexts):
        """Populate the context timeline."""
        self.context_timeline.clear()

        for context in contexts:
            context_type, context_data, relevance_score, timestamp = context

            item = QTreeWidgetItem(
                [
                    timestamp,
                    context_type,
                    context_data[:100] + "..."
                    if len(context_data) > 100
                    else context_data,
                    f"{relevance_score:.2f}",
                ]
            )

            # Color code by relevance
            if relevance_score > 0.7:
                item.setBackground(
                    0, QColor(255, 107, 107, 50)
                )  # Red tint for high relevance
            elif relevance_score < 0.3:
                item.setBackground(
                    0, QColor(107, 107, 255, 30)
                )  # Blue tint for low relevance

            self.context_timeline.addTopLevelItem(item)

    def refresh_context(self):
        """Refresh the current context."""
        self.current_context_display.setPlainText("Refreshing context analysis...")
        # Simulate context refresh
        QTimer.singleShot(
            1000,
            lambda: self.current_context_display.setPlainText(
                "Current Context: Working on Python development project\n"
                "Keywords: programming, python, GUI, PySide6\n"
                "Confidence: 85%"
            ),
        )

    def clear_context(self):
        """Clear the current context."""
        self.current_context_display.setPlainText("Context cleared. Analyzing...")

    def filter_recommendations(self):
        """Filter recommendations based on current filters."""
        # Implementation for filtering recommendations
        pass

    def update_context_patterns(self):
        """Update context pattern analysis."""
        # Update relevance bars with sample data
        sample_data = {
            "Work": 75,
            "Personal": 45,
            "Learning": 90,
            "Entertainment": 20,
            "Communication": 60,
        }

        for context_type, value in sample_data.items():
            if context_type in self.relevance_bars:
                self.relevance_bars[context_type].setValue(value)

        # Update pattern labels
        self.most_active_context.setText("Learning")
        self.context_switch_rate.setText("12/hour")
        self.peak_activity_time.setText("14:00-16:00")

    def save_surfacing_rule(self):
        """Save a new surfacing rule."""
        rule_name = self.rule_name_input.text().strip()
        if not rule_name:
            return

        # Create rule item
        rule_item = QListWidgetItem(f"🔧 {rule_name}")
        rule_item.setData(
            Qt.ItemDataRole.UserRole,
            {
                "name": rule_name,
                "trigger": self.trigger_context_input.text(),
                "content_types": self.content_types_input.text(),
                "min_relevance": self.min_relevance_slider.value(),
                "active": self.rule_active_checkbox.isChecked(),
            },
        )

        self.rules_list.addItem(rule_item)

        # Clear form
        self.rule_name_input.clear()
        self.trigger_context_input.clear()
        self.content_types_input.clear()
        self.min_relevance_slider.setValue(50)

    def refresh_recommendations(self):
        """Refresh recommendations periodically."""
        # Simulate new recommendations
        sample_recommendations = [
            "📄 Recent Python documentation updates",
            "💼 Similar UI design patterns in your codebase",
            "🔗 Related PySide6 tutorials and examples",
            "📝 Code snippets from similar projects",
            "🌐 Stack Overflow discussions on current topic",
        ]

        self.recommendations_list.clear()
        for rec in sample_recommendations:
            item = QListWidgetItem(rec)
            self.recommendations_list.addItem(item)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ContextAwareSurfacingUI()
    window.show()
    sys.exit(app.exec())
