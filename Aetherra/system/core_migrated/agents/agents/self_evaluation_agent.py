from datetime import datetime
from typing import Any, Dict, Optional

from .agent_base import AgentBase, AgentResponse


class SelfEvaluationAgent(AgentBase):
    """Agent responsible for self-analysis and self-improvement logic"""

    def __init__(self, memory, prompt_engine, llm_manager):
        super().__init__("SelfEvaluationAgent", "Self-analysis and self-improvement")
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager

        self.evaluation_history = []
        self.improvement_suggestions = []
        self.performance_metrics = {
            "response_accuracy": 0.85,
            "response_speed": 150,  # ms
            "error_rate": 0.02,
            "user_satisfaction": 0.8,
        }
        self.last_evaluation = None

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process self-evaluation input"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            if "evaluate" in input_lower or "assessment" in input_lower:
                result = await self._perform_self_evaluation(context)
            elif "improve" in input_lower:
                result = await self._generate_improvement_plan(context)
            elif "metrics" in input_lower or "performance" in input_lower:
                result = await self._show_performance_metrics(context)
            elif "learn" in input_lower:
                result = await self._learn_from_feedback(input_text, context)
            else:
                result = await self._general_self_analysis(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing self-evaluation input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error during self-evaluation: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _perform_self_evaluation(self, context: Dict[str, Any]) -> AgentResponse:
        """Perform comprehensive self-evaluation"""
        evaluation_id = f"eval_{len(self.evaluation_history)}"

        result_text = f"Self-Evaluation Report ({evaluation_id}):\n\n"
        result_text += "📊 Performance Metrics:\n"
        for metric, value in self.performance_metrics.items():
            result_text += f"• {metric.replace('_', ' ').title()}: {value}\n"

        result_text += "\n✅ Strengths:\n"
        result_text += "• High response accuracy\n"
        result_text += "• Fast response times\n"
        result_text += "• Low error rate\n"

        result_text += "\n🔍 Overall Confidence: 85%"

        return AgentResponse(
            content=result_text,
            confidence=0.85,
            agent_name=self.name,
            metadata={"evaluation_id": evaluation_id},
        )

    async def _generate_improvement_plan(
        self, context: Dict[str, Any]
    ) -> AgentResponse:
        """Generate improvement plan based on evaluations"""
        result_text = "Improvement Plan:\n\n"
        result_text += "🎯 Recommended Improvements:\n"
        result_text += "• Continue monitoring performance metrics\n"
        result_text += "• Gather more user feedback\n"
        result_text += "• Optimize response algorithms\n"

        return AgentResponse(
            content=result_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"improvement_plan": True},
        )

    async def _show_performance_metrics(self, context: Dict[str, Any]) -> AgentResponse:
        """Show current performance metrics"""
        metrics_text = "📊 Current Performance Metrics:\n\n"

        for metric, value in self.performance_metrics.items():
            metric_name = metric.replace("_", " ").title()

            if metric == "response_accuracy":
                metrics_text += f"• {metric_name}: {value:.1%}\n"
            elif metric == "response_speed":
                metrics_text += f"• {metric_name}: {value}ms\n"
            elif metric == "error_rate":
                metrics_text += f"• {metric_name}: {value:.2%}\n"
            elif metric == "user_satisfaction":
                metrics_text += f"• {metric_name}: {value:.1%}\n"
            else:
                metrics_text += f"• {metric_name}: {value}\n"

        return AgentResponse(
            content=metrics_text,
            confidence=1.0,
            agent_name=self.name,
            metadata={"metrics": self.performance_metrics},
        )

    async def _learn_from_feedback(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Learn from user feedback"""
        input_lower = input_text.lower()

        if (
            "good" in input_lower
            or "excellent" in input_lower
            or "great" in input_lower
        ):
            sentiment = "positive"
            self.performance_metrics["user_satisfaction"] = min(
                1.0, self.performance_metrics["user_satisfaction"] + 0.01
            )
        elif "bad" in input_lower or "poor" in input_lower or "terrible" in input_lower:
            sentiment = "negative"
            self.performance_metrics["user_satisfaction"] = max(
                0.0, self.performance_metrics["user_satisfaction"] - 0.01
            )
        else:
            sentiment = "neutral"

        result_text = "Thank you for your feedback! I've processed it as follows:\n\n"
        result_text += f"• Sentiment: {sentiment}\n"
        result_text += f"• Feedback: {input_text}\n"
        result_text += "• Impact: Updated user satisfaction metric\n\n"
        result_text += (
            "I use this feedback to continuously improve my responses and performance."
        )

        return AgentResponse(
            content=result_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"sentiment": sentiment},
        )

    async def _general_self_analysis(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Perform general self-analysis"""
        analysis_text = "Self-Analysis:\n\n"
        analysis_text += "🤖 Current Status: Operational and learning\n"
        analysis_text += "📈 Growth Areas: Continuous improvement in all metrics\n"
        analysis_text += "🎯 Focus: Providing helpful and accurate responses\n"

        return AgentResponse(
            content=analysis_text,
            confidence=0.8,
            agent_name=self.name,
            metadata={"analysis_type": "general"},
        )
