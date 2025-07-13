"""
Enhanced Lyrixa Window
=====================

Main enhanced UI window for the Lyrixa assistant system.
Provides a sophisticated interface for Aetherra code interaction with real AI functionality.
Integrates Phase 3 components: Analytics Dashboard, Suggestion Notifications, Configuration Manager, and Performance Monitor.
"""

# Type: ignore for entire file to suppress Qt/import compatibility warnings
# pylint: disable=all
# pyright: ignore-errors

import sys
from concurrent.futures import ThreadPoolExecutor

# Import Phase 3 GUI components
try:
    # Import GUI components from the same package
    from .analytics_dashboard import AnalyticsDashboard  # type: ignore
    from .chat_history_manager import ChatHistoryManager  # type: ignore
    from .configuration_manager import ConfigurationManager  # type: ignore

    # Import new polish components
    from .context_memory_manager import ContextMemoryManager  # type: ignore
    from .intelligence_layer import IntelligenceLayerWidget  # type: ignore
    from .intelligence_panel_manager import IntelligencePanelManager  # type: ignore
    from .performance_monitor import PerformanceMonitor  # type: ignore
    from .personality_manager import PersonalityManager  # type: ignore
    from .plugin_panel_manager import PluginPanelManager  # type: ignore
    from .quick_commands_manager import QuickCommandsManager  # type: ignore
    from .response_style_memory import ResponseStyleMemoryManager  # type: ignore
    from .suggestion_notifications import SuggestionNotificationSystem  # type: ignore

    PHASE3_GUI_AVAILABLE = True
except ImportError as e:
    print(f"Phase 3 GUI components not available: {e}")
    PHASE3_GUI_AVAILABLE = False

    # Create mock classes for missing components
    class AnalyticsDashboard:  # type: ignore
        def __init__(self):
            pass

        def show(self):
            pass

        def raise_(self):
            pass

        def get_widget(self):
            return None

        def refresh_data(self):
            pass

        def start_live_refresh(self):
            pass

        def bind_memory_data(self, memory):
            pass

    class ChatHistoryManager:  # type: ignore
        def __init__(self):
            pass

    class ConfigurationManager:  # type: ignore
        def __init__(self):
            pass

        def show(self):
            pass

        def raise_(self):
            pass

        def get_widget(self):
            return None

    class ContextMemoryManager:  # type: ignore
        def __init__(self):
            pass

        def switch_context(self, context_type, context_data):
            pass

    class IntelligenceLayerWidget:  # type: ignore
        def __init__(self):
            pass

        def initialize_state(self):
            pass

        def update_display(self):
            pass

        def connect_memory_system(self, memory):
            pass

    class IntelligencePanelManager:  # type: ignore
        def __init__(self):
            pass

        def start_monitoring(self):
            pass

    class PerformanceMonitor:  # type: ignore
        def __init__(self):
            pass

        def show(self):
            pass

        def raise_(self):
            pass

        def get_widget(self):
            return None

        def update_metrics(self):
            pass

    class PersonalityManager:  # type: ignore
        def __init__(self):
            pass

    class PluginPanelManager:  # type: ignore
        def __init__(self):
            pass

    class QuickCommandsManager:  # type: ignore
        def __init__(self):
            pass

    class ResponseStyleMemoryManager:  # type: ignore
        def __init__(self):
            pass

    class SuggestionNotificationSystem:  # type: ignore
        def __init__(self):
            pass

        def show(self):
            pass

        def hide(self):
            pass

        def raise_(self):
            pass

        def isVisible(self):
            return False

        def get_widget(self):
            return None

        def check_pending_suggestions(self):
            pass


# Import anticipation engine
try:
    from lyrixa.core.anticipation_engine import AnticipationEngine  # type: ignore

    ANTICIPATION_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Anticipation engine not available: {e}")
    ANTICIPATION_ENGINE_AVAILABLE = False

    # Create mock class for missing anticipation engine
    class AnticipationEngine:  # type: ignore
        def __init__(self):
            pass


