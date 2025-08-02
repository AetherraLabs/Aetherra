"""
🚨 Escalation Agent
===================

Agent responsible for handling escalations, priority management,
and routing complex requests to appropriate handlers.
"""

from typing import Any, Dict, List, Optional

from .agent_base import AgentBase


class EscalationAgent(AgentBase):
    """
    Agent for handling escalated requests and priority management.

    Manages:
    - Request prioritization
    - Escalation workflows
    - Complex request routing
    - Emergency handling
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize the escalation agent.

        Args:
            name: Optional agent name
        """
        super().__init__("escalation", name)
        self.escalation_queue = []
        self.priority_levels = ["low", "medium", "high", "critical", "emergency"]
        self.escalation_handlers = {}
        self.update_status("ready")

    def can_handle(self, request_type: str) -> bool:
        """Check if this agent can handle the request type."""
        return request_type in [
            "escalation",
            "priority",
            "emergency",
            "complex_routing",
        ]

    def get_capabilities(self) -> List[str]:
        """Get list of escalation capabilities."""
        capabilities = super().get_capabilities()
        capabilities.extend(
            [
                "priority_management",
                "escalation_routing",
                "emergency_handling",
                "request_prioritization",
                "workflow_management",
            ]
        )
        return capabilities

    async def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle escalation requests.

        Args:
            request: Escalation request data

        Returns:
            Escalation response
        """
        request_type = request.get("type", "escalation")
        priority = request.get("priority", "medium")
        content = request.get("content", {})

        if request_type == "escalation":
            return await self._handle_escalation(content, priority)
        elif request_type == "priority":
            return await self._handle_priority_request(content, priority)
        elif request_type == "emergency":
            return await self._handle_emergency(content)
        else:
            return await self._handle_complex_routing(content, priority)

    async def _handle_escalation(
        self, content: Dict[str, Any], priority: str
    ) -> Dict[str, Any]:
        """Handle escalation workflow."""
        escalation_id = f"esc_{len(self.escalation_queue) + 1:04d}"

        escalation = {
            "id": escalation_id,
            "priority": priority,
            "content": content,
            "status": "pending",
            "created_at": self.last_activity.isoformat(),
            "agent_id": self.agent_id,
        }

        # Add to queue in priority order
        self._add_to_queue(escalation)

        return {
            "success": True,
            "escalation_id": escalation_id,
            "priority": priority,
            "queue_position": self._get_queue_position(escalation_id),
            "estimated_handling_time": self._estimate_handling_time(priority),
            "agent_id": self.agent_id,
        }

    async def _handle_priority_request(
        self, content: Dict[str, Any], priority: str
    ) -> Dict[str, Any]:
        """Handle priority-based request routing."""
        if priority not in self.priority_levels:
            priority = "medium"

        return {
            "success": True,
            "assigned_priority": priority,
            "recommended_handler": self._get_recommended_handler(content, priority),
            "processing_guidelines": self._get_processing_guidelines(priority),
            "agent_id": self.agent_id,
        }

    async def _handle_emergency(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency situations."""
        emergency_id = f"emr_{len(self.escalation_queue) + 1:04d}"

        # Emergency requests get highest priority
        emergency = {
            "id": emergency_id,
            "priority": "emergency",
            "content": content,
            "status": "urgent_processing",
            "created_at": self.last_activity.isoformat(),
            "agent_id": self.agent_id,
        }

        # Add to front of queue
        self.escalation_queue.insert(0, emergency)

        return {
            "success": True,
            "emergency_id": emergency_id,
            "status": "emergency_activated",
            "immediate_actions": self._get_emergency_actions(content),
            "escalation_contacts": self._get_escalation_contacts(),
            "agent_id": self.agent_id,
        }

    async def _handle_complex_routing(
        self, content: Dict[str, Any], priority: str
    ) -> Dict[str, Any]:
        """Handle complex request routing."""
        routing_analysis = self._analyze_routing_requirements(content)

        return {
            "success": True,
            "routing_analysis": routing_analysis,
            "recommended_agents": routing_analysis.get("agents", []),
            "processing_sequence": routing_analysis.get("sequence", []),
            "estimated_complexity": routing_analysis.get("complexity", "medium"),
            "agent_id": self.agent_id,
        }

    def _add_to_queue(self, escalation: Dict[str, Any]):
        """Add escalation to queue in priority order."""
        priority_order = {level: i for i, level in enumerate(self.priority_levels)}
        escalation_priority = priority_order.get(escalation["priority"], 2)

        # Find insertion point based on priority
        insert_index = 0
        for i, existing in enumerate(self.escalation_queue):
            existing_priority = priority_order.get(existing["priority"], 2)
            if escalation_priority <= existing_priority:
                insert_index = i
                break
            insert_index = i + 1

        self.escalation_queue.insert(insert_index, escalation)

    def _get_queue_position(self, escalation_id: str) -> int:
        """Get position of escalation in queue."""
        for i, escalation in enumerate(self.escalation_queue):
            if escalation["id"] == escalation_id:
                return i + 1
        return -1

    def _estimate_handling_time(self, priority: str) -> str:
        """Estimate handling time based on priority."""
        time_estimates = {
            "emergency": "immediate",
            "critical": "within 5 minutes",
            "high": "within 15 minutes",
            "medium": "within 1 hour",
            "low": "within 4 hours",
        }
        return time_estimates.get(priority, "unknown")

    def _get_recommended_handler(self, content: Dict[str, Any], priority: str) -> str:
        """Get recommended handler for request."""
        if priority in ["emergency", "critical"]:
            return "senior_agent"
        elif "technical" in str(content).lower():
            return "technical_agent"
        elif "user" in str(content).lower():
            return "support_agent"
        else:
            return "general_agent"

    def _get_processing_guidelines(self, priority: str) -> List[str]:
        """Get processing guidelines for priority level."""
        guidelines = {
            "emergency": [
                "Immediate response required",
                "Escalate to human oversight",
                "Log all actions",
            ],
            "critical": [
                "Priority handling",
                "Regular status updates",
                "Senior agent review",
            ],
            "high": ["Expedited processing", "Monitor progress", "Quality checks"],
            "medium": ["Standard processing", "Regular workflow", "Basic monitoring"],
            "low": [
                "Queue for processing",
                "Standard workflow",
                "Batch processing allowed",
            ],
        }
        return guidelines.get(priority, ["Standard processing"])

    def _get_emergency_actions(self, content: Dict[str, Any]) -> List[str]:
        """Get immediate actions for emergency situations."""
        return [
            "Alert monitoring systems",
            "Activate emergency protocols",
            "Notify relevant stakeholders",
            "Begin immediate assessment",
            "Prepare contingency measures",
        ]

    def _get_escalation_contacts(self) -> List[str]:
        """Get escalation contact information."""
        return [
            "System Administrator",
            "Technical Lead",
            "Emergency Response Team",
            "Management Oversight",
        ]

    def _analyze_routing_requirements(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complex routing requirements."""
        complexity_indicators = [
            "multi_step",
            "technical",
            "user_sensitive",
            "data_processing",
        ]
        detected_complexity = []

        content_str = str(content).lower()
        for indicator in complexity_indicators:
            if indicator.replace("_", " ") in content_str:
                detected_complexity.append(indicator)

        complexity_level = (
            "high"
            if len(detected_complexity) > 2
            else "medium"
            if detected_complexity
            else "low"
        )

        return {
            "complexity": complexity_level,
            "detected_requirements": detected_complexity,
            "agents": self._recommend_agents_for_complexity(detected_complexity),
            "sequence": self._recommend_processing_sequence(detected_complexity),
        }

    def _recommend_agents_for_complexity(self, requirements: List[str]) -> List[str]:
        """Recommend agents based on complexity requirements."""
        agents = ["lyrixa_ai"]  # Always include main AI

        if "technical" in requirements:
            agents.append("technical_agent")
        if "user_sensitive" in requirements:
            agents.append("support_agent")
        if "data_processing" in requirements:
            agents.append("data_agent")

        return agents

    def _recommend_processing_sequence(self, requirements: List[str]) -> List[str]:
        """Recommend processing sequence."""
        sequence = ["initial_assessment"]

        if "technical" in requirements:
            sequence.append("technical_analysis")

        sequence.extend(["primary_processing", "quality_review", "final_response"])

        return sequence

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current escalation queue status."""
        return {
            "queue_length": len(self.escalation_queue),
            "by_priority": self._count_by_priority(),
            "oldest_escalation": self._get_oldest_escalation(),
            "agent_id": self.agent_id,
        }

    def _count_by_priority(self) -> Dict[str, int]:
        """Count escalations by priority level."""
        counts = {level: 0 for level in self.priority_levels}
        for escalation in self.escalation_queue:
            priority = escalation.get("priority", "medium")
            if priority in counts:
                counts[priority] += 1
        return counts

    def _get_oldest_escalation(self) -> Optional[str]:
        """Get oldest escalation timestamp."""
        if not self.escalation_queue:
            return None
        return min(esc["created_at"] for esc in self.escalation_queue)
