#!/usr/bin/env python3
"""
Memory Visualization Panel
=========================

Modular component for displaying and managing memory-related information.
"""

import json
from typing import Any, Dict

from ..cards import ModernCard
from ..theme import ModernTheme
from ..utils.qt_imports import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    Qt,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)


class MemoryVisualizationPanel(ModernCard):
    """Panel for visualizing and managing memory systems"""

    def __init__(self, parent=None):
        super().__init__("🧠 Memory Visualization", parent)
        self.memory_data = {}
        self.init_ui()
        self.load_memory_data()

    def init_ui(self):
        """Initialize the user interface"""
        # Memory stats section
        stats_layout = QHBoxLayout()

        # Memory count
        self.memory_count_label = QLabel("Memories: 0")
        self.memory_count_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY};")
        stats_layout.addWidget(self.memory_count_label)

        # Embeddings count
        self.embeddings_count_label = QLabel("Embeddings: 0")
        self.embeddings_count_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY};")
        stats_layout.addWidget(self.embeddings_count_label)

        # Vector dimensions
        self.vector_dims_label = QLabel("Vector Dims: 1536")
        self.vector_dims_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY};")
        stats_layout.addWidget(self.vector_dims_label)

        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        self.add_widget(stats_widget)

        # Memory tree view
        self.memory_tree = QTreeWidget()
        self.memory_tree.setHeaderLabels(["Memory", "Type", "Timestamp", "Relevance"])
        self.memory_tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QTreeWidget::item {{
                padding: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {ModernTheme.PRIMARY};
            }}
        """)
        self.add_widget(self.memory_tree)

        # Memory controls
        controls_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_memory_data)
        controls_layout.addWidget(self.refresh_btn)

        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.clicked.connect(self.clear_memory_data)
        controls_layout.addWidget(self.clear_btn)

        controls_layout.addStretch()

        # Similarity threshold
        controls_layout.addWidget(QLabel("Similarity:"))
        self.similarity_slider = QSlider(Qt.Orientation.Horizontal)
        self.similarity_slider.setRange(0, 100)
        self.similarity_slider.setValue(75)
        self.similarity_slider.valueChanged.connect(self.update_similarity_threshold)
        controls_layout.addWidget(self.similarity_slider)

        self.similarity_label = QLabel("0.75")
        controls_layout.addWidget(self.similarity_label)

        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        self.add_widget(controls_widget)

        # Memory details
        self.memory_details = QTextEdit()
        self.memory_details.setMaximumHeight(100)
        self.memory_details.setPlaceholderText("Select a memory to view details...")
        self.memory_details.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 11px;
            }}
        """)
        self.add_widget(self.memory_details)

    def load_memory_data(self):
        """Load memory data from storage"""
        try:
            import os

            memory_files = [
                "memory_store.json",
                "enhanced_memory.json",
                "vector_memory.json",
                "goals_store.json",
            ]

            total_memories = 0
            total_embeddings = 0

            for memory_file in memory_files:
                if os.path.exists(memory_file):
                    try:
                        with open(memory_file, encoding="utf-8") as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                total_memories += len(data)
                                # Add memories to tree
                                self.add_memories_to_tree(data, memory_file)
                            elif isinstance(data, list):
                                total_memories += len(data)
                                total_embeddings += sum(
                                    1 for item in data if "embedding" in str(item)
                                )
                    except Exception as e:
                        print(f"Error loading {memory_file}: {e}")

            self.memory_count_label.setText(f"Memories: {total_memories}")
            self.embeddings_count_label.setText(f"Embeddings: {total_embeddings}")

        except Exception as e:
            print(f"Error loading memory data: {e}")

    def add_memories_to_tree(self, data: Dict[str, Any], source: str):
        """Add memories to the tree widget"""
        for key, value in data.items():
            item = QTreeWidgetItem(self.memory_tree)
            item.setText(0, str(key)[:50] + "..." if len(str(key)) > 50 else str(key))
            item.setText(1, source.replace(".json", ""))

            # Try to extract timestamp
            timestamp = "Unknown"
            if isinstance(value, dict):
                if "timestamp" in value:
                    timestamp = str(value["timestamp"])
                elif "created_at" in value:
                    timestamp = str(value["created_at"])

            item.setText(2, timestamp)
            item.setText(3, "High")  # Default relevance

            # Store full data for details view
            item.setData(0, Qt.ItemDataRole.UserRole, value)

    def refresh_memory_data(self):
        """Refresh memory data display"""
        self.memory_tree.clear()
        self.load_memory_data()

    def clear_memory_data(self):
        """Clear all memory data (with confirmation)"""
        from ..utils.qt_imports import QMessageBox

        reply = QMessageBox.question(
            self,
            "Clear Memory Data",
            "Are you sure you want to clear all memory data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.memory_tree.clear()
            self.memory_count_label.setText("Memories: 0")
            self.embeddings_count_label.setText("Embeddings: 0")
            self.memory_details.clear()

    def update_similarity_threshold(self, value: int):
        """Update similarity threshold display"""
        threshold = value / 100.0
        self.similarity_label.setText(f"{threshold:.2f}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        return {
            "total_memories": self.memory_tree.topLevelItemCount(),
            "similarity_threshold": self.similarity_slider.value() / 100.0,
            "vector_dimensions": 1536,  # Default OpenAI embedding size
        }
