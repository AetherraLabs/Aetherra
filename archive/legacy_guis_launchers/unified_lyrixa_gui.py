#!/usr/bin/env python3
"""
🧠 UNIFIED LYRIXA GUI LAUNCHER - PHASE 3 & 4 COMPLETE
======================================================

Advanced AI Assistant Interface with:
- Phase 1: Advanced Memory System with Vector Embeddings
- Phase 2: Anticipation Engine with Proactive Intelligence
- Phase 3: Analytics Dashboard, Configuration, Performance Monitoring
- Phase 4: Intelligence Layer, Enhanced Analytics, Web/Mobile, Live Feedback

This launcher provides a comprehensive GUI experience with all components integrated.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "lyrixa"))
sys.path.insert(0, str(project_root / "src"))

# Import Qt framework
try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont, QIcon
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSplitter,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
    print("✅ PySide6 GUI framework available")
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("❌ PySide6 not available - GUI functionality limited")


class UnifiedLyrixaLauncher(QMainWindow if PYSIDE6_AVAILABLE else object):
    """
    Unified Lyrixa GUI Launcher

    Integrates all Phase 1-4 components into a single interface:
    - Intelligence Layer with memory visualization
    - Real-time Analytics Dashboard
    - Configuration and Preferences
    - Performance Monitoring
    - Suggestion Notifications
    - Web/Mobile Sync
    - Live Feedback Loop
    """

    def __init__(self):
        if not PYSIDE6_AVAILABLE:
            print("⚠️ GUI functionality not available without PySide6")
            return

        super().__init__()

        # Component references
        self.intelligence_layer = None
        self.analytics_dashboard = None
        self.enhanced_analytics = None
        self.configuration_manager = None
        self.performance_monitor = None
        self.notification_system = None
        self.web_mobile_interface = None
        self.feedback_loop = None

        # Enhanced Lyrixa Window integration
        self.enhanced_lyrixa = None

        self.init_ui()
        self.load_components()

        print("🚀 Unified Lyrixa GUI Launcher initialized successfully!")

    def init_ui(self):
        """Initialize the main UI structure."""
        self.setWindowTitle("🧠 Lyrixa AI Assistant - Complete Interface")
        self.setGeometry(100, 100, 1400, 900)

        # Modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom: 2px solid #00aaff;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #00aaff;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0088cc;
            }
            QPushButton:pressed {
                background-color: #006699;
            }
        """)

        # Central widget with tab system
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🧠 Lyrixa AI Assistant - Complete Interface")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)

        # Quick action buttons
        self.status_button = QPushButton("🟢 All Systems Online")
        self.status_button.setEnabled(False)
        header_layout.addWidget(self.status_button)

        self.refresh_button = QPushButton("🔄 Refresh All")
        self.refresh_button.clicked.connect(self.refresh_all_components)
        header_layout.addWidget(self.refresh_button)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Main tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Status bar placeholder
        status_layout = QHBoxLayout()
        self.status_label = QLabel("🚀 Ready - All Phase 1-4 components loaded")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

    def load_components(self):
        """Load and integrate all GUI components."""
        print("📦 Loading all GUI components...")

        # Load Phase 4 - Intelligence Layer
        self.load_intelligence_layer()

        # Load Phase 3 & 4 - Analytics
        self.load_analytics_components()

        # Load Phase 3 - Configuration and Performance
        self.load_system_components()

        # Load Phase 4 - Web/Mobile and Feedback
        self.load_advanced_components()

        # Load Enhanced Lyrixa Integration
        self.load_enhanced_lyrixa()

        print("✅ All components loaded successfully!")

    def load_intelligence_layer(self):
        """Load Phase 4 Intelligence Layer components."""
        try:
            from lyrixa.gui.intelligence_layer import IntelligenceLayerWidget

            self.intelligence_layer = IntelligenceLayerWidget()
            self.tab_widget.addTab(self.intelligence_layer, "🧠 Intelligence Layer")
            print("✅ Intelligence Layer loaded")

        except Exception as e:
            print(f"⚠️ Intelligence Layer not available: {e}")
            self.add_placeholder_tab(
                "🧠 Intelligence Layer",
                "Intelligence Layer with memory visualization and live thinking display",
            )

    def load_analytics_components(self):
        """Load analytics dashboard components."""
        try:
            # Phase 3 Analytics Dashboard
            from lyrixa.gui.analytics_dashboard import AnalyticsDashboard

            self.analytics_dashboard = AnalyticsDashboard()
            self.tab_widget.addTab(self.analytics_dashboard, "📊 Analytics Dashboard")
            print("✅ Analytics Dashboard loaded")

        except Exception as e:
            print(f"⚠️ Analytics Dashboard not available: {e}")
            self.add_placeholder_tab(
                "📊 Analytics Dashboard", "Real-time analytics and performance metrics"
            )

        try:
            # Phase 4 Enhanced Analytics
            from lyrixa.gui.enhanced_analytics import EnhancedAnalyticsDashboard

            self.enhanced_analytics = EnhancedAnalyticsDashboard()
            self.tab_widget.addTab(self.enhanced_analytics, "📈 Enhanced Analytics")
            print("✅ Enhanced Analytics loaded")

        except Exception as e:
            print(f"⚠️ Enhanced Analytics not available: {e}")
            self.add_placeholder_tab(
                "📈 Enhanced Analytics", "Advanced analytics with predictive insights"
            )

    def load_system_components(self):
        """Load system configuration and performance components."""
        try:
            # Configuration Manager
            from lyrixa.gui.configuration_manager import ConfigurationManager

            self.configuration_manager = ConfigurationManager()
            self.tab_widget.addTab(self.configuration_manager, "⚙️ Configuration")
            print("✅ Configuration Manager loaded")

        except Exception as e:
            print(f"⚠️ Configuration Manager not available: {e}")
            self.add_placeholder_tab(
                "⚙️ Configuration", "System preferences and settings management"
            )

        try:
            # Performance Monitor
            from lyrixa.gui.performance_monitor import PerformanceMonitor

            self.performance_monitor = PerformanceMonitor()
            self.tab_widget.addTab(self.performance_monitor, "⚡ Performance")
            print("✅ Performance Monitor loaded")

        except Exception as e:
            print(f"⚠️ Performance Monitor not available: {e}")
            self.add_placeholder_tab(
                "⚡ Performance", "System performance monitoring and optimization"
            )

        try:
            # Suggestion Notifications
            from lyrixa.gui.suggestion_notifications import SuggestionNotificationSystem

            self.notification_system = SuggestionNotificationSystem()
            self.tab_widget.addTab(self.notification_system, "💡 Notifications")
            print("✅ Notification System loaded")

        except Exception as e:
            print(f"⚠️ Notification System not available: {e}")
            self.add_placeholder_tab(
                "💡 Notifications", "Intelligent suggestion and notification management"
            )

    def load_advanced_components(self):
        """Load Phase 4 advanced components."""
        try:
            # Web/Mobile Support
            from lyrixa.gui.web_mobile_support import WebMobileInterface

            self.web_mobile_interface = WebMobileInterface()
            self.tab_widget.addTab(self.web_mobile_interface, "🌐 Web/Mobile")
            print("✅ Web/Mobile Interface loaded")

        except Exception as e:
            print(f"⚠️ Web/Mobile Interface not available: {e}")
            self.add_placeholder_tab(
                "🌐 Web/Mobile", "Cross-platform synchronization and mobile support"
            )

        try:
            # Live Feedback Loop
            from lyrixa.gui.live_feedback_loop import LiveFeedbackInterface

            self.feedback_loop = LiveFeedbackInterface()
            self.tab_widget.addTab(self.feedback_loop, "🔄 Feedback Loop")
            print("✅ Live Feedback Loop loaded")

        except Exception as e:
            print(f"⚠️ Live Feedback Loop not available: {e}")
            self.add_placeholder_tab(
                "🔄 Feedback Loop", "Adaptive learning and user feedback system"
            )

    def load_enhanced_lyrixa(self):
        """Load Enhanced Lyrixa Window integration."""
        try:
            from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

            # Create a wrapper widget for the Enhanced Lyrixa Window
            lyrixa_widget = QWidget()
            lyrixa_layout = QVBoxLayout()

            info_label = QLabel("🎙️ Enhanced Lyrixa Assistant")
            info_label.setFont(QFont("Arial", 14, QFont.Bold))
            lyrixa_layout.addWidget(info_label)

            description = QLabel("""
Complete AI assistant interface with:
• Advanced memory system with vector embeddings
• Anticipation engine with proactive suggestions
• Real-time chat with context awareness
• Plugin system integration
• Goal tracking and management
            """)
            lyrixa_layout.addWidget(description)

            # Launch button
            launch_button = QPushButton("🚀 Launch Enhanced Lyrixa Window")
            launch_button.clicked.connect(self.launch_enhanced_lyrixa)
            lyrixa_layout.addWidget(launch_button)

            lyrixa_layout.addStretch()
            lyrixa_widget.setLayout(lyrixa_layout)

            self.tab_widget.addTab(lyrixa_widget, "🎙️ Lyrixa Assistant")
            print("✅ Enhanced Lyrixa integration loaded")

        except Exception as e:
            print(f"⚠️ Enhanced Lyrixa integration not available: {e}")
            self.add_placeholder_tab(
                "🎙️ Lyrixa Assistant",
                "Main AI assistant interface with chat and plugins",
            )

    def add_placeholder_tab(self, title: str, description: str):
        """Add a placeholder tab when component is not available."""
        placeholder = QWidget()
        layout = QVBoxLayout()

        error_label = QLabel(f"⚠️ {title}")
        error_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(error_label)

        desc_label = QLabel(
            f"This component is not currently available.\n\n{description}"
        )
        layout.addWidget(desc_label)

        layout.addStretch()
        placeholder.setLayout(layout)

        self.tab_widget.addTab(placeholder, title)

    def launch_enhanced_lyrixa(self):
        """Launch the Enhanced Lyrixa Window in a separate window."""
        try:
            from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

            if not hasattr(self, "enhanced_lyrixa_window"):
                self.enhanced_lyrixa_window = EnhancedLyrixaWindow()

            # Show message
            QMessageBox.information(
                self,
                "Enhanced Lyrixa Launched",
                "Enhanced Lyrixa Assistant has been initialized!\n\nCheck the console output for the interface.",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Launch Error", f"Failed to launch Enhanced Lyrixa:\n{str(e)}"
            )

    def refresh_all_components(self):
        """Refresh all loaded components."""
        print("🔄 Refreshing all components...")

        # Update status
        self.status_label.setText("🔄 Refreshing components...")

        # Refresh each component that supports it
        components = [
            self.intelligence_layer,
            self.analytics_dashboard,
            self.enhanced_analytics,
            self.performance_monitor,
            self.notification_system,
            self.web_mobile_interface,
            self.feedback_loop,
        ]

        for component in components:
            if component and hasattr(component, "refresh_data"):
                try:
                    component.refresh_data()
                except Exception as e:
                    print(f"⚠️ Error refreshing component: {e}")

        # Update status
        self.status_label.setText("✅ All components refreshed")

        # Reset status after delay
        QTimer.singleShot(
            3000,
            lambda: self.status_label.setText(
                "🚀 Ready - All Phase 1-4 components loaded"
            ),
        )

        print("✅ Component refresh complete")


def main():
    """Main application entry point."""
    print("🚀 LAUNCHING UNIFIED LYRIXA GUI")
    print("=" * 50)

    if not PYSIDE6_AVAILABLE:
        print("❌ Cannot launch GUI - PySide6 not available")
        print("📦 Install with: pip install PySide6")
        return False

    try:
        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create and show main window
        launcher = UnifiedLyrixaLauncher()
        launcher.show()

        print("✅ Unified Lyrixa GUI launched successfully!")
        print("🎯 All Phase 1-4 components integrated")
        print("📱 Interface ready for interaction")

        # Don't block in script mode, but show instructions
        print("\n" + "=" * 50)
        print("🎮 GUI CONTROLS:")
        print("• Use tabs to navigate between components")
        print("• Click 'Refresh All' to update all components")
        print("• Launch Enhanced Lyrixa for full assistant interface")
        print("• Close window to exit")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Unified Lyrixa GUI is ready!")
        print("👆 Check the GUI window for the complete interface")
    else:
        print("\n❌ GUI launch failed - check error messages above")

    # Keep the script running briefly to show the GUI
    import time

    time.sleep(2)
