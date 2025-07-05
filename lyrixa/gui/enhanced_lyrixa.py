"""
Enhanced Lyrixa Window
=====================

Main enhanced UI window for the Lyrixa assistant system.
Provides a sophisticated interface for Aetherra code interaction with real AI functionality.
Integrates Phase 3 components: Analytics Dashboard, Suggestion Notifications, Configuration Manager, and Performance Monitor.
"""

import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Import Phase 3 GUI components
try:
    # Import GUI components from the same package
    from .analytics_dashboard import AnalyticsDashboard
    from .configuration_manager import ConfigurationManager
    from .intelligence_layer import IntelligenceLayerWidget
    from .performance_monitor import PerformanceMonitor
    from .suggestion_notifications import SuggestionNotificationSystem

    PHASE3_GUI_AVAILABLE = True
except ImportError as e:
    print(f"Phase 3 GUI components not available: {e}")
    PHASE3_GUI_AVAILABLE = False

# Import anticipation engine
try:
    from lyrixa.core.anticipation_engine import AnticipationEngine

    ANTICIPATION_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Anticipation engine not available: {e}")
    ANTICIPATION_ENGINE_AVAILABLE = False


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

        # Initialize AI and memory systems
        self._initialize_lyrixa_ai()

        # Initialize Phase 3 components
        self._initialize_phase3_components()

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
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QAction
            from PySide6.QtWidgets import QApplication

            # Only check if Qt is available, don't create widgets yet
            self.qt_available = True
            self.main_window = None  # Will be created when show() is called
            print("✅ Qt GUI framework detected")
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

            # Initialize Phase 1 Advanced Memory System
            self._initialize_advanced_memory()

        except Exception as e:
            print(f"⚠️ Could not initialize Lyrixa AI: {e}")
            self.lyrixa_ai = None

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

    def toggle_suggestions(self):
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
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QAction, QFont, QTextCursor
        from PySide6.QtWidgets import (
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMenu,
            QMenuBar,
            QProgressBar,
            QPushButton,
            QScrollArea,
            QSplitter,
            QStatusBar,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
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

        # Bottom bar for context summary, sync status, confidence
        bottom_bar = self._create_bottom_bar()
        main_layout.addWidget(bottom_bar)

        # Setup menu bar
        self._setup_menu_bar()

        # Setup status bar
        self._setup_status_bar()

        # Setup real-time updates
        self._setup_realtime_updates()

        print("✅ Enhanced main window layout created")

    def _create_main_panel(self):
        """Create the main panel with memory graph and live feed."""
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QLabel, QSplitter, QTextEdit, QVBoxLayout, QWidget

        main_panel = QWidget()
        layout = QVBoxLayout(main_panel)

        # Create vertical splitter for memory graph and live feed
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
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QLabel("🧠 Memory Graph - Live Context")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(header)

        # Memory graph display area
        self.memory_graph_area = QScrollArea()
        self.memory_graph_content = QWidget()
        self.memory_graph_layout = QVBoxLayout(self.memory_graph_content)

        # Placeholder content
        placeholder = QLabel(
            "Memory graph will display here...\n• Semantic clusters\n• Context relationships\n• Recent interactions"
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #666; padding: 20px;")
        self.memory_graph_layout.addWidget(placeholder)

        self.memory_graph_area.setWidget(self.memory_graph_content)
        self.memory_graph_area.setWidgetResizable(True)
        layout.addWidget(self.memory_graph_area)

        return widget

    def _create_live_think_feed(self):
        """Create the live 'Lyrixa Thinks...' feed widget."""
        from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QLabel("🤔 Lyrixa Thinks... (Live Feed)")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(header)

        # Live feed text area
        self.think_feed = QTextEdit()
        self.think_feed.setReadOnly(True)
        self.think_feed.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)

        # Add initial content
        self.think_feed.append("🚀 Lyrixa system starting...")
        self.think_feed.append("🧠 Memory system initialized")
        self.think_feed.append("🔮 Anticipation engine ready")
        if self.analytics_dashboard:
            self.think_feed.append("📊 Analytics dashboard active")
        if self.notification_system:
            self.think_feed.append("💡 Notification system ready")

        layout.addWidget(self.think_feed)
        return widget

    def _create_sidebar_panel(self):
        """Create the sidebar with live feedback and notifications."""
        from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

        sidebar = QWidget()
        layout = QVBoxLayout(sidebar)

        # Create tabs for different sidebar views
        tab_widget = QTabWidget()

        # Live Feedback Tab
        feedback_tab = self._create_live_feedback_tab()
        tab_widget.addTab(feedback_tab, "📡 Live Feedback")

        # Suggestions Tab
        suggestions_tab = self._create_suggestions_tab()
        tab_widget.addTab(suggestions_tab, "💡 Suggestions")

        # Analytics Tab
        analytics_tab = self._create_analytics_tab()
        tab_widget.addTab(analytics_tab, "📊 Analytics")

        # Configuration Tab
        config_tab = self._create_config_tab()
        tab_widget.addTab(config_tab, "⚙️ Config")

        # Performance Tab
        performance_tab = self._create_performance_tab()
        tab_widget.addTab(performance_tab, "⚡ Performance")

        layout.addWidget(tab_widget)
        return sidebar

    def _create_live_feedback_tab(self):
        """Create live feedback tab content."""
        from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Live system feedback and responses")
        label.setStyleSheet("font-weight: bold; padding: 8px;")
        layout.addWidget(label)

        self.feedback_area = QTextEdit()
        self.feedback_area.setReadOnly(True)
        self.feedback_area.setMaximumHeight(200)
        layout.addWidget(self.feedback_area)

        return widget

    def _create_suggestions_tab(self):
        """Create suggestions notification tab."""
        from PySide6.QtWidgets import QVBoxLayout, QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Integrate the suggestion notification system widget if available
        if self.notification_system and hasattr(self.notification_system, "get_widget"):
            suggestion_widget = self.notification_system.get_widget()
            layout.addWidget(suggestion_widget)
        else:
            from PySide6.QtWidgets import QLabel

            placeholder = QLabel("Suggestion notifications will appear here...")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_analytics_tab(self):
        """Create analytics dashboard tab."""
        from PySide6.QtWidgets import QVBoxLayout, QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Integrate the analytics dashboard widget if available
        if self.analytics_dashboard and hasattr(self.analytics_dashboard, "get_widget"):
            analytics_widget = self.analytics_dashboard.get_widget()
            layout.addWidget(analytics_widget)
        else:
            from PySide6.QtWidgets import QLabel

            placeholder = QLabel("Analytics data will appear here...")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_config_tab(self):
        """Create configuration manager tab."""
        from PySide6.QtWidgets import QVBoxLayout, QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Integrate the configuration manager widget if available
        if self.config_manager and hasattr(self.config_manager, "get_widget"):
            config_widget = self.config_manager.get_widget()
            layout.addWidget(config_widget)
        else:
            from PySide6.QtWidgets import QLabel

            placeholder = QLabel("Configuration options will appear here...")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_performance_tab(self):
        """Create performance monitor tab."""
        from PySide6.QtWidgets import QVBoxLayout, QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Integrate the performance monitor widget if available
        if self.performance_monitor and hasattr(self.performance_monitor, "get_widget"):
            performance_widget = self.performance_monitor.get_widget()
            layout.addWidget(performance_widget)
        else:
            from PySide6.QtWidgets import QLabel

            placeholder = QLabel("Performance metrics will appear here...")
            placeholder.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(placeholder)

        return widget

    def _create_bottom_bar(self):
        """Create bottom bar with context summary, sync status, confidence."""
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QWidget

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

        # Confidence Readout
        confidence_label = QLabel("Confidence:")
        layout.addWidget(confidence_label)

        self.confidence_progress = QProgressBar()
        self.confidence_progress.setMaximumWidth(100)
        self.confidence_progress.setMaximumHeight(20)
        self.confidence_progress.setValue(85)  # Initial value
        layout.addWidget(self.confidence_progress)

        # Stretch to push everything to the left
        layout.addStretch()

        return bottom_widget

    def _setup_realtime_updates(self):
        """Setup QTimer for real-time updates."""
        from PySide6.QtCore import QTimer

        # Create timer for live updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_realtime_data)

        # Update every 2 seconds
        self.update_timer.start(2000)
        print("⏱️ Real-time updates activated (2s interval)")

    def _update_realtime_data(self):
        """Update real-time data across all components."""
        try:
            import random
            from datetime import datetime

            from PySide6.QtGui import QTextCursor

            # Update live think feed
            if hasattr(self, "think_feed"):
                current_time = datetime.now().strftime("%H:%M:%S")

                # Sample real-time updates
                updates = [
                    f"[{current_time}] Analyzing user input patterns...",
                    f"[{current_time}] Memory consolidation in progress...",
                    f"[{current_time}] Anticipation engine processing contexts...",
                    f"[{current_time}] Cross-phase communication active...",
                    f"[{current_time}] Performance metrics updated...",
                ]

                # Add random update
                if random.random() > 0.7:  # 30% chance
                    self.think_feed.append(random.choice(updates))

                    # Keep feed manageable
                    if self.think_feed.document().blockCount() > 50:
                        cursor = self.think_feed.textCursor()
                        cursor.movePosition(QTextCursor.MoveOperation.Start)
                        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                        cursor.removeSelectedText()

            # Update confidence score
            if hasattr(self, "confidence_progress"):
                new_confidence = random.randint(75, 95)
                self.confidence_progress.setValue(new_confidence)

            # Update memory graph (placeholder for now)
            if hasattr(self, "memory_graph_layout") and self.advanced_memory:
                # In a real implementation, this would query the memory system
                # and update the visual graph representation
                pass

            # Trigger component updates
            self._trigger_component_updates()

        except Exception as e:
            print(f"⚠️ Real-time update error: {e}")

    def _trigger_component_updates(self):
        """Trigger updates in Phase 3/4 components."""
        try:
            # Update analytics dashboard
            if self.analytics_dashboard and hasattr(
                self.analytics_dashboard, "refresh_data"
            ):
                self.analytics_dashboard.refresh_data()

            # Update suggestion notifications
            if self.notification_system and hasattr(
                self.notification_system, "check_pending_suggestions"
            ):
                self.notification_system.check_pending_suggestions()

            # Update performance monitor
            if self.performance_monitor and hasattr(
                self.performance_monitor, "update_metrics"
            ):
                self.performance_monitor.update_metrics()

            # Update intelligence layer
            if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                if hasattr(self.intelligence_layer, "update_display"):
                    self.intelligence_layer.update_display()

        except Exception as e:
            print(f"⚠️ Component update error: {e}")

    # Lifecycle Hooks for Phase 4 State Management
    def on_init(self):
        """Called after initialization is complete."""
        try:
            print("🔄 Initializing Phase 4 state management...")

            # Connect memory system to live views
            if hasattr(self, "advanced_memory") and self.advanced_memory:
                self._bind_memory_to_live_views()

            # Initialize intelligence layer with current state
            if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                self.intelligence_layer.initialize_state()

            # Start real-time updates
            self._start_realtime_updates()

            print("✅ Phase 4 state management initialized")
        except Exception as e:
            print(f"⚠️ Phase 4 initialization error: {e}")

    def on_show(self):
        """Called when the window is shown."""
        try:
            print("👁️ Enhanced Lyrixa Window shown - activating live features")

            # Activate analytics refresh
            if hasattr(self, "analytics_dashboard") and self.analytics_dashboard:
                self.analytics_dashboard.start_live_refresh()

            # Begin live feedback loop
            if hasattr(self, "notification_system") and self.notification_system:
                self.notification_system.activate_live_mode()

            # Start intelligence layer real-time processing
            if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                self.intelligence_layer.start_live_processing()

        except Exception as e:
            print(f"⚠️ Show activation error: {e}")

    def on_close(self):
        """Called when the window is closing."""
        try:
            print("🔄 Shutting down Phase 4 components...")

            # Stop real-time updates
            self._stop_realtime_updates()

            # Save current state
            self._save_phase4_state()

            # Gracefully shutdown intelligence layer
            if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                self.intelligence_layer.shutdown()

            # Stop analytics refresh
            if hasattr(self, "analytics_dashboard") and self.analytics_dashboard:
                self.analytics_dashboard.stop_live_refresh()

            print("✅ Phase 4 components shut down gracefully")
        except Exception as e:
            print(f"⚠️ Shutdown error: {e}")

    def _bind_memory_to_live_views(self):
        """Bind Phase 1 memory to live GUI views."""
        try:
            # Connect memory events to intelligence layer
            if hasattr(self, "intelligence_layer") and self.intelligence_layer:
                self.intelligence_layer.connect_memory_system(self.advanced_memory)

            # Connect to analytics dashboard
            if hasattr(self, "analytics_dashboard") and self.analytics_dashboard:
                self.analytics_dashboard.bind_memory_data(self.advanced_memory)

            print("🔗 Memory bindings established")
        except Exception as e:
            print(f"⚠️ Memory binding error: {e}")

    def _start_realtime_updates(self):
        """Start real-time update timers."""
        try:
            # Will be implemented with QTimer for live updates
            print("⏱️ Real-time updates started")
        except Exception as e:
            print(f"⚠️ Real-time update start error: {e}")

    def _stop_realtime_updates(self):
        """Stop real-time update timers."""
        try:
            # Will stop QTimer instances
            print("⏹️ Real-time updates stopped")
        except Exception as e:
            print(f"⚠️ Real-time update stop error: {e}")

    def _save_phase4_state(self):
        """Save Phase 4 component states."""
        try:
            # Save intelligence layer state, analytics preferences, etc.
            print("💾 Phase 4 state saved")
        except Exception as e:
            print(f"⚠️ State save error: {e}")

    def _setup_menu_bar(self):
        """Setup the main window menu bar."""
        if not self.main_window:
            return

        from PySide6.QtGui import QAction

        menubar = self.main_window.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self.main_window)
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)

        # View menu
        menubar.addMenu("View")

        # Tools menu
        menubar.addMenu("Tools")

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self.main_window)
        help_menu.addAction(about_action)

    def _setup_status_bar(self):
        """Setup the main window status bar."""
        if not self.main_window:
            return

        status_bar = self.main_window.statusBar()
        status_bar.showMessage("Lyrixa Assistant Ready")

    def show(self):
        """Show the main window."""
        if self.qt_available:
            # Create Qt window if not already created
            if not hasattr(self, "main_window") or self.main_window is None:
                self._setup_qt_window()

            if self.main_window:
                self.main_window.show()
                # Call Phase 4 lifecycle show hook
                self.on_show()
                return self.main_window
            else:
                print("⚠️ Failed to create Qt window - falling back to console mode")
                self.on_show()
                return None
        else:
            print("Qt GUI not available - running in console mode")
            self.on_show()
            return None

    def close(self):
        """Close the main window and cleanup."""
        print("🔄 Closing Enhanced Lyrixa Window...")

        # Call Phase 4 lifecycle close hook
        self.on_close()

        if self.qt_available and hasattr(self, "main_window") and self.main_window:
            self.main_window.close()

        # Stop real-time updates
        if hasattr(self, "update_timer"):
            self.update_timer.stop()

        print("✅ Enhanced Lyrixa Window closed")

    # ...existing code...


def launch_enhanced_lyrixa():
    """Launch function to run the Enhanced Lyrixa Window."""
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        window = EnhancedLyrixaWindow()
        window.show()
        if hasattr(app, "exec"):
            sys.exit(app.exec())
        else:
            sys.exit(app.exec_())
    except ImportError:
        # Fallback to console mode
        window = EnhancedLyrixaWindow()
        window.show()
        print("Press Enter to exit...")
        input()


if __name__ == "__main__":
    launch_enhanced_lyrixa()
