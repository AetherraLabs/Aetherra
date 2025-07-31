#!/usr/bin/env python3
"""
🎬 aetherra Agent Replay Engine
Interactive debugging and decision playback system for agent consciousness analysis.

This module provides tools to replay agent decision-making processes,
enabling deep debugging, learning analysis, and "what-if" scenario exploration.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DecisionPoint:
    """Represents a single decision point in agent reasoning"""

    timestamp: str
    decision_id: str
    context: Dict[str, Any]
    options: List[Dict[str, Any]]
    chosen_option: str
    reasoning: str
    confidence: float
    outcome: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ReplaySession:
    """Represents a replay debugging session"""

    session_id: str
    agent_name: str
    start_time: str
    end_time: Optional[str] = None
    decision_count: int = 0
    current_position: int = 0
    breakpoints: List[int] = None
    annotations: Dict[int, str] = None

    def __post_init__(self):
        if self.breakpoints is None:
            self.breakpoints = []
        if self.annotations is None:
            self.annotations = {}


class DecisionTraceAnalyzer:
    """Analyzes decision traces for patterns and insights"""

    def __init__(self):
        self.analysis_cache = {}

    def analyze_decision_sequence(
        self, decisions: List[DecisionPoint]
    ) -> Dict[str, Any]:
        """Analyze a sequence of decisions for patterns"""
        if not decisions:
            return {"error": "No decisions to analyze"}

        analysis = {
            "total_decisions": len(decisions),
            "time_span": self._calculate_time_span(decisions),
            "confidence_stats": self._analyze_confidence(decisions),
            "decision_patterns": self._find_patterns(decisions),
            "outcome_analysis": self._analyze_outcomes(decisions),
            "reasoning_themes": self._extract_reasoning_themes(decisions),
        }

        return analysis

    def _calculate_time_span(self, decisions: List[DecisionPoint]) -> Dict[str, Any]:
        """Calculate time span of decisions"""
        try:
            timestamps = [
                datetime.fromisoformat(d.timestamp.replace("Z", "+00:00"))
                for d in decisions
            ]
            start_time = min(timestamps)
            end_time = max(timestamps)
            duration = (end_time - start_time).total_seconds()

            return {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": duration,
                "decisions_per_minute": len(decisions) / (duration / 60)
                if duration > 0
                else 0,
            }
        except Exception as e:
            logger.error(f"Failed to calculate time span: {e}")
            return {"error": str(e)}

    def _analyze_confidence(self, decisions: List[DecisionPoint]) -> Dict[str, Any]:
        """Analyze confidence levels across decisions"""
        confidences = [d.confidence for d in decisions if d.confidence is not None]

        if not confidences:
            return {"error": "No confidence data available"}

        return {
            "average": sum(confidences) / len(confidences),
            "min": min(confidences),
            "max": max(confidences),
            "std_dev": self._calculate_std_dev(confidences),
            "low_confidence_count": len([c for c in confidences if c < 0.5]),
            "high_confidence_count": len([c for c in confidences if c > 0.8]),
        }

    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance**0.5

    def _find_patterns(self, decisions: List[DecisionPoint]) -> Dict[str, Any]:
        """Find patterns in decision-making"""
        patterns = {
            "repeated_decisions": self._find_repeated_decisions(decisions),
            "decision_sequences": self._find_common_sequences(decisions),
            "context_triggers": self._find_context_triggers(decisions),
        }
        return patterns

    def _find_repeated_decisions(
        self, decisions: List[DecisionPoint]
    ) -> List[Dict[str, Any]]:
        """Find decisions that are repeated frequently"""
        decision_counts = {}
        for decision in decisions:
            key = f"{decision.chosen_option}|{decision.reasoning[:50]}"  # Truncate reasoning for grouping
            decision_counts[key] = decision_counts.get(key, 0) + 1

        repeated = [
            {"pattern": key, "count": count}
            for key, count in decision_counts.items()
            if count > 1
        ]
        return sorted(repeated, key=lambda x: x["count"], reverse=True)

    def _find_common_sequences(
        self, decisions: List[DecisionPoint]
    ) -> List[Dict[str, Any]]:
        """Find common sequences of decisions"""
        sequences = {}
        window_size = 3

        for i in range(len(decisions) - window_size + 1):
            sequence = tuple(d.chosen_option for d in decisions[i : i + window_size])
            sequences[sequence] = sequences.get(sequence, 0) + 1

        common_sequences = [
            {"sequence": list(seq), "count": count}
            for seq, count in sequences.items()
            if count > 1
        ]
        return sorted(common_sequences, key=lambda x: x["count"], reverse=True)

    def _find_context_triggers(
        self, decisions: List[DecisionPoint]
    ) -> List[Dict[str, Any]]:
        """Find context patterns that trigger specific decisions"""
        triggers = {}

        for decision in decisions:
            context_keys = list(decision.context.keys()) if decision.context else []
            context_signature = "|".join(sorted(context_keys))

            if context_signature:
                key = f"{context_signature}->{decision.chosen_option}"
                triggers[key] = triggers.get(key, 0) + 1

        trigger_patterns = [
            {"trigger": key, "count": count}
            for key, count in triggers.items()
            if count > 1
        ]
        return sorted(trigger_patterns, key=lambda x: x["count"], reverse=True)

    def _analyze_outcomes(self, decisions: List[DecisionPoint]) -> Dict[str, Any]:
        """Analyze decision outcomes"""
        outcomes = [d.outcome for d in decisions if d.outcome is not None]

        if not outcomes:
            return {"error": "No outcome data available"}

        # Categorize outcomes
        success_count = 0
        failure_count = 0
        neutral_count = 0

        for outcome in outcomes:
            if isinstance(outcome, dict):
                status = outcome.get("status", "unknown")
                if status in ["success", "completed", "positive"]:
                    success_count += 1
                elif status in ["failure", "error", "negative"]:
                    failure_count += 1
                else:
                    neutral_count += 1

        return {
            "total_outcomes": len(outcomes),
            "success_rate": success_count / len(outcomes) if outcomes else 0,
            "failure_rate": failure_count / len(outcomes) if outcomes else 0,
            "neutral_rate": neutral_count / len(outcomes) if outcomes else 0,
            "outcome_distribution": {
                "success": success_count,
                "failure": failure_count,
                "neutral": neutral_count,
            },
        }

    def _extract_reasoning_themes(
        self, decisions: List[DecisionPoint]
    ) -> List[Dict[str, Any]]:
        """Extract common themes from reasoning text"""
        reasoning_texts = [d.reasoning for d in decisions if d.reasoning]

        if not reasoning_texts:
            return []

        # Simple keyword extraction (in real implementation, could use NLP)
        word_counts = {}
        for text in reasoning_texts:
            words = text.lower().split()
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_counts[word] = word_counts.get(word, 0) + 1

        themes = [
            {"theme": word, "frequency": count}
            for word, count in word_counts.items()
            if count > 2
        ]
        return sorted(themes, key=lambda x: x["frequency"], reverse=True)[:10]


class ReplayEngine:
    """Core replay engine for decision playback and debugging"""

    def __init__(self):
        self.active_sessions = {}
        self.breakpoint_handlers = {}
        self.decision_analyzer = DecisionTraceAnalyzer()

    def start_replay_session(
        self, agent_name: str, decision_trace: List[Dict[str, Any]]
    ) -> str:
        """Start a new replay session"""
        session_id = f"replay_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Convert decision trace to DecisionPoint objects
        decisions = []
        for i, trace_data in enumerate(decision_trace):
            try:
                decision = DecisionPoint(
                    timestamp=trace_data.get(
                        "timestamp", datetime.now(timezone.utc).isoformat()
                    ),
                    decision_id=trace_data.get("decision_id", f"decision_{i}"),
                    context=trace_data.get("context", {}),
                    options=trace_data.get("options", []),
                    chosen_option=trace_data.get("chosen_option", "unknown"),
                    reasoning=trace_data.get("reasoning", "No reasoning recorded"),
                    confidence=trace_data.get("confidence", 0.5),
                    outcome=trace_data.get("outcome"),
                    metadata=trace_data.get("metadata"),
                )
                decisions.append(decision)
            except Exception as e:
                logger.warning(f"Failed to parse decision {i}: {e}")

        session = ReplaySession(
            session_id=session_id,
            agent_name=agent_name,
            start_time=datetime.now(timezone.utc).isoformat(),
            decision_count=len(decisions),
        )

        self.active_sessions[session_id] = {
            "session": session,
            "decisions": decisions,
            "current_position": 0,
        }

        logger.info(
            f"Started replay session {session_id} with {len(decisions)} decisions"
        )
        return session_id

    def step_forward(self, session_id: str, steps: int = 1) -> Dict[str, Any]:
        """Step forward in replay session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session_data = self.active_sessions[session_id]
        session = session_data["session"]
        decisions = session_data["decisions"]

        new_position = min(session.current_position + steps, len(decisions) - 1)
        session.current_position = new_position

        if new_position < len(decisions):
            current_decision = decisions[new_position]
            return {
                "position": new_position,
                "total_decisions": len(decisions),
                "current_decision": asdict(current_decision),
                "at_breakpoint": new_position in session.breakpoints,
            }
        else:
            return {
                "position": new_position,
                "total_decisions": len(decisions),
                "status": "end_of_replay",
            }

    def step_backward(self, session_id: str, steps: int = 1) -> Dict[str, Any]:
        """Step backward in replay session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session_data = self.active_sessions[session_id]
        session = session_data["session"]
        decisions = session_data["decisions"]

        new_position = max(session.current_position - steps, 0)
        session.current_position = new_position

        current_decision = decisions[new_position]
        return {
            "position": new_position,
            "total_decisions": len(decisions),
            "current_decision": asdict(current_decision),
            "at_breakpoint": new_position in session.breakpoints,
        }

    def set_breakpoint(self, session_id: str, position: int) -> bool:
        """Set a breakpoint at specific position"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]["session"]
        if position not in session.breakpoints:
            session.breakpoints.append(position)
            logger.info(f"Breakpoint set at position {position}")
            return True
        return False

    def remove_breakpoint(self, session_id: str, position: int) -> bool:
        """Remove breakpoint at specific position"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]["session"]
        if position in session.breakpoints:
            session.breakpoints.remove(position)
            logger.info(f"Breakpoint removed at position {position}")
            return True
        return False

    def run_to_breakpoint(self, session_id: str) -> Dict[str, Any]:
        """Run replay until next breakpoint"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session_data = self.active_sessions[session_id]
        session = session_data["session"]
        decisions = session_data["decisions"]

        current_pos = session.current_position

        # Find next breakpoint
        next_breakpoint = None
        for bp in sorted(session.breakpoints):
            if bp > current_pos:
                next_breakpoint = bp
                break

        if next_breakpoint is not None:
            session.current_position = next_breakpoint
            current_decision = decisions[next_breakpoint]
            return {
                "position": next_breakpoint,
                "total_decisions": len(decisions),
                "current_decision": asdict(current_decision),
                "status": "stopped_at_breakpoint",
            }
        else:
            # Run to end
            session.current_position = len(decisions) - 1
            return {
                "position": session.current_position,
                "total_decisions": len(decisions),
                "status": "end_of_replay",
            }

    def inspect_context(
        self, session_id: str, position: Optional[int] = None
    ) -> Dict[str, Any]:
        """Inspect agent context at specific position"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session_data = self.active_sessions[session_id]
        session = session_data["session"]
        decisions = session_data["decisions"]

        if position is None:
            position = session.current_position

        if 0 <= position < len(decisions):
            decision = decisions[position]
            return {
                "position": position,
                "decision_id": decision.decision_id,
                "timestamp": decision.timestamp,
                "context": decision.context,
                "available_options": decision.options,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "outcome": decision.outcome,
                "metadata": decision.metadata,
            }
        else:
            raise IndexError(f"Position {position} out of range")

    def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """Analyze entire replay session for insights"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session_data = self.active_sessions[session_id]
        decisions = session_data["decisions"]

        analysis = self.decision_analyzer.analyze_decision_sequence(decisions)
        analysis["session_info"] = asdict(session_data["session"])

        return analysis

    def export_session(self, session_id: str, filepath: Optional[Path] = None) -> str:
        """Export replay session to file"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session_data = self.active_sessions[session_id]

        export_data = {
            "session": asdict(session_data["session"]),
            "decisions": [asdict(d) for d in session_data["decisions"]],
            "analysis": self.analyze_session(session_id),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        if filepath is None:
            filepath = Path(f"replay_session_{session_id}.json")

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Session exported to {filepath}")
        return str(filepath)

    def load_session(self, filepath: Path) -> str:
        """Load replay session from file"""
        with open(filepath) as f:
            data = json.load(f)

        session_data = data["session"]
        decisions_data = data["decisions"]

        # Reconstruct session
        session = ReplaySession(**session_data)
        decisions = [DecisionPoint(**d) for d in decisions_data]

        session_id = session.session_id
        self.active_sessions[session_id] = {
            "session": session,
            "decisions": decisions,
            "current_position": session.current_position,
        }

        logger.info(f"Loaded session {session_id} from {filepath}")
        return session_id

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active replay sessions"""
        sessions_info = []
        for session_id, session_data in self.active_sessions.items():
            session = session_data["session"]
            sessions_info.append(
                {
                    "session_id": session_id,
                    "agent_name": session.agent_name,
                    "decision_count": session.decision_count,
                    "current_position": session.current_position,
                    "breakpoints": len(session.breakpoints),
                    "start_time": session.start_time,
                }
            )
        return sessions_info

    def end_session(self, session_id: str) -> bool:
        """End and cleanup replay session"""
        if session_id in self.active_sessions:
            session_data = self.active_sessions[session_id]
            session_data["session"].end_time = datetime.now(timezone.utc).isoformat()
            del self.active_sessions[session_id]
            logger.info(f"Ended replay session {session_id}")
            return True
        return False


