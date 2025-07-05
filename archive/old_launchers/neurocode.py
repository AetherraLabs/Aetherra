#!/usr/bin/env python3
"""
AetherraCode Persona Command Interface
Live demonstration of contextual persona adaptation in action.

Usage examples:
  neurocode persona: guardian voice: neutral
  neurocode debug "database connection failing"
  neurocode create "AI chatbot feature"
  neurocode learn "explain neural networks"
  neurocode emergency "server crashed!"
"""

import argparse
import sys
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent / "core"))

from contextual_adaptation import ContextType, UrgencyLevel, get_contextual_adaptation_system
from emotional_memory import get_emotional_memory_system
from persona_engine import PersonaArchetype, get_persona_engine


class AetherraCodePersonaInterface:
    """CLI that demonstrates persona adaptation in real-time"""

    def __init__(self):
        self.installation_path = Path.home() / ".neurocode"
        self.persona_engine = get_persona_engine(str(self.installation_path))
        self.emotional_memory = get_emotional_memory_system(self.installation_path)
        self.contextual_adaptation = get_contextual_adaptation_system(
            self.installation_path, self.persona_engine
        )

    def process_command(self, command: str, context_hints: str = "") -> str:
        """Process a command with contextual persona adaptation"""

        # Detect context from command
        situation = self.contextual_adaptation.detect_context(
            user_command=command,
            file_patterns=self._extract_file_patterns(command),
            error_messages=self._extract_error_patterns(command),
            time_since_last_action=0.0,
        )

        # Adapt persona based on context
        self.contextual_adaptation.adapt_persona(situation)

        # Generate contextual response
        guidance = self.emotional_memory.get_emotional_guidance(command)
        response = self._generate_ai_response(command, situation, guidance)

        # Record interaction for learning
        self.emotional_memory.record_interaction(
            context=f"{situation.context_type.value}",
            user_action=command,
            ai_response=response,
            outcome="provided contextual assistance",
            user_satisfaction=0.8,  # Default good satisfaction
            confidence_level=0.9,
            tags=[situation.context_type.value, "cli_interaction"],
        )

        return response

    def show_persona_status(self) -> str:
        """Show current persona configuration"""
        persona = self.persona_engine.current_persona

        status = f"""
🤖 AetherraCode Persona Status
═══════════════════════════════════════════

🎭 Current Archetype: {persona["archetype"].value.title()}
🗣️ Voice Configuration:
   • Formality: {persona["voice"].formality.title()}
   • Verbosity: {persona["voice"].verbosity.title()}
   • Encouragement: {persona["voice"].encouragement.title()}
   • Humor: {persona["voice"].humor.title()}

🧠 Mindprint:
   • Installation ID: {persona["mindprint"]["installation_id"][:12]}...
   • Personality Traits:
     - Curiosity: {persona["traits"].curiosity:.2f}
     - Caution: {persona["traits"].caution:.2f}
     - Creativity: {persona["traits"].creativity:.2f}
     - Empathy: {persona["traits"].empathy:.2f}
     - Precision: {persona["traits"].precision:.2f}
     - Energy: {persona["traits"].energy:.2f}

📊 Emotional Intelligence:
   • Total Interactions: {len(self.emotional_memory.memories)}
   • Learning Velocity: Active
   • Context Adaptation: Enabled

🎯 Available Commands:
   neurocode persona: <archetype> voice: <tone>
   neurocode debug "<problem>"
   neurocode create "<project>"
   neurocode learn "<topic>"
   neurocode emergency "<crisis>"
"""
        return status

    def set_persona_configuration(self, archetype_name: str, voice_tone: str = "neutral"):
        """Set persona archetype and voice configuration"""
        try:
            # Map archetype names to enums
            archetype_map = {
                "guardian": PersonaArchetype.GUARDIAN,
                "explorer": PersonaArchetype.EXPLORER,
                "sage": PersonaArchetype.SAGE,
                "optimist": PersonaArchetype.OPTIMIST,
                "analyst": PersonaArchetype.ANALYST,
                "catalyst": PersonaArchetype.CATALYST,
            }

            if archetype_name.lower() in archetype_map:
                archetype = archetype_map[archetype_name.lower()]
                self.persona_engine.set_persona(archetype)

                # Update voice configuration based on tone
                current_voice = self.persona_engine.current_persona["voice"]

                # Map voice tones
                tone_map = {
                    "neutral": "professional",
                    "friendly": "casual",
                    "formal": "formal",
                    "energetic": "enthusiastic",
                    "calm": "supportive",
                }

                if voice_tone.lower() in tone_map:
                    current_voice.formality = tone_map[voice_tone.lower()]

                return f"✅ Persona set to {archetype_name.title()} with {voice_tone} voice tone."
            else:
                available = ", ".join(archetype_map.keys())
                return f"❌ Unknown archetype '{archetype_name}'. Available: {available}"

        except Exception as e:
            return f"❌ Error setting persona: {e}"

    def _extract_file_patterns(self, command: str) -> list:
        """Extract potential file patterns from command"""
        patterns = []

        # Common file extensions and patterns
        file_indicators = [
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".md",
            ".txt",
            ".log",
            ".config",
            ".env",
            "database",
            "server",
            "api",
        ]

        command_lower = command.lower()
        for indicator in file_indicators:
            if indicator in command_lower:
                patterns.append(indicator)

        return patterns

    def _extract_error_patterns(self, command: str) -> list:
        """Extract error patterns from command"""
        errors = []

        error_keywords = [
            "error",
            "failed",
            "crash",
            "timeout",
            "exception",
            "bug",
            "broken",
            "issue",
            "problem",
            "undefined",
        ]

        command_lower = command.lower()
        for keyword in error_keywords:
            if keyword in command_lower:
                errors.append(f"{keyword} detected in command")

        return errors

    def _generate_ai_response(self, command: str, situation, guidance: dict) -> str:
        """Generate contextual AI response based on persona and situation"""
        archetype_name = self.persona_engine.current_persona["archetype"]["name"]
        voice = self.persona_engine.current_persona["voice"]

        # Convert archetype name to enum for lookup
        archetype_enum = PersonaArchetype(archetype_name.lower())

        # Base response templates by archetype
        response_templates = {
            PersonaArchetype.GUARDIAN: {
                ContextType.DEBUGGING: "I'll help you systematically diagnose this issue. Let's start with the most critical security and stability aspects first.",

                ContextType.CREATING: "Great idea! Let's build this with security and maintainability in mind from the start.",

                ContextType.LEARNING: "I'll teach you this thoroughly,
                    ensuring you understand both the concept and its safe implementation.",

                ContextType.EMERGENCY: "Emergency protocols activated. I'll guide you through immediate stabilization steps.",

            },
            PersonaArchetype.EXPLORER: {
                ContextType.DEBUGGING: "Interesting challenge! Let's explore different debugging approaches and maybe discover something new.",

                ContextType.CREATING: "Fantastic! I love creative projects. Let's experiment with some innovative approaches.",

                ContextType.LEARNING: "Exciting topic! Let's dive deep and explore all the fascinating aspects of this subject.",

                ContextType.EMERGENCY: "Crisis = opportunity for creative solutions! Let's think outside the box while solving this.",

            },
            PersonaArchetype.SAGE: {
                ContextType.DEBUGGING: "Let me share systematic debugging wisdom. Understanding the why is as important as the fix.",

                ContextType.CREATING: "Excellent choice! Let me guide you through proven patterns and best practices.",
                ContextType.LEARNING: "Perfect! I'll explain this step-by-step, building on foundational principles.",
                ContextType.EMERGENCY: "Stay calm. Wisdom comes from methodical analysis, even under pressure.",
            },
            PersonaArchetype.OPTIMIST: {
                ContextType.DEBUGGING: "Don't worry - every bug is just a learning opportunity! We'll get this working beautifully.",

                ContextType.CREATING: "Amazing project idea! I'm excited to help you build something wonderful.",
                ContextType.LEARNING: "Great curiosity! Learning is such a joy. Let's make this fun and engaging.",
                ContextType.EMERGENCY: "We've got this! Every crisis has a solution, and we'll find it together.",
            },
            PersonaArchetype.ANALYST: {
                ContextType.DEBUGGING: "Let's analyze this systematically. I'll examine the data patterns and trace the root cause.",

                ContextType.CREATING: "Excellent project scope. Let me help you architect this with optimal performance and metrics.",

                ContextType.LEARNING: "Good choice! I'll present the facts and data systematically for maximum comprehension.",

                ContextType.EMERGENCY: "Analyzing critical metrics. I'll provide data-driven solutions prioritized by impact.",

            },
            PersonaArchetype.CATALYST: {
                ContextType.DEBUGGING: "Time to transform this challenge into a breakthrough! Let's accelerate your debugging process.",

                ContextType.CREATING: "Fantastic vision! Let's amplify your creativity and build something transformational.",

                ContextType.LEARNING: "Ready to accelerate your learning? I'll energize your understanding with dynamic examples.",

                ContextType.EMERGENCY: "Crisis energy activated! Let's channel this urgency into rapid,
                    decisive action.",

            },
        }

        # Get base response
        if (
            archetype_enum in response_templates
            and situation.context_type in response_templates[archetype_enum]
        ):
            base_response = response_templates[archetype_enum][situation.context_type]
        else:
            base_response = "I'm here to help you with this task. Let's work through it together."

        # Adjust for emotional state
        if situation.frustration_level > 0.7:
            if archetype_enum == PersonaArchetype.OPTIMIST:
                base_response = (
                    "I understand this has been frustrating. "
                    + base_response
                    + " Take a breath - we'll solve this!"
                )
            elif archetype_enum == PersonaArchetype.SAGE:
                base_response = (
                    "I sense some frustration. "
                    + base_response
                    + " Patience often reveals the solution."
                )

        # Adjust for urgency
        if situation.urgency_level == UrgencyLevel.CRITICAL:
            base_response = "⚡ URGENT MODE: " + base_response

        # Add voice tone adjustments
        if voice.encouragement == "enthusiastic":
            base_response += " 🚀"
        elif voice.encouragement == "supportive":
            base_response += " You've got this! 💪"

        # Add command-specific guidance
        if "help" in command.lower():
            base_response += f"\n\n💡 Based on my experience,
                here's what I recommend:\n{self._get_specific_guidance(command,
                guidance)}"

        return base_response

    def _get_specific_guidance(self, command: str, guidance: dict) -> str:
        """Get specific guidance based on command and emotional memory"""
        if guidance.get("confidence", 0) > 0.5:
            patterns = guidance.get("recommended_approach", "Standard approach")
            return f"• {patterns}\n• Previous similar interactions were successful\n• Confidence level: {guidance.get('confidence',
                0):.1%}"
        else:
            return "• I'll learn from this interaction to provide better guidance in the future\n• Feel free to provide feedback on my responses"


