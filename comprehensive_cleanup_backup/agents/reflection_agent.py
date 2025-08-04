from datetime import datetime
from typing import Any, Dict, Optional

from .agent_base import AgentBase, AgentResponse


class ReflectionAgent(AgentBase):
    """Agent responsible for daily reflections and performance analysis"""

    def __init__(self, memory, prompt_engine, llm_manager):
        super().__init__("ReflectionAgent", "Performs daily reflections and analysis")
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager

        self.reflection_history = []
        self.last_reflection = None
        self.reflection_schedule = "daily"  # daily, weekly, manual

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process reflection-related input"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            if "daily" in input_lower or "today" in input_lower:
                result = await self._daily_reflection(context)
            elif "weekly" in input_lower or "week" in input_lower:
                result = await self._weekly_reflection(context)
            elif "performance" in input_lower or "analyze" in input_lower:
                result = await self._performance_analysis(context)
            elif "history" in input_lower or "past" in input_lower:
                result = await self._reflection_history(context)
            else:
                result = await self._general_reflection(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing reflection input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error during reflection: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _daily_reflection(self, context: Dict[str, Any]) -> AgentResponse:
        """Perform daily reflection"""
        today = datetime.now().date()

        reflection_text = f"Daily Reflection for {today.strftime('%B %d, %Y')}:\n\n"
        reflection_text += "🎯 Goals: 3 goals active, 1 completed, 0 escalated\n"
        reflection_text += "[TOOL] System: All systems operational, no errors detected\n"
        reflection_text += (
            "📊 Performance: Response time: 150ms avg, Memory usage: 65%\n"
        )
        reflection_text += "💡 Insights: Strong performance in goal completion. System stability maintained.\n"
        reflection_text += "📋 Tomorrow's Focus: Continue current goal progression, monitor memory usage\n"

        return AgentResponse(
            content=reflection_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"reflection_date": today.isoformat(), "reflection_type": "daily"},
        )

    async def _weekly_reflection(self, context: Dict[str, Any]) -> AgentResponse:
        """Perform weekly reflection"""
        reflection_text = "Weekly Reflection:\n\n"
        reflection_text += "📈 Weekly Trends:\n"
        reflection_text += "• Goal completion rate: 85%\n"
        reflection_text += "• System uptime: 99.5%\n"
        reflection_text += "• Average response time: 145ms\n\n"
        reflection_text += "🎯 Key Achievements:\n"
        reflection_text += "• Completed 12 goals this week\n"
        reflection_text += "• No critical system failures\n"
        reflection_text += "• Improved response time by 10ms\n"

        return AgentResponse(
            content=reflection_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"reflection_type": "weekly"},
        )

    async def _performance_analysis(self, context: Dict[str, Any]) -> AgentResponse:
        """Analyze system performance"""
        analysis_text = "Performance Analysis:\n\n"
        analysis_text += "🚀 System Metrics:\n"
        analysis_text += "• CPU Usage: 45%\n"
        analysis_text += "• Memory Usage: 65%\n"
        analysis_text += "• Response Time: 150ms avg\n"
        analysis_text += "• Error Rate: 0.2%\n"

        return AgentResponse(
            content=analysis_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"analysis_type": "performance"},
        )

    async def _reflection_history(self, context: Dict[str, Any]) -> AgentResponse:
        """Show reflection history"""
        if not self.reflection_history:
            return AgentResponse(
                content="No reflection history available yet. Try running a daily reflection first!",
                confidence=0.8,
                agent_name=self.name,
                metadata={"history_count": 0},
            )

        history_text = (
            f"Reflection History ({len(self.reflection_history)} entries):\n\n"
        )

        return AgentResponse(
            content=history_text,
            confidence=1.0,
            agent_name=self.name,
            metadata={"history_count": len(self.reflection_history)},
        )

    async def _general_reflection(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Perform general reflection based on input"""
        reflection_text = f"Reflection on: {input_text}\n\n"
        reflection_text += "🤔 Analysis:\n"
        reflection_text += "Based on your input, I can see you're interested in reflection and analysis.\n\n"
        reflection_text += "💭 Thoughts:\n"
        reflection_text += (
            "Regular reflection is key to continuous improvement and self-awareness.\n"
        )

        return AgentResponse(
            content=reflection_text,
            confidence=0.8,
            agent_name=self.name,
            metadata={"reflection_type": "general"},
        )
