#!/usr/bin/env python3
"""
🎭 Neuroplex Agent Integration
=============================

Seamless integration between the Enhanced Agent and Neuroplex interface.
This module provides the "nervous system" connecting the autonomous agent
(the intelligence) with Neuroplex (the face) for real-time collaboration.

Features:
- Real-time agent status display in Neuroplex
- Agent suggestions and recommendations in the UI
- User-agent collaboration workflows
- Visual feedback for agent activities
- Agent-driven UI improvements and adaptations
"""

import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional

# Qt imports for Neuroplex integration
try:
    from PySide6.QtCore import QObject, QThread, QTimer, Signal
    from PySide6.QtWidgets import QLabel, QProgressBar, QTextEdit, QVBoxLayout, QWidget

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

# Agent imports
try:
    from core.enhanced_agent import AgentState, EnhancedNeuroAgent

    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False


class AgentStatusWidget(QWidget):
    """Widget to display agent status in Neuroplex"""

    def __init__(self, agent: Optional[EnhancedNeuroAgent] = None, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """Setup the status widget UI"""
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("🤖 Agent Status")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Status indicator
        self.status_label = QLabel("Agent: Offline")
        layout.addWidget(self.status_label)

        # Activity indicator
        self.activity_bar = QProgressBar()
        self.activity_bar.setRange(0, 100)
        self.activity_bar.setValue(0)
        layout.addWidget(self.activity_bar)

        # Statistics
        self.stats_label = QLabel("No statistics available")
        layout.addWidget(self.stats_label)

        # Recent activities
        self.activities_text = QTextEdit()
        self.activities_text.setMaximumHeight(100)
        self.activities_text.setPlaceholderText("Agent activities will appear here...")
        layout.addWidget(self.activities_text)

    def setup_timer(self):
        """Setup timer for status updates"""
        if QT_AVAILABLE:
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_status)
            self.update_timer.start(2000)  # Update every 2 seconds

    def update_status(self):
        """Update the agent status display"""
        if not self.agent:
            return

        try:
            status = self.agent.get_agent_status()

            # Update status label
            state = status.get("state", "unknown")
            is_running = status.get("is_running", False)
            status_text = f"Agent: {state.title()}" if is_running else "Agent: Offline"
            self.status_label.setText(status_text)

            # Update activity bar
            uptime = status.get("uptime_seconds", 0)
            activity_level = min(100, int((uptime % 60) * 100 / 60))  # Cycle every minute
            self.activity_bar.setValue(activity_level)

            # Update statistics
            stats = status.get("stats", {})
            stats_text = (
                f"Cycles: {stats.get('cycles_completed', 0)} | "
                f"Actions: {stats.get('actions_triggered', 0)} | "
                f"Reflections: {stats.get('reflections_generated', 0)}"
            )
            self.stats_label.setText(stats_text)

            # Update recent activities (simplified for demo)
            if hasattr(self.agent, "recent_activities"):
                activities = "\n".join(self.agent.recent_activities[-5:])
                self.activities_text.setPlainText(activities)

        except Exception as e:
            self.status_label.setText(f"Agent: Error - {str(e)[:50]}")


class AgentRecommendationsWidget(QWidget):
    """Widget to display agent recommendations in Neuroplex"""

    def __init__(self, agent: Optional[EnhancedNeuroAgent] = None, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """Setup the recommendations widget UI"""
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("💡 Agent Recommendations")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Recommendations display
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setPlaceholderText("Agent recommendations will appear here...")
        layout.addWidget(self.recommendations_text)

    def setup_timer(self):
        """Setup timer for recommendation updates"""
        if QT_AVAILABLE:
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_recommendations)
            self.update_timer.start(10000)  # Update every 10 seconds

    def update_recommendations(self):
        """Update the agent recommendations display"""
        if not self.agent or not self.agent.memory:
            return

        try:
            # Get recent agent suggestions from memory
            suggestions = self.agent.memory.recall(
                tags=["agent_suggestion", "neuroplex_suggestions"]
            )

            if suggestions:
                latest_suggestions = suggestions[-3:]  # Get last 3 suggestions
                recommendations_text = ""

                for i, suggestion in enumerate(latest_suggestions, 1):
                    timestamp = suggestion.get("timestamp", "Unknown time")
                    content = (
                        suggestion.get("text", "")[:200] + "..."
                        if len(suggestion.get("text", "")) > 200
                        else suggestion.get("text", "")
                    )
                    recommendations_text += f"{i}. {content}\n   📅 {timestamp}\n\n"

                self.recommendations_text.setPlainText(recommendations_text)
            else:
                self.recommendations_text.setPlainText("No recent recommendations available.")

        except Exception as e:
            self.recommendations_text.setPlainText(f"Error loading recommendations: {str(e)}")


