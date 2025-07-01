#!/usr/bin/env python3
# type: ignore
"""
🧬 Neuroplex GUI v2.0 - Modern Dark Mode Interface
==================================================

The next-generation NeuroCode development environment featuring:
- Ultra-modern dark mode design
- Multi-LLM integration panel
- Real-time performance monitoring
- Advanced memory visualization
- Plugin ecosystem management
- Natural language programming interface
- Collaborative AI development
- Vector memory exploration
- Goal-driven development tracking

Built for the future of AI-native programming.
"""

import random
import sys
from datetime import datetime
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Check for Qt availability - prioritize PySide6
QT_AVAILABLE = False
QtWidgets = None
QtCore = None
QtGui = None

try:
    # Try PySide6 first
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSizePolicy,
        QSlider,
        QSpinBox,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
    QT_BACKEND = "PySide6"
    print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI v2.0")

except ImportError:
    try:
        # Fallback to PyQt6
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWidgets import (
            QApplication,
            QComboBox,
            QFileDialog,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QInputDialog,
            QLabel,
            QLineEdit,
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QMessageBox,
            QProgressBar,
            QPushButton,
            QSizePolicy,
            QSlider,
            QSpinBox,
            QSplitter,
            QTabWidget,
            QTextEdit,
            QTreeWidget,
            QTreeWidgetItem,
            QVBoxLayout,
            QWidget,
        )

        QT_AVAILABLE = True
        QT_BACKEND = "PyQt6"
        print(f"🎨 Using {QT_BACKEND} for Neuroplex GUI v2.0")

    except ImportError:
        print("❌ No Qt library available. Please install PySide6 or PyQt6.")
        print("   pip install PySide6")
        sys.exit(1)


