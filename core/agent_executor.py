#!/usr/bin/env python3
"""
🤖 AetherraCode Agent Executor
===========================

Execution engine for agent-related AetherraCode syntax, enabling direct
control of the agent system through AetherraCode commands.

Supported Agent Commands:
- agent.mode = "state"       # Set agent mode/state
- agent.start()              # Start agent background process
- agent.stop()               # Stop agent background process
- agent.add_goal("text")     # Add a goal to the agent
- agent.clear_goals()        # Clear all agent goals
- agent.status()             # Get agent status information
"""

from typing import Any, Dict, Optional

from core.syntax_tree import NodeType, SyntaxNode

try:
    from core.enhanced_agent import EnhancedNeuroAgent

    AGENT_AVAILABLE = True
except ImportError:
    EnhancedNeuroAgent = None
    AGENT_AVAILABLE = False


class AgentExecutor:
    """Executor for agent-related AetherraCode commands"""

    def __init__(self, agent: Optional[EnhancedNeuroAgent] = None):
        self.agent = agent

    def set_agent(self, agent: EnhancedNeuroAgent):
        """Set the agent instance for execution"""
        self.agent = agent

    def execute_agent_node(self, node: SyntaxNode) -> Dict[str, Any]:
        """Execute an agent-related syntax node"""
        if not self.agent:
            return {
                "status": "error",
                "message": "Agent system not available",
                "node_type": node.type.value,
            }

        try:
            if node.type == NodeType.AGENT:
                return self._execute_agent_command(node)
            elif node.type == NodeType.AGENT_MODE:
                return self._execute_agent_mode(node)
            elif node.type == NodeType.AGENT_GOAL:
                return self._execute_agent_goal(node)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown agent node type: {node.type.value}",
                    "node_type": node.type.value,
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Agent execution error: {str(e)}",
                "node_type": node.type.value,
            }

    def _execute_agent_command(self, node: SyntaxNode) -> Dict[str, Any]:
        """Execute general agent commands (start, stop, status)"""
        action = node.value.get("action")

        if action == "start":
            result = self.agent.start()
            return {
                "status": "success",
                "action": "start",
                "result": result,
                "message": f"Agent start result: {result.get('status', 'unknown')}",
            }

        elif action == "stop":
            result = self.agent.stop()
            return {
                "status": "success",
                "action": "stop",
                "result": result,
                "message": f"Agent stop result: {result.get('status', 'unknown')}",
            }

        elif action == "status":
            status_info = {
                "state": self.agent.get_state(),
                "is_running": getattr(self.agent, "is_running", False),
                "goals_count": len(self.agent.get_goals()),
                "stats": getattr(self.agent, "stats", {}),
            }
            return {
                "status": "success",
                "action": "status",
                "result": status_info,
                "message": f"Agent status: {status_info['state']}",
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown agent action: {action}",
                "action": action,
            }

    def _execute_agent_mode(self, node: SyntaxNode) -> Dict[str, Any]:
        """Execute agent mode setting commands"""
        action = node.value.get("action")
        mode = node.value.get("mode")

        if action == "set_mode" and mode:
            try:
                self.agent.set_state(mode)
                return {
                    "status": "success",
                    "action": "set_mode",
                    "mode": mode,
                    "message": f"Agent mode set to: {mode}",
                }
            except ValueError as e:
                return {
                    "status": "error",
                    "action": "set_mode",
                    "mode": mode,
                    "message": f"Invalid agent mode: {e}",
                }
        else:
            return {
                "status": "error",
                "message": "Invalid agent mode command",
                "action": action,
                "mode": mode,
            }

    def _execute_agent_goal(self, node: SyntaxNode) -> Dict[str, Any]:
        """Execute agent goal management commands"""
        action = node.value.get("action")

        if action == "add":
            goal_text = node.value.get("goal")
            priority = node.value.get("priority", "medium")

            if goal_text:
                goal_dict = {
                    "text": goal_text,
                    "priority": priority,
                    "created": "AetherraCode execution",
                }
                self.agent.add_goal(goal_dict)
                return {
                    "status": "success",
                    "action": "add_goal",
                    "goal": goal_text,
                    "priority": priority,
                    "message": f"Goal added: {goal_text}",
                }
            else:
                return {"status": "error", "message": "Goal text is required", "action": action}

        elif action == "clear":
            current_count = len(self.agent.get_goals())
            self.agent.set_goals([])
            return {
                "status": "success",
                "action": "clear_goals",
                "cleared_count": current_count,
                "message": f"Cleared {current_count} goals",
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown agent goal action: {action}",
                "action": action,
            }


def create_agent_executor(agent: Optional[EnhancedNeuroAgent] = None) -> AgentExecutor:
    """Create an agent executor instance"""
    return AgentExecutor(agent)


def execute_agent_syntax(
    node: SyntaxNode, agent: Optional[EnhancedNeuroAgent] = None
) -> Dict[str, Any]:
    """Convenience function to execute agent syntax nodes"""
    executor = AgentExecutor(agent)
    return executor.execute_agent_node(node)