class NeuroplexAgentIntegration(QObject):
    """Main integration class connecting agent to Neuroplex"""

    # Signals for agent events
    agent_started = Signal()
    agent_stopped = Signal()
    agent_suggestion = Signal(str)
    agent_state_changed = Signal(str)

    def __init__(self, neuroplex_window=None):
        super().__init__()
        self.neuroplex_window = neuroplex_window
        self.agent = None
        self.status_widget = None
        self.recommendations_widget = None

        # Agent event handlers
        self.event_handlers = {
            "user_action": self._handle_user_action,
            "code_execution": self._handle_code_execution,
            "goal_update": self._handle_goal_update,
            "memory_operation": self._handle_memory_operation,
        }

    def set_agent(self, agent: EnhancedNeuroAgent):
        """Set the agent instance for integration"""
        self.agent = agent

        # Create UI widgets
        if QT_AVAILABLE:
            self.status_widget = AgentStatusWidget(agent)
            self.recommendations_widget = AgentRecommendationsWidget(agent)

        # Connect agent events to Neuroplex
        self._setup_agent_monitoring()

    def get_status_widget(self) -> Optional[QWidget]:
        """Get the agent status widget for embedding in Neuroplex"""
        return self.status_widget

    def get_recommendations_widget(self) -> Optional[QWidget]:
        """Get the agent recommendations widget for embedding in Neuroplex"""
        return self.recommendations_widget

    def start_agent(self):
        """Start the agent with Neuroplex integration"""
        if not self.agent:
            return {"status": "error", "message": "No agent configured"}

        result = self.agent.start()

        if result.get("status") == "started":
            self.agent_started.emit()

            # Notify agent that Neuroplex is active
            self.agent.context.neuroplex_active = True
            self.agent.notify_event(
                "neuroplex_connected",
                {"timestamp": datetime.now().isoformat(), "interface": "neuroplex"},
            )

        return result

    def stop_agent(self):
        """Stop the agent gracefully"""
        if not self.agent:
            return {"status": "error", "message": "No agent configured"}

        # Notify agent that Neuroplex is disconnecting
        self.agent.context.neuroplex_active = False
        self.agent.notify_event(
            "neuroplex_disconnecting", {"timestamp": datetime.now().isoformat()}
        )

        result = self.agent.stop()

        if result.get("status") == "stopped":
            self.agent_stopped.emit()

        return result

    def notify_user_action(self, action_type: str, action_data: Dict[str, Any]):
        """Notify agent of user actions in Neuroplex"""
        if self.agent:
            event_data = {
                "action_type": action_type,
                "data": action_data,
                "source": "neuroplex",
                "timestamp": datetime.now().isoformat(),
            }
            self.agent.notify_event("user_action", event_data)
            self._handle_user_action(event_data)

    def request_agent_suggestion(self, context: str = "") -> str:
        """Request a suggestion from the agent"""
        if not self.agent:
            return "Agent not available"

        try:
            # Use agent's adaptive suggestion capability
            suggestion = self.agent.adaptive_suggest(context)
            self.agent_suggestion.emit(suggestion)
            return suggestion
        except Exception as e:
            return f"Error getting agent suggestion: {str(e)}"

    def get_agent_insights(self) -> Dict[str, Any]:
        """Get current agent insights and analysis"""
        if not self.agent:
            return {"status": "error", "message": "Agent not available"}

        try:
            status = self.agent.get_agent_status()

            # Get recent memory patterns
            recent_patterns = self.agent.memory.recall(tags=["pattern_analysis"], limit=3)

            # Get recent reflections
            recent_reflections = self.agent.memory.recall(tags=["agent_reflection"], limit=3)

            return {
                "status": "success",
                "agent_status": status,
                "recent_patterns": recent_patterns,
                "recent_reflections": recent_reflections,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _setup_agent_monitoring(self):
        """Setup monitoring of agent state changes"""
        if not self.agent:
            return

        # Start a monitoring thread
        def monitor_agent():
            last_state = None
            while self.agent and self.agent.is_running:
                try:
                    current_state = self.agent.state
                    if current_state != last_state:
                        self.agent_state_changed.emit(current_state.value)
                        last_state = current_state
                    time.sleep(1)
                except Exception:
                    break

        monitor_thread = threading.Thread(target=monitor_agent, daemon=True)
        monitor_thread.start()

    def _handle_user_action(self, event_data: Dict[str, Any]):
        """Handle user action events"""
        action_type = event_data.get("action_type", "unknown")

        # Log user interaction patterns for agent learning
        if self.agent:
            self.agent.memory.remember(
                f"User action in Neuroplex: {action_type}",
                tags=["user_interaction", "neuroplex", action_type],
                category="user_behavior",
            )

    def _handle_code_execution(self, event_data: Dict[str, Any]):
        """Handle code execution events"""
        if self.agent:
            self.agent.memory.remember(
                f"Code executed in Neuroplex: {event_data}",
                tags=["code_execution", "neuroplex"],
                category="development_activity",
            )

    def _handle_goal_update(self, event_data: Dict[str, Any]):
        """Handle goal update events"""
        if self.agent:
            self.agent.notify_event("goal_update", event_data)

    def _handle_memory_operation(self, event_data: Dict[str, Any]):
        """Handle memory operation events"""
        if self.agent:
            # Agent can learn from memory operation patterns
            self.agent.memory.remember(
                f"Memory operation in Neuroplex: {event_data}",
                tags=["memory_operation", "neuroplex"],
                category="system_usage",
            )


# Factory function for easy integration
def create_neuroplex_agent_integration(neuroplex_window=None) -> NeuroplexAgentIntegration:
    """Create a Neuroplex agent integration instance"""
    return NeuroplexAgentIntegration(neuroplex_window)


# Integration helper functions
def add_agent_to_neuroplex(neuroplex_window, agent: EnhancedNeuroAgent):
    """Helper function to add agent integration to existing Neuroplex window"""
    if not QT_AVAILABLE or not AGENT_AVAILABLE:
        print("⚠️ Agent integration requires PySide6 and enhanced agent")
        return None

    integration = create_neuroplex_agent_integration(neuroplex_window)
    integration.set_agent(agent)

    # Add widgets to Neuroplex if it has a tab widget
    if hasattr(neuroplex_window, "tab_widget") and hasattr(neuroplex_window.tab_widget, "addTab"):
        # Add agent status tab
        status_widget = integration.get_status_widget()
        if status_widget:
            neuroplex_window.tab_widget.addTab(status_widget, "🤖 Agent Status")

        # Add recommendations tab
        recommendations_widget = integration.get_recommendations_widget()
        if recommendations_widget:
            neuroplex_window.tab_widget.addTab(recommendations_widget, "💡 Agent Insights")

    return integration


def main():
    """Demo of Neuroplex agent integration"""
    print("🎭 Neuroplex Agent Integration Demo")
    print("=" * 50)

    if not QT_AVAILABLE:
        print("❌ Qt not available - cannot demo UI integration")
        return

    if not AGENT_AVAILABLE:
        print("❌ Enhanced agent not available")
        return

    # Create integration
    integration = create_neuroplex_agent_integration()
    print("✅ Integration created")

    # This would normally be done with a real Neuroplex window
    print("💡 In a real implementation, this would:")
    print("   • Add agent status widget to Neuroplex")
    print("   • Add agent recommendations widget")
    print("   • Connect agent events to UI updates")
    print("   • Enable real-time agent-user collaboration")


if __name__ == "__main__":
    main()
