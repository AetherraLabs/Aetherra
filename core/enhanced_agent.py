#!/usr/bin/env python3
"""
🤖 Enhanced AetherraCode Agent System
==================================

Advanced autonomous agent with:
- Background threading for continuous operation
- Goal-monitoring reflection loop with intelligent state tracking
- Periodic triggers for context-aware actions
- Deep integration with AetherraCode (blood) and Lyrixa(face)
- Real-time collaboration with user workflow

The agent operates as the autonomous intelligence layer of the AI OS,
continuously learning, reflecting, and acting on behalf of the user.
"""

import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

# Core AetherraCode imports
try:
    from core.aetherra_memory import AetherraMemory
except ImportError:
    AetherraMemory = None

try:
    from core.goal_system import GoalSystem
except ImportError:
    GoalSystem = None

try:
    from core.plugin_manager import PluginManager
except ImportError:
    PluginManager = None

try:
    from core.interpreter import AetherraInterpreter
except ImportError:
    AetherraInterpreter = None

try:
    from core.syntax_tree import analyze_syntax_tree, parse_aetherra
except ImportError:
    parse_aetherra = None
    analyze_syntax_tree = None


class AgentState(Enum):
    """Agent operational states"""

    IDLE = "idle"
    REFLECTING = "reflecting"
    GOAL_MONITORING = "goal_monitoring"
    ACTION_PLANNING = "action_planning"
    EXECUTING = "executing"
    LEARNING = "learning"
    COLLABORATING = "collaborating"


class TriggerType(Enum):
    """Types of agent triggers"""

    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    GOAL_BASED = "goal_based"
    PATTERN_DETECTED = "pattern_detected"
    USER_CONTEXT = "user_context"
    SYSTEM_STATE = "system_state"


@dataclass
class AgentContext:
    """Current context and state information"""

    current_goals: List[Dict[str, Any]] = field(default_factory=list)
    recent_activities: List[Dict[str, Any]] = field(default_factory=list)
    system_state: Dict[str, Any] = field(default_factory=dict)
    user_presence: bool = True
    active_session_time: float = 0.0
    last_interaction: Optional[datetime] = None
    aetherplex_active: bool = False


@dataclass
class AgentTrigger:
    """Trigger for agent actions"""

    trigger_id: str
    trigger_type: TriggerType
    condition: Callable
    action: Callable
    cooldown_seconds: int = 60
    last_triggered: Optional[datetime] = None
    enabled: bool = True


