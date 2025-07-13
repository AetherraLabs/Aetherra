from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .agent_base import AgentBase, AgentResponse


class EscalationLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class EscalationAgent(AgentBase):
    """Agent responsible for handling failed or stalled workflows"""

    def __init__(self, memory, prompt_engine, llm_manager):
        super().__init__("EscalationAgent", "Handles failed or stalled workflows")
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager

        self.escalations = {}
        self.escalation_counter = 0

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process escalation-related input"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            if "escalate" in input_lower:
                result = await self._create_escalation(input_text, context)
            elif "status" in input_lower:
                result = await self._check_escalation_status(context)
            elif "resolve" in input_lower:
                result = await self._resolve_escalation(input_text, context)
            elif "critical" in input_lower:
                result = await self._handle_critical_escalation(input_text, context)
            else:
                result = await self._analyze_for_escalation(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing escalation input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error handling escalation: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _create_escalation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Create a new escalation"""
        escalation_id = f"esc_{self.escalation_counter}"
        self.escalation_counter += 1

        # Determine escalation level
        if "critical" in input_text.lower():
            level = EscalationLevel.CRITICAL
        elif "high" in input_text.lower():
            level = EscalationLevel.HIGH
        elif "medium" in input_text.lower():
            level = EscalationLevel.MEDIUM
        else:
            level = EscalationLevel.LOW

        escalation = {
            "id": escalation_id,
            "description": input_text,
            "level": level,
            "status": "open",
            "created_at": datetime.now(),
            "context": context,
        }

        self.escalations[escalation_id] = escalation
        self.log(f"Created escalation: {escalation_id} - Level: {level.name}")

        result_text = f"Escalation Created:\n"
        result_text += f"ID: {escalation_id}\n"
        result_text += f"Level: {level.name}\n"
        result_text += f"Description: {input_text}\n"
        result_text += f"Status: Open\n"

        return AgentResponse(
            content=result_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"escalation_id": escalation_id, "level": level.name},
        )

    async def _check_escalation_status(self, context: Dict[str, Any]) -> AgentResponse:
        """Check status of escalations"""
        if not self.escalations:
            return AgentResponse(
                content="No escalations currently tracked.",
                confidence=1.0,
                agent_name=self.name,
                metadata={"escalation_count": 0},
            )

        open_escalations = [
            e for e in self.escalations.values() if e["status"] == "open"
        ]

        status_text = f"Escalation Status:\n\n"
        status_text += f"Open Escalations: {len(open_escalations)}\n"

        return AgentResponse(
            content=status_text,
            confidence=1.0,
            agent_name=self.name,
            metadata={"open_count": len(open_escalations)},
        )

    async def _resolve_escalation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Resolve an escalation"""
        escalation_id = context.get("escalation_id")

        if not escalation_id or escalation_id not in self.escalations:
            return AgentResponse(
                content="Please specify a valid escalation ID to resolve.",
                confidence=0.5,
                agent_name=self.name,
                metadata={"error": "invalid_escalation_id"},
            )

        escalation = self.escalations[escalation_id]
        escalation["status"] = "resolved"
        escalation["resolution"] = input_text
        escalation["resolved_at"] = datetime.now()

        self.log(f"Resolved escalation: {escalation_id}")

        return AgentResponse(
            content=f"Escalation {escalation_id} resolved successfully.\nResolution: {input_text}",
            confidence=0.9,
            agent_name=self.name,
            metadata={"escalation_id": escalation_id, "resolved": True},
        )

    async def _handle_critical_escalation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle critical escalation with immediate action"""
        action_text = "🚨 CRITICAL ESCALATION PROTOCOL ACTIVATED\n\n"
        action_text += "Immediate Actions Taken:\n"
        action_text += "✅ Alerting system administrators\n"
        action_text += "✅ Triggering emergency protocols\n"
        action_text += "✅ Initiating system health checks\n"

        return AgentResponse(
            content=action_text,
            confidence=1.0,
            agent_name=self.name,
            metadata={"critical_escalation": True},
        )

    async def _analyze_for_escalation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Analyze input to determine if escalation is needed"""
        escalation_keywords = [
            "error",
            "fail",
            "stuck",
            "broken",
            "critical",
            "urgent",
            "help",
        ]

        input_lower = input_text.lower()
        found_keywords = [kw for kw in escalation_keywords if kw in input_lower]

        if found_keywords:
            recommendation = f"Based on your input, I detected potential escalation triggers: {', '.join(found_keywords)}\n\n"
            recommendation += "Would you like me to create an escalation ticket?"
            confidence = 0.8
        else:
            recommendation = "No immediate escalation needed based on your input."
            confidence = 0.6

        return AgentResponse(
            content=recommendation,
            confidence=confidence,
            agent_name=self.name,
            metadata={"escalation_keywords": found_keywords},
        )
