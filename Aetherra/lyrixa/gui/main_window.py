#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎙️ Lyrixa Hybrid Window - Phase 1
==================================

PySide6 + Embedded Web Hybrid UI for Lyrixa AI Operating System
Combines native Qt performance with beautiful web-styled panels
matching the Aetherra.dev aesthetic.

Architecture:
- Base: PySide6 QMainWindow for native performance
- Panels: QWebEngineView embedding HTML panels styled like Aetherra.dev
- Communication: QWebChannel for bidirectional Python ↔ JavaScript
- Styling: Authentic Aetherra colors and effects
"""

import json
import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from PySide6.QtCore import Qt, QTimer, QUrl, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .context_bridge import LyrixaContextBridge as LyrixaWebBridge

# Phase 3: Auto-Generation System
from .phase3_auto_generator import Phase3AutoGenerator

# Phase 4: Cognitive UI Integration
from .phase4_cognitive_ui import CognitiveStateMonitor

# Phase 5: Plugin-Driven UI System
from .phase5_plugin_ui import PluginUIManager

# Phase 6: Full GUI Personality + State Memory
from .phase6_personality import GUIPersonalityManager
from .widgets.metrics_panel import MetricsPanel
from .widgets.nav_panel import NavPanel

# Import Unicode-safe logger
try:
    # Try to import from project root
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from unicode_logger import get_safe_logger

    logger = get_safe_logger(__name__)
    print(f"✅ Unicode logger successfully imported for {__name__}")
except ImportError as e:
    # Fallback to regular logger if unicode_logger not available
    print(f"❌ Unicode logger import failed: {e}, falling back to standard logger")
    import logging

    logger = logging.getLogger(__name__)


def datetime_serializer(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def safe_json_dumps(data):
    """Safely dump data to JSON with datetime handling"""
    try:
        return json.dumps(data, default=datetime_serializer)
    except Exception as e:
        logger.error(f"[ERROR] JSON serialization failed: {e}")
        return "{}"


# LyrixaContextBridge now imported as LyrixaWebBridge from context_bridge.py


class LyrixaHybridWindow(QMainWindow):
    """
    🎙️ Lyrixa Hybrid Window - PySide6 + Web Panel Integration

    Features:
    - Native Qt controls for performance-critical operations
    - Beautiful web panels matching Aetherra.dev styling
    - Dynamic panel loading and switching
    - Real-time data synchronization
    """

    def __init__(self):
        super().__init__()
        self.web_bridge = LyrixaWebBridge()
        self.web_panels = {}
        self.current_panel = None

        # Backend connections (will be set by launcher)
        self.service_registry = None
        self.plugin_manager = None
        self.lyrixa_engine = None
        self.memory_system = None
        self.agent_orchestrator = None

        # Real backend system connections
        self.conversation_manager = None
        self.real_data_manager = None

        # Phase 3: Auto-Generation System
        gui_dir = Path(__file__).parent
        self.auto_generator = Phase3AutoGenerator(gui_dir)
        self.auto_generated_panels = {}

        # Phase 4: Cognitive UI Integration
        self.cognitive_monitor = CognitiveStateMonitor()
        self.cognitive_timer = QTimer()

        # Phase 5: Plugin-Driven UI System
        self.plugin_ui_manager = PluginUIManager()
        self.plugin_panels = {}

        # Phase 6: Full GUI Personality + State Memory
        self.personality_manager = GUIPersonalityManager()
        self.chat_interface = None

        # Consciousness Integration
        self.consciousness_integrator = None

        self.setupUI()
        self.setupWebChannel()
        self.setupTimers()
        self.setupPhase3Integration()
        self.setupPhase4Integration()
        self.setupPhase5Integration()
        self.setupPhase6Integration()
        self.applyAetherraTheme()

    def setupUI(self):
        """Setup the main UI structure."""
        self.setWindowTitle("🎙️ Lyrixa AI Operating System")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Left panel - Native controls (extracted NavPanel)
        self.left_panel = self.createLeftPanel()
        self.splitter.addWidget(self.left_panel)

        # Center panel - Web view
        self.center_panel = self.createCenterPanel()
        self.splitter.addWidget(self.center_panel)

        # Right panel - Status and metrics
        self.right_panel = self.createRightPanel()
        self.splitter.addWidget(self.right_panel)

        # Set splitter proportions (20% : 60% : 20%)
        self.splitter.setSizes([280, 840, 280])

        # Menu bar
        self.createMenuBar()

        # Status bar
        self.createStatusBar()

        # Load default panel
        QTimer.singleShot(
            100, lambda: self.loadPanel("dashboard")
        )  # Small delay to ensure web channel is ready

    def createLeftPanel(self) -> QWidget:
        """Create the left native control panel using NavPanel widget."""
        self.nav_panel = NavPanel(button_style=self.getButtonStyle())
        # Bridge navigation requests into existing loadPanel
        self.nav_panel.navigationRequested.connect(self.loadPanel)
        return self.nav_panel

    def createCenterPanel(self) -> QWidget:
        """Create the center web panel area."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Web engine view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        return panel

    def createRightPanel(self) -> QWidget:
        """Create the right metrics/status panel (extracted widget)."""
        self.metrics_panel = MetricsPanel()
        return self.metrics_panel

    def createMetricWidget(self, name: str, value: str, color: str) -> QWidget:
        """Create a metric display widget."""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background: rgba(26, 26, 26, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                margin: 5px 0;
            }
        """
        )

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)

        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"color: {color}; font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(name_label)
        layout.addWidget(value_label)

        return widget

    def createMenuBar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Project")
        file_menu.addAction("&Open Project")
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("&Dashboard", lambda: self.loadPanel("dashboard"))
        view_menu.addAction("&Plugins", lambda: self.loadPanel("plugins"))
        view_menu.addAction("&Memory", lambda: self.loadPanel("memory"))

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&Plugin Manager")
        tools_menu.addAction("&Memory Browser")
        tools_menu.addAction("&System Diagnostics")

    def createStatusBar(self):
        """Create the status bar."""
        status_bar = self.statusBar()
        status_bar.showMessage("🌟 Lyrixa AI Operating System - Ready")
        status_bar.setStyleSheet(
            """
            QStatusBar {
                background: #1a1a1a;
                color: #00ff88;
                border-top: 1px solid rgba(0, 255, 136, 0.3);
            }
        """
        )

    def setupWebChannel(self):
        """Setup QWebChannel for Python ↔ JavaScript communication."""
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("pybridge", self.web_bridge)

        # Phase 4: Register cognitive monitor
        if hasattr(self, "cognitive_monitor"):
            self.web_channel.registerObject("cognitiveMonitor", self.cognitive_monitor)

        # Phase 5: Register plugin UI manager
        if hasattr(self, "plugin_ui_manager"):
            self.web_channel.registerObject("pluginManager", self.plugin_ui_manager)

        # Phase 6: Register personality manager
        if hasattr(self, "personality_manager"):
            self.web_channel.registerObject(
                "personality_manager", self.personality_manager
            )

            # Also register chat interface if available
            if hasattr(self.personality_manager, "chat_interface"):
                self.web_channel.registerObject(
                    "chat_interface", self.personality_manager.chat_interface
                )

        self.web_view.page().setWebChannel(self.web_channel)

    def _recreateWebView(self):
        """Recreate the web view when it's been deleted."""
        try:
            logger.debug("Recreating web view due to deletion")

            # Get the center panel layout
            if not hasattr(self, "center_panel") or not self.center_panel:
                logger.error("No center panel found to recreate web view")
                return False

            layout = self.center_panel.layout()
            if not layout:
                logger.error("No layout found in center panel")
                return False

            # Remove old web view if it exists
            if hasattr(self, "web_view"):
                try:
                    layout.removeWidget(self.web_view)
                    self.web_view.deleteLater()
                except Exception as e:
                    logger.debug(f"Error removing old web view: {e}")

            # Create new web view
            self.web_view = QWebEngineView()
            layout.addWidget(self.web_view)

            # Re-setup web channel - this is crucial!
            if hasattr(self, "web_channel"):
                self.web_view.page().setWebChannel(self.web_channel)
                logger.debug("Web channel re-established for new web view")

            logger.info("Successfully recreated web view")
            return True

        except Exception as e:
            logger.error(f"Failed to recreate web view: {e}")
            return False

    def setupTimers(self):
        """Setup periodic timers for live updates."""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(2000)  # Update every 2 seconds

        # Metrics update timer
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.updateMetrics)
        self.metrics_timer.start(5000)  # Update every 5 seconds

    def setupPhase3Integration(self):
        """Setup Phase 3: Auto-Generation System integration."""
        try:
            # Connect Phase 3 signals to handlers
            self.auto_generator.panels_generated.connect(self.on_panels_auto_generated)
            self.auto_generator.layout_changed.connect(self.on_layout_auto_changed)

            # Connect auto-generator to web bridge
            self.web_bridge.auto_generator = self.auto_generator

            logger.info("[PHASE3] Auto-Generation System integrated successfully")

        except Exception as e:
            logger.error(f"[ERROR] Phase 3 integration failed: {e}")

    @Slot(str)
    def on_panels_auto_generated(self, panels_data_json: str):
        """Handle auto-generated panels from Phase 3"""
        try:
            panels_data = json.loads(panels_data_json)
            panels = panels_data.get("panels", [])

            # Store auto-generated panels
            for panel_info in panels:
                panel_id = panel_info["id"]
                self.auto_generated_panels[panel_id] = panel_info

            # Update navigation to include auto-generated panels
            self.update_navigation_with_auto_panels(panels)

            # If no current panel is loaded, load the first auto-generated one
            if not self.current_panel and panels:
                first_panel = panels[0]
                self.load_auto_generated_panel(first_panel["id"])

            # Update status
            self.statusBar().showMessage(
                f"[AUTO] Auto-generated {len(panels)} panels from system state"
            )
            logger.info(f"[GENERATE] Loaded {len(panels)} auto-generated panels")

        except Exception as e:
            logger.error(f"[ERROR] Failed to handle auto-generated panels: {e}")

    @Slot(str)
    def on_layout_auto_changed(self, layout_json: str):
        """Handle layout changes from Phase 3"""
        try:
            layout = json.loads(layout_json)
            logger.info(
                f"[LAYOUT] Auto-layout updated: {layout.get('total_panels', 0)} panels in {len(layout.get('sections', []))} sections"
            )

            # Could update UI layout here if needed

        except Exception as e:
            logger.error(f"[ERROR] Failed to handle layout change: {e}")

    def setupPhase4Integration(self):
        """Setup Phase 4: Cognitive UI Integration."""
        try:
            # Connect cognitive monitor to web bridge
            self.web_bridge.cognitive_monitor = self.cognitive_monitor

            # Setup cognitive state monitoring timer
            self.cognitive_timer.timeout.connect(self.update_cognitive_state)
            self.cognitive_timer.start(500)  # Update every 500ms

            # Couple cognitive signals to personality manager (bridge Phase 4 -> Phase 6)
            if hasattr(self, "personality_manager") and self.personality_manager:
                # Cognitive load drives energy/focus, depth maps to analytical mood
                self.cognitive_monitor.cognitive_load_changed.connect(
                    self._on_cognitive_load_changed
                )
                # Thoughts and goals nudge traits subtly
                self.cognitive_monitor.thought_generated.connect(
                    self._on_thought_generated
                )
                self.cognitive_monitor.goal_updated.connect(self._on_goal_updated)

            logger.info("[PHASE4] Cognitive UI Integration setup successfully")

        except Exception as e:
            logger.error(f"[ERROR] Phase 4 integration failed: {e}")

    @Slot(str)
    def _on_cognitive_load_changed(self, cognitive_json: str):
        """Map cognitive metrics to personality state and theme updates."""
        try:
            data = json.loads(cognitive_json)
            load = float(data.get("load", 0.3))
            depth = float(data.get("depth", 0.5))
            freq = float(data.get("frequency", 1.0))

            pm = getattr(self, "personality_manager", None)
            if not pm or not hasattr(pm, "ai"):
                return

            # Clamp helper
            def clamp(v: float) -> float:
                return max(0.0, min(1.0, v))

            # Update levels based on cognitive state
            ps = pm.ai.personality_state
            ps.energy_level = clamp(0.35 + 0.6 * load)
            ps.focus_level = clamp(0.3 + 0.7 * depth)
            ps.creativity_level = clamp(0.4 + 0.15 * min(freq, 4.0))

            # Adjust emotional state heuristically
            try:
                from .phase6_personality import EmotionalState

                if depth > 0.75:
                    ps.emotional_state = EmotionalState.ANALYTICAL
                elif load > 0.85:
                    ps.emotional_state = EmotionalState.EXCITED
                elif load < 0.25 and freq < 1.2:
                    ps.emotional_state = EmotionalState.CALM
                # else: keep current
            except Exception:
                pass

            # Emit updates (will also regenerate theme)
            pm.update_personality_state()

        except Exception as e:
            logger.debug(f"[PHASE4→6] Cognitive load coupling error: {e}")

    @Slot(str)
    def _on_thought_generated(self, thought_json: str):
        """Use thought type to gently influence personality dimensions."""
        try:
            data = json.loads(thought_json)
            thought_type = data.get("thought_type", "")
            pm = getattr(self, "personality_manager", None)
            if not pm or not hasattr(pm, "ai"):
                return
            ps = pm.ai.personality_state

            # Small nudges based on thought type
            if "reasoning" in thought_type:
                ps.focus_level = min(1.0, ps.focus_level + 0.02)
            elif "goal_planning" in thought_type:
                ps.focus_level = min(1.0, ps.focus_level + 0.03)
            elif "memory_recall" in thought_type:
                # contemplative nudge
                try:
                    from .phase6_personality import EmotionalState

                    ps.emotional_state = EmotionalState.CONTEMPLATIVE
                except Exception:
                    pass
            elif "response_generation" in thought_type:
                ps.creativity_level = min(1.0, ps.creativity_level + 0.03)

            pm.update_personality_state()
        except Exception as e:
            logger.debug(f"[PHASE4→6] Thought coupling error: {e}")

    @Slot(str)
    def _on_goal_updated(self, goal_json: str):
        """Map goal status to emotion/energy adjustments."""
        try:
            data = json.loads(goal_json)
            status = data.get("status", "")
            pm = getattr(self, "personality_manager", None)
            if not pm or not hasattr(pm, "ai"):
                return

            ps = pm.ai.personality_state
            try:
                from .phase6_personality import EmotionalState

                if status == "completed":
                    ps.energy_level = min(1.0, ps.energy_level + 0.05)
                    ps.emotional_state = EmotionalState.ENERGETIC
                elif status == "blocked":
                    ps.focus_level = max(0.0, ps.focus_level - 0.05)
                    ps.emotional_state = EmotionalState.ANXIOUS
                elif status == "planning":
                    ps.emotional_state = EmotionalState.CONTEMPLATIVE
            except Exception:
                pass

            pm.update_personality_state()
        except Exception as e:
            logger.debug(f"[PHASE4→6] Goal coupling error: {e}")

    def setupPhase5Integration(self):
        """Setup Phase 5: Plugin-Driven UI System integration."""
        try:
            # Connect plugin UI manager signals
            if self.plugin_ui_manager:
                self.plugin_ui_manager.plugin_ui_loaded.connect(self.onPluginUILoaded)
                self.plugin_ui_manager.plugin_ui_unloaded.connect(
                    self.onPluginUIUnloaded
                )
                self.plugin_ui_manager.plugin_ui_updated.connect(self.onPluginUIUpdated)
                self.plugin_ui_manager.plugin_ui_error.connect(self.onPluginUIError)

                # Start plugin scanning and monitoring
                self.plugin_ui_manager.scan_for_plugins()

                logger.info("[PHASE5] Plugin-Driven UI System setup successfully")

        except Exception as e:
            logger.error(f"[ERROR] Phase 5 integration failed: {e}")

    @Slot(str, str)
    def onPluginUILoaded(self, plugin_id: str, panel_html: str):
        """Handle plugin UI loaded signal"""
        try:
            logger.info(f"[PHASE5] Plugin UI loaded: {plugin_id}")
            # Store plugin panel HTML
            self.plugin_panels[plugin_id] = panel_html

            # Emit signal to web bridge for UI integration
            if hasattr(self.web_bridge, "plugin_ui_loaded"):
                self.web_bridge.plugin_ui_loaded.emit(
                    safe_json_dumps(
                        {
                            "plugin_id": plugin_id,
                            "panel_html": panel_html,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

        except Exception as e:
            logger.error(f"[PHASE5] Error handling plugin UI loaded: {e}")

    @Slot(str)
    def onPluginUIUnloaded(self, plugin_id: str):
        """Handle plugin UI unloaded signal"""
        try:
            logger.info(f"[PHASE5] Plugin UI unloaded: {plugin_id}")
            if plugin_id in self.plugin_panels:
                del self.plugin_panels[plugin_id]

        except Exception as e:
            logger.error(f"[PHASE5] Error handling plugin UI unloaded: {e}")

    @Slot(str, str)
    def onPluginUIUpdated(self, plugin_id: str, updated_data: str):
        """Handle plugin UI updated signal"""
        try:
            # Forward update to web interface
            if hasattr(self.web_bridge, "plugin_ui_updated"):
                self.web_bridge.plugin_ui_updated.emit(
                    safe_json_dumps(
                        {
                            "plugin_id": plugin_id,
                            "data": updated_data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

        except Exception as e:
            logger.error(f"[PHASE5] Error handling plugin UI updated: {e}")

    @Slot(str, str)
    def onPluginUIError(self, plugin_id: str, error_message: str):
        """Handle plugin UI error signal"""
        logger.error(f"[PHASE5] Plugin UI error in {plugin_id}: {error_message}")

    def update_cognitive_state(self):
        """Update cognitive state for Phase 4 visualization."""
        try:
            # Update cognitive monitor with current AI state
            if self.cognitive_monitor:
                # Trigger monitoring update
                self.cognitive_monitor.monitor_cognitive_state()

                # Get cognitive state and emit update
                cognitive_data = self.cognitive_monitor.getCognitiveState()
                if cognitive_data:
                    # Use safe JSON dumps to handle datetime objects
                    cognitive_json = safe_json_dumps(cognitive_data)
                    self.web_bridge.cognitive_updated.emit(cognitive_json)
                    self.web_bridge.data_cache["cognitive"] = cognitive_data

        except Exception as e:
            logger.error(f"[ERROR] Failed to update cognitive state: {e}")

    def get_recent_thoughts(self):
        """Get recent AI thoughts for cognitive visualization."""
        # Placeholder - would integrate with actual AI reasoning system
        return []

    def get_current_goals(self):
        """Get current goals for cognitive visualization."""
        # Placeholder - would integrate with actual goal management system
        return []

    def get_memory_activations(self):
        """Get memory activations for cognitive visualization."""
        # Placeholder - would integrate with actual memory system
        return []

    def update_navigation_with_auto_panels(self, panels: List[Dict[str, Any]]):
        """Update navigation to include auto-generated panels"""
        try:
            if hasattr(self, "nav_panel") and self.nav_panel:
                self.nav_panel.add_auto_panels(
                    panels, on_click=lambda pid: self.load_auto_generated_panel(pid)
                )
        except Exception as e:
            logger.warning(f"Failed to update navigation with auto panels: {e}")

    def load_auto_generated_panel(self, panel_id: str):
        """Load an auto-generated panel"""
        try:
            if panel_id in self.auto_generated_panels:
                panel_info = self.auto_generated_panels[panel_id]

                # Get the HTML file path
                panel_file = (
                    Path(__file__).parent
                    / "web_panels"
                    / "auto_generated"
                    / f"{panel_id}.html"
                )

                if panel_file.exists():
                    self.web_view.load(QUrl.fromLocalFile(str(panel_file.absolute())))
                    self.current_panel = panel_id
                    self.statusBar().showMessage(
                        f"🔮 Loaded auto-generated panel: {panel_info.get('title', panel_id)}"
                    )
                else:
                    logger.warning(f"Auto-generated panel file not found: {panel_file}")
            else:
                logger.warning(f"Auto-generated panel not found: {panel_id}")

        except Exception as e:
            logger.error(f"❌ Failed to load auto-generated panel {panel_id}: {e}")

    def setupPhase6Integration(self):
        """Setup Phase 6: Full GUI Personality + State Memory integration."""
        try:
            # Connect personality manager signals
            if self.personality_manager:
                self.personality_manager.personality_changed.connect(
                    self.onPersonalityChanged
                )
                self.personality_manager.theme_updated.connect(self.onThemeUpdated)
                self.personality_manager.layout_adapted.connect(self.onLayoutAdapted)
                self.personality_manager.chat_message.connect(self.onChatMessage)
                self.personality_manager.gui_state_saved.connect(self.onGUIStateSaved)

                # Set up current panel tracking
                if hasattr(self, "current_panel"):
                    self.personality_manager.update_current_panel(
                        self.current_panel or "dashboard"
                    )

                logger.info(
                    "[PHASE6] GUI Personality + State Memory setup successfully"
                )

        except Exception as e:
            logger.error(f"[ERROR] Phase 6 integration failed: {e}")

    @Slot(str)
    def onPersonalityChanged(self, personality_json: str):
        """Handle personality state changes"""
        try:
            personality_data = json.loads(personality_json)
            logger.info(
                f"[PHASE6] Personality changed: {personality_data.get('emotional_state', 'unknown')}"
            )

            # Forward to web interface
            if hasattr(self.web_bridge, "agent_updated"):
                self.web_bridge.agent_updated.emit(
                    safe_json_dumps(
                        {
                            "type": "personality_update",
                            "personality": personality_data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                )

        except Exception as e:
            logger.error(f"[PHASE6] Error handling personality change: {e}")

    @Slot(str)
    def onThemeUpdated(self, theme_css: str):
        """Handle dynamic theme updates"""
        try:
            logger.info("[PHASE6] Theme updated based on personality state")

            # Apply theme to the interface (inject CSS) with object validation
            if (
                hasattr(self, "web_view")
                and self.web_view
                and not self._is_web_view_deleted()
            ):
                # Use style manager for safe CSS injection
                try:
                    from Aetherra.lyrixa.integrations.style_manager import (
                        JavaScriptStyleManager,
                    )

                    style_manager = JavaScriptStyleManager()
                    safe_js = style_manager.create_safe_style_injection(
                        theme_css, "phase6-theme"
                    )
                    self.web_view.page().runJavaScript(safe_js)
                except ImportError:
                    # Fallback to direct injection with improved safety
                    if not self._is_web_view_deleted():
                        # Sanitize CSS and inject safely
                        sanitized_css = theme_css.replace('"', '\\"').replace(
                            "\n", "\\n"
                        )
                        safe_js = f"""
                        (function() {{
                            try {{
                                var style = document.getElementById('phase6-theme');
                                if (!style) {{
                                    style = document.createElement('style');
                                    style.id = 'phase6-theme';
                                    document.head.appendChild(style);
                                }}
                                style.textContent = "{sanitized_css}";
                            }} catch(e) {{
                                console.log('Theme injection failed:', e);
                            }}
                        }})();
                        """
                        self.web_view.page().runJavaScript(safe_js)

        except Exception as e:
            logger.error(f"[PHASE6] Error handling theme update: {e}")

    def cleanupConsciousnessPanel(self):
        """Clean up consciousness panel to prepare for switching to web panels."""
        try:
            if (
                hasattr(self, "consciousness_widget")
                and self.consciousness_widget is not None
            ):
                # Get reference before removing
                widget = self.consciousness_widget

                # Hide the consciousness widget
                widget.hide()

                # Remove from layout if it's in there
                center_layout = self.center_panel.layout()
                if center_layout and center_layout.indexOf(widget) != -1:
                    center_layout.removeWidget(widget)

                # Clean up the widget
                widget.deleteLater()
                self.consciousness_widget = None

                logger.debug("Consciousness panel cleaned up successfully")

        except Exception as e:
            logger.error(f"Error cleaning up consciousness panel: {e}")

    def _is_web_view_deleted(self):
        """Check if web view object has been deleted"""
        try:
            if not hasattr(self, "web_view"):
                logger.debug("No web_view attribute found")
                return True
            if not self.web_view:
                logger.debug("web_view is None")
                return True
            # Try to access a simple property to check if object is still valid
            # Use a more reliable check than objectName()
            try:
                _ = self.web_view.isVisible()  # This should work if object is valid
                return False
            except RuntimeError as re:
                logger.debug(f"RuntimeError accessing web_view: {re}")
                return True
        except Exception as e:
            logger.debug(f"Exception in _is_web_view_deleted: {e}")
            return True

    @Slot(str)
    def onLayoutAdapted(self, layout_json: str):
        """Handle layout adaptations based on AI state"""
        try:
            layout_data = json.loads(layout_json)
            logger.info(f"[PHASE6] Layout adapted: {layout_data}")

        except Exception as e:
            logger.error(f"[PHASE6] Error handling layout adaptation: {e}")

    @Slot(str)
    def onChatMessage(self, message_json: str):
        """Handle chat messages with real conversation manager"""
        try:
            message_data = json.loads(message_json)
            user_message = message_data.get("message", "")

            if (
                user_message
                and hasattr(self, "conversation_manager")
                and self.conversation_manager
            ):
                # Process message through real conversation manager
                try:
                    # Generate response using real AI conversation system
                    response = self.conversation_manager.generate_response_sync(
                        user_message
                    )

                    # Send response back to chat interface
                    if (
                        hasattr(self.personality_manager, "chat_interface")
                        and self.personality_manager.chat_interface
                    ):
                        self.personality_manager.chat_interface.responseReady.emit(
                            response
                        )

                    logger.info(
                        f"[PHASE6] Real chat response generated: {len(response)} chars"
                    )

                except Exception as conv_error:
                    logger.error(f"[PHASE6] Conversation manager error: {conv_error}")
                    # Fallback response
                    fallback_response = f"I understand you said: '{user_message}'. I'm currently experiencing some technical difficulties but I'm working on it!"
                    if (
                        hasattr(self.personality_manager, "chat_interface")
                        and self.personality_manager.chat_interface
                    ):
                        self.personality_manager.chat_interface.responseReady.emit(
                            fallback_response
                        )
            else:
                logger.warning("[PHASE6] No conversation manager available for chat")

        except Exception as e:
            logger.error(f"[PHASE6] Error handling chat message: {e}")

    @Slot(str)
    def onGUIStateSaved(self, state_json: str):
        """Handle GUI state saving"""
        try:
            state_data = json.loads(state_json)
            logger.info(
                f"[PHASE6] GUI state saved for panel: {state_data.get('current_panel', 'unknown')}"
            )

        except Exception as e:
            logger.error(f"[PHASE6] Error handling GUI state save: {e}")

    def loadPanel(self, panel_id: str):
        """Enhanced loadPanel with Phase 6 personality integration"""
        try:
            logger.debug(f"Attempting to load panel: {panel_id}")

            # Check if web view exists - be more permissive
            if not hasattr(self, "web_view"):
                logger.error(f"❌ Cannot load panel {panel_id}: No web_view attribute")
                return

            if not self.web_view:
                logger.error(f"❌ Cannot load panel {panel_id}: web_view is None")
                return

            # Only do the deletion check if absolutely necessary
            web_view_deleted = self._is_web_view_deleted()
            logger.debug(f"Web view deleted check result: {web_view_deleted}")

            if web_view_deleted:
                logger.warning(
                    f"⚠️ Web view deleted for panel {panel_id}, attempting recreation..."
                )
                if self._recreateWebView():
                    logger.info(
                        f"✅ Web view successfully recreated for panel {panel_id}"
                    )
                else:
                    logger.error(
                        f"❌ Cannot load panel {panel_id}: Failed to recreate web view"
                    )
                    return

            # Track panel change with personality manager
            if hasattr(self, "personality_manager") and self.personality_manager:
                self.personality_manager.update_current_panel(panel_id)

            # Handle Phase 6 chat panel
            if panel_id == "chat":
                panel_file = Path(__file__).parent / "web_panels" / "phase6_chat.html"
                if panel_file.exists():
                    self.web_view.load(QUrl.fromLocalFile(str(panel_file.absolute())))
                    self.current_panel = panel_id
                    self.statusBar().showMessage(
                        "💬 Chat with Lyrixa - AI conversation interface"
                    )
                    return
                else:
                    logger.warning(f"Chat panel file not found: {panel_file}")

            # Handle consciousness panel
            if panel_id == "consciousness":
                self.loadConsciousnessPanel()
                return

            # Special handling for Phase 5 plugin demo
            if panel_id == "plugin_demo":
                panel_path = (
                    Path(__file__).parent / "web_panels" / "phase5_plugin_demo.html"
                )
            else:
                panel_path = (
                    Path(__file__).parent / "web_panels" / f"{panel_id}_panel.html"
                )

            if not panel_path.exists():
                # Create default panel if it doesn't exist
                self.createDefaultPanel(panel_id, panel_path)

            # Clean up consciousness panel if switching from it
            self.cleanupConsciousnessPanel()

            # Ensure web view is visible
            if (
                hasattr(self, "web_view")
                and self.web_view
                and not self.web_view.isVisible()
            ):
                self.web_view.show()

            # Load the panel
            logger.debug(f"Loading panel from: {panel_path}")
            self.web_view.load(QUrl.fromLocalFile(str(panel_path.absolute())))
            self.current_panel = panel_id
            self.statusBar().showMessage(f"🌟 Loaded {panel_id.title()} Panel")
            logger.info(f"[CHECK] Successfully loaded panel: {panel_id}")

        except Exception as e:
            logger.error(f"❌ Error loading panel {panel_id}: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")

    def loadConsciousnessPanel(self):
        """Load the consciousness integration panel."""
        try:
            logger.debug("Attempting to load consciousness panel")

            # Try to import consciousness panel
            try:
                from .consciousness_panel import create_consciousness_panel

                logger.debug("Successfully imported consciousness_panel")
            except ImportError as e:
                logger.warning(f"Could not import consciousness_panel: {e}")
                # Fallback to web-based panel
                self.loadWebConsciousnessPanel()
                return

            # Create consciousness panel with current integrator
            try:
                consciousness_panel = create_consciousness_panel(
                    self.consciousness_integrator, self
                )
                logger.debug("Successfully created consciousness panel")
            except Exception as e:
                logger.warning(f"Failed to create consciousness panel: {e}")
                # Fallback to web-based panel
                self.loadWebConsciousnessPanel()
                return

            # Instead of replacing layout, hide web view and add consciousness panel
            if hasattr(self, "center_panel") and self.center_panel:
                layout = self.center_panel.layout()
                if layout and hasattr(self, "web_view") and self.web_view:
                    # Hide the web view but keep it in the layout
                    self.web_view.hide()

                    # Clean up any existing consciousness widget
                    self.cleanupConsciousnessPanel()

                    # Add consciousness panel to existing layout
                    self.consciousness_widget = consciousness_panel
                    layout.addWidget(consciousness_panel)

                    self.current_panel = "consciousness"
                    self.statusBar().showMessage(
                        "⚛️ Consciousness Interface - Phase 1-5 Integration"
                    )

                    logger.info("[CHECK] Consciousness panel loaded successfully")
                else:
                    logger.error(
                        "Cannot load consciousness panel: No valid center panel layout"
                    )
            else:
                logger.error("❌ Center panel not found")
                # Fallback to web-based panel
                self.loadWebConsciousnessPanel()

        except Exception as e:
            logger.error(f"❌ Failed to load consciousness panel: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")
            # Fallback to web-based panel
            self.loadWebConsciousnessPanel()

    def loadWebConsciousnessPanel(self):
        """Fallback: Load web-based consciousness panel."""
        try:
            logger.debug("Loading web-based consciousness panel as fallback")

            # Check if web view is available - more permissive than before
            if not hasattr(self, "web_view") or not self.web_view:
                logger.warning(
                    "⚠️ Web view not available for consciousness panel, attempting recreation..."
                )
                if self._recreateWebView():
                    logger.info(
                        "✅ Web view successfully recreated for consciousness panel"
                    )
                else:
                    logger.error(
                        "❌ Cannot load web consciousness panel: Failed to recreate web view"
                    )
                    return

            # Check if recreated web view is still deleted
            if self._is_web_view_deleted():
                logger.warning(
                    "⚠️ Web view still deleted after recreation attempt, trying once more..."
                )
                if self._recreateWebView():
                    logger.info("✅ Web view successfully recreated on second attempt")
                else:
                    logger.error(
                        "❌ Cannot load web consciousness panel: Web view recreation failed"
                    )
                    return

            panel_path = (
                Path(__file__).parent / "web_panels" / "consciousness_panel.html"
            )

            if not panel_path.exists():
                logger.debug("Creating consciousness web panel HTML file")
                self.createConsciousnessWebPanel(panel_path)

            # Try to load the panel
            logger.debug(f"Loading web consciousness panel from: {panel_path}")
            self.web_view.load(QUrl.fromLocalFile(str(panel_path.absolute())))
            self.current_panel = "consciousness"
            self.statusBar().showMessage("⚛️ Consciousness Interface (Web Mode)")
            logger.info("[CHECK] Web consciousness panel loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load web consciousness panel: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")

    def createConsciousnessWebPanel(self, path: Path):
        """Create a basic consciousness web panel."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Consciousness Interface</title>
            <style>
                body {
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                    color: #e0e0e0;
                    font-family: 'Segoe UI', sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .header h1 {
                    color: #00d4ff;
                    font-size: 2.5em;
                    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
                }
                .status {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(0, 212, 255, 0.3);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚛️ Consciousness Interface</h1>
                <p>Phase 1-5 Integration</p>
            </div>
            <div class="status">
                <h3>System Status</h3>
                <p>Consciousness integration is being initialized...</p>
                <p>Please wait for backend connection.</p>
            </div>
        </body>
        </html>
        """

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html_content, encoding="utf-8")
            logger.debug(f"Created consciousness web panel at: {path}")
        except Exception as e:
            logger.error(f"❌ Failed to create consciousness web panel: {e}")

    def createDefaultPanel(self, panel_id: str, path: Path):
        """Create a default panel if it doesn't exist."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{panel_id.title()} Panel</title>
            <link rel="stylesheet" href="../assets/style.css">
        </head>
        <body>
            <div class="panel-container" data-panel="{panel_id}">
                <div class="panel-header">
                    <h1>🎙️ {panel_id.title()} Panel</h1>
                </div>
                <div class="panel-content">
                    <div class="placeholder">
                        <div class="glow-orb"></div>
                        <p>Panel coming in Phase 2...</p>
                    </div>
                </div>
            </div>
            <script src="../assets/effects.js"></script>
        </body>
        </html>
        """

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html_content, encoding="utf-8")

    def applyAetherraTheme(self):
        """Apply the Aetherra color scheme and styling."""
        self.setStyleSheet(
            """
            QMainWindow {
                background: #0a0a0a;
                color: #ffffff;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }

            QFrame {
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
            }

            QMenuBar {
                background: #1a1a1a;
                color: #ffffff;
                border-bottom: 1px solid rgba(0, 255, 136, 0.3);
            }

            QMenuBar::item {
                background: transparent;
                padding: 8px 16px;
            }

            QMenuBar::item:selected {
                background: rgba(0, 255, 136, 0.2);
                border-radius: 4px;
            }
        """
        )

    def getButtonStyle(self) -> str:
        """Get the Aetherra-themed button style."""
        return """
            QPushButton {
                background: rgba(26, 26, 26, 0.8);
                color: #ffffff;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                margin: 4px 0;
                text-align: left;
            }

            QPushButton:hover {
                background: rgba(0, 255, 136, 0.1);
                border-color: rgba(0, 255, 136, 0.6);
                /* box-shadow removed for Qt compatibility */
            }

            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.2);
            }
        """

    def updateStatus(self):
        """Update system status display."""
        # This will be connected to real backend data in later phases
        if self.service_registry:
            if hasattr(self, "nav_panel") and self.nav_panel:
                self.nav_panel.set_status("🌟 All Systems Online")
        else:
            if hasattr(self, "nav_panel") and self.nav_panel:
                self.nav_panel.set_status("[WARN] Connecting...")

    def updateMetrics(self):
        """Update metrics display."""
        # This will be connected to real backend metrics in later phases
        import random

        # Simulate live metrics for now
        metrics_data = {
            "memory_load": random.randint(30, 70),
            "cpu_usage": random.randint(10, 40),
            "agents_active": random.randint(5, 12),
            "plugins_loaded": 12,
        }

        # Update web bridge data
        self.web_bridge.data_cache["metrics"] = metrics_data
        self.web_bridge.metrics_updated.emit(json.dumps(metrics_data))

        # Update extracted metrics panel if present
        if hasattr(self, "metrics_panel") and self.metrics_panel:
            try:
                self.metrics_panel.update_values(metrics_data)
            except Exception:
                pass

    # Backend connection methods (called by launcher)
    def set_service_registry(self, service_registry):
        """Connect service registry."""
        self.service_registry = service_registry
        self._update_backend_services()

    def set_plugin_manager(self, plugin_manager):
        """Connect plugin manager."""
        self.plugin_manager = plugin_manager
        self._update_backend_services()

    def set_lyrixa_engine(self, lyrixa_engine):
        """Connect Lyrixa engine."""
        self.lyrixa_engine = lyrixa_engine
        self._update_backend_services()

    def set_memory_system(self, memory_system):
        """Connect memory system."""
        self.memory_system = memory_system
        self._update_backend_services()

    def set_agent_orchestrator(self, agent_orchestrator):
        """Connect agent orchestrator."""
        self.agent_orchestrator = agent_orchestrator
        self._update_backend_services()

    def set_consciousness_integrator(self, consciousness_integrator):
        """Connect consciousness integrator."""
        self.consciousness_integrator = consciousness_integrator
        self._update_backend_services()
        logger.info("✅ Consciousness integrator connected to GUI")

    def _update_backend_services(self):
        """Update the context bridge with current backend services."""
        services = {}

        if hasattr(self, "service_registry") and self.service_registry:
            services["service_registry"] = self.service_registry

        if hasattr(self, "plugin_manager") and self.plugin_manager:
            services["plugin_manager"] = self.plugin_manager

        if hasattr(self, "lyrixa_engine") and self.lyrixa_engine:
            services["lyrixa_engine"] = self.lyrixa_engine

        if hasattr(self, "memory_system") and self.memory_system:
            services["memory_system"] = self.memory_system

        if hasattr(self, "agent_orchestrator") and self.agent_orchestrator:
            services["agent_orchestrator"] = self.agent_orchestrator

        if hasattr(self, "consciousness_integrator") and self.consciousness_integrator:
            services["consciousness_integrator"] = self.consciousness_integrator

        # Connect services to the context bridge
        self.web_bridge.connect_backend_services(services)

        # Connect real conversation manager for the main window too
        try:
            import Aetherra.aetherra_core.agents.conversation_manager as cm

            workspace_path = os.path.join(os.path.dirname(__file__), "..", "..", "..")
            manager_cls = getattr(cm, "LyrixaConversationManager", None)
            if manager_cls:
                self.conversation_manager = manager_cls(
                    workspace_path=workspace_path, gui_interface=self
                )
                logger.info("✅ LyrixaHybridWindow conversation manager connected")
            else:
                raise ImportError("LyrixaConversationManager not found")
        except Exception as e:
            logger.warning(
                f"❌ Failed to connect conversation manager to main window: {e}"
            )
            self.conversation_manager = None

        # Phase 3: Connect auto-generator to backend services and start introspection
        if services and hasattr(self, "auto_generator"):
            self.auto_generator.connect_backend_services(services)
            # Start auto-generation after a short delay to allow services to settle
            QTimer.singleShot(1000, self.auto_generator.start_auto_generation)


def main():
    """Standalone launcher for testing."""
    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa Hybrid UI")

    window = LyrixaHybridWindow()
    window.show()

    sys.exit(app.exec())


# Compatibility aliasing: prefer the new LyrixaBasicWindow when available
# unless explicitly forced to use the legacy hybrid via AETHERRA_USE_HYBRID=1
try:
    if os.getenv("AETHERRA_USE_HYBRID", "0") != "1":
        from Aetherra.lyrixa.lyrixa_basic_gui import (
            LyrixaBasicWindow as _LyrixaBasicWindow,
        )

        # Rebind public names to the basic GUI for external imports
        LyrixaHybridWindow = _LyrixaBasicWindow  # type: ignore[assignment]
        MainWindow = _LyrixaBasicWindow  # type: ignore[assignment]

        warnings.warn(
            "Aetherra.lyrixa.gui.main_window is deprecated; use Aetherra.lyrixa.lyrixa_basic_gui. "
            "Temporarily aliasing LyrixaHybridWindow/MainWindow to LyrixaBasicWindow.",
            DeprecationWarning,
            stacklevel=2,
        )
    else:
        # Legacy mode explicitly requested
        MainWindow = LyrixaHybridWindow
except Exception:
    # Fallback to legacy hybrid window if basic GUI import fails for any reason
    MainWindow = LyrixaHybridWindow

# Export classes for external use
__all__ = ["LyrixaWebBridge", "LyrixaHybridWindow", "MainWindow"]


if __name__ == "__main__":
    main()
