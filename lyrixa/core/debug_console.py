#!/usr/bin/env python3
"""
🐛🔍 LYRIXA DEBUG CONSOLE / DEVELOPER VIEW
==========================================

Advanced debugging and introspection system that shows:
- What Lyrixa sees (input analysis, context, memory)
- What she's thinking (reasoning process, confidence levels)
- Why she picks suggestions or plans (decision matrix, scoring)
- Real-time cognitive state monitoring

This system provides transparency into AI decision-making for developers.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class DebugLevel(Enum):
    """Debug output levels"""

    MINIMAL = 1  # Only major decisions
    STANDARD = 2  # Standard debug info
    DETAILED = 3  # Detailed reasoning
    VERBOSE = 4  # Everything including internal state
    TRACE = 5  # Full execution trace


class CognitiveState(Enum):
    """Current cognitive state of Lyrixa"""

    IDLE = "idle"
    ANALYZING = "analyzing"
    REASONING = "reasoning"
    DECIDING = "deciding"
    EXECUTING = "executing"
    LEARNING = "learning"
    REFLECTING = "reflecting"


@dataclass
class ThoughtProcess:
    """Individual thought or reasoning step"""

    timestamp: datetime
    thought_id: str
    cognitive_state: CognitiveState
    input_analysis: Dict[str, Any]
    reasoning_steps: List[str]
    confidence_scores: Dict[str, float]
    decision_factors: Dict[str, Any]
    alternatives_considered: List[Dict[str, Any]]
    final_decision: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class DecisionMatrix:
    """Decision scoring and reasoning matrix"""

    options: List[Dict[str, Any]]
    scoring_criteria: Dict[str, float]
    weighted_scores: Dict[str, float]
    final_rankings: List[Tuple[str, float]]
    reasoning: str
    confidence: float


@dataclass
class PerceptionSnapshot:
    """What Lyrixa perceives at a moment in time"""

    timestamp: datetime
    user_input: str
    context_window: Dict[str, Any]
    memory_context: List[Dict[str, Any]]
    current_goals: List[str]
    system_state: Dict[str, Any]
    environmental_factors: Dict[str, Any]
    attention_focus: List[str]


class LyrixaDebugConsole:
    """
    🐛🔍 Debug Console for Lyrixa AI Decision-Making

    Provides real-time insight into:
    - Input perception and analysis
    - Reasoning and decision processes
    - Confidence scoring and uncertainty
    - Alternative options considered
    - Execution pathways chosen
    """

    def __init__(self, debug_level: DebugLevel = DebugLevel.STANDARD):
        self.debug_level = debug_level
        self.is_active = True
        self.trace_enabled = False

        # Debug history and state
        self.thought_history: List[ThoughtProcess] = []
        self.perception_history: List[PerceptionSnapshot] = []
        self.current_cognitive_state = CognitiveState.IDLE

        # Performance tracking
        self.decision_timings: List[float] = []
        self.confidence_trends: List[float] = []

        # Output formatting
        self.use_colors = True
        self.show_timestamps = True
        self.max_history = 100

        print("🐛🔍 Lyrixa Debug Console initialized")
        print(f"   📊 Debug Level: {debug_level.name}")
        print("   🎯 Cognitive transparency enabled")

    def set_cognitive_state(self, state: CognitiveState, context: Optional[str] = None):
        """Update current cognitive state"""
        self.current_cognitive_state = state

        if self.debug_level.value >= DebugLevel.STANDARD.value:
            timestamp = self._get_timestamp()
            state_emoji = {
                CognitiveState.IDLE: "😴",
                CognitiveState.ANALYZING: "🔍",
                CognitiveState.REASONING: "🧠",
                CognitiveState.DECIDING: "⚖️",
                CognitiveState.EXECUTING: "⚡",
                CognitiveState.LEARNING: "📚",
                CognitiveState.REFLECTING: "💭",
            }

            emoji = state_emoji.get(state, "🤖")
            print(f"\n{emoji} [{timestamp}] COGNITIVE STATE: {state.value.upper()}")
            if context:
                print(f"   📝 Context: {context}")

    def capture_perception(
        self,
        user_input: str,
        context_window: Dict[str, Any],
        memory_context: List[Dict[str, Any]],
        current_goals: List[str],
        system_state: Dict[str, Any],
        environmental_factors: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Capture what Lyrixa perceives"""

        snapshot_id = f"perception_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Analyze attention focus
        attention_focus = self._analyze_attention_focus(
            user_input, context_window, memory_context, current_goals
        )

        perception = PerceptionSnapshot(
            timestamp=datetime.now(),
            user_input=user_input,
            context_window=context_window,
            memory_context=memory_context,
            current_goals=current_goals,
            system_state=system_state,
            environmental_factors=environmental_factors or {},
            attention_focus=attention_focus,
        )

        self.perception_history.append(perception)
        self._trim_history()

        if self.debug_level.value >= DebugLevel.DETAILED.value:
            self._display_perception(perception)

        return snapshot_id

    def start_thought_process(
        self, input_analysis: Dict[str, Any], initial_reasoning: str
    ) -> str:
        """Start a new thought process"""

        thought_id = f"thought_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        thought = ThoughtProcess(
            timestamp=datetime.now(),
            thought_id=thought_id,
            cognitive_state=self.current_cognitive_state,
            input_analysis=input_analysis,
            reasoning_steps=[initial_reasoning],
            confidence_scores={},
            decision_factors={},
            alternatives_considered=[],
        )

        self.thought_history.append(thought)

        if self.debug_level.value >= DebugLevel.STANDARD.value:
            print(
                f"\n🧠 [{self._get_timestamp()}] THOUGHT PROCESS STARTED: {thought_id}"
            )
            print(f"   💭 Initial reasoning: {initial_reasoning}")

        return thought_id

    def add_reasoning_step(
        self, thought_id: str, reasoning: str, confidence: Optional[float] = None
    ):
        """Add a reasoning step to current thought process"""

        thought = self._find_thought(thought_id)
        if thought:
            thought.reasoning_steps.append(reasoning)

            if confidence is not None:
                step_key = f"step_{len(thought.reasoning_steps)}"
                thought.confidence_scores[step_key] = confidence

            if self.debug_level.value >= DebugLevel.DETAILED.value:
                confidence_str = (
                    f" (confidence: {confidence:.2f})" if confidence else ""
                )
                print(f"   🔗 Reasoning: {reasoning}{confidence_str}")

    def evaluate_decision_matrix(
        self, thought_id: str, options: List[Dict[str, Any]], criteria: Dict[str, float]
    ) -> DecisionMatrix:
        """Evaluate decision options and show scoring"""

        # Calculate weighted scores for each option
        scored_options = []
        for option in options:
            total_score = 0.0
            option_scores = {}

            for criterion, weight in criteria.items():
                criterion_score = option.get(criterion, 0.0)
                weighted_score = criterion_score * weight
                option_scores[criterion] = weighted_score
                total_score += weighted_score

            scored_options.append(
                {"option": option, "scores": option_scores, "total_score": total_score}
            )

        # Rank options by total score
        ranked_options = sorted(
            scored_options, key=lambda x: x["total_score"], reverse=True
        )
        rankings = [
            (opt["option"].get("name", "Unknown"), opt["total_score"])
            for opt in ranked_options
        ]

        # Generate reasoning explanation
        best_option = ranked_options[0]
        reasoning = f"Selected '{best_option['option'].get('name', 'Unknown')}' based on highest weighted score ({best_option['total_score']:.2f})"

        # Calculate confidence (based on score separation)
        if len(ranked_options) > 1:
            score_gap = best_option["total_score"] - ranked_options[1]["total_score"]
            confidence = min(0.95, 0.5 + (score_gap / 2.0))
        else:
            confidence = 0.8

        decision_matrix = DecisionMatrix(
            options=options,
            scoring_criteria=criteria,
            weighted_scores={
                opt["option"].get("name", f"option_{i}"): opt["total_score"]
                for i, opt in enumerate(ranked_options)
            },
            final_rankings=rankings,
            reasoning=reasoning,
            confidence=confidence,
        )

        # Update thought process
        thought = self._find_thought(thought_id)
        if thought:
            thought.decision_factors["decision_matrix"] = decision_matrix.__dict__
            thought.confidence_scores["decision_confidence"] = confidence
            thought.alternatives_considered = options

        if self.debug_level.value >= DebugLevel.STANDARD.value:
            self._display_decision_matrix(decision_matrix)

        return decision_matrix

    def finalize_decision(
        self, thought_id: str, decision: str, execution_time_ms: float
    ):
        """Finalize a thought process with decision"""

        thought = self._find_thought(thought_id)
        if thought:
            thought.final_decision = decision
            thought.execution_time_ms = execution_time_ms

            # Track performance metrics
            self.decision_timings.append(execution_time_ms)
            if thought.confidence_scores:
                avg_confidence = float(
                    np.mean(list(thought.confidence_scores.values()))
                )
                self.confidence_trends.append(avg_confidence)

            if self.debug_level.value >= DebugLevel.STANDARD.value:
                print(f"\n✅ [{self._get_timestamp()}] DECISION FINALIZED")
                print(f"   🎯 Decision: {decision}")
                print(f"   ⏱️ Processing time: {execution_time_ms:.1f}ms")

                if thought.confidence_scores:
                    avg_conf = np.mean(list(thought.confidence_scores.values()))
                    print(f"   📊 Average confidence: {avg_conf:.2f}")

    def show_current_state(self) -> Dict[str, Any]:
        """Show current cognitive and system state"""

        recent_thoughts = self.thought_history[-5:] if self.thought_history else []
        recent_perceptions = (
            self.perception_history[-3:] if self.perception_history else []
        )

        state = {
            "cognitive_state": self.current_cognitive_state.value,
            "debug_level": self.debug_level.name,
            "recent_decision_count": len(recent_thoughts),
            "avg_decision_time": np.mean(self.decision_timings[-10:])
            if self.decision_timings
            else 0,
            "avg_confidence": np.mean(self.confidence_trends[-10:])
            if self.confidence_trends
            else 0,
            "recent_thoughts": [t.thought_id for t in recent_thoughts],
            "recent_perceptions": len(recent_perceptions),
        }

        print(f"\n🔍 [{self._get_timestamp()}] CURRENT DEBUG STATE")
        print(f"   🧠 Cognitive State: {state['cognitive_state']}")
        print(f"   📊 Debug Level: {state['debug_level']}")
        print(f"   ⚡ Recent Decisions: {state['recent_decision_count']}")
        print(f"   ⏱️ Avg Decision Time: {state['avg_decision_time']:.1f}ms")
        print(f"   📈 Avg Confidence: {state['avg_confidence']:.2f}")

        return state

    def get_thought_analysis(self, thought_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed analysis of a thought process"""

        if thought_id:
            thought = self._find_thought(thought_id)
            if not thought:
                return {"error": "Thought process not found"}
        else:
            # Get most recent thought
            thought = self.thought_history[-1] if self.thought_history else None
            if not thought:
                return {"error": "No thought processes recorded"}

        analysis = {
            "thought_id": thought.thought_id,
            "timestamp": thought.timestamp.isoformat(),
            "cognitive_state": thought.cognitive_state.value,
            "reasoning_steps": thought.reasoning_steps,
            "confidence_scores": thought.confidence_scores,
            "alternatives_count": len(thought.alternatives_considered),
            "final_decision": thought.final_decision,
            "execution_time_ms": thought.execution_time_ms,
            "decision_factors": thought.decision_factors,
        }

        if self.debug_level.value >= DebugLevel.VERBOSE.value:
            self._display_thought_analysis(analysis)

        return analysis

    def export_debug_session(self, filepath: Optional[str] = None) -> str:
        """Export debug session to file"""

        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"lyrixa_debug_session_{timestamp}.json"

        session_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "debug_level": self.debug_level.name,
                "total_thoughts": len(self.thought_history),
                "total_perceptions": len(self.perception_history),
            },
            "thoughts": [
                {
                    "thought_id": t.thought_id,
                    "timestamp": t.timestamp.isoformat(),
                    "cognitive_state": t.cognitive_state.value,
                    "reasoning_steps": t.reasoning_steps,
                    "confidence_scores": t.confidence_scores,
                    "final_decision": t.final_decision,
                    "execution_time_ms": t.execution_time_ms,
                }
                for t in self.thought_history
            ],
            "performance_metrics": {
                "decision_timings": self.decision_timings,
                "confidence_trends": self.confidence_trends,
                "avg_decision_time": np.mean(self.decision_timings)
                if self.decision_timings
                else 0,
                "avg_confidence": np.mean(self.confidence_trends)
                if self.confidence_trends
                else 0,
            },
        }

        with open(filepath, "w") as f:
            json.dump(session_data, f, indent=2)

        print(f"📁 Debug session exported to: {filepath}")
        return filepath

    def toggle_debug_level(self, level: DebugLevel):
        """Change debug level on the fly"""
        old_level = self.debug_level
        self.debug_level = level

        print(f"🔧 Debug level changed: {old_level.name} → {level.name}")

    def _analyze_attention_focus(
        self,
        user_input: str,
        context_window: Dict[str, Any],
        memory_context: List[Dict[str, Any]],
        current_goals: List[str],
    ) -> List[str]:
        """Analyze what Lyrixa is focusing attention on"""

        focus_areas = []

        # Analyze input for key concepts
        input_words = user_input.lower().split()

        # Check for technical terms
        tech_terms = ["code", "function", "debug", "error", "api", "database", "server"]
        if any(term in input_words for term in tech_terms):
            focus_areas.append("technical_assistance")

        # Check for questions
        if "?" in user_input or any(
            word in input_words for word in ["what", "how", "why", "when", "where"]
        ):
            focus_areas.append("information_seeking")

        # Check for goal-related terms
        if current_goals and any(
            goal.lower() in user_input.lower() for goal in current_goals
        ):
            focus_areas.append("goal_progress")

        # Check memory relevance
        if memory_context:
            focus_areas.append("memory_integration")

        # Default focus
        if not focus_areas:
            focus_areas.append("general_conversation")

        return focus_areas

    def _display_perception(self, perception: PerceptionSnapshot):
        """Display what Lyrixa perceives"""

        print(f"\n👁️ [{self._get_timestamp()}] PERCEPTION SNAPSHOT")
        print(
            f'   📝 Input: "{perception.user_input[:100]}{"..." if len(perception.user_input) > 100 else ""}"'
        )
        print(f"   🎯 Attention Focus: {', '.join(perception.attention_focus)}")
        print(f"   🧠 Memory Context: {len(perception.memory_context)} entries")
        print(f"   📋 Active Goals: {len(perception.current_goals)}")

        if self.debug_level.value >= DebugLevel.VERBOSE.value:
            print(f"   🔍 Context Window: {list(perception.context_window.keys())}")
            if perception.environmental_factors:
                print(
                    f"   🌍 Environment: {list(perception.environmental_factors.keys())}"
                )

    def _display_decision_matrix(self, matrix: DecisionMatrix):
        """Display decision scoring matrix"""

        print(f"\n⚖️ [{self._get_timestamp()}] DECISION MATRIX")
        print(f"   🎯 Options evaluated: {len(matrix.options)}")
        print(f"   📊 Scoring criteria: {list(matrix.scoring_criteria.keys())}")

        # Show top 3 options
        for i, (option, score) in enumerate(matrix.final_rankings[:3]):
            emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            print(f"   {emoji} {option}: {score:.2f}")

        print(f"   💭 Reasoning: {matrix.reasoning}")
        print(f"   📈 Confidence: {matrix.confidence:.2f}")

    def _display_thought_analysis(self, analysis: Dict[str, Any]):
        """Display detailed thought analysis"""

        print(f"\n🧠 [{self._get_timestamp()}] THOUGHT ANALYSIS")
        print(f"   🆔 ID: {analysis['thought_id']}")
        print(f"   🕐 Duration: {analysis['execution_time_ms']:.1f}ms")
        print(f"   🧩 Reasoning Steps: {len(analysis['reasoning_steps'])}")

        for i, step in enumerate(analysis["reasoning_steps"], 1):
            print(f"      {i}. {step}")

        if analysis["confidence_scores"]:
            avg_conf = np.mean(list(analysis["confidence_scores"].values()))
            print(f"   📊 Average Confidence: {avg_conf:.2f}")

        if analysis["final_decision"]:
            print(f"   ✅ Final Decision: {analysis['final_decision']}")

    def _find_thought(self, thought_id: str) -> Optional[ThoughtProcess]:
        """Find thought process by ID"""
        for thought in reversed(self.thought_history):
            if thought.thought_id == thought_id:
                return thought
        return None

    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        if self.show_timestamps:
            return datetime.now().strftime("%H:%M:%S.%f")[:-3]
        return ""

    def _trim_history(self):
        """Keep history within limits"""
        if len(self.thought_history) > self.max_history:
            self.thought_history = self.thought_history[-self.max_history :]

        if len(self.perception_history) > self.max_history:
            self.perception_history = self.perception_history[-self.max_history :]


class DebugConsoleGUI:
    """GUI components for the debug console"""

    def __init__(self, debug_console: LyrixaDebugConsole):
        self.debug_console = debug_console

    def create_debug_widget(self) -> Dict[str, Any]:
        """Create debug console widget for GUI integration"""

        return {
            "type": "debug_console",
            "title": "🐛 Lyrixa Debug Console",
            "components": {
                "cognitive_state_indicator": {
                    "type": "status_indicator",
                    "current_state": self.debug_console.current_cognitive_state.value,
                },
                "thought_process_viewer": {
                    "type": "scrollable_list",
                    "items": [
                        t.thought_id for t in self.debug_console.thought_history[-10:]
                    ],
                },
                "perception_timeline": {
                    "type": "timeline",
                    "entries": len(self.debug_console.perception_history),
                },
                "confidence_chart": {
                    "type": "line_chart",
                    "data": self.debug_console.confidence_trends[-20:],
                },
                "decision_timing_chart": {
                    "type": "bar_chart",
                    "data": self.debug_console.decision_timings[-20:],
                },
                "controls": {
                    "debug_level_selector": {
                        "type": "dropdown",
                        "options": [level.name for level in DebugLevel],
                        "current": self.debug_console.debug_level.name,
                    },
                    "export_button": {
                        "type": "button",
                        "text": "Export Debug Session",
                        "action": "export_debug_session",
                    },
                    "clear_button": {
                        "type": "button",
                        "text": "Clear History",
                        "action": "clear_debug_history",
                    },
                },
            },
        }

    def handle_gui_action(self, action: str, params: Dict[str, Any]) -> str:
        """Handle GUI actions"""

        if action == "export_debug_session":
            filepath = self.debug_console.export_debug_session()
            return f"Debug session exported to {filepath}"

        elif action == "clear_debug_history":
            self.debug_console.thought_history.clear()
            self.debug_console.perception_history.clear()
            return "Debug history cleared"

        elif action == "change_debug_level":
            level = DebugLevel[params.get("level", "STANDARD")]
            self.debug_console.toggle_debug_level(level)
            return f"Debug level changed to {level.name}"

        elif action == "get_thought_analysis":
            thought_id = params.get("thought_id")
            analysis = self.debug_console.get_thought_analysis(thought_id)
            return str(analysis)  # Convert dict to string for return type consistency

        return "Unknown action"


# Example usage demonstration
if __name__ == "__main__":
    # Create debug console
    debug = LyrixaDebugConsole(DebugLevel.DETAILED)

    # Simulate AI decision process
    print("\n" + "=" * 60)
    print("🐛 LYRIXA DEBUG CONSOLE DEMONSTRATION")
    print("=" * 60)

    # Set cognitive state
    debug.set_cognitive_state(CognitiveState.ANALYZING, "Processing user request")

    # Capture perception
    debug.capture_perception(
        user_input="Help me debug this Python function",
        context_window={"conversation_turn": 5, "topic": "debugging"},
        memory_context=[{"type": "code_help", "relevance": 0.8}],
        current_goals=["assist_with_coding"],
        system_state={"memory_loaded": True, "plugins_active": 2},
    )

    # Start thought process
    thought_id = debug.start_thought_process(
        input_analysis={
            "intent": "debugging_help",
            "complexity": "medium",
            "confidence": 0.85,
        },
        initial_reasoning="User needs debugging assistance for Python function",
    )

    # Add reasoning steps
    debug.add_reasoning_step(
        thought_id, "Analyzing function for common Python errors", 0.9
    )
    debug.add_reasoning_step(thought_id, "Checking syntax and logic patterns", 0.8)
    debug.add_reasoning_step(
        thought_id, "Generating specific debugging suggestions", 0.85
    )

    # Evaluate decision matrix
    options = [
        {"name": "syntax_check", "relevance": 0.9, "effort": 0.2, "impact": 0.7},
        {"name": "logic_analysis", "relevance": 0.8, "effort": 0.6, "impact": 0.9},
        {"name": "step_by_step_debug", "relevance": 0.7, "effort": 0.8, "impact": 0.95},
    ]

    criteria = {"relevance": 0.4, "effort": -0.2, "impact": 0.4}

    decision_matrix = debug.evaluate_decision_matrix(thought_id, options, criteria)

    # Finalize decision
    debug.finalize_decision(thought_id, "step_by_step_debug", 125.5)

    # Show current state
    debug.show_current_state()

    # Get thought analysis
    analysis = debug.get_thought_analysis(thought_id)

    # Export session
    debug.export_debug_session()

    print("\n🎉 Debug console demonstration complete!")