class InteractiveReplayDebugger:
    """Interactive debugging interface for replay sessions"""

    def __init__(self, replay_engine: ReplayEngine):
        self.replay_engine = replay_engine
        self.current_session = None

    def start_debug_session(
        self, agent_name: str, decision_trace: List[Dict[str, Any]]
    ) -> str:
        """Start interactive debugging session"""
        session_id = self.replay_engine.start_replay_session(agent_name, decision_trace)
        self.current_session = session_id

        print(f"🎬 Started debug session for agent '{agent_name}'")
        print(f"📋 Session ID: {session_id}")
        print(f"🎯 Total decisions: {len(decision_trace)}")
        print("\nUse debug commands: step, back, breakpoint, inspect, analyze, help")

        return session_id

    def debug_command(self, command: str, *args) -> Any:
        """Execute debug command"""
        if not self.current_session:
            print("❌ No active debug session. Start one first.")
            return

        try:
            if command == "step":
                steps = int(args[0]) if args else 1
                result = self.replay_engine.step_forward(self.current_session, steps)
                self._display_step_result(result)
                return result

            elif command == "back":
                steps = int(args[0]) if args else 1
                result = self.replay_engine.step_backward(self.current_session, steps)
                self._display_step_result(result)
                return result

            elif command == "breakpoint":
                if args and args[0] == "list":
                    self._list_breakpoints()
                elif args and args[0] == "clear":
                    position = int(args[1]) if len(args) > 1 else None
                    if position is not None:
                        self.replay_engine.remove_breakpoint(
                            self.current_session, position
                        )
                        print(f"🚫 Removed breakpoint at position {position}")
                elif args:
                    position = int(args[0])
                    self.replay_engine.set_breakpoint(self.current_session, position)
                    print(f"🔴 Set breakpoint at position {position}")

            elif command == "inspect":
                position = int(args[0]) if args else None
                context = self.replay_engine.inspect_context(
                    self.current_session, position
                )
                self._display_context(context)
                return context

            elif command == "analyze":
                analysis = self.replay_engine.analyze_session(self.current_session)
                self._display_analysis(analysis)
                return analysis

            elif command == "run":
                result = self.replay_engine.run_to_breakpoint(self.current_session)
                self._display_step_result(result)
                return result

            elif command == "export":
                filepath = args[0] if args else None
                export_path = self.replay_engine.export_session(
                    self.current_session, filepath
                )
                print(f"💾 Session exported to: {export_path}")
                return export_path

            elif command == "help":
                self._show_help()

            else:
                print(f"❌ Unknown command: {command}")
                self._show_help()

        except Exception as e:
            print(f"❌ Command failed: {e}")

    def _display_step_result(self, result: Dict[str, Any]):
        """Display step result"""
        pos = result["position"]
        total = result["total_decisions"]

        print(f"\n📍 Position: {pos + 1}/{total}")

        if "current_decision" in result:
            decision = result["current_decision"]
            print(f"🎯 Decision: {decision['chosen_option']}")
            print(f"💭 Reasoning: {decision['reasoning'][:100]}...")
            print(f"🎲 Confidence: {decision['confidence']:.2f}")

            if result.get("at_breakpoint"):
                print("🔴 Stopped at breakpoint")

        if result.get("status") == "end_of_replay":
            print("🏁 Reached end of replay")

    def _display_context(self, context: Dict[str, Any]):
        """Display context information"""
        print(f"\n🔍 Context at position {context['position'] + 1}")
        print(f"🆔 Decision ID: {context['decision_id']}")
        print(f"⏰ Timestamp: {context['timestamp']}")
        print(f"🎯 Chosen: {context['reasoning']}")
        print(f"🎲 Confidence: {context['confidence']:.2f}")

        if context["available_options"]:
            print(f"⚡ Options: {len(context['available_options'])} available")

        if context["outcome"]:
            print(f"📊 Outcome: {context['outcome']}")

    def _display_analysis(self, analysis: Dict[str, Any]):
        """Display session analysis"""
        print("\n📊 Session Analysis")
        print(f"🎯 Total decisions: {analysis['total_decisions']}")

        if "confidence_stats" in analysis:
            stats = analysis["confidence_stats"]
            print(f"🎲 Avg confidence: {stats.get('average', 0):.2f}")
            print(f"🔴 Low confidence: {stats.get('low_confidence_count', 0)}")
            print(f"🟢 High confidence: {stats.get('high_confidence_count', 0)}")

        if "outcome_analysis" in analysis:
            outcomes = analysis["outcome_analysis"]
            success_rate = outcomes.get("success_rate", 0)
            print(f"✅ Success rate: {success_rate:.1%}")

    def _list_breakpoints(self):
        """List all breakpoints"""
        session_data = self.replay_engine.active_sessions[self.current_session]
        breakpoints = session_data["session"].breakpoints

        if breakpoints:
            print(f"🔴 Active breakpoints: {sorted(breakpoints)}")
        else:
            print("🚫 No breakpoints set")

    def _show_help(self):
        """Show help information"""
        print("\n🆘 Debug Commands:")
        print("  step [n]        - Step forward n positions (default: 1)")
        print("  back [n]        - Step backward n positions (default: 1)")
        print("  breakpoint <pos> - Set breakpoint at position")
        print("  breakpoint list  - List all breakpoints")
        print("  breakpoint clear <pos> - Remove breakpoint")
        print("  inspect [pos]    - Inspect context (default: current)")
        print("  analyze         - Analyze entire session")
        print("  run             - Run to next breakpoint")
        print("  export [file]   - Export session to file")
        print("  help            - Show this help")


