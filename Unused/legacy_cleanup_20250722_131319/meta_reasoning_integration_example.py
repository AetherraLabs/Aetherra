"""
🧠 Meta-Reasoning Engine Integration Example
Demonstrates how to integrate the MetaReasoningEngine into Lyrixa systems
"""

import asyncio
import time
from typing import Dict, List, Any

# Example integration with conversation manager
class EnhancedConversationManager:
    """
    Example showing how to integrate MetaReasoningEngine into conversation flow
    """

    def __init__(self, memory_system, plugin_manager):
        self.memory = memory_system
        self.plugin_manager = plugin_manager

        # 🧠 Initialize Meta-Reasoning Engine
        from Aetherra.lyrixa.intelligence.meta_reasoning import MetaReasoningEngine, DecisionType
        self.meta_reasoning = MetaReasoningEngine(memory_system, plugin_manager)
        self.DecisionType = DecisionType

    async def process_user_request(self, user_input: str) -> str:
        """
        Enhanced request processing with meta-reasoning integration
        """
        # 1. 🎯 Plan the goal with reasoning trace
        planned_steps = await self._plan_goal(user_input)

        # 2. 🧩 Choose plugin with reasoning trace
        chosen_plugin = await self._choose_plugin(user_input, planned_steps)

        # 3. 💬 Generate answer with reasoning trace
        answer = await self._generate_answer(user_input, chosen_plugin, planned_steps)

        return answer

    async def _plan_goal(self, user_input: str) -> List[str]:
        """Plan goal with meta-reasoning tracking"""

        # Analyze user input and plan steps
        if "summarize" in user_input.lower():
            planned_steps = ["retrieve_relevant_data", "analyze_patterns", "generate_summary"]
            confidence = 0.9
            reasoning = "User explicitly requested summary - high confidence in multi-step approach"
        elif "help" in user_input.lower():
            planned_steps = ["understand_problem", "find_solution"]
            confidence = 0.7
            reasoning = "Help request requires understanding then assistance"
        else:
            planned_steps = ["analyze_intent", "provide_response"]
            confidence = 0.6
            reasoning = "General request - using standard two-step approach"

        # 🧠 Trace the goal planning decision
        trace = self.meta_reasoning.explain_goal_planning(
            user_request=user_input,
            planned_steps=planned_steps,
            confidence=confidence,
            reasoning=reasoning
        )

        print(f"🎯 Goal Planning Trace: {trace.trace_id}")
        print(f"   Steps: {planned_steps}")
        print(f"   Confidence: {confidence}")

        return planned_steps

    async def _choose_plugin(self, user_input: str, planned_steps: List[str]) -> str:
        """Choose plugin with meta-reasoning tracking"""

        # Plugin selection logic (simplified)
        if "summarize" in user_input.lower():
            chosen_plugin = "summarizer_plugin"
            confidence = 0.87
            reason = "Plugin is specifically designed for summarization tasks and has 87% success rate"
            intent = "data_summarization"
        elif "file" in user_input.lower():
            chosen_plugin = "file_manager_plugin"
            confidence = 0.82
            reason = "File-related request detected, plugin has file manipulation capabilities"
            intent = "file_operations"
        else:
            chosen_plugin = "general_assistant_plugin"
            confidence = 0.65
            reason = "No specific plugin requirements detected, using general assistant"
            intent = "general_assistance"

        # 🧠 Trace the plugin choice decision
        trace = self.meta_reasoning.explain_plugin_choice(
            goal="Process user request effectively",
            context_summary=f"User said: '{user_input}', planned {len(planned_steps)} steps",
            plugin_chosen=chosen_plugin,
            reason=reason,
            confidence=confidence,
            memory_links=["recent_plugin_performance", "user_preferences"],
            intent=intent
        )

        print(f"🧩 Plugin Choice Trace: {trace.trace_id}")
        print(f"   Chosen: {chosen_plugin}")
        print(f"   Confidence: {confidence}")
        print(f"   Intent: {intent}")

        return chosen_plugin

    async def _generate_answer(self, user_input: str, plugin: str, steps: List[str]) -> str:
        """Generate answer with meta-reasoning tracking"""

        # Answer generation logic (simplified)
        if plugin == "summarizer_plugin":
            answer_approach = "structured_summary"
            confidence = 0.88
            sources = ["memory_system", "recent_interactions", "context_analysis"]
            reasoning = "Using structured approach with multiple data sources for comprehensive summary"
            answer = "Here's a comprehensive summary based on recent data..."

        elif plugin == "file_manager_plugin":
            answer_approach = "direct_file_operation"
            confidence = 0.85
            sources = ["file_system", "user_permissions"]
            reasoning = "Direct file operation approach with permission validation"
            answer = "File operation completed successfully..."

        else:
            answer_approach = "conversational_response"
            confidence = 0.70
            sources = ["general_knowledge", "context"]
            reasoning = "Using general conversational approach with contextual awareness"
            answer = "I understand you're looking for assistance. Let me help..."

        # 🧠 Trace the answer generation decision
        trace = self.meta_reasoning.explain_answer_generation(
            question=user_input,
            answer_approach=answer_approach,
            confidence=confidence,
            sources_used=sources,
            reasoning=reasoning
        )

        print(f"💬 Answer Generation Trace: {trace.trace_id}")
        print(f"   Approach: {answer_approach}")
        print(f"   Sources: {sources}")

        return answer