class EnhancedNeuroAgent:
    """Enhanced autonomous agent for AetherraCode/Lyrixaintegration"""

    def __init__(
        self,
        memory: Optional["AetherraMemory"] = None,
        goal_system: Optional["GoalSystem"] = None,
        interpreter: Optional["AetherraInterpreter"] = None,
    ):
        # Core components
        self.memory = memory or (AetherraMemory() if AetherraMemory else None)
        self.goal_system = goal_system or (GoalSystem() if GoalSystem else None)
        self.interpreter = interpreter or (
            AetherraInterpreter() if AetherraInterpreter else None
        )

        # Agent state
        self.state = AgentState.IDLE
        self.context = AgentContext()
        self.is_running = False

        # Threading
        self.background_thread = None
        self.event_queue = Queue()
        self.action_queue = Queue()

        # Configuration
        self.config = {
            "reflection_interval": 45,  # seconds
            "goal_check_interval": 20,  # seconds
            "pattern_analysis_interval": 120,  # seconds
            "max_actions_per_cycle": 2,
            "learning_threshold": 0.8,
            "collaboration_timeout": 300,  # 5 minutes
        }

        # Triggers and actions
        self.triggers: Dict[str, AgentTrigger] = {}
        self.registered_actions: Dict[str, Callable] = {}

        # Statistics
        self.stats = {
            "cycles_completed": 0,
            "goals_processed": 0,
            "actions_triggered": 0,
            "patterns_detected": 0,
            "reflections_generated": 0,
            "aetherplex_interactions": 0,
        }

        # Initialize triggers
        self._setup_default_triggers()
        self._setup_aetherplex_integration()

    def start(self):
        """Start the agent background process"""
        if self.is_running:
            return {"status": "already_running", "state": self.state.value}

        self.is_running = True
        self.background_thread = threading.Thread(target=self._agent_loop, daemon=True)
        self.background_thread.start()

        # Log startup
        self._log_agent_event(
            "agent_started",
            {
                "timestamp": datetime.now().isoformat(),
                "initial_state": self.state.value,
                "configured_triggers": len(self.triggers),
            },
        )

        return {
            "status": "started",
            "state": self.state.value,
            "pid": self.background_thread.ident,
            "triggers": list(self.triggers.keys()),
        }

    def stop(self):
        """Stop the agent gracefully"""
        if not self.is_running:
            return {"status": "not_running"}

        self.is_running = False

        # Wait for thread to finish
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=5.0)

        # Log shutdown
        self._log_agent_event(
            "agent_stopped",
            {
                "timestamp": datetime.now().isoformat(),
                "final_state": self.state.value,
                "stats": self.stats.copy(),
            },
        )

        return {
            "status": "stopped",
            "stats": self.stats,
            "uptime_seconds": self.context.active_session_time,
        }

    def _agent_loop(self):
        """Main agent background loop"""
        startup_time = datetime.now()
        last_reflection = datetime.now()
        last_goal_check = datetime.now()
        last_pattern_analysis = datetime.now()

        while self.is_running:
            try:
                current_time = datetime.now()
                self.context.active_session_time = (
                    current_time - startup_time
                ).total_seconds()

                # Process events from queue
                self._process_event_queue()

                # Periodic reflection
                if (current_time - last_reflection).total_seconds() >= self.config[
                    "reflection_interval"
                ]:
                    self._trigger_reflection()
                    last_reflection = current_time

                # Goal monitoring
                if (current_time - last_goal_check).total_seconds() >= self.config[
                    "goal_check_interval"
                ]:
                    self._monitor_goals()
                    last_goal_check = current_time

                # Pattern analysis
                if (
                    current_time - last_pattern_analysis
                ).total_seconds() >= self.config["pattern_analysis_interval"]:
                    self._analyze_patterns()
                    last_pattern_analysis = current_time

                # Check triggers
                self._check_triggers()

                # Process actions
                self._process_action_queue()

                # Update stats
                self.stats["cycles_completed"] += 1

                # Brief sleep to prevent CPU spinning
                time.sleep(1.0)

            except Exception as e:
                self._log_agent_event(
                    "agent_error",
                    {
                        "error": str(e),
                        "state": self.state.value,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                time.sleep(5.0)  # Wait longer on error

    def _trigger_reflection(self):
        """Trigger periodic reflection and learning"""
        if self.state == AgentState.REFLECTING:
            return  # Already reflecting

        previous_state = self.state
        self.state = AgentState.REFLECTING

        try:
            # Analyze recent memories
            recent_memories = self.memory.get_recent_memories(limit=10)

            # Generate insights
            insights = self._generate_insights(recent_memories)

            # Learn from patterns
            patterns = self._detect_learning_patterns()

            # Update knowledge
            if insights:
                self.memory.remember(
                    f"Agent reflection insights: {insights}",
                    tags=["agent_reflection", "insights"],
                    category="agent_learning",
                )

            # Suggest improvements to Lyrixaif active
            if self.context.aetherplex_active:
                self._suggest_aetherplex_improvements(insights, patterns)

            self.stats["reflections_generated"] += 1

        except Exception as e:
            self._log_agent_event("reflection_error", {"error": str(e)})
        finally:
            self.state = previous_state

    def _monitor_goals(self):
        """Monitor and analyze goal progress"""
        if self.state == AgentState.GOAL_MONITORING:
            return

        previous_state = self.state
        self.state = AgentState.GOAL_MONITORING

        try:
            # Get active goals
            active_goals = self.goal_system.get_active_goals()
            self.context.current_goals = active_goals

            for goal in active_goals:
                # Check goal progress
                progress = self._assess_goal_progress(goal)

                # Suggest actions if needed
                if progress["needs_attention"]:
                    self._queue_goal_action(goal, progress)

                # Update goal status
                self.goal_system.update_goal_progress(goal["id"], progress)

            self.stats["goals_processed"] += len(active_goals)

        except Exception as e:
            self._log_agent_event("goal_monitoring_error", {"error": str(e)})
        finally:
            self.state = previous_state

    def _analyze_patterns(self):
        """Analyze system patterns and suggest optimizations"""
        try:
            # Analyze memory patterns
            memory_patterns = self._analyze_memory_patterns()

            # Analyze user behavior patterns
            behavior_patterns = self._analyze_behavior_patterns()

            # Analyze AetherraCode usage patterns
            code_patterns = self._analyze_code_patterns()

            # Combine insights
            all_patterns = {
                "memory": memory_patterns,
                "behavior": behavior_patterns,
                "code": code_patterns,
                "timestamp": datetime.now().isoformat(),
            }

            # Store pattern analysis
            self.memory.remember(
                f"Pattern analysis: {json.dumps(all_patterns, indent=2)}",
                tags=["pattern_analysis", "system_insights"],
                category="agent_analysis",
            )

            self.stats["patterns_detected"] += len(all_patterns)

            return all_patterns

        except Exception as e:
            self._log_agent_event("pattern_analysis_error", {"error": str(e)})
            return {}

    def _setup_default_triggers(self):
        """Setup default agent triggers"""

        # User inactivity trigger
        self.add_trigger(
            "user_inactivity",
            TriggerType.PERIODIC,
            lambda: self._check_user_inactivity(),
            lambda: self._handle_user_inactivity(),
            cooldown_seconds=300,
        )

        # Goal completion trigger
        self.add_trigger(
            "goal_completion",
            TriggerType.GOAL_BASED,
            lambda: self._check_goal_completion(),
            lambda: self._handle_goal_completion(),
            cooldown_seconds=60,
        )

        # Learning opportunity trigger
        self.add_trigger(
            "learning_opportunity",
            TriggerType.PATTERN_DETECTED,
            lambda: self._check_learning_opportunity(),
            lambda: self._handle_learning_opportunity(),
            cooldown_seconds=180,
        )

        # System optimization trigger
        self.add_trigger(
            "system_optimization",
            TriggerType.SYSTEM_STATE,
            lambda: self._check_optimization_opportunity(),
            lambda: self._handle_system_optimization(),
            cooldown_seconds=600,
        )

    def _setup_aetherplex_integration(self):
        """Setup integration hooks with Lyrixa"""
        self.aetherplex_hooks = {
            "on_user_action": self._on_aetherplex_user_action,
            "on_code_execution": self._on_aetherplex_code_execution,
            "on_goal_update": self._on_aetherplex_goal_update,
            "on_memory_operation": self._on_aetherplex_memory_operation,
        }

    def add_trigger(
        self,
        trigger_id: str,
        trigger_type: TriggerType,
        condition: Callable,
        action: Callable,
        cooldown_seconds: int = 60,
    ):
        """Add a new trigger to the agent"""
        trigger = AgentTrigger(
            trigger_id=trigger_id,
            trigger_type=trigger_type,
            condition=condition,
            action=action,
            cooldown_seconds=cooldown_seconds,
        )
        self.triggers[trigger_id] = trigger

        self._log_agent_event(
            "trigger_added", {"trigger_id": trigger_id, "type": trigger_type.value}
        )

    def notify_event(self, event_type: str, event_data: Dict[str, Any]):
        """Notify agent of external events"""
        event = {"type": event_type, "data": event_data, "timestamp": datetime.now()}
        self.event_queue.put(event)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "uptime_seconds": self.context.active_session_time,
            "stats": self.stats.copy(),
            "triggers": {
                trigger_id: {
                    "type": trigger.trigger_type.value,
                    "enabled": trigger.enabled,
                    "last_triggered": trigger.last_triggered.isoformat()
                    if trigger.last_triggered
                    else None,
                }
                for trigger_id, trigger in self.triggers.items()
            },
            "context": {
                "current_goals": len(self.context.current_goals),
                "user_presence": self.context.user_presence,
                "aetherplex_active": self.context.aetherplex_active,
                "last_interaction": self.context.last_interaction.isoformat()
                if self.context.last_interaction
                else None,
            },
        }

    def get_state(self) -> str:
        """Get the current agent state/mode as a string."""
        return self.state.value

    def set_state(self, new_state: str) -> None:
        """Set the agent state/mode. Must be a valid AgentState value."""
        if new_state in AgentState._value2member_map_:
            self.state = AgentState(new_state)
        else:
            raise ValueError(f"Invalid agent state: {new_state}")

    def get_goals(self) -> list:
        """Get the current list of agent goals (dicts)."""
        return self.context.current_goals

    def set_goals(self, goals: list) -> None:
        """Replace the current list of agent goals."""
        self.context.current_goals = goals

    def add_goal(self, goal: dict) -> None:
        """Add a new goal to the agent's current goals."""
        self.context.current_goals.append(goal)

    # LyrixaIntegration Methods
    def _on_aetherplex_user_action(self, action_data: Dict[str, Any]):
        """Handle user actions from Lyrixa"""
        self.context.last_interaction = datetime.now()
        self.context.user_presence = True
        self.stats["aetherplex_interactions"] += 1

        # Analyze action for learning
        self._learn_from_user_action(action_data)

    def _suggest_aetherplex_improvements(self, insights: str, patterns: Dict[str, Any]):
        """Suggest improvements to Lyrixainterface"""
        suggestions = {
            "insights": insights,
            "patterns": patterns,
            "timestamp": datetime.now().isoformat(),
            "suggestions": self._generate_ui_suggestions(patterns),
        }

        # Store suggestions for Lyrixato retrieve
        self.memory.remember(
            f"Lyrixaimprovement suggestions: {json.dumps(suggestions)}",
            tags=["aetherplex_suggestions", "ui_improvements"],
            category="interface_optimization",
        )

    # Internal helper methods
    def _process_event_queue(self):
        """Process events from the event queue"""
        try:
            while True:
                event = self.event_queue.get_nowait()
                self._handle_event(event)
        except Empty:
            pass

    def _process_action_queue(self):
        """Process actions from the action queue"""
        actions_processed = 0
        max_actions = self.config["max_actions_per_cycle"]

        try:
            while actions_processed < max_actions:
                action = self.action_queue.get_nowait()
                self._execute_action(action)
                actions_processed += 1
        except Empty:
            pass

    def _check_triggers(self):
        """Check all triggers for activation"""
        current_time = datetime.now()

        for trigger_id, trigger in self.triggers.items():
            if not trigger.enabled:
                continue

            # Check cooldown
            if (
                trigger.last_triggered
                and (current_time - trigger.last_triggered).total_seconds()
                < trigger.cooldown_seconds
            ):
                continue

            # Check condition
            try:
                if trigger.condition():
                    trigger.last_triggered = current_time
                    self._queue_action(trigger_id, trigger.action)
                    self.stats["actions_triggered"] += 1
            except Exception as e:
                self._log_agent_event(
                    "trigger_error", {"trigger_id": trigger_id, "error": str(e)}
                )

    def _queue_action(self, action_id: str, action: Callable):
        """Queue an action for execution"""
        action_item = {
            "id": action_id,
            "action": action,
            "timestamp": datetime.now(),
            "attempts": 0,
        }
        self.action_queue.put(action_item)

    def _execute_action(self, action_item: Dict[str, Any]):
        """Execute a queued action"""
        try:
            action_item["attempts"] += 1
            result = action_item["action"]()

            self._log_agent_event(
                "action_executed",
                {
                    "action_id": action_item["id"],
                    "result": str(result)[:200],  # Truncate long results
                    "attempts": action_item["attempts"],
                },
            )

        except Exception as e:
            self._log_agent_event(
                "action_execution_error",
                {
                    "action_id": action_item["id"],
                    "error": str(e),
                    "attempts": action_item["attempts"],
                },
            )

    def _log_agent_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log agent events for debugging and analysis"""
        log_entry = {
            "event_type": event_type,
            "data": event_data,
            "timestamp": datetime.now().isoformat(),
            "agent_state": self.state.value,
        }

        # Store in memory for pattern analysis
        self.memory.remember(
            f"Agent event: {event_type} - {json.dumps(event_data)}",
            tags=["agent_log", event_type],
            category="agent_events",
        )

    # Placeholder methods for specific implementations
    def _generate_insights(self, memories: List[Dict[str, Any]]) -> str:
        """Generate insights from recent memories"""
        if not memories:
            return "No recent activity to analyze"

        # Analyze memory themes and patterns
        themes = {}
        for memory in memories:
            for tag in memory.get("tags", []):
                themes[tag] = themes.get(tag, 0) + 1

        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]
        return f"Recent focus areas: {', '.join([f'{theme}({count})' for theme, count in top_themes])}"

    def _detect_learning_patterns(self) -> Dict[str, Any]:
        """Detect patterns that indicate learning opportunities"""
        return {
            "repeated_queries": [],
            "error_patterns": [],
            "skill_gaps": [],
            "optimization_opportunities": [],
        }

    def _assess_goal_progress(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess progress toward a specific goal"""
        return {
            "completion_percentage": 0.5,
            "needs_attention": False,
            "suggested_actions": [],
            "blockers": [],
        }

    def _queue_goal_action(self, goal: Dict[str, Any], progress: Dict[str, Any]):
        """Queue an action related to goal progress"""
        action = lambda: self._handle_goal_progress(goal, progress)
        self._queue_action(f"goal_progress_{goal['id']}", action)

    # Condition check methods
    def _check_user_inactivity(self) -> bool:
        """Check if user has been inactive"""
        if not self.context.last_interaction:
            return False

        inactive_time = (datetime.now() - self.context.last_interaction).total_seconds()
        return inactive_time > 600  # 10 minutes

    def _check_goal_completion(self) -> bool:
        """Check if any goals have been completed"""
        # Implementation would check goal system
        return False

    def _check_learning_opportunity(self) -> bool:
        """Check if there's a learning opportunity"""
        # Implementation would analyze patterns
        return False

    def _check_optimization_opportunity(self) -> bool:
        """Check if system optimization is needed"""
        # Implementation would analyze system state
        return False

    # Action handler methods
    def _handle_user_inactivity(self):
        """Handle user inactivity"""
        self.context.user_presence = False
        return "User marked as inactive"

    def _handle_goal_completion(self):
        """Handle goal completion"""
        return "Goal completion processed"

    def _handle_learning_opportunity(self):
        """Handle learning opportunity"""
        return "Learning opportunity processed"

    def _handle_system_optimization(self):
        """Handle system optimization"""
        return "System optimization performed"


def create_enhanced_agent(
    memory=None, goal_system=None, interpreter=None
) -> EnhancedNeuroAgent:
    """Factory function to create an enhanced agent"""
    return EnhancedNeuroAgent(
        memory=memory, goal_system=goal_system, interpreter=interpreter
    )


def main():
    """Demo of the enhanced agent system"""
    print("🤖 Enhanced AetherraCode Agent System Demo")
    print("=" * 50)

    # Create agent
    agent = create_enhanced_agent()

    # Start agent
    start_result = agent.start()
    print(f"✅ Agent started: {start_result}")

    # Let it run for a bit
    try:
        print("🔄 Agent running... (Press Ctrl+C to stop)")
        time.sleep(30)

        # Check status
        status = agent.get_agent_status()
        print(f"📊 Agent status: {json.dumps(status, indent=2)}")

    except KeyboardInterrupt:
        print("\n🛑 Stopping agent...")

    finally:
        # Stop agent
        stop_result = agent.stop()
        print(f"✅ Agent stopped: {stop_result}")


if __name__ == "__main__":
    main()
