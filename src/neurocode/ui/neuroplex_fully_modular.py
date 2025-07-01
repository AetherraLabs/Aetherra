#!/usr/bin/env python3
"""
Neuroplex GUI v2.0 - Fully Modular Implementation
=================================================

Complete modular implementation using all extracted panel components.
This file demonstrates the power of the modular architecture.
"""

import sys
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import Qt components
from neurocode.ui.components.utils.qt_imports import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    Qt,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    ensure_qt_app,
    is_qt_available,
)

# Import theme and components
try:
    from neurocode.ui.components.panels import (
        GoalTrackingPanel,
        LLMProviderPanel,
        MemoryVisualizationPanel,
        NaturalLanguagePanel,
        PerformanceMonitorPanel,
        PluginManagerPanel,
    )
    from neurocode.ui.components.theme import ModernTheme

    COMPONENTS_AVAILABLE = True
    print("✅ All modular components loaded successfully")
except ImportError as e:
    print(f"⚠️ Component import error: {e}")
    COMPONENTS_AVAILABLE = False


class FullyModularNeuroplexWindow(QMainWindow):
    """Fully modular Neuroplex window using all extracted components"""

    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("🧬 Neuroplex v2.0 - Fully Modular")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        # Apply theme
        if COMPONENTS_AVAILABLE:
            self.setStyleSheet(ModernTheme.get_main_stylesheet())

        # Initialize UI
        self.init_menu_bar()
        self.init_central_widget()
        self.init_status_bar()

        print("🎨 Fully modular Neuroplex window initialized")

    def init_menu_bar(self):
        """Initialize the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Project")
        file_menu.addAction("Open Project")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Toggle LLM Panel")
        view_menu.addAction("Toggle Memory Panel")
        view_menu.addAction("Toggle Performance Panel")

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Plugin Manager")
        tools_menu.addAction("Settings")
        tools_menu.addAction("Debug Console")

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Documentation")
        help_menu.addAction("About")

    def init_central_widget(self):
        """Initialize the central widget with modular panels"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Core AI and Language
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # Center panel - Main workspace
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)

        # Right panel - Monitoring and Management
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions (30% - 40% - 30%)
        main_splitter.setSizes([300, 500, 300])

        main_layout.addWidget(main_splitter)

    def create_left_panel(self) -> QWidget:
        """Create the left panel with AI and language components"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        if COMPONENTS_AVAILABLE:
            # LLM Provider panel
            self.llm_panel = LLMProviderPanel()
            left_layout.addWidget(self.llm_panel)

            # Natural Language panel
            self.natural_lang_panel = NaturalLanguagePanel()
            left_layout.addWidget(self.natural_lang_panel)
        else:
            # Fallback content
            fallback_label = QLabel("LLM & Natural Language\n(Components not available)")
            fallback_label.setStyleSheet("color: orange; text-align: center; padding: 20px;")
            left_layout.addWidget(fallback_label)

        return left_widget

    def create_center_panel(self) -> QWidget:
        """Create the center panel with tabbed workspace"""
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)

        # Create tab widget for different workspaces
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        if COMPONENTS_AVAILABLE:
            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid {ModernTheme.BORDER};
                    background-color: {ModernTheme.SURFACE};
                }}
                QTabBar::tab {{
                    background-color: {ModernTheme.SURFACE_VARIANT};
                    color: {ModernTheme.TEXT_SECONDARY};
                    padding: 8px 16px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {ModernTheme.PRIMARY};
                    color: {ModernTheme.TEXT_PRIMARY};
                }}
            """)

        # Memory & Goal Management tab
        if COMPONENTS_AVAILABLE:
            memory_goal_widget = QWidget()
            memory_goal_layout = QVBoxLayout(memory_goal_widget)

            self.memory_panel = MemoryVisualizationPanel()
            memory_goal_layout.addWidget(self.memory_panel)

            self.goal_panel = GoalTrackingPanel()
            memory_goal_layout.addWidget(self.goal_panel)

            self.tab_widget.addTab(memory_goal_widget, "🧠 Memory & Goals")
        else:
            fallback_tab = QLabel("Memory & Goals\n(Components not available)")
            fallback_tab.setStyleSheet("color: orange; text-align: center;")
            self.tab_widget.addTab(fallback_tab, "Memory & Goals")

        # Plugin Management tab
        if COMPONENTS_AVAILABLE:
            self.plugin_panel = PluginManagerPanel()
            self.tab_widget.addTab(self.plugin_panel, "🔌 Plugins")
        else:
            fallback_plugin = QLabel("Plugin Manager\n(Components not available)")
            fallback_plugin.setStyleSheet("color: orange; text-align: center;")
            self.tab_widget.addTab(fallback_plugin, "Plugins")

        # Playground tab (placeholder for NeuroCode)
        playground_widget = QLabel(
            "🎮 NeuroCode Playground\n\nThis area would contain:\n• Code editor\n• Execution environment\n• Syntax highlighting\n• Debug tools"
        )
        playground_widget.setStyleSheet("color: #888; text-align: center; padding: 40px;")
        self.tab_widget.addTab(playground_widget, "🎮 Playground")

        center_layout.addWidget(self.tab_widget)
        return center_widget

    def create_right_panel(self) -> QWidget:
        """Create the right panel with monitoring components"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        if COMPONENTS_AVAILABLE:
            # Performance Monitor
            self.performance_panel = PerformanceMonitorPanel()
            right_layout.addWidget(self.performance_panel)

            # System Status (placeholder)
            status_label = QLabel(
                "📊 System Status\n\n✅ All systems operational\n🔄 Background tasks: 3\n📈 Uptime: 2h 34m"
            )
            status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.CARD};
                    border: 1px solid {ModernTheme.BORDER};
                    border-radius: 6px;
                    padding: 16px;
                    color: {ModernTheme.TEXT_SECONDARY};
                    font-family: monospace;
                }}
            """)
            right_layout.addWidget(status_label)
        else:
            # Fallback content
            fallback_label = QLabel("Performance Monitor\n(Components not available)")
            fallback_label.setStyleSheet("color: orange; text-align: center; padding: 20px;")
            right_layout.addWidget(fallback_label)

        return right_widget

    def init_status_bar(self):
        """Initialize the status bar"""
        status_bar = self.statusBar()

        # Left side status
        if COMPONENTS_AVAILABLE:
            status_bar.showMessage("🧬 Neuroplex v2.0 - Fully Modular | Ready")
        else:
            status_bar.showMessage("🧬 Neuroplex v2.0 - Limited Mode (Components unavailable)")

        # Right side widgets (placeholder)
        status_bar.addPermanentWidget(QLabel("🟢 Connected"))

    def get_component_status(self) -> dict:
        """Get status of all modular components"""
        if not COMPONENTS_AVAILABLE:
            return {"status": "limited", "reason": "Components not available"}

        status = {
            "status": "operational",
            "components": {
                "llm_provider": hasattr(self, "llm_panel"),
                "memory_visualization": hasattr(self, "memory_panel"),
                "performance_monitor": hasattr(self, "performance_panel"),
                "goal_tracking": hasattr(self, "goal_panel"),
                "plugin_manager": hasattr(self, "plugin_panel"),
                "natural_language": hasattr(self, "natural_lang_panel"),
            },
        }

        return status


def main():
    """Main entry point for the fully modular Neuroplex"""
    print("🚀 Starting Neuroplex v2.0 - Fully Modular")

    # Check Qt availability
    if not is_qt_available():
        print("❌ Qt framework not available. Please install PySide6 or PyQt6.")
        return 1

    # Create application
    app = ensure_qt_app()
    if not app:
        print("❌ Failed to create Qt application")
        return 1

    try:
        # Create and show main window
        window = FullyModularNeuroplexWindow()
        window.show()

        # Print component status
        status = window.get_component_status()
        print(f"📊 Component Status: {status['status']}")

        if status["status"] == "operational":
            active_components = sum(status["components"].values())
            total_components = len(status["components"])
            print(f"✅ Active Components: {active_components}/{total_components}")

        print("🎨 Neuroplex is now running - enjoy the modular experience!")

        # Run application
        return app.exec()

    except Exception as e:
        print(f"❌ Error starting Neuroplex: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