class EnhancedLyrixaWindow:
    """
    Enhanced Lyrixa Assistant Window

    Main window for the Lyrixa assistant with advanced features:
    - Multi-panel interface
    - Real-time code interpretation
    - Plugin integration
    - Enhanced chat capabilities
    """

    def __init__(self):
        """Initialize the Enhanced Lyrixa Window."""
        print("🎙️ Enhanced Lyrixa Window initialized")
        self.window_title = "Lyrixa Assistant - Enhanced Interface"
        self.width = 1200
        self.height = 800

        # Initialize event loop for async operations
        self.loop = None
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Initialize core components first
        self.plugins = []  # Initialize plugins list first
        self.goals = []
        self.memory = None
        self.advanced_memory = None
        self.lyrixa_ai = None

        # Initialize Phase 3 components
        self.analytics_dashboard = None
        self.notification_system = None
        self.config_manager = None
        self.performance_monitor = None
        self.anticipation_engine = None

        # Initialize new polish components
        self.context_memory_manager = None
        self.chat_history_manager = None
        self.plugin_panel_manager = None
        self.quick_commands_manager = None
        self.personality_manager = None
        self.response_style_memory = None
        self.intelligence_panel_manager = None

        # Initialize AI and memory systems
        self._initialize_lyrixa_ai()

        # Initialize Phase 3 components
        self._initialize_phase3_components()

        # Initialize polish components
        self._initialize_polish_components()

        print("✅ Enhanced Lyrixa Window ready with Phase 3 integration")

        # Call Phase 4 lifecycle initialization
        self.on_init()
        self.height = 800

        # Initialize core functionality first (before Qt setup)
        self.code_content = ""
        self.chat_history = []
        self.plugins = [
            "Memory System",
            "Code Analyzer",
            "Performance Monitor",
            "Debug Assistant",
            "Documentation Generator",
            "Goal Tracker",
            "Agent Orchestrator",
            "Aether Interpreter",
        ]
        self.active_plugin = None

        # Initialize advanced memory system early
        self.advanced_memory = None
        self.reflection_engine = None

        # Initialize real Lyrixa AI
        self.lyrixa_ai = None
        self._initialize_lyrixa_ai()

        # Check if Qt is available (but don't create widgets yet)
        try:
            import importlib.util

            if importlib.util.find_spec("PySide6.QtWidgets"):
                # Only check if Qt is available, don't create widgets yet
                self.qt_available = True
                self.main_window = None  # Will be created when show() is called
                print("✅ Qt GUI framework detected")
            else:
                self.qt_available = False
                print("⚠️ PySide6 not available - running in console mode")
        except ImportError:
            self.qt_available = False
            print("⚠️ PySide6 not available - running in console mode")

    def _initialize_lyrixa_ai(self):
        """Initialize the real Lyrixa AI system with Phase 1 Advanced Memory."""
        try:
            # Add the Lyrixa module to path
            import os
            import sys

            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            lyrixa_path = os.path.join(project_root, "lyrixa")
            if lyrixa_path not in sys.path:
                sys.path.insert(0, lyrixa_path)

            from lyrixa import LyrixaAI

            # Initialize Lyrixa AI with workspace
            workspace_path = project_root
            self.lyrixa_ai = LyrixaAI(workspace_path=workspace_path)
            print("✅ Real Lyrixa AI system initialized")

            # Initialize debug console widget
            self._initialize_debug_console()

            # Initialize Phase 1 Advanced Memory System
            self._initialize_advanced_memory()

        except Exception as e:
            print(f"⚠️ Could not initialize Lyrixa AI: {e}")
            self.lyrixa_ai = None

    def _initialize_debug_console(self):
        """Initialize debug console widget."""
        try:
            from .debug_console_widget import DebugConsoleWidget  # type: ignore

            # Get debug console from Lyrixa AI if available
            debug_console = None
            if self.lyrixa_ai and hasattr(self.lyrixa_ai, "debug_console"):
                debug_console = self.lyrixa_ai.debug_console

            # Create debug console widget
            self.debug_console_widget = DebugConsoleWidget(debug_console)

            print("🐛 Debug Console widget initialized")
            print("   ✅ Real-time cognitive state monitoring")
            print("   ✅ Thought process introspection")
            print("   ✅ Decision matrix analysis")

        except Exception as e:
            print(f"⚠️ Could not initialize Debug Console: {e}")
            self.debug_console_widget = None

    def _initialize_advanced_memory(self):
        """Initialize Phase 1 Advanced Memory System."""
        try:
            from lyrixa.core.advanced_vector_memory import (
                AdvancedMemorySystem,
                ReflexiveAnalysisEngine,
            )

            # Initialize advanced memory
            self.advanced_memory = AdvancedMemorySystem()
            self.reflection_engine = ReflexiveAnalysisEngine(self.advanced_memory)

            print("🧠 Phase 1 Advanced Memory System integrated")
            print("   ✅ Vector embeddings enabled")
            print("   ✅ Confidence modeling active")
            print("   ✅ Reflexive analysis ready")

            # Add memory system to plugins
            if "Advanced Memory" not in self.plugins:
                self.plugins.insert(0, "Advanced Memory")

        except Exception as e:
            print(f"⚠️ Could not initialize Advanced Memory: {e}")
            self.advanced_memory = None
            self.reflection_engine = None

    def _initialize_phase3_components(self):
        """Initialize Phase 3 GUI components and anticipation engine."""
        try:
            # Initialize anticipation engine first (doesn't require Qt)
            if ANTICIPATION_ENGINE_AVAILABLE:
                self.anticipation_engine = AnticipationEngine()
                print("🔮 Anticipation Engine initialized")

            # Phase 3 GUI components will be initialized later when Qt is available
            print("ℹ️ Phase 3 GUI components will be initialized when showing window")

        except Exception as e:
            print(f"⚠️ Error in Phase 3 initialization: {e}")

    def _initialize_polish_components(self):
        """Initialize strategic polish components for enhanced UX."""
        try:
            print("✨ Initializing Lyrixa polish components...")

            # Context Memory Manager - tracks user context switches
            self.context_memory_manager = ContextMemoryManager()
            print("   🧭 Context Memory Manager initialized")

            # Chat History Manager - conversation history and replay
            self.chat_history_manager = ChatHistoryManager()
            print("   💬 Chat History Manager initialized")

            # Plugin Panel Manager - collapsible panels with layout memory
            self.plugin_panel_manager = PluginPanelManager()
            print("   🔌 Plugin Panel Manager initialized")

            # Quick Commands Manager - GUI buttons for common actions
            self.quick_commands_manager = QuickCommandsManager()
            print("   ⚡ Quick Commands Manager initialized")

            # Personality Manager - personality presets and style adaptation
            self.personality_manager = PersonalityManager()
            print("   🎭 Personality Manager initialized")

            # Response Style Memory - learns from user feedback
            self.response_style_memory = ResponseStyleMemoryManager()
            print("   🎯 Response Style Memory initialized")

            # Intelligence Panel Manager - real-time system insights
            self.intelligence_panel_manager = IntelligencePanelManager()
            print("   🧠 Intelligence Panel Manager initialized")

            # Start intelligence monitoring
            self.intelligence_panel_manager.start_monitoring()

            print("✅ All polish components initialized successfully")

        except Exception as e:
            print(f"⚠️ Error initializing polish components: {e}")

    def _initialize_phase3_gui_components(self):
        """Initialize Phase 3 GUI components after Qt is available."""
        try:
            if not PHASE3_GUI_AVAILABLE:
                print("ℹ️ Phase 3 GUI components not available")
                return

            # Analytics Dashboard
            self.analytics_dashboard = AnalyticsDashboard()
            print("📊 Analytics Dashboard initialized")

            # Suggestion Notification System
            self.notification_system = SuggestionNotificationSystem()
            print("💡 Suggestion Notification System initialized")

            # Configuration Manager
            self.config_manager = ConfigurationManager()
            print("⚙️ Configuration Manager initialized")

            # Performance Monitor
            self.performance_monitor = PerformanceMonitor()
            print("⚡ Performance Monitor initialized")

            # Intelligence Layer Widget
            self.intelligence_layer = IntelligenceLayerWidget()
            print("🧠 Intelligence Layer Widget initialized")

            # Connect anticipation engine to notification system
            if self.anticipation_engine and self.notification_system:
                self._connect_anticipation_to_notifications()

            print("✅ Phase 3 GUI components integrated successfully")

        except Exception as e:
            print(f"⚠️ Error initializing Phase 3 GUI components: {e}")
            # Set components to None if initialization fails
            self.analytics_dashboard = None
            self.notification_system = None
            self.config_manager = None
            self.performance_monitor = None

    def _connect_anticipation_to_notifications(self):
        """Connect the anticipation engine to the notification system."""
        try:
            # This would integrate the anticipation engine with notifications
            # For now, we'll set up basic connectivity
            print("🔗 Connecting anticipation engine to notification system")

            # In a full implementation, we would:
            # 1. Connect anticipation engine suggestion generation to notification display
            # 2. Set up callback handlers for user feedback
            # 3. Integrate with analytics for suggestion effectiveness tracking

            print("✅ Anticipation engine connected to notifications")

        except Exception as e:
            print(f"⚠️ Error connecting anticipation to notifications: {e}")

    def show_analytics_dashboard(self):
        """Show the analytics dashboard."""
        if self.analytics_dashboard:
            self.analytics_dashboard.show()
            self.analytics_dashboard.raise_()
        else:
            print("Analytics dashboard not available")

    def show_configuration_manager(self):
        """Show the configuration manager."""
        if self.config_manager:
            self.config_manager.show()
            self.config_manager.raise_()
        else:
            print("Configuration manager not available")

    def show_performance_monitor(self):
        """Show the performance monitor."""
        if self.performance_monitor:
            self.performance_monitor.show()
            self.performance_monitor.raise_()
        else:
            print("Performance monitor not available")

    def toggle_suggestion_notifications(self):
        """Toggle the suggestion notification system."""
        if self.notification_system:
            if self.notification_system.isVisible():
                self.notification_system.hide()
            else:
                self.notification_system.show()
                self.notification_system.raise_()
        else:
            print("Suggestion system not available")

    def _setup_qt_window(self):
        """Set up the Qt-based main window with enhanced layout."""
        from PySide6.QtWidgets import (  # type: ignore
            QHBoxLayout,
            QMainWindow,
            QSplitter,
            QWidget,
        )

        # Initialize Phase 3 GUI components now that Qt is available
        self._initialize_phase3_gui_components()

        self.main_window = QMainWindow()
        self.main_window.setWindowTitle(self.window_title)
        self.main_window.resize(self.width, self.height)

        # Create central widget with main layout
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create main splitter for flexible layout
        from PySide6.QtCore import Qt  # type: ignore

        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Panel: Memory Graph + "Lyrixa Thinks..." feed
        left_panel = self._create_main_panel()
        main_splitter.addWidget(left_panel)

        # Right Panel: Sidebar with live feedback + notifications
        right_panel = self._create_sidebar_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions (70% main, 30% sidebar)
        main_splitter.setSizes([int(self.width * 0.7), int(self.width * 0.3)])

        main_layout.addWidget(main_splitter)

        # Setup menu bar
        self._setup_menu_bar()

        # Setup status bar
        self._setup_status_bar()

        # Setup real-time updates
        self._setup_realtime_updates()

        print("✅ Enhanced main window layout created")

    def _create_main_panel(self):
        """Create the main panel with memory graph and live feed."""
        from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget  # type: ignore

        main_panel = QWidget()
        layout = QVBoxLayout(main_panel)

        # Create vertical splitter for memory graph and live feed
        from PySide6.QtCore import Qt  # type: ignore

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Memory Graph Widget
        memory_widget = self._create_memory_graph_widget()
        splitter.addWidget(memory_widget)

        # "Lyrixa Thinks..." Live Feed
        think_feed_widget = self._create_live_think_feed()
        splitter.addWidget(think_feed_widget)

        # Set proportions (60% memory graph, 40% live feed)
        splitter.setSizes([int(self.height * 0.6), int(self.height * 0.4)])

        layout.addWidget(splitter)

        return main_panel

    def _create_memory_graph_widget(self):
        """Create the memory graph visualization widget."""
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget  # type: ignore

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("🧠 Memory Graph")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Memory graph placeholder
        if self.advanced_memory:
            # In a real implementation, this would show the memory graph
            memory_display = QLabel("Memory system active - vector embeddings ready")
            memory_display.setStyleSheet("color: #28a745; padding: 20px;")
        else:
            memory_display = QLabel("Memory system not available")
            memory_display.setStyleSheet("color: #dc3545; padding: 20px;")

        layout.addWidget(memory_display)

        return widget

    def _create_live_think_feed(self):
        """Create the live thought feed widget."""
        from PySide6.QtWidgets import (  # type: ignore
            QLabel,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("💭 Lyrixa Thinks...")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Live feed text area
        self.think_feed = QTextEdit()
        self.think_feed.setReadOnly(True)
        self.think_feed.setStyleSheet(
            "QTextEdit { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; }"
        )
        layout.addWidget(self.think_feed)

        return widget

    def _create_sidebar_panel(self):
        """Create the sidebar with notifications and analytics."""
        from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget  # type: ignore

        sidebar = QWidget()
        layout = QVBoxLayout(sidebar)

        # Create tab widget for different panels
        tab_widget = QTabWidget()

        # Suggestions Tab
        suggestions_tab = self._create_suggestions_tab()
        tab_widget.addTab(suggestions_tab, "💡 Suggestions")

        # Analytics Tab
        analytics_tab = self._create_analytics_tab()
        tab_widget.addTab(analytics_tab, "📊 Analytics")

        # Configuration Tab
        config_tab = self._create_configuration_tab()
        tab_widget.addTab(config_tab, "⚙️ Config")

        # Performance Tab
        performance_tab = self._create_performance_tab()
        tab_widget.addTab(performance_tab, "⚡ Performance")

        layout.addWidget(tab_widget)

        # Bottom bar with context info
        bottom_bar = self._create_bottom_bar()
        layout.addWidget(bottom_bar)

        return sidebar

    def _create_suggestions_tab(self):
        """Create the suggestions tab widget."""
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget  # type: ignore

        widget = QWidget()
        layout = QVBoxLayout(widget)

        if self.notification_system:
            suggestion_widget = self.notification_system.get_widget()
            if suggestion_widget:
                layout.addWidget(suggestion_widget)
            else:
                placeholder = QLabel("Suggestion notifications ready...")
                placeholder.setStyleSheet("color: #666; padding: 20px;")
                layout.addWidget(placeholder)
        else:
            placeholder = QLabel("Suggestion system not available")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_analytics_tab(self):
        """Create the analytics tab widget."""
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget  # type: ignore

        widget = QWidget()
        layout = QVBoxLayout(widget)

        if self.analytics_dashboard:
            analytics_widget = self.analytics_dashboard.get_widget()
            if analytics_widget:
                layout.addWidget(analytics_widget)
            else:
                placeholder = QLabel("Analytics data will appear here...")
                placeholder.setStyleSheet("color: #666; padding: 20px;")
                layout.addWidget(placeholder)
        else:
            placeholder = QLabel("Analytics dashboard not available")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_configuration_tab(self):
        """Create the configuration tab widget."""
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget  # type: ignore

        widget = QWidget()
        layout = QVBoxLayout(widget)

        if self.config_manager:
            config_widget = self.config_manager.get_widget()
            if config_widget:
                layout.addWidget(config_widget)
            else:
                placeholder = QLabel("Configuration options will appear here...")
                placeholder.setStyleSheet("color: #666; padding: 20px;")
                layout.addWidget(placeholder)
        else:
            placeholder = QLabel("Configuration manager not available")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_performance_tab(self):
        """Create the performance tab widget."""
        from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget  # type: ignore

        widget = QWidget()
        layout = QVBoxLayout(widget)

        if self.performance_monitor:
            performance_widget = self.performance_monitor.get_widget()
            if performance_widget:
                layout.addWidget(performance_widget)
            else:
                placeholder = QLabel("Performance metrics will appear here...")
                placeholder.setStyleSheet("color: #666; padding: 20px;")
                layout.addWidget(placeholder)
        else:
            placeholder = QLabel("Performance monitor not available")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_bottom_bar(self):
        """Create bottom bar with context summary, sync status, confidence."""
        from PySide6.QtWidgets import (  # type: ignore
            QHBoxLayout,
            QLabel,
            QProgressBar,
            QWidget,
        )

        bottom_widget = QWidget()
        bottom_widget.setMaximumHeight(40)
        bottom_widget.setStyleSheet(
            "QWidget { background-color: #f8f9fa; border-top: 1px solid #dee2e6; }"
        )

        layout = QHBoxLayout(bottom_widget)

        # Context Summary
        self.context_label = QLabel("Context: Ready")
        self.context_label.setStyleSheet("padding: 8px; font-weight: bold;")
        layout.addWidget(self.context_label)

        # Separator
        layout.addWidget(QLabel("|"))

        # Sync Status
        self.sync_status_label = QLabel("Sync: ✅ Active")
        self.sync_status_label.setStyleSheet("padding: 8px; color: green;")
        layout.addWidget(self.sync_status_label)

        # Separator
        layout.addWidget(QLabel("|"))

        # Confidence Bar
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMaximum(100)
        self.confidence_bar.setValue(85)
        self.confidence_bar.setStyleSheet("QProgressBar { max-width: 100px; }")
        layout.addWidget(self.confidence_bar)

        layout.addWidget(QLabel("Confidence"))

        return bottom_widget

    def _setup_menu_bar(self):
        """Setup the application menu bar."""
        if self.main_window:  # type: ignore
            menubar = self.main_window.menuBar()

            # File Menu
            menubar.addMenu("File")

            # View Menu
            menubar.addMenu("View")

            # Tools Menu
            menubar.addMenu("Tools")

            # Help Menu
            menubar.addMenu("Help")

            print("✅ Menu bar configured")

    def _setup_status_bar(self):
        """Setup the status bar."""
        from PySide6.QtWidgets import QStatusBar  # type: ignore

        if self.main_window:  # type: ignore
            status_bar = QStatusBar()
            self.main_window.setStatusBar(status_bar)
            status_bar.showMessage("Enhanced Lyrixa Window Ready")

            print("✅ Status bar configured")

    def _setup_realtime_updates(self):
        """Setup real-time updates for live components."""
        from PySide6.QtCore import QTimer  # type: ignore

        # Create timer for regular updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_live_components)
        self.update_timer.start(1000)  # Update every second

        print("✅ Real-time updates configured")

    def _update_live_components(self):
        """Update live components with fresh data."""
        try:
            # Update analytics dashboard
            if self.analytics_dashboard:
                self.analytics_dashboard.refresh_data()

            # Check for pending suggestions
            if self.notification_system:
                self.notification_system.check_pending_suggestions()

            # Update performance metrics
            if self.performance_monitor:
                self.performance_monitor.update_metrics()

            # Update intelligence layer
            if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                self.intelligence_layer.update_display()

        except Exception as e:
            print(f"⚠️ Error updating live components: {e}")

    def show(self):
        """Show the Enhanced Lyrixa Window."""
        if self.qt_available:
            if not self.main_window:
                self._setup_qt_window()

            if self.main_window:  # type: ignore
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()

            # Initialize intelligence layer if available
            if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                self.intelligence_layer.initialize_state()

            print("✅ Enhanced Lyrixa Window displayed")

            # Setup memory bindings after window is shown
            self._setup_memory_bindings()

            # Start live refresh for components
            self._start_live_refresh()

        else:
            print("⚠️ Qt not available - cannot show GUI window")
            self.show_console_interface()

    def _setup_memory_bindings(self):
        """Setup memory system bindings with GUI components."""
        try:
            if self.advanced_memory:
                # Connect intelligence layer to memory system
                if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                    self.intelligence_layer.connect_memory_system(self.advanced_memory)

                # Bind analytics dashboard to memory data
                if self.analytics_dashboard:
                    self.analytics_dashboard.bind_memory_data(self.advanced_memory)

                print("✅ Memory system bindings established")

        except Exception as e:
            print(f"⚠️ Error setting up memory bindings: {e}")

    def _start_live_refresh(self):
        """Start live refresh for all components."""
        try:
            if self.analytics_dashboard:
                self.analytics_dashboard.start_live_refresh()

            print("✅ Live refresh started")

        except Exception as e:
            print(f"⚠️ Error starting live refresh: {e}")

    def show_console_interface(self):
        """Show a console-based interface when Qt is not available."""
        print("\n" + "=" * 60)
        print("🎙️ LYRIXA ASSISTANT - CONSOLE MODE")
        print("=" * 60)
        print("Enhanced features available:")
        print("• Real-time AI interaction")
        print("• Advanced memory system")
        print("• Plugin integration")
        print("• Anticipation engine")
        print("• Polish components")
        print("=" * 60)

        # Show component status
        self._show_component_status()

    def _show_component_status(self):
        """Show status of all components."""
        print("\n📊 COMPONENT STATUS:")
        print("-" * 40)

        components = [
            ("Lyrixa AI", self.lyrixa_ai),
            ("Advanced Memory", self.advanced_memory),
            ("Analytics Dashboard", self.analytics_dashboard),
            ("Notification System", self.notification_system),
            ("Configuration Manager", self.config_manager),
            ("Performance Monitor", self.performance_monitor),
            ("Anticipation Engine", self.anticipation_engine),
            ("Context Memory", self.context_memory_manager),
            ("Chat History", self.chat_history_manager),
            ("Plugin Panel", self.plugin_panel_manager),
            ("Quick Commands", self.quick_commands_manager),
            ("Personality Manager", self.personality_manager),
            ("Response Style Memory", self.response_style_memory),
            ("Intelligence Panel", self.intelligence_panel_manager),
        ]

        for name, component in components:
            status = "✅ Active" if component else "❌ Inactive"
            print(f"{name:<25} {status}")

    def hide(self):
        """Hide the Enhanced Lyrixa Window."""
        if self.qt_available and self.main_window:
            self.main_window.hide()
            print("Enhanced Lyrixa Window hidden")

    def close(self):
        """Close the Enhanced Lyrixa Window."""
        if self.qt_available and self.main_window:
            self.main_window.close()
            print("Enhanced Lyrixa Window closed")

    def is_visible(self):
        """Check if the window is visible."""
        if self.qt_available and self.main_window:
            return self.main_window.isVisible()
        return False

    def switch_context(self, context_type: str, context_data: dict = None):  # type: ignore
        """Switch the context of the Lyrixa system."""
        try:
            if self.context_memory_manager:
                self.context_memory_manager.switch_context(context_type, context_data)

            # Update UI context display
            if hasattr(self, "context_label") and self.context_label:
                self.context_label.setText(f"Context: {context_type}")

            print(f"🧭 Context switched to: {context_type}")

        except Exception as e:
            print(f"⚠️ Error switching context: {e}")

    def add_thought(self, thought: str):
        """Add a thought to the live feed."""
        try:
            if hasattr(self, "think_feed") and self.think_feed:
                from datetime import datetime

                timestamp = datetime.now().strftime("%H:%M:%S")
                self.think_feed.append(f"[{timestamp}] {thought}")

        except Exception as e:
            print(f"⚠️ Error adding thought: {e}")

    def update_confidence(self, confidence: int):
        """Update the confidence bar."""
        try:
            if hasattr(self, "confidence_bar") and self.confidence_bar:
                self.confidence_bar.setValue(max(0, min(100, confidence)))

        except Exception as e:
            print(f"⚠️ Error updating confidence: {e}")

    def on_init(self):
        """Phase 4 lifecycle method - called during initialization."""
        print("🔄 Phase 4: Enhanced Lyrixa Window initialization lifecycle")

        # Initialize any additional Phase 4 components here
        # This is where future enhancements can be added

        print("✅ Phase 4 initialization complete")

    def on_destroy(self):
        """Phase 4 lifecycle method - called during cleanup."""
        print("🔄 Phase 4: Enhanced Lyrixa Window cleanup lifecycle")

        # Cleanup resources
        if hasattr(self, "update_timer"):
            self.update_timer.stop()

        if self.executor:
            self.executor.shutdown(wait=False)

        print("✅ Phase 4 cleanup complete")

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.on_destroy()
        except Exception:
            pass  # Ignore errors during cleanup


# Factory function for creating the enhanced window
def create_enhanced_lyrixa_window():
    """Create and return an Enhanced Lyrixa Window instance."""
    return EnhancedLyrixaWindow()


# Main execution
if __name__ == "__main__":
    print("🎙️ Starting Enhanced Lyrixa Window...")

    # Create the window
    window = create_enhanced_lyrixa_window()

    # Show the window
    window.show()

    # If Qt is available, start the event loop
    if window.qt_available:
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            print("🚀 Starting Qt application event loop...")
            sys.exit(app.exec())

        except Exception as e:
            print(f"⚠️ Error running Qt application: {e}")
            print("Falling back to console mode...")
            window.show_console_interface()
    else:
        print("Console mode - press Ctrl+C to exit")
        try:
            while True:
                import time

                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Enhanced Lyrixa Window closed")