if __name__ == "__main__":
    # Demo/test functionality
    sample_decisions = [
        {
            "timestamp": "2025-06-30T10:00:00Z",
            "decision_id": "opt_001",
            "context": {"memory_pressure": "high", "user_request": "optimize"},
            "options": [{"action": "cache_clear"}, {"action": "memory_gc"}],
            "chosen_option": "memory_gc",
            "reasoning": "Memory garbage collection more effective for sustained optimization",
            "confidence": 0.85,
            "outcome": {"status": "success", "memory_freed": "45MB"},
        },
        {
            "timestamp": "2025-06-30T10:05:00Z",
            "decision_id": "opt_002",
            "context": {"memory_pressure": "medium", "performance": "improved"},
            "options": [{"action": "continue"}, {"action": "fine_tune"}],
            "chosen_option": "fine_tune",
            "reasoning": "Opportunity to further optimize while system is stable",
            "confidence": 0.65,
            "outcome": {"status": "success", "performance_gain": "12%"},
        },
    ]

    # Test replay engine
    engine = ReplayEngine()
    session_id = engine.start_replay_session("TestAgent", sample_decisions)

    print(f"✅ Created test session: {session_id}")

    # Test stepping
    result = engine.step_forward(session_id)
    print(f"📍 Stepped to position: {result['position']}")

    # Test analysis
    analysis = engine.analyze_session(session_id)
    print(f"📊 Analysis complete: {analysis['total_decisions']} decisions analyzed")

    # Test interactive debugger
    debugger = InteractiveReplayDebugger(engine)
    print("\n🎬 Testing interactive debugger...")
    debugger.start_debug_session("TestAgent", sample_decisions)

    print("🎯 Use debugger.debug_command('step') to test commands")