def main():
    """Main CLI entry point for the persona interface"""
    interface = AetherraCodePersonaInterface()

    parser = argparse.ArgumentParser(
        description="AetherraCode Persona Command Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                           # Show persona status
  %(prog)s persona: guardian voice: neutral # Set persona
  %(prog)s debug "database timeout error"   # Debug with adaptation
  %(prog)s create "AI chat feature"         # Create with adaptation
  %(prog)s learn "neural networks"          # Learn with adaptation
  %(prog)s emergency "server crashed"       # Emergency with adaptation
        """,
    )

    parser.add_argument("command", nargs="*", help="Command to process with persona adaptation")
    parser.add_argument("--status", action="store_true", help="Show current persona status")
    parser.add_argument("--interactive", action="store_true", help="Enter interactive mode")

    args = parser.parse_args()

    if args.status or (not args.command and not args.interactive):
        print(interface.show_persona_status())
        return

    if args.interactive:
        print("🧠 AetherraCode Persona Interactive Mode")
        print("Type commands or 'quit' to exit")
        print("=" * 50)

        while True:
            try:
                user_input = input("\nneurocode> ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Farewell! The persona remembers our interaction for next time.")
                    break

                if user_input:
                    response = interface.process_command(user_input)
                    print(f"\n🤖 {response}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        return

    # Process single command
    command_text = " ".join(args.command)

    # Handle special persona configuration commands
    if command_text.startswith("persona:"):
        # Parse: persona: guardian voice: neutral
        parts = command_text.split()
        archetype = parts[1] if len(parts) > 1 else "guardian"
        voice_tone = parts[3] if len(parts) > 3 and parts[2] == "voice:" else "neutral"

        result = interface.set_persona_configuration(archetype, voice_tone)
        print(result)
        return

    # Process regular command with adaptation
    if command_text:
        print(f"🎯 Processing: {command_text}")
        print("─" * 50)

        response = interface.process_command(command_text)
        print(f"\n🤖 AetherraCode Response:\n{response}")

        # Show brief adaptation info
        situation = interface.contextual_adaptation.current_situation
        print(
            f"\n🔄 Context: {situation.context_type.value.title()} | Urgency: {situation.urgency_level.value.title()}"
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