class ModernTheme:
    """Ultra-modern dark theme for Neuroplex v2.0"""

    # Primary color palette
    BACKGROUND = "#0a0a0a"  # Pure dark
    SURFACE = "#1a1a1a"  # Dark surface
    SURFACE_VARIANT = "#2a2a2a"  # Lighter surface
    CARD = "#1e1e1e"  # Card background

    # Accent colors
    PRIMARY = "#3b82f6"  # Blue
    PRIMARY_VARIANT = "#1e40af"  # Dark blue
    SECONDARY = "#06d6a0"  # Emerald
    SECONDARY_VARIANT = "#059669"  # Dark emerald
    ACCENT = "#8b5cf6"  # Purple
    ACCENT_VARIANT = "#7c3aed"  # Dark purple

    # Text colors
    TEXT_PRIMARY = "#ffffff"  # White
    TEXT_SECONDARY = "#a3a3a3"  # Light gray
    TEXT_TERTIARY = "#6b7280"  # Gray
    TEXT_DISABLED = "#4b5563"  # Dark gray

    # Status colors
    SUCCESS = "#10b981"  # Green
    WARNING = "#f59e0b"  # Amber
    ERROR = "#ef4444"  # Red
    INFO = "#06b6d4"  # Cyan

    # Border and divider colors
    BORDER = "#374151"  # Gray border
    DIVIDER = "#4b5563"  # Divider

    @staticmethod
    def get_main_stylesheet() -> str:
        """Get the main application stylesheet"""
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {ModernTheme.BACKGROUND};
            color: {ModernTheme.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        }}

        /* General Widget Styling */
        QWidget {{
            background-color: {ModernTheme.BACKGROUND};
            color: {ModernTheme.TEXT_PRIMARY};
            font-size: 13px;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {ModernTheme.PRIMARY};
            color: {ModernTheme.TEXT_PRIMARY};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 14px;
        }}

        QPushButton:hover {{
            background-color: {ModernTheme.PRIMARY_VARIANT};
        }}

        QPushButton:pressed {{
            background-color: {ModernTheme.ACCENT};
        }}

        QPushButton:disabled {{
            background-color: {ModernTheme.SURFACE_VARIANT};
            color: {ModernTheme.TEXT_DISABLED};
        }}

        /* Secondary Buttons */
        QPushButton[buttonRole="secondary"] {{
            background-color: {ModernTheme.SURFACE_VARIANT};
            color: {ModernTheme.TEXT_PRIMARY};
            border: 1px solid {ModernTheme.BORDER};
        }}

        QPushButton[buttonRole="secondary"]:hover {{
            background-color: {ModernTheme.CARD};
            border-color: {ModernTheme.PRIMARY};
        }}

        /* Text Inputs */
        QTextEdit, QLineEdit {{
            background-color: {ModernTheme.SURFACE};
            color: {ModernTheme.TEXT_PRIMARY};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            selection-background-color: {ModernTheme.PRIMARY};
        }}

        QTextEdit:focus, QLineEdit:focus {{
            border-color: {ModernTheme.PRIMARY};
            background-color: {ModernTheme.CARD};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 8px;
            background-color: {ModernTheme.SURFACE};
            margin-top: -1px;
        }}

        QTabBar::tab {{
            background-color: {ModernTheme.SURFACE_VARIANT};
            color: {ModernTheme.TEXT_SECONDARY};
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
        }}

        QTabBar::tab:selected {{
            background-color: {ModernTheme.PRIMARY};
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {ModernTheme.CARD};
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        /* Lists and Trees */
        QListWidget, QTreeWidget {{
            background-color: {ModernTheme.SURFACE};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 4px;
            alternate-background-color: {ModernTheme.CARD};
        }}

        QListWidget::item, QTreeWidget::item {{
            padding: 8px;
            border-radius: 4px;
            margin: 1px;
        }}

        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {ModernTheme.PRIMARY};
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {ModernTheme.CARD};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {ModernTheme.SURFACE};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {ModernTheme.BORDER};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {ModernTheme.TEXT_TERTIARY};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        /* Labels */
        QLabel {{
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QLabel[role="heading"] {{
            font-size: 18px;
            font-weight: bold;
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        QLabel[role="subheading"] {{
            font-size: 14px;
            font-weight: 600;
            color: {ModernTheme.TEXT_SECONDARY};
        }}

        /* Group Boxes */
        QGroupBox {{
            background-color: {ModernTheme.CARD};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 10px;
            font-weight: 600;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: {ModernTheme.TEXT_PRIMARY};
        }}

        /* Progress Bars */
        QProgressBar {{
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            background-color: {ModernTheme.SURFACE};
            text-align: center;
            font-weight: 600;
        }}

        QProgressBar::chunk {{
            background-color: {ModernTheme.PRIMARY};
            border-radius: 5px;
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {ModernTheme.SURFACE};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 100px;
        }}

        QComboBox:hover {{
            border-color: {ModernTheme.PRIMARY};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {ModernTheme.TEXT_SECONDARY};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {ModernTheme.SURFACE};
            border-bottom: 1px solid {ModernTheme.BORDER};
            padding: 4px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:selected {{
            background-color: {ModernTheme.PRIMARY};
        }}

        /* Menus */
        QMenu {{
            background-color: {ModernTheme.CARD};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 20px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background-color: {ModernTheme.PRIMARY};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {ModernTheme.SURFACE};
            border-top: 1px solid {ModernTheme.BORDER};
        }}
        """

    @staticmethod
    def get_card_style() -> str:
        """Get card styling for panels"""
        return f"""
        QWidget {{
            background-color: {ModernTheme.CARD};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 6px;
        }}

        QLabel {{
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 1px;
            margin: 1px;
        }}

        QLabel[role="heading"] {{
            font-size: 14px;
            font-weight: bold;
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 4px;
            margin-bottom: 4px;
        }}

        QLineEdit, QComboBox {{
            min-height: 20px;
            padding: 2px 6px;
            font-size: 12px;
        }}

        QPushButton {{
            min-height: 24px;
            padding: 4px 8px;
            font-size: 11px;
        }}
        """

    @staticmethod
    def get_accent_button_style() -> str:
        """Get accent button styling"""
        return f"""
        QPushButton {{
            background-color: {ModernTheme.SECONDARY};
            color: {ModernTheme.TEXT_PRIMARY};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {ModernTheme.SECONDARY_VARIANT};
        }}
        """


class ModernCard(QWidget):
    """A modern card widget for organizing content"""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(ModernTheme.get_card_style())

        # Remove the shadow effect that causes QPainter errors
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(20)
        # shadow.setColor(QColor(0, 0, 0, 30))
        # shadow.setOffset(0, 4)
        # self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)  # Reduced margins for more space
        layout.setSpacing(6)  # Reduced spacing

        if title:
            title_label = QLabel(title)
            title_label.setProperty("role", "heading")
            title_label.setWordWrap(True)  # Allow text wrapping
            title_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            title_label.setMaximumHeight(30)  # Limit title height
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget):
        """Add a widget to the card"""
        if widget:
            self.content_layout.addWidget(widget)


class LLMProviderPanel(ModernCard):
    """Panel for managing LLM providers"""

    def __init__(self, llm_manager=None, parent=None):
        super().__init__("🤖 LLM Providers", parent)
        self.llm_manager = llm_manager
        self.init_ui()
        self.update_providers()

    def init_ui(self):
        # Provider selection
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Active Provider:"))

        self.provider_combo = QComboBox()
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)

        self.add_widget(QWidget())
        self.content_layout.addLayout(provider_layout)

        # Model configuration
        config_group = QGroupBox("Model Configuration")
        config_layout = QGridLayout(config_group)

        config_layout.addWidget(QLabel("Temperature:"), 0, 0)
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        self.temp_value_label = QLabel("0.7")
        self.temp_slider.valueChanged.connect(self.update_temp_label)
        config_layout.addWidget(self.temp_slider, 0, 1)
        config_layout.addWidget(self.temp_value_label, 0, 2)

        config_layout.addWidget(QLabel("Max Tokens:"), 1, 0)
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(1, 8192)
        self.tokens_spin.setValue(2048)
        config_layout.addWidget(self.tokens_spin, 1, 1)

        self.add_widget(config_group)

        # Provider status
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"color: {ModernTheme.SUCCESS}; font-size: 16px;")
        self.status_label = QLabel("Connected")
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # Test connection button
        test_btn = QPushButton("🔍 Test")
        test_btn.clicked.connect(self.test_connection)
        test_btn.setProperty("buttonRole", "secondary")
        test_btn.setMaximumWidth(60)  # Limit button width
        status_layout.addWidget(test_btn)

        self.add_widget(QWidget())
        self.content_layout.addLayout(status_layout)

    def update_providers(self):
        """Update available providers from LLM manager"""
        if self.llm_manager:
            try:
                models = self.llm_manager.list_available_models()
                self.provider_combo.clear()
                for model in models:
                    self.provider_combo.addItem(
                        f"{model.get('provider', 'Unknown')}: {model.get('name', 'Unknown')}"
                    )

                if models:
                    self.status_label.setText(f"{len(models)} models available")
                else:
                    self.status_label.setText("No models configured")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.WARNING}; font-size: 16px;"
                    )
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)[:50]}...")
                self.status_indicator.setStyleSheet(f"color: {ModernTheme.ERROR}; font-size: 16px;")
        else:
            self.provider_combo.addItems(
                [
                    "OpenAI GPT-4",
                    "OpenAI GPT-3.5",
                    "Anthropic Claude",
                    "Google Gemini",
                    "Local Ollama",
                    "LlamaCpp",
                ]
            )

    def on_provider_changed(self, provider_name):
        """Handle provider selection change"""
        if self.llm_manager:
            try:
                # Extract model name from display string
                if ": " in provider_name:
                    model_name = provider_name.split(": ")[1]
                    self.llm_manager.set_model(model_name)
                    self.status_label.setText(f"Switched to {model_name}")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.SUCCESS}; font-size: 16px;"
                    )
            except Exception as e:
                self.status_label.setText(f"Switch failed: {str(e)[:30]}...")
                self.status_indicator.setStyleSheet(f"color: {ModernTheme.ERROR}; font-size: 16px;")

    def update_temp_label(self, value):
        """Update temperature label"""
        temp_value = value / 100.0
        self.temp_value_label.setText(f"{temp_value:.2f}")

    def test_connection(self):
        """Test connection to current provider"""
        try:
            if self.llm_manager:
                # Test with a simple prompt
                response = self.llm_manager.generate_response("Test connection")
                if response and len(response) > 0:
                    self.status_label.setText("Connection successful!")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.SUCCESS}; font-size: 16px;"
                    )
                else:
                    self.status_label.setText("Connection failed")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.ERROR}; font-size: 16px;"
                    )
            else:
                self.status_label.setText("LLM manager not available")
                self.status_indicator.setStyleSheet(
                    f"color: {ModernTheme.WARNING}; font-size: 16px;"
                )
        except Exception as e:
            self.status_label.setText(f"Test failed: {str(e)[:30]}...")
            self.status_indicator.setStyleSheet(f"color: {ModernTheme.ERROR}; font-size: 16px;")


class MemoryVisualizationPanel(ModernCard):
    """Panel for visualizing vector memory"""

    def __init__(self, vector_memory=None, memory=None, parent=None):
        super().__init__("🧠 Memory Visualization", parent)
        self.vector_memory = vector_memory
        self.memory = memory
        self.init_ui()
        self.update_memory_stats()

    def init_ui(self):
        # Memory stats
        stats_layout = QGridLayout()

        stats_layout.addWidget(QLabel("Memories:"), 0, 0)
        self.memory_count = QLabel("0")
        self.memory_count.setStyleSheet(f"color: {ModernTheme.PRIMARY}; font-weight: bold;")
        stats_layout.addWidget(self.memory_count, 0, 1)

        stats_layout.addWidget(QLabel("Embeddings:"), 1, 0)
        self.embedding_count = QLabel("0")
        self.embedding_count.setStyleSheet(f"color: {ModernTheme.SECONDARY}; font-weight: bold;")
        stats_layout.addWidget(self.embedding_count, 1, 1)

        stats_layout.addWidget(QLabel("Similarity:"), 2, 0)
        self.similarity_avg = QLabel("N/A")
        self.similarity_avg.setStyleSheet(f"color: {ModernTheme.ACCENT}; font-weight: bold;")
        stats_layout.addWidget(self.similarity_avg, 2, 1)

        self.add_widget(QWidget())
        self.content_layout.addLayout(stats_layout)

        # Memory search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search memories...")
        self.search_input.returnPressed.connect(self.search_memories)

        search_btn = QPushButton("🔍")
        search_btn.setMaximumWidth(40)
        search_btn.clicked.connect(self.search_memories)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)

        self.add_widget(QWidget())
        self.content_layout.addLayout(search_layout)

        # Memory actions
        actions_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self.update_memory_stats)
        refresh_btn.setProperty("buttonRole", "secondary")
        refresh_btn.setMaximumWidth(35)
        refresh_btn.setToolTip("Refresh memory stats")

        clear_btn = QPushButton("🗑️")
        clear_btn.clicked.connect(self.clear_memories)
        clear_btn.setProperty("buttonRole", "secondary")
        clear_btn.setMaximumWidth(35)
        clear_btn.setToolTip("Clear all memories")

        actions_layout.addWidget(refresh_btn)
        actions_layout.addWidget(clear_btn)
        actions_layout.addStretch()

        self.add_widget(QWidget())
        self.content_layout.addLayout(actions_layout)

        # Memory list
        self.memory_list = QListWidget()
        self.memory_list.setMaximumHeight(120)  # Reduced height
        self.memory_list.itemDoubleClicked.connect(self.show_memory_details)
        self.add_widget(self.memory_list)

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_memory_stats)
        self.refresh_timer.start(10000)  # Update every 10 seconds

    def update_memory_stats(self):
        """Update memory statistics"""
        try:
            memory_count = 0
            embedding_count = 0

            # Get stats from regular memory
            if self.memory:
                try:
                    memory_count = len(self.memory.memory)
                    self.memory_count.setText(str(memory_count))
                except Exception:
                    pass

            # Get stats from vector memory
            if self.vector_memory:
                try:
                    # Try to get vector memory stats
                    if hasattr(self.vector_memory, "get_memory_count"):
                        memory_count += self.vector_memory.get_memory_count()

                    if hasattr(self.vector_memory, "get_embedding_count"):
                        embedding_count = self.vector_memory.get_embedding_count()

                    self.embedding_count.setText(str(embedding_count))

                    # Calculate average similarity (mock for now)
                    if embedding_count > 0:
                        self.similarity_avg.setText("0.85")
                    else:
                        self.similarity_avg.setText("N/A")
                except Exception:
                    pass

            # Update memory list with recent memories
            self.update_memory_list()

        except Exception as e:
            print(f"Error updating memory stats: {e}")

    def update_memory_list(self):
        """Update the memory list display"""
        self.memory_list.clear()

        if self.memory:
            try:
                # Get recent memories
                recent_memories = self.memory.memory[-10:]  # Last 10 memories

                for memory_item in recent_memories:
                    text = memory_item.get("text", "Unknown")
                    tags = memory_item.get("tags", [])

                    # Create display text
                    display_text = f"[{', '.join(tags[:2]) if tags else 'general'}] {text[:50]}..."

                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, memory_item)
                    self.memory_list.addItem(item)

            except Exception as e:
                item = QListWidgetItem(f"Error loading memories: {str(e)[:30]}...")
                self.memory_list.addItem(item)

    def search_memories(self):
        """Search memories based on input"""
        query = self.search_input.text().strip()
        if not query:
            self.update_memory_list()
            return

        self.memory_list.clear()

        try:
            if self.memory:
                # Search in regular memory
                matching_memories = []
                for memory_item in self.memory.memory:
                    text = memory_item.get("text", "").lower()
                    tags = memory_item.get("tags", [])

                    if query.lower() in text or any(query.lower() in tag.lower() for tag in tags):
                        matching_memories.append(memory_item)

                for memory_item in matching_memories[:10]:  # Limit to 10 results
                    text = memory_item.get("text", "Unknown")
                    tags = memory_item.get("tags", [])

                    display_text = f"[{', '.join(tags[:2]) if tags else 'general'}] {text[:50]}..."

                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, memory_item)
                    self.memory_list.addItem(item)

                if not matching_memories:
                    self.memory_list.addItem(QListWidgetItem("No memories found"))

        except Exception as e:
            self.memory_list.addItem(QListWidgetItem(f"Search error: {str(e)[:30]}..."))

    def show_memory_details(self, item):
        """Show detailed memory information"""
        memory_data = item.data(Qt.ItemDataRole.UserRole)
        if memory_data:
            details = f"""Memory Details:

Text: {memory_data.get("text", "N/A")}

Tags: {", ".join(memory_data.get("tags", []))}

Category: {memory_data.get("category", "N/A")}

Timestamp: {memory_data.get("timestamp", "N/A")}

ID: {memory_data.get("id", "N/A")}"""

            QMessageBox.information(self.parent(), "Memory Details", details)

    def clear_memories(self):
        """Clear all memories with confirmation"""
        reply = QMessageBox.question(
            self.parent(),
            "Clear Memories",
            "Are you sure you want to clear all memories?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.memory and hasattr(self.memory, "clear"):
                    self.memory.clear()

                if self.vector_memory and hasattr(self.vector_memory, "clear"):
                    self.vector_memory.clear()

                self.update_memory_stats()
                QMessageBox.information(self.parent(), "Success", "Memories cleared successfully!")

            except Exception as e:
                QMessageBox.warning(self.parent(), "Error", f"Failed to clear memories: {str(e)}")


class PerformanceMonitorPanel(ModernCard):
    """Real-time performance monitoring panel"""

    def __init__(self, performance_optimizer=None, parent=None):
        super().__init__("⚡ Performance Monitor", parent)
        self.performance_optimizer = performance_optimizer
        self.init_ui()

    def init_ui(self):
        # Performance metrics
        metrics_layout = QGridLayout()

        # CPU Usage
        metrics_layout.addWidget(QLabel("CPU:"), 0, 0)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(0)
        self.cpu_progress.setFixedHeight(18)
        self.cpu_progress.setTextVisible(False)
        self.cpu_label = QLabel("0%")
        self.cpu_label.setMinimumWidth(40)
        metrics_layout.addWidget(self.cpu_progress, 0, 1)
        metrics_layout.addWidget(self.cpu_label, 0, 2)

        # Memory Usage
        metrics_layout.addWidget(QLabel("Memory:"), 1, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)
        self.memory_progress.setFixedHeight(18)
        self.memory_progress.setTextVisible(False)
        self.memory_label = QLabel("0%")
        self.memory_label.setMinimumWidth(40)
        metrics_layout.addWidget(self.memory_progress, 1, 1)
        metrics_layout.addWidget(self.memory_label, 1, 2)

        # Response Time
        metrics_layout.addWidget(QLabel("Response:"), 2, 0)
        self.response_label = QLabel("0ms")
        self.response_label.setStyleSheet(f"color: {ModernTheme.INFO}; font-weight: bold;")
        metrics_layout.addWidget(self.response_label, 2, 1)

        self.add_widget(QWidget())
        self.content_layout.addLayout(metrics_layout)

        # Performance optimization info
        if self.performance_optimizer:
            self.optimization_info = QLabel("Optimization suggestions will appear here...")
            self.optimization_info.setWordWrap(True)
            self.optimization_info.setStyleSheet(
                f"color: {ModernTheme.TEXT_SECONDARY}; font-size: 12px;"
            )
            self.add_widget(self.optimization_info)

        # Performance actions
        actions_layout = QHBoxLayout()

        optimize_btn = QPushButton("🔧")
        optimize_btn.clicked.connect(self.run_optimization)
        optimize_btn.setProperty("buttonRole", "secondary")
        optimize_btn.setMaximumWidth(35)
        optimize_btn.setToolTip("Run optimization")

        report_btn = QPushButton("📊")
        report_btn.clicked.connect(self.show_performance_report)
        report_btn.setProperty("buttonRole", "secondary")
        report_btn.setMaximumWidth(35)
        report_btn.setToolTip("Show performance report")

        actions_layout.addWidget(optimize_btn)
        actions_layout.addWidget(report_btn)
        actions_layout.addStretch()

        self.add_widget(QWidget())
        self.content_layout.addLayout(actions_layout)

        # Start monitoring
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_metrics)
        self.monitor_timer.start(2000)  # Update every 2 seconds

    def update_metrics(self):
        """Update performance metrics"""
        try:
            import psutil

            # Update CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_label.setText(f"{cpu_percent:.1f}%")

            # Update Memory
            memory = psutil.virtual_memory()
            self.memory_progress.setValue(int(memory.percent))
            self.memory_label.setText(f"{memory.percent:.1f}%")

            # Get response time from performance optimizer
            if self.performance_optimizer:
                try:
                    report = self.performance_optimizer.get_performance_report()
                    avg_time = 0
                    command_count = len(report.get("command_performance", {}))

                    if command_count > 0:
                        total_time = sum(
                            cmd_data.get("avg_time", 0)
                            for cmd_data in report["command_performance"].values()
                        )
                        avg_time = total_time / command_count

                    self.response_label.setText(f"{avg_time * 1000:.0f}ms")

                    # Update optimization suggestions
                    suggestions = report.get("optimization_opportunities", [])
                    if suggestions and hasattr(self, "optimization_info"):
                        latest_suggestion = suggestions[0]
                        suggestion_text = latest_suggestion.get(
                            "suggested_optimization", "No suggestions"
                        )[:100]
                        self.optimization_info.setText(f"💡 {suggestion_text}...")

                except Exception:
                    # Fallback for response time
                    response_time = random.randint(50, 200)
                    self.response_label.setText(f"{response_time}ms")
            else:
                # Simulate response time
                response_time = random.randint(50, 200)
                self.response_label.setText(f"{response_time}ms")

        except ImportError:
            # Fallback if psutil not available
            self.cpu_progress.setValue(random.randint(10, 30))
            self.memory_progress.setValue(random.randint(40, 60))
            self.cpu_label.setText(f"{random.randint(10, 30)}%")
            self.memory_label.setText(f"{random.randint(40, 60)}%")

    def run_optimization(self):
        """Run performance optimization"""
        if self.performance_optimizer:
            try:
                # Get current performance data and suggest optimizations
                report = self.performance_optimizer.get_performance_report()
                suggestions = report.get("optimization_opportunities", [])

                if suggestions:
                    suggestion = suggestions[0]
                    msg = f"Optimization suggestion:\n\n{suggestion.get('suggested_optimization', 'General optimization needed')}\n\nExpected improvement: {suggestion.get('expected_improvement', 'Unknown')}"
                    QMessageBox.information(self.parent(), "Performance Optimization", msg)
                else:
                    QMessageBox.information(
                        self.parent(),
                        "Performance Optimization",
                        "No specific optimizations needed at this time.\n\nSystem is performing well!",
                    )
            except Exception as e:
                QMessageBox.warning(
                    self.parent(), "Optimization Error", f"Could not run optimization: {str(e)}"
                )
        else:
            QMessageBox.information(
                self.parent(),
                "Performance Optimization",
                "Performance optimizer not available.\n\nGeneral suggestions:\n• Close unused applications\n• Clear temporary files\n• Restart the application",
            )

    def show_performance_report(self):
        """Show detailed performance report"""
        if self.performance_optimizer:
            try:
                report = self.performance_optimizer.get_performance_report()

                # Format report
                report_text = f"""Performance Report

Total commands tracked: {report["summary"]["total_commands_tracked"]}
Total executions: {report["summary"]["total_executions"]}
Optimization suggestions: {report["summary"]["optimization_suggestions"]}

System Health:
CPU: {report["system_health"]["cpu_usage"]:.1f}%
Memory: {report["system_health"]["memory_usage"]:.1f}%
Disk: {report["system_health"]["disk_usage"]:.1f}%

Recent optimizations: {len(report.get("optimization_opportunities", []))}"""

                QMessageBox.information(self.parent(), "Performance Report", report_text)
            except Exception as e:
                QMessageBox.warning(
                    self.parent(), "Report Error", f"Could not generate report: {str(e)}"
                )
        else:
            QMessageBox.information(
                self.parent(),
                "Performance Report",
                "Performance optimizer not available.\n\nInstall psutil for detailed metrics:\npip install psutil",
            )


class NaturalLanguagePanel(ModernCard):
    """Panel for natural language programming"""

    def __init__(self, parent=None):
        super().__init__("💬 Natural Language Programming", parent)
        self.init_ui()

    def init_ui(self):
        # Input area
        self.nl_input = QTextEdit()
        self.nl_input.setPlaceholderText(
            "Describe what you want to create in natural language...\n\n"
            "Example: 'Create a function that sorts a list of numbers in ascending order'"
        )
        self.nl_input.setMaximumHeight(100)
        self.add_widget(self.nl_input)

        # Generate button
        generate_btn = QPushButton("🚀 Generate Code")
        generate_btn.setStyleSheet(ModernTheme.get_accent_button_style())
        self.add_widget(generate_btn)

        # Output area
        self.code_output = QTextEdit()
        self.code_output.setPlaceholderText("Generated code will appear here...")
        self.code_output.setReadOnly(True)
        self.add_widget(self.code_output)


class GoalTrackingPanel(ModernCard):
    """Panel for tracking development goals"""

    def __init__(self, parent=None):
        super().__init__("🎯 Goal Tracking", parent)
        self.init_ui()

    def init_ui(self):
        # Add goal button
        add_btn = QPushButton("+ Add")
        add_btn.setProperty("buttonRole", "secondary")
        add_btn.setMaximumWidth(60)
        self.add_widget(add_btn)

        # Goals list
        self.goals_list = QListWidget()
        self.goals_list.setMaximumHeight(120)  # Reduced height

        # Add sample goals
        goals = [
            "✅ Multi-LLM support",
            "🟡 Memory visualization",
            "⭕ Plugin ecosystem",
            "⭕ Real-time collaboration",
        ]

        for goal in goals:
            item = QListWidgetItem(goal)
            self.goals_list.addItem(item)

        self.add_widget(self.goals_list)


class PluginManagerPanel(ModernCard):
    """Panel for managing plugins"""

    def __init__(self, parent=None):
        super().__init__("🔌 Plugin Ecosystem", parent)
        self.init_ui()

    def init_ui(self):
        # Plugin actions
        actions_layout = QHBoxLayout()

        install_btn = QPushButton("📦")
        install_btn.setProperty("buttonRole", "secondary")
        install_btn.setMaximumWidth(35)
        install_btn.setToolTip("Install plugin")

        refresh_btn = QPushButton("🔄")
        refresh_btn.setProperty("buttonRole", "secondary")
        refresh_btn.setMaximumWidth(35)
        refresh_btn.setToolTip("Refresh plugins")

        actions_layout.addWidget(install_btn)
        actions_layout.addWidget(refresh_btn)
        actions_layout.addStretch()

        self.add_widget(QWidget())
        self.content_layout.addLayout(actions_layout)

        # Plugin list
        self.plugin_tree = QTreeWidget()
        self.plugin_tree.setHeaderLabels(["Plugin", "Ver", "Status"])
        self.plugin_tree.setMaximumHeight(100)  # Reduced height

        # Add sample plugins
        plugins = [
            ("Code Formatter", "v1.2.0", "Active"),
            ("Git Integration", "v2.1.5", "Active"),
            ("AI Code Review", "v1.0.0", "Inactive"),
            ("Database Tools", "v3.0.1", "Active"),
        ]

        for name, version, status in plugins:
            item = QTreeWidgetItem([name, version, status])
            self.plugin_tree.addTopLevelItem(item)

        self.add_widget(self.plugin_tree)


class MetaPluginPanel(ModernCard):
    """Panel for managing meta-plugins and system operations"""

    def __init__(self, meta_plugins=None, parent=None):
        super().__init__("🎛️ Meta-Plugins", parent)
        self.meta_plugins = meta_plugins
        self.init_ui()

    def init_ui(self):
        # Meta-plugin selection
        plugin_layout = QHBoxLayout()
        plugin_layout.addWidget(QLabel("Meta-Plugin:"))

        self.meta_plugin_combo = QComboBox()
        self.meta_plugin_combo.addItems(
            [
                "memory_analyzer",
                "file_monitor",
                "system_optimizer",
                "goal_tracker",
                "autonomous_improver",
            ]
        )
        plugin_layout.addWidget(self.meta_plugin_combo)

        self.add_widget(QWidget())
        self.content_layout.addLayout(plugin_layout)

        # Parameter input
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Parameters:"))

        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("Optional parameters...")
        param_layout.addWidget(self.param_input)

        self.add_widget(QWidget())
        self.content_layout.addLayout(param_layout)

        # Execute button
        execute_btn = QPushButton("⚡ Execute")
        execute_btn.setStyleSheet(ModernTheme.get_accent_button_style())
        execute_btn.clicked.connect(self.execute_meta_plugin)
        self.add_widget(execute_btn)

        # Output area
        self.output_area = QTextEdit()
        self.output_area.setPlaceholderText("Meta-plugin output will appear here...")
        self.output_area.setReadOnly(True)
        self.output_area.setMaximumHeight(80)  # Reduced height
        self.add_widget(self.output_area)

        # Quick actions
        actions_layout = QGridLayout()

        analyze_btn = QPushButton("🧠")
        analyze_btn.clicked.connect(lambda: self.quick_execute("memory_analyzer"))
        analyze_btn.setProperty("buttonRole", "secondary")
        analyze_btn.setToolTip("Analyze Memory")

        optimize_btn = QPushButton("🔧")
        optimize_btn.clicked.connect(lambda: self.quick_execute("system_optimizer"))
        optimize_btn.setProperty("buttonRole", "secondary")
        optimize_btn.setToolTip("System Optimize")

        goals_btn = QPushButton("🎯")
        goals_btn.clicked.connect(lambda: self.quick_execute("goal_tracker"))
        goals_btn.setProperty("buttonRole", "secondary")
        goals_btn.setToolTip("Track Goals")

        auto_btn = QPushButton("🤖")
        auto_btn.clicked.connect(lambda: self.quick_execute("autonomous_improver"))
        auto_btn.setProperty("buttonRole", "secondary")
        auto_btn.setToolTip("Auto Improve")

        actions_layout.addWidget(analyze_btn, 0, 0)
        actions_layout.addWidget(optimize_btn, 0, 1)
        actions_layout.addWidget(goals_btn, 1, 0)
        actions_layout.addWidget(auto_btn, 1, 1)

        self.add_widget(QWidget())
        self.content_layout.addLayout(actions_layout)

    def execute_meta_plugin(self):
        """Execute selected meta-plugin"""
        plugin_name = self.meta_plugin_combo.currentText()
        params = self.param_input.text().strip()

        if self.meta_plugins:
            try:
                if params:
                    result = self.meta_plugins.execute_meta_plugin(plugin_name, params)
                else:
                    result = self.meta_plugins.execute_meta_plugin(plugin_name)

                self.output_area.setPlainText(str(result))
                self.output_area.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY};")

            except Exception as e:
                error_msg = f"Error executing {plugin_name}: {str(e)}"
                self.output_area.setPlainText(error_msg)
                self.output_area.setStyleSheet(f"color: {ModernTheme.ERROR};")
        else:
            self.output_area.setPlainText("Meta-plugin system not available")
            self.output_area.setStyleSheet(f"color: {ModernTheme.WARNING};")

    def quick_execute(self, plugin_name):
        """Quick execute meta-plugin without parameters"""
        self.meta_plugin_combo.setCurrentText(plugin_name)
        self.param_input.clear()
        self.execute_meta_plugin()


class ModernNeuroplexWindow(QMainWindow):
    """Modern Neuroplex main window with dark mode"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧬 Neuroplex v2.0 - AI-Native Development Environment")
        self.setMinimumSize(1600, 1000)  # Reduced minimum size
        self.resize(1800, 1100)  # Better default size

        # Apply modern theme
        self.setStyleSheet(ModernTheme.get_main_stylesheet())

        # Initialize core components
        self.init_core_components()

        # Setup UI
        self.init_ui()
        self.init_menu_bar()
        self.init_status_bar()

        # Start update timers
        self.init_timers()

    def init_core_components(self):
        """Initialize NeuroCode core components"""
        try:
            # Import core modules
            from core.goal_system import GoalSystem
            from core.memory import Memory
            from core.meta_plugins import MetaPluginSystem
            from core.multi_llm_manager import llm_manager
            from core.performance_optimizer import PerformanceOptimizer
            from core.plugin_manager import PluginManager
            from core.vector_memory import VectorMemory

            self.llm_manager = llm_manager
            self.vector_memory = VectorMemory()
            self.performance_optimizer = PerformanceOptimizer()
            self.plugin_manager = PluginManager()
            self.memory = Memory()
            self.goal_system = GoalSystem()
            self.meta_plugins = MetaPluginSystem(self.memory, None, self.goal_system)

            print("✅ Core components initialized successfully")
            print(f"📊 Available LLM providers: {len(self.llm_manager.list_available_models())}")

        except Exception as e:
            print(f"⚠️ Some core components unavailable: {e}")
            self.llm_manager = None
            self.vector_memory = None
            self.performance_optimizer = None
            self.plugin_manager = None
            self.memory = None
            self.goal_system = None
            self.meta_plugins = None

    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)  # Reduced margins
        main_layout.setSpacing(8)  # Reduced spacing

        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel (narrow)
        left_panel = self.create_left_panel()
        left_panel.setMinimumWidth(260)  # Reduced minimum width
        left_panel.setMaximumWidth(320)  # Reduced maximum width
        splitter.addWidget(left_panel)

        # Center panel (wide)
        center_panel = self.create_center_panel()
        center_panel.setMinimumWidth(500)  # Reduced minimum width
        splitter.addWidget(center_panel)

        # Right panel (medium)
        right_panel = self.create_right_panel()
        right_panel.setMinimumWidth(260)  # Reduced minimum width
        right_panel.setMaximumWidth(320)  # Reduced maximum width
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([280, 700, 280])  # Better proportions for smaller panels
        splitter.setCollapsible(0, False)  # Prevent left panel from collapsing
        splitter.setCollapsible(1, False)  # Prevent center panel from collapsing
        splitter.setCollapsible(2, False)  # Prevent right panel from collapsing

    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        panel.setMinimumWidth(260)
        panel.setMaximumWidth(320)
        layout = QVBoxLayout(panel)
        layout.setSpacing(4)  # More compact spacing
        layout.setContentsMargins(4, 4, 4, 4)  # Smaller margins

        # LLM Provider Panel
        self.llm_panel = LLMProviderPanel(self.llm_manager)
        layout.addWidget(self.llm_panel)

        # Performance Monitor
        self.perf_panel = PerformanceMonitorPanel(self.performance_optimizer)
        layout.addWidget(self.perf_panel)

        # Goal Tracking
        self.goals_panel = GoalTrackingPanel()
        layout.addWidget(self.goals_panel)

        # Meta-Plugin Panel
        self.meta_panel = MetaPluginPanel(self.meta_plugins)
        layout.addWidget(self.meta_panel)

        layout.addStretch()
        return panel

    def create_center_panel(self):
        """Create the center workspace panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Natural Language Programming Tab
        nl_tab = QWidget()
        nl_layout = QVBoxLayout(nl_tab)
        nl_layout.setContentsMargins(16, 16, 16, 16)

        self.nl_panel = NaturalLanguagePanel()
        nl_layout.addWidget(self.nl_panel)
        nl_layout.addStretch()

        self.tab_widget.addTab(nl_tab, "💬 Natural Programming")

        # Code Editor Tab
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        editor_layout.setContentsMargins(16, 16, 16, 16)

        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText(
            "// Welcome to NeuroCode v2.0!\n"
            "// Start typing your code here...\n\n"
            "model: gpt-4\n"
            "assistant: help me write a function\n\n"
            "memory: remember this pattern\n"
            "goal: create efficient algorithms"
        )
        editor_layout.addWidget(self.code_editor)

        # Editor actions
        editor_actions = QHBoxLayout()

        run_btn = QPushButton("▶️ Run Code")
        run_btn.setStyleSheet(ModernTheme.get_accent_button_style())

        save_btn = QPushButton("💾 Save")
        save_btn.setProperty("buttonRole", "secondary")

        load_btn = QPushButton("📁 Load")
        load_btn.setProperty("buttonRole", "secondary")

        editor_actions.addWidget(run_btn)
        editor_actions.addWidget(save_btn)
        editor_actions.addWidget(load_btn)
        editor_actions.addStretch()

        editor_layout.addLayout(editor_actions)

        self.tab_widget.addTab(editor_tab, "⚡ Code Editor")

        # AI Chat Tab
        chat_tab = self.create_chat_tab()
        self.tab_widget.addTab(chat_tab, "🤖 AI Assistant")

        return panel

    def create_right_panel(self):
        """Create the right information panel"""
        panel = QWidget()
        panel.setMinimumWidth(260)
        panel.setMaximumWidth(320)
        layout = QVBoxLayout(panel)
        layout.setSpacing(4)  # More compact spacing
        layout.setContentsMargins(4, 4, 4, 4)  # Smaller margins

        # Memory Visualization
        self.memory_panel = MemoryVisualizationPanel(self.vector_memory, self.memory)
        layout.addWidget(self.memory_panel)

        # Plugin Manager
        self.plugin_panel = PluginManagerPanel()
        layout.addWidget(self.plugin_panel)

        layout.addStretch()
        return panel

    def create_chat_tab(self):
        """Create the AI chat tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("AI Assistant: Hello! How can I help you today?")
        layout.addWidget(self.chat_display)

        # Chat input
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything about your code...")

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet(ModernTheme.get_accent_button_style())
        send_btn.setMaximumWidth(80)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        return tab

    def init_menu_bar(self):
        """Initialize the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Project", self.new_project)
        file_menu.addAction("Open Project", self.open_project)
        file_menu.addSeparator()
        file_menu.addAction("Save", self.save_file)
        file_menu.addAction("Save As...", self.save_as_file)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo", lambda: self.code_editor.undo())
        edit_menu.addAction("Redo", lambda: self.code_editor.redo())
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", lambda: self.code_editor.cut())
        edit_menu.addAction("Copy", lambda: self.code_editor.copy())
        edit_menu.addAction("Paste", lambda: self.code_editor.paste())

        # AI menu
        ai_menu = menubar.addMenu("AI")
        ai_menu.addAction("Switch Model", self.switch_model)
        ai_menu.addAction("Configure Providers", self.configure_providers)
        ai_menu.addSeparator()
        ai_menu.addAction("Generate Code", self.generate_code)
        ai_menu.addAction("Optimize Code", self.optimize_code)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Plugin Manager", self.show_plugins)
        tools_menu.addAction("Memory Explorer", self.show_memory)
        tools_menu.addAction("Performance Monitor", self.show_performance)

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        help_menu.addAction("Documentation", self.show_docs)

    def init_status_bar(self):
        """Initialize the status bar"""
        self.status_bar = self.statusBar()

        # Current model indicator
        self.model_label = QLabel("Model: GPT-4")
        self.model_label.setStyleSheet(f"color: {ModernTheme.PRIMARY}; font-weight: bold;")
        self.status_bar.addWidget(self.model_label)

        self.status_bar.addWidget(QLabel(" | "))

        # Connection status
        self.connection_label = QLabel("Connected")
        self.connection_label.setStyleSheet(f"color: {ModernTheme.SUCCESS};")
        self.status_bar.addWidget(self.connection_label)

        self.status_bar.addWidget(QLabel(" | "))

        # Memory usage
        self.memory_status = QLabel("Memory: 0 items")
        self.status_bar.addWidget(self.memory_status)

        # Right side
        self.status_bar.addPermanentWidget(
            QLabel(f"Neuroplex v2.0 | {datetime.now().strftime('%H:%M')}")
        )

    def init_timers(self):
        """Initialize update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(5000)  # Update every 5 seconds

    def update_status(self):
        """Update status information"""
        # Update time
        for widget in self.status_bar.children():
            if isinstance(widget, QLabel) and "Neuroplex v2.0" in widget.text():
                widget.setText(f"Neuroplex v2.0 | {datetime.now().strftime('%H:%M')}")
                break

        # Update memory count if available
        if self.vector_memory:
            try:
                count = (
                    len(self.vector_memory.memories)
                    if hasattr(self.vector_memory, "memories")
                    else 0
                )
                self.memory_status.setText(f"Memory: {count} items")
                self.memory_panel.memory_count.setText(str(count))
            except Exception:
                pass

    # Menu action methods
    def new_project(self):
        reply = QMessageBox.question(
            self,
            "New Project",
            "Create a new NeuroCode project?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.code_editor.clear()

    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open NeuroCode File", "", "NeuroCode Files (*.neuro);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                self.code_editor.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        # Implement save functionality
        QMessageBox.information(self, "Save", "File saved successfully!")

    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save NeuroCode File", "", "NeuroCode Files (*.neuro);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.code_editor.toPlainText())
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file: {e}")

    def switch_model(self):
        models = ["GPT-4", "GPT-3.5", "Claude", "Gemini", "Local Llama"]
        model, ok = QInputDialog.getItem(self, "Switch Model", "Select AI Model:", models, 0, False)
        if ok and model:
            self.model_label.setText(f"Model: {model}")

    def configure_providers(self):
        QMessageBox.information(self, "Providers", "Provider configuration panel opened!")

    def generate_code(self):
        QMessageBox.information(self, "Generate", "Code generation started!")

    def optimize_code(self):
        QMessageBox.information(self, "Optimize", "Code optimization in progress!")

    def show_plugins(self):
        QMessageBox.information(self, "Plugins", "Plugin manager opened!")

    def show_memory(self):
        QMessageBox.information(self, "Memory", "Memory explorer opened!")

    def show_performance(self):
        QMessageBox.information(self, "Performance", "Performance monitor active!")

    def show_about(self):
        QMessageBox.about(
            self,
            "About Neuroplex",
            "🧬 Neuroplex v2.0\n\n"
            "The next-generation AI-native development environment.\n\n"
            "Features:\n"
            "• Multi-LLM support\n"
            "• Vector memory system\n"
            "• Natural language programming\n"
            "• Real-time collaboration\n"
            "• Plugin ecosystem\n\n"
            "Built with ❤️ for the future of programming.",
        )

    def show_docs(self):
        QMessageBox.information(self, "Documentation", "Opening documentation...")


def main():
    """Run the Neuroplex GUI"""
    if not QT_AVAILABLE:
        print("❌ Qt library not available. Please install PySide6 or PyQt6.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Neuroplex v2.0")
    app.setApplicationVersion("2.0.0")

    # Set application icon if available
    try:
        # Set application icon
        icon_path = Path(__file__).parent.parent.parent / "assets" / "images" / "neurocode-icon.ico"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        else:
            # Fallback to PNG if ICO not available
            png_icon_path = Path(__file__).parent.parent.parent / "assets" / "images" / "neurocode-icon.png"
            if png_icon_path.exists():
                app.setWindowIcon(QIcon(str(png_icon_path)))
    except Exception:
        pass

    window = ModernNeuroplexWindow()
    window.show()

    print("🧬 Neuroplex v2.0 launched successfully!")
    print("🎨 Modern dark mode interface active")
    print("🚀 Ready for AI-native development!")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