# 🧪 Example testing and demonstration
class MetaReasoningDemo:
    """Demonstration of Meta-Reasoning Engine capabilities"""

    def __init__(self):
        # Mock memory and plugin systems for demo
        self.memory = MockMemorySystem()
        self.plugin_manager = MockPluginManager()

        # Initialize conversation manager with meta-reasoning
        self.conversation_manager = EnhancedConversationManager(
            self.memory, self.plugin_manager
        )

    async def run_demo(self):
        """Run a comprehensive demo of meta-reasoning capabilities"""

        print("🚀 Meta-Reasoning Engine Demo")
        print("=" * 50)

        # Example conversations with reasoning traces
        test_inputs = [
            "Can you summarize my recent goals?",
            "Help me organize my files",
            "What's the weather like today?"
        ]

        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n📝 Test {i}: '{user_input}'")
            print("-" * 30)

            # Process with full reasoning
            await self.conversation_manager.process_user_request(user_input)

            # Show reasoning analysis
            await self._show_reasoning_analysis()

    async def _show_reasoning_analysis(self):
        """Show analysis of reasoning patterns"""
        meta_engine = self.conversation_manager.meta_reasoning

        # Get recent history
        recent_traces = meta_engine.get_reasoning_history(3)
        print(f"\n📊 Recent Decisions: {len(recent_traces)}")

        # Show confidence trends
        trends = meta_engine.get_confidence_trends()
        print(f"🎯 Confidence Trends: {trends}")

        # Generate report
        report = meta_engine.generate_reasoning_report()
        print(f"📈 Total Decisions: {report['total_decisions']}")
        print(f"📈 Average Confidence: {report['average_confidence']:.2f}")


# 🎭 Mock systems for demonstration
class MockMemorySystem:
    """Mock memory system for demonstration"""
    def __init__(self):
        self.stored_data = []

    def store(self, data):
        self.stored_data.append(data)
        print(f"💾 Stored: {data.get('type', 'unknown')} trace")


class MockPluginManager:
    """Mock plugin manager for demonstration"""
    def list_plugin_names(self):
        return [
            "summarizer_plugin",
            "file_manager_plugin",
            "general_assistant_plugin",
            "goal_tracker_plugin",
            "memory_analyzer_plugin"
        ]


# 🎯 Usage examples for integration
def integration_examples():
    """
    📚 Examples of how to integrate Meta-Reasoning Engine
    """

    print("🔧 Integration Examples:")
    print("=" * 30)

    print("""
    1️⃣ In Intent Resolver:

    # When resolving user intent
    trace = meta_engine.trace_decision(
        context={"user_input": user_input, "detected_entities": entities},
        decision=resolved_intent,
        options=possible_intents,
        confidence=intent_confidence,
        explanation=f"Matched intent based on {matching_patterns}",
        decision_type=DecisionType.CONTEXT_ANALYSIS
    )

    2️⃣ In Plugin Selector:

    # When choosing which plugin to use
    trace = meta_engine.explain_plugin_choice(
        goal=current_goal,
        context_summary=context_summary,
        plugin_chosen=selected_plugin,
        reason=selection_reasoning,
        confidence=selection_confidence,
        memory_links=relevant_memories,
        intent=detected_intent
    )

    3️⃣ In Error Handler:

    # When handling errors
    trace = meta_engine.trace_decision(
        context={"error": error_details, "attempted_action": action},
        decision=recovery_strategy,
        options=available_strategies,
        confidence=recovery_confidence,
        explanation=f"Chose {recovery_strategy} based on error type",
        decision_type=DecisionType.ERROR_HANDLING
    )

    4️⃣ Learning from Feedback:

    # When user provides feedback
    success = meta_engine.add_feedback(
        trace_id=decision_trace_id,
        feedback_score=user_rating,  # 0.0 to 1.0
        feedback_text="This response was very helpful"
    )

    5️⃣ Reflection and Learning:

    # After completing a task
    meta_engine.reflect_on_decision(
        trace_id=original_decision_id,
        outcome="Task completed successfully",
        learned="User prefers detailed explanations for technical topics"
    )
    """)


if __name__ == "__main__":
    # Run the demo
    demo = MetaReasoningDemo()
    asyncio.run(demo.run_demo())

    # Show integration examples
    integration_examples()
