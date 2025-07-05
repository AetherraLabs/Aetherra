#!/usr/bin/env python3
"""
🤖 AetherraCode Agent Reflection Loop
===================================

Autonomous agent system that:
- Continuously evaluates memory patterns
- Generates insights from stored experiences
- Suggests and executes AetherraCode based on analysis
- Learns and adapts behavior over time

This completes the AI-native vision where AetherraCode becomes truly self-aware
and can autonomously improve itself through reflection.
"""

import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Add core modules to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Import AetherraCode components
try:
    from memory import AetherraMemory

    from scripts.neuro_runner_standalone import StandaloneNeuroRunner
except ImportError as e:
    print(f"⚠️ Some components not available: {e}")


class AgentReflectionLoop:
    """Autonomous agent that reflects on memory and suggests actions"""

    def __init__(self, memory_instance: Optional[AetherraMemory] = None):
        self.memory = memory_instance or AetherraMemory()
        self.runner = StandaloneNeuroRunner(verbose=False)
        self.is_running = False
        self.reflection_thread = None

        # Agent configuration
        self.config = {
            "reflection_interval": 30,  # seconds
            "max_suggestions_per_cycle": 3,
            "confidence_threshold": 0.7,
            "auto_execute_threshold": 0.9,
            "learning_rate": 0.1,
        }

        # State tracking
        self.reflection_count = 0
        self.suggestions_made = 0
        self.actions_taken = 0
        self.insights_generated = []
        self.last_reflection = None

        # Callback for UI integration
        self.on_insight_callback: Optional[Callable[[Dict], None]] = None
        self.on_suggestion_callback: Optional[Callable[[str, float], None]] = None
        self.on_action_callback: Optional[Callable[[str, bool], None]] = None

        print("🤖 Agent Reflection Loop initialized")

    def start(self):
        """Start the autonomous reflection loop"""
        if self.is_running:
            print("⚠️ Agent already running")
            return

        self.is_running = True
        self.reflection_thread = threading.Thread(target=self._reflection_loop, daemon=True)
        self.reflection_thread.start()

        print("🚀 Agent Reflection Loop started")
        print(f"   📊 Reflection interval: {self.config['reflection_interval']}s")
        print(f"   🎯 Confidence threshold: {self.config['confidence_threshold']}")

    def stop(self):
        """Stop the reflection loop"""
        self.is_running = False
        if self.reflection_thread:
            self.reflection_thread.join(timeout=2)

        print("🛑 Agent Reflection Loop stopped")

    def _reflection_loop(self):
        """Main reflection loop that runs autonomously"""
        while self.is_running:
            try:
                self._perform_reflection_cycle()
                time.sleep(self.config["reflection_interval"])
            except Exception as e:
                print(f"❌ Reflection loop error: {e}")
                time.sleep(5)  # Brief pause on error

    def _perform_reflection_cycle(self):
        """Perform one complete reflection cycle"""
        self.reflection_count += 1
        self.last_reflection = datetime.now()

        print(f"\n🔄 Reflection Cycle #{self.reflection_count}")
        print("=" * 40)

        # 1. Analyze current memory state
        insights = self._analyze_memory_patterns()

        # 2. Generate suggestions based on insights
        suggestions = self._generate_suggestions(insights)

        # 3. Evaluate and potentially execute suggestions
        for suggestion in suggestions:
            self._evaluate_suggestion(suggestion)

        # 4. Update agent knowledge
        self._update_agent_knowledge(insights, suggestions)

        print(f"📊 Cycle complete - {len(insights)} insights, {len(suggestions)} suggestions")

    def _analyze_memory_patterns(self) -> List[Dict[str, Any]]:
        """Analyze memory to find patterns and generate insights"""
        insights = []

        try:
            # Get memory statistics
            total_memories = len(self.memory.memory)

            if total_memories == 0:
                return [
                    {
                        "type": "initialization",
                        "message": "No memories found - agent needs initial learning",
                        "confidence": 0.9,
                        "suggested_action": "recommend_initial_learning",
                    }
                ]

            # Analyze tag patterns
            tag_analysis = self._analyze_tag_patterns()
            if tag_analysis:
                insights.append(tag_analysis)

            # Analyze temporal patterns
            temporal_analysis = self._analyze_temporal_patterns()
            if temporal_analysis:
                insights.append(temporal_analysis)

            # Analyze content patterns
            content_analysis = self._analyze_content_patterns()
            if content_analysis:
                insights.append(content_analysis)

            # Check for knowledge gaps
            gaps = self._identify_knowledge_gaps()
            insights.extend(gaps)

        except Exception as e:
            print(f"⚠️ Pattern analysis error: {e}")

        self.insights_generated.extend(insights)

        # Notify UI if callback is set
        for insight in insights:
            if self.on_insight_callback:
                self.on_insight_callback(insight)

        return insights

    def _analyze_tag_patterns(self) -> Optional[Dict[str, Any]]:
        """Analyze tag frequency and relationships"""
        tag_freq = {}
        tag_co_occurrence = {}

        for memory in self.memory.memory:
            tags = memory.get("tags", [])

            # Count tag frequency
            for tag in tags:
                tag_freq[tag] = tag_freq.get(tag, 0) + 1

            # Track tag co-occurrence
            for i, tag1 in enumerate(tags):
                for tag2 in tags[i + 1 :]:
                    pair = tuple(sorted([tag1, tag2]))
                    tag_co_occurrence[pair] = tag_co_occurrence.get(pair, 0) + 1

        # Find dominant patterns
        if tag_freq:
            most_common = max(tag_freq.items(), key=lambda x: x[1])

            if most_common[1] >= 3:  # Threshold for pattern significance
                return {
                    "type": "tag_pattern",
                    "message": f'Strong focus on "{most_common[0]}" domain ({most_common[1]} memories)',
                    "confidence": min(0.9, most_common[1] * 0.1),
                    "data": {"dominant_tag": most_common[0], "frequency": most_common[1]},
                    "suggested_action": "expand_domain_knowledge",
                }

        return None

    def _analyze_temporal_patterns(self) -> Optional[Dict[str, Any]]:
        """Analyze when memories are created to find behavioral patterns"""
        if len(self.memory.memory) < 5:
            return None

        recent_memories = 0

        for memory in self.memory.memory:
            try:
                timestamp = memory.get("timestamp", "")
                if timestamp:
                    # Simple check for recent activity
                    recent_memories += 1
            except (KeyError, ValueError, TypeError):
                # Skip malformed memory entries
                continue

        if recent_memories > 10:  # High activity threshold
            return {
                "type": "temporal_pattern",
                "message": f"High learning activity detected ({recent_memories} recent memories)",
                "confidence": 0.8,
                "data": {"recent_count": recent_memories},
                "suggested_action": "consolidate_learning",
            }

        return None

    def _analyze_content_patterns(self) -> Optional[Dict[str, Any]]:
        """Analyze memory content for semantic patterns"""
        content_words = {}

        for memory in self.memory.memory:
            text = memory.get("text", "").lower()
            words = text.split()

            for word in words:
                if len(word) > 3:  # Skip short words
                    content_words[word] = content_words.get(word, 0) + 1

        if content_words:
            common_word = max(content_words.items(), key=lambda x: x[1])

            if common_word[1] >= 3:
                return {
                    "type": "content_pattern",
                    "message": f'Recurring concept: "{common_word[0]}" appears frequently',
                    "confidence": 0.7,
                    "data": {"concept": common_word[0], "frequency": common_word[1]},
                    "suggested_action": "deepen_concept_understanding",
                }

        return None

    def _identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Identify potential knowledge gaps that need attention"""
        gaps = []

        # Check for missing fundamental domains
        fundamental_domains = ["best_practice", "performance", "security", "architecture"]
        existing_tags = set()

        for memory in self.memory.memory:
            existing_tags.update(memory.get("tags", []))

        missing_domains = [domain for domain in fundamental_domains if domain not in existing_tags]

        for domain in missing_domains[:2]:  # Limit to top 2 gaps
            gaps.append(
                {
                    "type": "knowledge_gap",
                    "message": f'Missing knowledge in "{domain}" domain',
                    "confidence": 0.6,
                    "data": {"missing_domain": domain},
                    "suggested_action": "learn_domain_basics",
                }
            )

        return gaps

    def _generate_suggestions(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable AetherraCode suggestions based on insights"""
        suggestions = []

        for insight in insights[: self.config["max_suggestions_per_cycle"]]:
            suggestion = self._create_suggestion_from_insight(insight)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def _create_suggestion_from_insight(self, insight: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a specific AetherraCode suggestion from an insight"""
        action = insight.get("suggested_action")
        confidence = insight.get("confidence", 0.5)

        if action == "recommend_initial_learning":
            return {
                "type": "aethercode_generation",
                "neurocode": """# Agent-suggested initial learning
remember("AetherraCode enables AI-native programming") as "programming_paradigm"
remember("Memory systems track learning patterns") as "memory_system"
remember("Agents can reflect on their own knowledge") as "meta_learning"
goal: establish foundational knowledge priority: high""",
                "confidence": confidence,
                "rationale": "Building foundational knowledge base",
            }

        elif action == "expand_domain_knowledge":
            domain = insight.get("data", {}).get("dominant_tag", "general")
            return {
                "type": "aethercode_generation",
                "neurocode": f'''# Agent-suggested domain expansion for {domain}
reflect on tags="{domain}"
analyze patterns in "{domain}"
goal: deepen {domain} understanding priority: medium
remember("Domain analysis completed for {domain}") as "{domain},analysis"''',
                "confidence": confidence,
                "rationale": f"Expanding knowledge in {domain} domain",
            }

        elif action == "consolidate_learning":
            return {
                "type": "aethercode_generation",
                "neurocode": """# Agent-suggested learning consolidation
memory summary
detect patterns
reflect on tags="learning"
remember("Learning consolidation cycle completed") as "meta_learning,consolidation"
goal: organize and synthesize knowledge priority: medium""",
                "confidence": confidence,
                "rationale": "Consolidating recent learning activity",
            }

        elif action == "learn_domain_basics":
            domain = insight.get("data", {}).get("missing_domain", "general")
            return {
                "type": "aethercode_generation",
                "neurocode": f'''# Agent-suggested domain learning for {domain}
remember("Learning {domain} fundamentals") as "{domain},learning"
goal: acquire {domain} knowledge priority: high
remember("Basic {domain} concepts established") as "{domain},foundation"''',
                "confidence": confidence,
                "rationale": f"Learning fundamentals of {domain}",
            }

        return None

    def _evaluate_suggestion(self, suggestion: Dict[str, Any]):
        """Evaluate and potentially execute a suggestion"""
        confidence = suggestion.get("confidence", 0)
        neurocode = suggestion.get("neurocode", "")
        rationale = suggestion.get("rationale", "Unknown reason")

        print(f"\n💡 Suggestion (confidence: {confidence:.1f}): {rationale}")

        # Notify UI
        if self.on_suggestion_callback:
            self.on_suggestion_callback(neurocode, confidence)

        self.suggestions_made += 1

        # Auto-execute high-confidence suggestions
        if confidence >= self.config["auto_execute_threshold"]:
            success = self._execute_neurocode(neurocode)
            self.actions_taken += 1

            print(f"🤖 Auto-executed: {'✅ Success' if success else '❌ Failed'}")

            # Notify UI
            if self.on_action_callback:
                self.on_action_callback(neurocode, success)

        elif confidence >= self.config["confidence_threshold"]:
            print(f"🤔 Suggestion ready for user approval (confidence: {confidence:.1f})")
        else:
            print("💭 Low confidence suggestion logged for future consideration")

    def _execute_neurocode(self, neurocode: str) -> bool:
        """Execute AetherraCode and return success status"""
        try:
            # Create temporary file
            temp_file = project_root / "temp_agent_suggestion.neuro"
            temp_file.write_text(neurocode, encoding="utf-8")

            # Execute using the standalone runner
            results = self.runner.run_file(str(temp_file))

            # Clean up
            if temp_file.exists():
                temp_file.unlink()

            return results.get("success", False)
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return False

    def _update_agent_knowledge(self, insights: List[Dict], suggestions: List[Dict]):
        """Update agent's self-knowledge based on reflection cycle"""
        # Calculate cycle statistics for potential future use
        cycle_stats = {
            "timestamp": datetime.now().isoformat(),
            "cycle_number": self.reflection_count,
            "insights_count": len(insights),
            "suggestions_count": len(suggestions),
            "confidence_avg": sum(s.get("confidence", 0) for s in suggestions)
            / max(len(suggestions), 1),
        }

        # Store reflection results in memory
        if self.memory:
            try:
                summary_text = f"Reflection cycle #{self.reflection_count}: {len(insights)} insights,
                    {len(suggestions)} suggestions (avg confidence: {cycle_stats['confidence_avg']:.2f})"
                self.memory.remember(
                    summary_text,
                    ["agent_reflection", "meta_learning"],
                )
            except Exception as e:
                print(f"⚠️ Failed to store reflection in memory: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status for UI display"""
        return {
            "is_running": self.is_running,
            "reflection_count": self.reflection_count,
            "suggestions_made": self.suggestions_made,
            "actions_taken": self.actions_taken,
            "last_reflection": self.last_reflection.isoformat() if self.last_reflection else None,
            "config": self.config.copy(),
            "recent_insights": self.insights_generated[-5:] if self.insights_generated else [],
        }

    def update_config(self, new_config: Dict[str, Any]):
        """Update agent configuration"""
        self.config.update(new_config)
        print(f"🔧 Agent configuration updated: {new_config}")

    def set_ui_callbacks(
        self,
        on_insight: Optional[Callable] = None,
        on_suggestion: Optional[Callable] = None,
        on_action: Optional[Callable] = None,
    ):
        """Set callbacks for UI integration"""
        self.on_insight_callback = on_insight
        self.on_suggestion_callback = on_suggestion
        self.on_action_callback = on_action
        print("🔗 UI callbacks configured")


def main():
    """Standalone agent runner for testing"""
    print("🤖 AetherraCode Agent Reflection Loop - Standalone Mode")
    print("=" * 50)

    # Create agent
    agent = AgentReflectionLoop()

    try:
        # Start the agent
        agent.start()

        print("\n🎮 Agent is running! Commands:")
        print("  'status' - Show agent status")
        print("  'stop' - Stop the agent")
        print("  'config' - Show configuration")
        print("  'exit' - Exit program")

        # Simple command interface
        while agent.is_running:
            try:
                cmd = input("\nAgent> ").strip().lower()

                if cmd == "status":
                    status = agent.get_status()
                    print("\n📊 Agent Status:")
                    print(f"   Running: {status['is_running']}")
                    print(f"   Reflections: {status['reflection_count']}")
                    print(f"   Suggestions: {status['suggestions_made']}")
                    print(f"   Actions: {status['actions_taken']}")
                    print(f"   Last reflection: {status['last_reflection']}")

                elif cmd == "config":
                    print("\n⚙️ Configuration:")
                    for key, value in agent.config.items():
                        print(f"   {key}: {value}")

                elif cmd == "stop":
                    agent.stop()
                    break

                elif cmd in ["exit", "quit"]:
                    agent.stop()
                    break

                else:
                    print("❓ Unknown command")

            except KeyboardInterrupt:
                print("\n🛑 Stopping agent...")
                agent.stop()
                break
            except EOFError:
                agent.stop()
                break

    except Exception as e:
        print(f"❌ Agent error: {e}")
        agent.stop()

    print("🏁 Agent Reflection Loop terminated")


if __name__ == "__main__":
    main()
