"""
Advanced Memory System UI
Comprehensive interface for memory management and analysis
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont
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
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AdvancedMemorySystemUI(QWidget):
    """Advanced Memory System Plugin UI with comprehensive memory management."""

    def __init__(self):
        super().__init__()
        self.db_path = Path(__file__).parent.parent / "memory_system.db"
        self.init_database()
        self.setup_ui()
        self.apply_styling()
        self.load_memory_data()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_memory_stats)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def init_database(self):
        """Initialize the memory database if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create memories table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        context TEXT,
                        importance REAL DEFAULT 0.5,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        tags TEXT,
                        access_count INTEGER DEFAULT 0,
                        last_accessed DATETIME
                    )
                """)

                # Create memory_embeddings table for vector search
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_embeddings (
                        memory_id INTEGER,
                        embedding_vector TEXT,
                        FOREIGN KEY (memory_id) REFERENCES memories (id)
                    )
                """)

                conn.commit()

        except Exception as e:
            print(f"Database initialization error: {e}")

    def setup_ui(self):
        """Set up the comprehensive memory management interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🧠 Advanced Memory System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #00ff88; margin: 10px;"
        )
        layout.addWidget(title)

        # Create main tab widget
        self.tabs = QTabWidget()

        # Memory Browser Tab
        self.tabs.addTab(self.create_memory_browser(), "📖 Memory Browser")

        # Memory Analytics Tab
        self.tabs.addTab(self.create_memory_analytics(), "📊 Analytics")

        # Memory Search Tab
        self.tabs.addTab(self.create_memory_search(), "🔍 Advanced Search")

        # Memory Management Tab
        self.tabs.addTab(self.create_memory_management(), "⚙️ Management")

        # Add Memory Tab
        self.tabs.addTab(self.create_add_memory(), "➕ Add Memory")

        layout.addWidget(self.tabs)

    def create_memory_browser(self):
        """Create the memory browsing interface."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left panel - Memory list
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("📚 Recent Memories"))

        self.memory_list = QListWidget()
        left_layout.addWidget(self.memory_list)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.importance_filter = QComboBox()
        self.importance_filter.addItems(
            ["All", "High (>0.7)", "Medium (0.3-0.7)", "Low (<0.3)"]
        )
        filter_layout.addWidget(self.importance_filter)
        left_layout.addLayout(filter_layout)

        # Right panel - Memory details
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("💾 Memory Details"))

        self.memory_content = QTextEdit()
        self.memory_content.setReadOnly(True)
        right_layout.addWidget(self.memory_content)

        # Memory metadata
        metadata_layout = QGridLayout()
        metadata_layout.addWidget(QLabel("Importance:"), 0, 0)
        self.importance_display = QLabel("N/A")
        metadata_layout.addWidget(self.importance_display, 0, 1)

        metadata_layout.addWidget(QLabel("Access Count:"), 1, 0)
        self.access_count_display = QLabel("N/A")
        metadata_layout.addWidget(self.access_count_display, 1, 1)

        metadata_layout.addWidget(QLabel("Created:"), 2, 0)
        self.created_display = QLabel("N/A")
        metadata_layout.addWidget(self.created_display, 2, 1)

        right_layout.addLayout(metadata_layout)

        # Action buttons
        action_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️ Edit")
        delete_btn = QPushButton("🗑️ Delete")
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        right_layout.addLayout(action_layout)

        # Add panels to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

        # Connect signals
        self.memory_list.currentItemChanged.connect(self.on_memory_selected)
        self.importance_filter.currentTextChanged.connect(self.filter_memories)

        return widget

    def create_memory_analytics(self):
        """Create the memory analytics dashboard."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Stats overview
        stats_group = QGroupBox("📈 Memory Statistics")
        stats_layout = QGridLayout(stats_group)

        self.total_memories_label = QLabel("0")
        self.avg_importance_label = QLabel("0.0")
        self.most_accessed_label = QLabel("N/A")

        stats_layout.addWidget(QLabel("Total Memories:"), 0, 0)
        stats_layout.addWidget(self.total_memories_label, 0, 1)
        stats_layout.addWidget(QLabel("Average Importance:"), 1, 0)
        stats_layout.addWidget(self.avg_importance_label, 1, 1)
        stats_layout.addWidget(QLabel("Most Accessed:"), 2, 0)
        stats_layout.addWidget(self.most_accessed_label, 2, 1)

        layout.addWidget(stats_group)

        # Memory distribution
        dist_group = QGroupBox("📊 Importance Distribution")
        dist_layout = QVBoxLayout(dist_group)

        self.high_importance_bar = QProgressBar()
        self.medium_importance_bar = QProgressBar()
        self.low_importance_bar = QProgressBar()

        dist_layout.addWidget(QLabel("High Importance (>0.7):"))
        dist_layout.addWidget(self.high_importance_bar)
        dist_layout.addWidget(QLabel("Medium Importance (0.3-0.7):"))
        dist_layout.addWidget(self.medium_importance_bar)
        dist_layout.addWidget(QLabel("Low Importance (<0.3):"))
        dist_layout.addWidget(self.low_importance_bar)

        layout.addWidget(dist_group)

        # Recent activity
        activity_group = QGroupBox("🕒 Recent Activity")
        activity_layout = QVBoxLayout(activity_group)

        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)

        layout.addWidget(activity_group)

        return widget

    def create_memory_search(self):
        """Create the advanced memory search interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search controls
        search_group = QGroupBox("🔍 Search Parameters")
        search_layout = QVBoxLayout(search_group)

        # Text search
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Query:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search terms...")
        text_layout.addWidget(self.search_input)
        search_btn = QPushButton("🔍 Search")
        text_layout.addWidget(search_btn)
        search_layout.addLayout(text_layout)

        # Advanced filters
        filter_layout = QGridLayout()

        filter_layout.addWidget(QLabel("Min Importance:"), 0, 0)
        self.min_importance = QSlider(Qt.Orientation.Horizontal)
        self.min_importance.setRange(0, 100)
        self.min_importance.setValue(0)
        filter_layout.addWidget(self.min_importance, 0, 1)

        filter_layout.addWidget(QLabel("Max Results:"), 1, 0)
        self.max_results = QSpinBox()
        self.max_results.setRange(1, 1000)
        self.max_results.setValue(50)
        filter_layout.addWidget(self.max_results, 1, 1)

        filter_layout.addWidget(QLabel("Include Tags:"), 2, 0)
        self.include_tags = QLineEdit()
        self.include_tags.setPlaceholderText("comma,separated,tags")
        filter_layout.addWidget(self.include_tags, 2, 1)

        search_layout.addLayout(filter_layout)
        layout.addWidget(search_group)

        # Search results
        results_group = QGroupBox("📋 Search Results")
        results_layout = QVBoxLayout(results_group)

        self.search_results = QListWidget()
        results_layout.addWidget(self.search_results)

        layout.addWidget(results_group)

        # Connect search
        search_btn.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)

        return widget

    def create_memory_management(self):
        """Create the memory management interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Cleanup options
        cleanup_group = QGroupBox("🧹 Memory Cleanup")
        cleanup_layout = QVBoxLayout(cleanup_group)

        cleanup_options = QHBoxLayout()
        self.auto_cleanup = QCheckBox("Auto-cleanup low importance memories")
        cleanup_options.addWidget(self.auto_cleanup)

        cleanup_btn = QPushButton("🗑️ Clean Low Priority")
        cleanup_options.addWidget(cleanup_btn)
        cleanup_layout.addLayout(cleanup_options)

        # Importance thresholds
        threshold_layout = QGridLayout()
        threshold_layout.addWidget(QLabel("Cleanup Threshold:"), 0, 0)
        self.cleanup_threshold = QSlider(Qt.Orientation.Horizontal)
        self.cleanup_threshold.setRange(0, 100)
        self.cleanup_threshold.setValue(20)
        threshold_layout.addWidget(self.cleanup_threshold, 0, 1)

        cleanup_layout.addLayout(threshold_layout)
        layout.addWidget(cleanup_group)

        # Backup/Export
        backup_group = QGroupBox("💾 Backup & Export")
        backup_layout = QHBoxLayout(backup_group)

        export_btn = QPushButton("📤 Export Memories")
        import_btn = QPushButton("📥 Import Memories")
        backup_btn = QPushButton("💿 Create Backup")

        backup_layout.addWidget(export_btn)
        backup_layout.addWidget(import_btn)
        backup_layout.addWidget(backup_btn)

        layout.addWidget(backup_group)

        # System status
        status_group = QGroupBox("⚡ System Status")
        status_layout = QVBoxLayout(status_group)

        self.system_status = QLabel("System Status: Operational")
        self.memory_usage = QLabel("Memory Usage: 0 MB")
        self.db_size = QLabel("Database Size: 0 MB")

        status_layout.addWidget(self.system_status)
        status_layout.addWidget(self.memory_usage)
        status_layout.addWidget(self.db_size)

        layout.addWidget(status_group)

        # Connect cleanup
        cleanup_btn.clicked.connect(self.cleanup_memories)

        return widget

    def create_add_memory(self):
        """Create the add memory interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        add_group = QGroupBox("➕ Add New Memory")
        add_layout = QVBoxLayout(add_group)

        # Memory content
        add_layout.addWidget(QLabel("Memory Content:"))
        self.new_memory_content = QTextEdit()
        self.new_memory_content.setPlaceholderText("Enter the memory content here...")
        add_layout.addWidget(self.new_memory_content)

        # Memory metadata
        metadata_layout = QGridLayout()

        metadata_layout.addWidget(QLabel("Context:"), 0, 0)
        self.new_memory_context = QLineEdit()
        self.new_memory_context.setPlaceholderText("Optional context information")
        metadata_layout.addWidget(self.new_memory_context, 0, 1)

        metadata_layout.addWidget(QLabel("Importance:"), 1, 0)
        self.new_memory_importance = QSlider(Qt.Orientation.Horizontal)
        self.new_memory_importance.setRange(0, 100)
        self.new_memory_importance.setValue(50)
        metadata_layout.addWidget(self.new_memory_importance, 1, 1)

        metadata_layout.addWidget(QLabel("Tags:"), 2, 0)
        self.new_memory_tags = QLineEdit()
        self.new_memory_tags.setPlaceholderText("comma,separated,tags")
        metadata_layout.addWidget(self.new_memory_tags, 2, 1)

        add_layout.addLayout(metadata_layout)

        # Add button
        add_btn = QPushButton("💾 Save Memory")
        add_btn.clicked.connect(self.add_new_memory)
        add_layout.addWidget(add_btn)

        layout.addWidget(add_group)

        return widget

    def apply_styling(self):
        """Apply dark theme styling to the memory system."""
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
                background-color: #00ff88;
                color: black;
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
                color: #00ff88;
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
                border-color: #00ff88;
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
                border-color: #00ff88;
            }
            QListWidget {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                alternate-background-color: #404040;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #00ff88;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #505050;
            }
            QProgressBar {
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #666666;
                height: 8px;
                background: #353535;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00ff88;
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
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
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
                background-color: #00ff88;
                image: none;
            }
        """)

    def load_memory_data(self):
        """Load memory data from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, content, context, importance, timestamp, tags, access_count
                    FROM memories
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)

                memories = cursor.fetchall()
                self.populate_memory_list(memories)
                self.update_analytics()

        except Exception as e:
            print(f"Error loading memory data: {e}")

    def populate_memory_list(self, memories):
        """Populate the memory list widget."""
        self.memory_list.clear()

        for memory in memories:
            memory_id, content, context, importance, timestamp, tags, access_count = (
                memory
            )

            # Create list item
            preview = content[:100] + "..." if len(content) > 100 else content
            item_text = f"[{importance:.2f}] {preview}"

            item = QListWidgetItem(item_text)
            item.setData(
                Qt.ItemDataRole.UserRole,
                {
                    "id": memory_id,
                    "content": content,
                    "context": context,
                    "importance": importance,
                    "timestamp": timestamp,
                    "tags": tags,
                    "access_count": access_count,
                },
            )

            # Color code by importance
            if importance > 0.7:
                item.setBackground(
                    QColor(0, 255, 136, 50)
                )  # Green tint for high importance
            elif importance < 0.3:
                item.setBackground(
                    QColor(255, 136, 0, 30)
                )  # Orange tint for low importance

            self.memory_list.addItem(item)

    def on_memory_selected(self, current, previous):
        """Handle memory selection in the list."""
        if current:
            data = current.data(Qt.ItemDataRole.UserRole)
            if data:
                self.memory_content.setPlainText(data["content"])
                self.importance_display.setText(f"{data['importance']:.2f}")
                self.access_count_display.setText(str(data["access_count"]))
                self.created_display.setText(data["timestamp"])

                # Update access count
                self.update_access_count(data["id"])

    def update_access_count(self, memory_id):
        """Update the access count for a memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE memories
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (memory_id,),
                )
                conn.commit()
        except Exception as e:
            print(f"Error updating access count: {e}")

    def filter_memories(self, filter_text):
        """Filter memories by importance."""
        # Implementation for filtering memories
        pass

    def update_analytics(self):
        """Update the analytics dashboard."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total memories
                cursor.execute("SELECT COUNT(*) FROM memories")
                total = cursor.fetchone()[0]
                self.total_memories_label.setText(str(total))

                # Average importance
                cursor.execute("SELECT AVG(importance) FROM memories")
                avg_importance = cursor.fetchone()[0] or 0
                self.avg_importance_label.setText(f"{avg_importance:.2f}")

                # Distribution
                cursor.execute("SELECT COUNT(*) FROM memories WHERE importance > 0.7")
                high_count = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(*) FROM memories WHERE importance BETWEEN 0.3 AND 0.7"
                )
                medium_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM memories WHERE importance < 0.3")
                low_count = cursor.fetchone()[0]

                if total > 0:
                    self.high_importance_bar.setValue(int((high_count / total) * 100))
                    self.medium_importance_bar.setValue(
                        int((medium_count / total) * 100)
                    )
                    self.low_importance_bar.setValue(int((low_count / total) * 100))

        except Exception as e:
            print(f"Error updating analytics: {e}")

    def perform_search(self):
        """Perform advanced memory search."""
        query = self.search_input.text().strip()
        if not query:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, content, context, importance, timestamp
                    FROM memories
                    WHERE content LIKE ? OR context LIKE ?
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                """,
                    (f"%{query}%", f"%{query}%", self.max_results.value()),
                )

                results = cursor.fetchall()
                self.search_results.clear()

                for result in results:
                    memory_id, content, context, importance, timestamp = result
                    preview = content[:150] + "..." if len(content) > 150 else content
                    item_text = f"[{importance:.2f}] {preview}"
                    self.search_results.addItem(item_text)

        except Exception as e:
            print(f"Error performing search: {e}")

    def add_new_memory(self):
        """Add a new memory to the system."""
        content = self.new_memory_content.toPlainText().strip()
        if not content:
            return

        context = self.new_memory_context.text().strip()
        importance = self.new_memory_importance.value() / 100.0
        tags = self.new_memory_tags.text().strip()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO memories (content, context, importance, tags)
                    VALUES (?, ?, ?, ?)
                """,
                    (content, context, importance, tags),
                )
                conn.commit()

                # Clear form
                self.new_memory_content.clear()
                self.new_memory_context.clear()
                self.new_memory_importance.setValue(50)
                self.new_memory_tags.clear()

                # Refresh data
                self.load_memory_data()

        except Exception as e:
            print(f"Error adding memory: {e}")

    def cleanup_memories(self):
        """Clean up low importance memories."""
        threshold = self.cleanup_threshold.value() / 100.0

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM memories WHERE importance < ?", (threshold,)
                )
                deleted = cursor.rowcount
                conn.commit()

                print(f"Cleaned up {deleted} low importance memories")
                self.load_memory_data()

        except Exception as e:
            print(f"Error cleaning up memories: {e}")

    def refresh_memory_stats(self):
        """Refresh memory statistics periodically."""
        self.update_analytics()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = AdvancedMemorySystemUI()
    window.show()
    sys.exit(app.exec())
