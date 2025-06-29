#!/usr/bin/env python3
"""
Modular Neuroplex GUI v2.0 - Main Window
========================================

Simplified main window that demonstrates the modular structure.
This version imports components from separate modules for better organization.
"""

import sys
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Qt imports with fallback
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


# Import theme and components - fallback to inline if import fails
try:
    from ui.components.theme import ModernTheme

    print("✅ Imported ModernTheme from modular components")
except ImportError:
    print("⚠️ Using inline theme - components not available")

    # Inline theme as fallback
    class ModernTheme:
        BACKGROUND = "#0a0a0a"
        SURFACE = "#1a1a1a"
        SURFACE_VARIANT = "#2a2a2a"
        CARD = "#1e1e1e"
        PRIMARY = "#3b82f6"
        PRIMARY_VARIANT = "#1e40af"
        SECONDARY = "#06d6a0"
        SECONDARY_VARIANT = "#059669"
        ACCENT = "#8b5cf6"
        SUCCESS = "#10b981"
        WARNING = "#f59e0b"
        ERROR = "#ef4444"
        INFO = "#06b6d4"
        TEXT_PRIMARY = "#ffffff"
        TEXT_SECONDARY = "#a3a3a3"
        TEXT_TERTIARY = "#6b7280"
        TEXT_DISABLED = "#4b5563"
        BORDER = "#374151"

        @staticmethod
        def get_main_stylesheet():
            return f"""
            QMainWindow {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            }}
            QWidget {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: {ModernTheme.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_VARIANT};
            }}
            """


class SimpleCard(QWidget):
    """Simple card for demonstration"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.CARD};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)


class SimpleLLMPanel(SimpleCard):
    """Simplified LLM Provider Panel"""

    def __init__(self, parent=None):
        super().__init__("🤖 LLM Providers", parent)
        self.init_ui()

    def init_ui(self):
        # Provider selection
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Provider:"))

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(
            ["OpenAI GPT-4", "OpenAI GPT-3.5", "Anthropic Claude", "Google Gemini"]
        )
        provider_layout.addWidget(self.provider_combo)

        provider_widget = QWidget()
        provider_widget.setLayout(provider_layout)
        self.add_widget(provider_widget)

        # Status
        self.status_label = QLabel("✅ Ready")
        self.status_label.setStyleSheet(f"color: {ModernTheme.SUCCESS};")
        self.add_widget(self.status_label)


class SimpleMemoryPanel(SimpleCard):
    """Simplified Memory Panel"""

    def __init__(self, parent=None):
        super().__init__("🧠 Memory", parent)
        self.init_ui()

    def init_ui(self):
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Memories:"), 0, 0)
        stats_layout.addWidget(QLabel("42"), 0, 1)
        stats_layout.addWidget(QLabel("Embeddings:"), 1, 0)
        stats_layout.addWidget(QLabel("128"), 1, 1)

        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        self.add_widget(stats_widget)


class ModularNeuroplexWindow(QMainWindow):
    """Modular Neuroplex main window demonstrating component separation"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧬 Neuroplex v2.0 - Modular Interface")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Apply theme
        self.setStyleSheet(ModernTheme.get_main_stylesheet())

        # Initialize components (simplified)
        self.init_core_components()
        self.init_ui()
        self.init_menu_bar()

    def init_core_components(self):
        """Initialize core components with graceful fallbacks"""
        print("⚠️ Core components not loaded - using mock data")
        self.llm_manager = None
        self.vector_memory = None
        self.performance_optimizer = None

    def init_ui(self):
        """Initialize the modular user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Modular components
        left_panel = self.create_left_panel()
        left_panel.setMinimumWidth(250)
        left_panel.setMaximumWidth(350)
        splitter.addWidget(left_panel)

        # Center panel - Main workspace
        center_panel = self.create_center_panel()
        center_panel.setMinimumWidth(400)
        splitter.addWidget(center_panel)

        # Right panel - Information
        right_panel = self.create_right_panel()
        right_panel.setMinimumWidth(250)
        right_panel.setMaximumWidth(350)
        splitter.addWidget(right_panel)

        # Set proportions
        splitter.setSizes([300, 600, 300])

    def create_left_panel(self):
        """Create left panel with modular components"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)

        # Add modular components
        self.llm_panel = SimpleLLMPanel()
        layout.addWidget(self.llm_panel)

        # Performance monitor (simplified)
        perf_panel = SimpleCard("⚡ Performance")
        perf_layout = QGridLayout()
        perf_layout.addWidget(QLabel("CPU:"), 0, 0)
        perf_layout.addWidget(QLabel("25%"), 0, 1)
        perf_layout.addWidget(QLabel("Memory:"), 1, 0)
        perf_layout.addWidget(QLabel("60%"), 1, 1)
        perf_widget = QWidget()
        perf_widget.setLayout(perf_layout)
        perf_panel.add_widget(perf_widget)
        layout.addWidget(perf_panel)

        layout.addStretch()
        return panel

    def create_center_panel(self):
        """Create center workspace panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Code editor tab
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)

        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText(
            "// Modular Neuroplex v2.0\n"
            "// Components are now in separate modules!\n\n"
            "model: gpt-4\n"
            "memory: vector_search\n"
            "goal: modular_architecture"
        )
        editor_layout.addWidget(self.code_editor)

        # Buttons
        buttons_layout = QHBoxLayout()
        run_btn = QPushButton("▶️ Run")
        save_btn = QPushButton("💾 Save")
        buttons_layout.addWidget(run_btn)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addStretch()
        editor_layout.addLayout(buttons_layout)

        self.tab_widget.addTab(editor_tab, "⚡ Code Editor")

        return panel

    def create_right_panel(self):
        """Create right information panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)

        # Memory panel (modular)
        self.memory_panel = SimpleMemoryPanel()
        layout.addWidget(self.memory_panel)

        # Plugin panel (simplified)
        plugin_panel = SimpleCard("🔌 Plugins")
        plugin_list = QListWidget()
        plugin_list.addItems(["Code Formatter ✅", "Git Tools ✅", "AI Assistant ⚠️"])
        plugin_list.setMaximumHeight(100)
        plugin_panel.add_widget(plugin_list)
        layout.addWidget(plugin_panel)

        layout.addStretch()
        return panel

    def init_menu_bar(self):
        """Initialize menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction(
            "New Project", lambda: QMessageBox.information(self, "Info", "New Project")
        )
        file_menu.addAction("Exit", self.close)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Reload Modules", self.reload_modules)

    def reload_modules(self):
        """Demonstrate module reloading capability"""
        QMessageBox.information(
            self,
            "Module Reload",
            "In a full implementation, this would reload component modules\n"
            "allowing for hot-swapping of UI components during development!",
        )


def main():
    """Run the modular Neuroplex GUI"""
    if not QT_AVAILABLE:
        print("❌ Qt library not available.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Neuroplex v2.0 - Modular")

    window = ModularNeuroplexWindow()
    window.show()

    print("🧬 Modular Neuroplex v2.0 launched successfully!")
    print("🎨 Demonstrating separated component architecture")
    print("🚀 Ready for modular development!")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
