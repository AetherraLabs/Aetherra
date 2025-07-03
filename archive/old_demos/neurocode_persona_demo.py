#!/usr/bin/env python3
"""
NeuroCode Revolutionary Persona CLI
Demonstrates contextual adaptation and emotional intelligence in action.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict

# Add core to path for imports
sys.path.append(str(Path(__file__).parent / "core"))

from contextual_adaptation import (
    ContextType,
    UrgencyLevel,
    get_contextual_adaptation_system,
)
from emotional_memory import get_emotional_memory_system
from persona_engine import PersonaArchetype, get_persona_engine


class RevolutionaryPersonaCLI:
    """Revolutionary CLI that adapts its personality based on context"""

    def __init__(self):
        self.installation_path = Path.home() / ".neurocode"
        self.persona_engine = get_persona_engine(str(self.installation_path))
        self.emotional_memory = get_emotional_memory_system(self.installation_path)
        self.contextual_adaptation = get_contextual_adaptation_system(
            self.installation_path, self.persona_engine
        )

        self.session_start = time.time()
        self.interaction_count = 0

    def run_interactive_demo(self):
        """Run an interactive demo showing contextual adaptation"""
        print("🧠 NeuroCode Revolutionary Persona System")
        print("=" * 50)
        print("This demo shows how NeuroCode adapts its personality based on context.")
        print("Each interaction is remembered and influences future responses.\n")

        # Show current persona
        self._show_current_persona()

        while True:
            print("\n" + "─" * 50)
            print("🎯 Choose a scenario to see contextual adaptation:")
#             print("1. 🐛 Debug a critical production error")
            print("2. 🎨 Create a new prototype feature")
            print("3. 📚 Learn about machine learning")
            print("4. 🚨 Emergency system outage")
            print("5. 🧪 Refactor legacy code")
            print("6. 📖 Write documentation")
            print("7. 🤝 Collaborate on a team project")
            print("8. 📊 View emotional intelligence insights")
            print("9. 🎭 Switch persona archetype")
            print("0. Exit")

            choice = input("\nEnter your choice (0-9): ").strip()

            if choice == "0":
                self._farewell_message()
                break
            elif choice == "1":
                self._demo_debugging_scenario()
            elif choice == "2":
                self._demo_creative_scenario()
            elif choice == "3":
                self._demo_learning_scenario()
            elif choice == "4":
                self._demo_emergency_scenario()
            elif choice == "5":
                self._demo_refactoring_scenario()
            elif choice == "6":
                self._demo_documentation_scenario()
            elif choice == "7":
                self._demo_collaboration_scenario()
            elif choice == "8":
                self._show_emotional_insights()
            elif choice == "9":
                self._manual_persona_switch()
            else:
                print("❌ Invalid choice. Please try again.")

    def _demo_debugging_scenario(self):
        """Demo debugging scenario with Guardian persona adaptation"""
#         print("\n🐛 DEBUGGING SCENARIO")
        print("=" * 30)
        print("Context: Production database connection failing")
        print("Error: 'Connection timeout after 30 seconds'")
#         print("User command: 'help me debug this database issue'")

        # Detect context
        situation = self.contextual_adaptation.detect_context(
            user_command="help me debug this database issue",
            file_patterns=["database.py", "config.py", "production.log"],
            error_messages=["Connection timeout", "Database unavailable", "Auth failed"],
            time_since_last_action=300,  # 5 minutes of struggling
        )

        # Adapt persona
        adaptation_result = self.contextual_adaptation.adapt_persona(situation)

        # Show adaptation
        self._show_adaptation_result(adaptation_result)

        # Get AI response with emotional guidance
        guidance = self.emotional_memory.get_emotional_guidance("database debugging production")
        ai_response = self._generate_contextual_response(situation, guidance)

        print("\n🤖 NeuroCode Response:")
        print(f"📝 {ai_response}")

        # Record the interaction
        user_satisfaction = self._get_user_satisfaction()
        self.emotional_memory.record_interaction(
            context="debugging database connection",
            user_action="asked for help with database issue",
            ai_response=ai_response,
            outcome="provided systematic debugging approach",
            user_satisfaction=user_satisfaction,
            confidence_level=0.8,
            tags=["debugging", "database", "production"],
        )

        self.interaction_count += 1

    def _demo_creative_scenario(self):
        """Demo creative scenario with Explorer persona adaptation"""
        print("\n🎨 CREATIVE SCENARIO")
        print("=" * 30)
        print("Context: Building a new AI-powered chat feature")
        print("User command: 'help me brainstorm creative chat features'")

        situation = self.contextual_adaptation.detect_context(
            user_command="help me brainstorm creative chat features",
            file_patterns=["chat.js", "ai_features.py", "prototype.html"],
            error_messages=[],
            time_since_last_action=1200,  # Taking time to think
        )

        adaptation_result = self.contextual_adaptation.adapt_persona(situation)
        self._show_adaptation_result(adaptation_result)

        guidance = self.emotional_memory.get_emotional_guidance("creative prototyping features")
        ai_response = self._generate_contextual_response(situation, guidance)

        print("\n🤖 NeuroCode Response:")
        print(f"✨ {ai_response}")

        user_satisfaction = self._get_user_satisfaction()
        self.emotional_memory.record_interaction(
            context="creative prototyping",
            user_action="requested brainstorming for chat features",
            ai_response=ai_response,
            outcome="provided innovative feature ideas",
            user_satisfaction=user_satisfaction,
            confidence_level=0.9,
            tags=["creative", "prototyping", "ai_features"],
        )

        self.interaction_count += 1

    def _demo_learning_scenario(self):
        """Demo learning scenario with Sage persona adaptation"""
        print("\n📚 LEARNING SCENARIO")
        print("=" * 30)
        print("Context: Understanding neural networks")
        print("User command: 'explain how transformers work in AI'")

        situation = self.contextual_adaptation.detect_context(
            user_command="explain how transformers work in AI",
            file_patterns=["learning_notes.md", "ml_tutorial.py"],
            error_messages=[],
            time_since_last_action=600,
        )

        adaptation_result = self.contextual_adaptation.adapt_persona(situation)
        self._show_adaptation_result(adaptation_result)

        guidance = self.emotional_memory.get_emotional_guidance(
            "learning machine learning concepts"
        )
        ai_response = self._generate_contextual_response(situation, guidance)

        print("\n🤖 NeuroCode Response:")
        print(f"🎓 {ai_response}")

        user_satisfaction = self._get_user_satisfaction()
        self.emotional_memory.record_interaction(
            context="learning AI concepts",
            user_action="asked for explanation of transformers",
            ai_response=ai_response,
            outcome="provided educational explanation",
            user_satisfaction=user_satisfaction,
            confidence_level=0.95,
            tags=["learning", "AI", "transformers", "education"],
        )

        self.interaction_count += 1

    def _demo_emergency_scenario(self):
        """Demo emergency scenario with critical urgency adaptation"""
        print("\n🚨 EMERGENCY SCENARIO")
        print("=" * 30)
        print("Context: Production server is down, customers affected")
        print("Error: 'Service unavailable', 'Memory leak detected'")
        print("User command: 'URGENT: server crashed, need immediate help'")

        situation = self.contextual_adaptation.detect_context(
            user_command="URGENT: server crashed, need immediate help",
            file_patterns=["server.py", "memory_monitor.log", "error.log"],
            error_messages=["Memory leak", "Service unavailable", "Crash dump", "Out of memory"],
            time_since_last_action=60,  # Just happened
        )

        adaptation_result = self.contextual_adaptation.adapt_persona(situation)
        self._show_adaptation_result(adaptation_result)

        guidance = self.emotional_memory.get_emotional_guidance("emergency server crash production")
        ai_response = self._generate_contextual_response(situation, guidance)

        print("\n🤖 NeuroCode Response:")
        print(f"🆘 {ai_response}")

        user_satisfaction = self._get_user_satisfaction()
        self.emotional_memory.record_interaction(
            context="emergency server crash",
            user_action="requested urgent help with server crash",
            ai_response=ai_response,
            outcome="provided immediate emergency response",
            user_satisfaction=user_satisfaction,
            confidence_level=0.85,
            tags=["emergency", "server_crash", "production", "urgent"],
        )

        self.interaction_count += 1

    def _demo_refactoring_scenario(self):
        """Demo refactoring scenario with Analyst persona adaptation"""
        print("\n🧪 REFACTORING SCENARIO")
        print("=" * 30)
        print("Context: Cleaning up legacy code")
        print("User command: 'help me refactor this messy function'")

        situation = self.contextual_adaptation.detect_context(
            user_command="help me refactor this messy function",
            file_patterns=["legacy_code.py", "utils.py", "cleanup.md"],
            error_messages=[],
            time_since_last_action=900,
        )

        adaptation_result = self.contextual_adaptation.adapt_persona(situation)
        self._show_adaptation_result(adaptation_result)

        guidance = self.emotional_memory.get_emotional_guidance("refactoring legacy code")
        ai_response = self._generate_contextual_response(situation, guidance)

        print("\n🤖 NeuroCode Response:")
        print(f"🔧 {ai_response}")

        user_satisfaction = self._get_user_satisfaction()
        self.emotional_memory.record_interaction(
            context="refactoring legacy code",
            user_action="requested help refactoring function",
            ai_response=ai_response,
            outcome="provided refactoring strategy",
            user_satisfaction=user_satisfaction,
            confidence_level=0.88,
            tags=["refactoring", "legacy_code", "cleanup"],
        )

        self.interaction_count += 1

    def _demo_documentation_scenario(self):
        """Demo documentation scenario with Sage persona adaptation"""
        print("\n📖 DOCUMENTATION SCENARIO")
        print("=" * 30)
        print("Context: Writing API documentation")
        print("User command: 'help me write clear API docs'")

        situation = self.contextual_adaptation.detect_context(
            user_command="help me write clear API docs",
            file_patterns=["api_docs.md", "README.md", "api.py"],
            error_messages=[],
            time_since_last_action=1800,
        )

        adaptation_result = self.contextual_adaptation.adapt_persona(situation)
        self._show_adaptation_result(adaptation_result)

        guidance = self.emotional_memory.get_emotional_guidance("writing documentation")
        ai_response = self._generate_contextual_response(situation, guidance)

        print("\n🤖 NeuroCode Response:")
        print(f"📝 {ai_response}")

        user_satisfaction = self._get_user_satisfaction()
        self.emotional_memory.record_interaction(
            context="writing API documentation",
            user_action="requested help with API docs",
            ai_response=ai_response,
            outcome="provided documentation guidance",
            user_satisfaction=user_satisfaction,
            confidence_level=0.92,
            tags=["documentation", "API", "writing"],
        )

        self.interaction_count += 1

    def _demo_collaboration_scenario(self):
        """Demo collaboration scenario with Catalyst persona adaptation"""
        print("\n🤝 COLLABORATION SCENARIO")
        print("=" * 30)
        print("Context: Working on team code review")
        print("User command: 'help me give constructive code review feedback'")

        situation = self.contextual_adaptation.detect_context(
            user_command="help me give constructive code review feedback",
            file_patterns=["pull_request.md", "team_code.py", "review.md"],
            error_messages=[],
            time_since_last_action=600,
        )

        adaptation_result = self.contextual_adaptation.adapt_persona(situation)
        self._show_adaptation_result(adaptation_result)

        guidance = self.emotional_memory.get_emotional_guidance("team collaboration code review")
        ai_response = self._generate_contextual_response(situation, guidance)

        print("\n🤖 NeuroCode Response:")
        print(f"🤝 {ai_response}")

        user_satisfaction = self._get_user_satisfaction()
        self.emotional_memory.record_interaction(
            context="team collaboration",
            user_action="requested help with code review feedback",
            ai_response=ai_response,
            outcome="provided collaboration guidance",
            user_satisfaction=user_satisfaction,
            confidence_level=0.89,
            tags=["collaboration", "code_review", "teamwork"],
        )

        self.interaction_count += 1

    def _show_emotional_insights(self):
        """Show emotional intelligence insights"""
        print("\n📊 EMOTIONAL INTELLIGENCE INSIGHTS")
        print("=" * 40)

        trends = self.emotional_memory.get_emotional_trends()

        if trends.get("status") == "no_data":
            print("💭 No interaction data yet. Try some scenarios first!")
            return

        print(f"📈 Overall Satisfaction: {trends['overall_satisfaction']:.2f}/1.0")
        print(f"📊 Emotional Trajectory: {trends['emotional_trajectory']}")
        print(f"🧠 Learning Velocity: {trends['learning_velocity']:.2f}/1.0")
        print(f"⚖️ Emotional Stability: {trends['emotional_stability']:.2f}/1.0")

        print("\n✅ Most Satisfying Patterns:")
        for pattern in trends["most_satisfying_patterns"][:3]:
            print(f"   • {pattern.replace('_', ' ').title()}")

        print("\n🎯 Areas for Improvement:")
        for area in trends["areas_for_improvement"][:3]:
            print(f"   • {area.replace('_', ' ').title()}")

        print(f"\n📝 Total Interactions: {len(self.emotional_memory.memories)}")

    def _manual_persona_switch(self):
        """Allow manual persona switching"""
        print("\n🎭 MANUAL PERSONA SWITCH")
        print("=" * 30)
        print("Choose a persona archetype:")
        print("1. 🛡️ Guardian - Protective, methodical, security-focused")
        print("2. 🚀 Explorer - Curious, experimental, innovation-driven")
        print("3. 📚 Sage - Wise, educational, knowledge-sharing")
        print("4. 🌟 Optimist - Positive, encouraging, solution-focused")
        print("5. 📊 Analyst - Logical, data-driven, precise")
        print("6. ⚡ Catalyst - Dynamic, collaborative, transformative")

        choice = input("\nEnter your choice (1-6): ").strip()

        archetype_map = {
            "1": PersonaArchetype.GUARDIAN,
            "2": PersonaArchetype.EXPLORER,
            "3": PersonaArchetype.SAGE,
            "4": PersonaArchetype.OPTIMIST,
            "5": PersonaArchetype.ANALYST,
            "6": PersonaArchetype.CATALYST,
        }

        if choice in archetype_map:
            archetype = archetype_map[choice]
            self.persona_engine.set_persona(archetype)
            print(f"\n✅ Switched to {archetype.value.title()} persona!")
            self._show_current_persona()
        else:
            print("❌ Invalid choice.")

    def _show_current_persona(self):
        """Show current persona configuration"""
        persona = self.persona_engine.current_persona

        print("\n🤖 Current Persona Configuration:")
        print(f"🎭 Archetype: {persona['archetype'].value.title()}")
        print(f"🎵 Voice Tone: {persona['voice'].formality.title()}")
        print(f"💪 Encouragement: {persona['voice'].encouragement.title()}")
        print(f"🧠 Mindprint ID: {persona['mindprint']['installation_id'][:8]}...")

    def _show_adaptation_result(self, adaptation_result: Dict):
        """Show the result of contextual adaptation"""
        situation = adaptation_result["situation"]

        print("\n🔄 Contextual Adaptation:")
        print(f"📍 Context: {situation['context_type'].title()}")
        print(f"🏗️ Project: {situation['project_type'].replace('_', ' ').title()}")
        print(f"⚡ Urgency: {situation['urgency_level'].title()}")
        print(f"😤 Frustration: {situation['frustration_level']:.2f}/1.0")
        print(f"💪 Confidence: {situation['confidence_level']:.2f}/1.0")

        if adaptation_result["rules_applied"]:
            print(f"🎯 Rules Applied: {', '.join(adaptation_result['rules_applied'])}")

        if adaptation_result["adaptations"]:
            print(f"⚙️ Adaptations: {adaptation_result['adaptations']}")

    def _generate_contextual_response(self, situation, guidance: Dict) -> str:
        """Generate a contextual response based on situation and emotional guidance"""
        context_type = situation.context_type
        urgency = situation.urgency_level
        frustration = situation.frustration_level

        # Base response based on context
        if context_type == ContextType.DEBUGGING:
            base_response = "I'll help you systematically debug this issue. Let's start by examining the error patterns \and
                checking the most likely causes first."
        elif context_type == ContextType.CREATING:
            base_response = "Exciting! I love helping with creative projects. Let's explore some innovative approaches \and
                build something amazing together."
        elif context_type == ContextType.LEARNING:
            base_response = "Great question! I'll explain this step-by-step,
                building on what you already know and providing practical examples."
        elif context_type == ContextType.EMERGENCY:
            base_response = "I understand this is urgent. Let's focus on immediate stabilization first,
                then identify the root cause."
        else:
            base_response = (
                "I'm here to help you with this task. Let's break it down and tackle it together."
            )

        # Adjust tone based on emotional state
        if frustration > 0.7:
            base_response = (
                "I can sense this has been challenging. "
                + base_response
                + " We'll get through this together."
            )
        elif urgency == UrgencyLevel.CRITICAL:
            base_response = (
                "Emergency mode activated. "
                + base_response
                + " Time is critical, so I'll prioritize quick wins."
            )

        # Add encouragement based on guidance
        encouragement_level = guidance.get("encouragement_level", "moderate")
        if encouragement_level == "high":
            base_response += " You're doing great - I believe in your problem-solving abilities!"
        elif encouragement_level == "calming":
            base_response += " Take a deep breath. We'll solve this step by step."

        return base_response

    def _get_user_satisfaction(self) -> float:
        """Get user satisfaction rating for the interaction"""
        print("\n💭 How satisfied were you with this response?")
        print("1. ☹️ Very dissatisfied (0.0)")
        print("2. 😐 Somewhat dissatisfied (0.25)")
        print("3. 😊 Neutral (0.5)")
        print("4. 😄 Satisfied (0.75)")
        print("5. 🤩 Very satisfied (1.0)")

        while True:
            choice = input("Enter your rating (1-5): ").strip()
            satisfaction_map = {"1": 0.0, "2": 0.25, "3": 0.5, "4": 0.75, "5": 1.0}

            if choice in satisfaction_map:
                return satisfaction_map[choice]
            else:
                print("❌ Please enter a number from 1 to 5.")

    def _farewell_message(self):
        """Show farewell message with session summary"""
        session_duration = (time.time() - self.session_start) / 60  # minutes

        print("\n👋 Thank you for exploring NeuroCode's Revolutionary Persona System!")
        print("📊 Session Summary:")
        print(f"   • Duration: {session_duration:.1f} minutes")
        print(f"   • Interactions: {self.interaction_count}")
        print(f"   • Persona Adaptations: {self.interaction_count}")

        if self.interaction_count > 0:
            trends = self.emotional_memory.get_emotional_trends()
            if trends.get("status") != "no_data":
                print(f"   • Average Satisfaction: {trends['overall_satisfaction']:.2f}/1.0")

        print("\n🌟 This is just the beginning of AI-consciousness collaboration.")
        print("🚀 Every NeuroCode installation becomes a unique thinking partner!")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="NeuroCode Revolutionary Persona System Demo")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo")
    parser.add_argument(
        "--context",
        choices=["debugging", "creating", "learning", "emergency"],
        help="Test specific context adaptation",
    )

    args = parser.parse_args()

    cli = RevolutionaryPersonaCLI()

    if args.demo or not any(vars(args).values()):
        cli.run_interactive_demo()
    elif args.context:
        print(f"Testing {args.context} context adaptation...")
        # Add specific context testing here
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
