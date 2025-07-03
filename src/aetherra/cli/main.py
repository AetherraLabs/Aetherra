#!/usr/bin/env python3
"""
NeuroCode Persona Command Interface
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

# Dynamic imports with global variables
PERSONA_AVAILABLE = False
ContextType = None  # type: ignore
UrgencyLevel = None  # type: ignore
get_contextual_adaptation_system = None  # type: ignore
get_emotional_memory_system = None  # type: ignore
PersonaArchetype = None  # type: ignore
get_persona_engine = None  # type: ignore

try:
    # Try multiple import paths for persona modules
    try:
        import src.aethercode.persona.contextual_adaptation as context_module
        import src.aethercode.persona.emotional_memory as memory_module
        import src.aethercode.persona.engine as engine_module
    except ImportError:
        try:
            import aetherra.persona.contextual_adaptation as context_module
            import aetherra.persona.emotional_memory as memory_module
            import aetherra.persona.engine as engine_module
        except ImportError:
            # Skip the core imports as they don't exist
            raise ImportError("Persona modules not found")

    # Assign to global variables
    ContextType = context_module.ContextType  # type: ignore
    UrgencyLevel = context_module.UrgencyLevel  # type: ignore
    get_contextual_adaptation_system = context_module.get_contextual_adaptation_system  # type: ignore
    get_emotional_memory_system = memory_module.get_emotional_memory_system  # type: ignore
    PersonaArchetype = engine_module.PersonaArchetype  # type: ignore
    get_persona_engine = engine_module.get_persona_engine  # type: ignore
    PERSONA_AVAILABLE = True

except ImportError:
    # Fallback for when persona modules are not available
    # Note: This is expected in some configurations
    PERSONA_AVAILABLE = False

    # Create fallback enums and classes
    from enum import Enum

    class ContextType(Enum):  # type: ignore
        STANDARD = "standard"
        DEBUG = "debug"
        DEBUGGING = "debugging"
        CREATIVE = "creative"
        CREATING = "creating"
        LEARNING = "learning"
        EMERGENCY = "emergency"

    class UrgencyLevel(Enum):  # type: ignore
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class PersonaArchetype(Enum):  # type: ignore
        OPTIMIST = "optimist"
        ANALYST = "analyst"
        CATALYST = "catalyst"
        GUARDIAN = "guardian"
        EXPLORER = "explorer"
        SAGE = "sage"

    # Fallback functions that return None
    def get_contextual_adaptation_system(*args, **kwargs):  # type: ignore
        return None

    def get_emotional_memory_system(*args, **kwargs):  # type: ignore
        return None

    def get_persona_engine(*args, **kwargs):  # type: ignore
        return None


class NeuroCodePersonaInterface:
    """CLI that demonstrates persona adaptation in real-time"""

    def __init__(self):
        self.installation_path = Path.home() / ".aethercode"
        self.persona_engine = get_persona_engine(str(self.installation_path))
        self.emotional_memory = get_emotional_memory_system(self.installation_path)
        self.contextual_adaptation = get_contextual_adaptation_system(
            self.installation_path, self.persona_engine
        )

    def process_command(self, command: str, context_hints: str = "") -> str:
        """Process a command with contextual persona adaptation"""

        if not PERSONA_AVAILABLE:
            return f"[Basic Mode] Command received: {command}\nPersona functionality not available."

        # Detect context from command
        if self.contextual_adaptation:
            situation = self.contextual_adaptation.detect_context(
                user_command=command,
                file_patterns=self._extract_file_patterns(command),
                error_messages=self._extract_error_patterns(command),
                time_since_last_action=0.0,
            )

            # Adapt persona based on context
            self.contextual_adaptation.adapt_persona(situation)
        else:
            situation = None

        # Get emotional guidance if available (for future use)
        if self.emotional_memory:
            self.emotional_memory.get_emotional_guidance(command)

        # Generate response
        if self.persona_engine and self.persona_engine.current_persona:
            persona = self.persona_engine.current_persona
            if hasattr(persona, "archetype"):
                archetype_name = persona.archetype.value
            elif isinstance(persona, dict) and "archetype" in persona:
                archetype_name = (
                    persona["archetype"].value
                    if hasattr(persona["archetype"], "value")
                    else str(persona["archetype"])
                )
            else:
                archetype_name = "Unknown"
            response = f"[{archetype_name}] {command}"
        else:
            response = f"[Basic Mode] {command}"

        # Record interaction if emotional memory is available
        if self.emotional_memory:
            self.emotional_memory.record_interaction(
                command,
                response,
                situation.context_type if situation else ContextType.STANDARD,
                1.0,
            )

        return response

    def show_persona_status(self) -> str:
        """Show current persona configuration"""
        if not PERSONA_AVAILABLE or not self.persona_engine:
            return """
🤖 NeuroCode Persona Status
═══════════════════════════════════════════

⚠️ Persona system not available
🔧 Running in basic CLI mode

Available commands:
• Basic NeuroCode execution
• Standard help and information
• Limited functionality without persona features
"""

        try:
            persona = self.persona_engine.current_persona

            # Safe extraction of persona information
            def safe_get(obj, key, default="unknown"):
                try:
                    if isinstance(obj, dict):
                        value = obj.get(key, default)
                        if hasattr(value, "value"):
                            return value.value
                        return value
                    elif hasattr(obj, key):
                        value = getattr(obj, key)
                        if hasattr(value, "value"):
                            return value.value
                        return value
                    return default
                except Exception:
                    return default

            archetype_name = safe_get(persona, "archetype", "Unknown")
            voice = persona.get("voice", {}) if isinstance(persona, dict) else {}
            mindprint = (
                persona.get("mindprint", {}) if isinstance(persona, dict) else {}
            )

            # Extract voice details
            formality = safe_get(voice, "formality", "neutral")
            verbosity = safe_get(voice, "verbosity", "moderate")
            encouragement = safe_get(voice, "encouragement", "supportive")
            humor = safe_get(voice, "humor", "subtle")

            # Extract mindprint ID
            installation_id = safe_get(mindprint, "installation_id", "unknown")
            if len(str(installation_id)) > 12:
                installation_id = str(installation_id)[:12] + "..."

        except Exception:
            return "⚠️ Error accessing persona information"

        status = f"""
🤖 NeuroCode Persona Status
═══════════════════════════════════════════

🎭 Current Archetype: {str(archetype_name).title()}
🗣️ Voice Configuration:
   • Formality: {str(formality).title()}
   • Verbosity: {str(verbosity).title()}
   • Encouragement: {str(encouragement).title()}
   • Humor: {str(humor).title()}

🧠 Mindprint:
   • Installation ID: {installation_id}
   • Personality Traits: Available
   • Learning: Active

📊 Emotional Intelligence:
   • Total Interactions: {len(self.emotional_memory.memories) if self.emotional_memory and hasattr(self.emotional_memory, "memories") else 0}
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

    def set_persona_configuration(
        self, archetype_name: str, voice_tone: str = "neutral"
    ):
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
                if not PERSONA_AVAILABLE or not self.persona_engine:
                    return "⚠️ Persona system not available - cannot set archetype"

                archetype = archetype_map[archetype_name.lower()]
                try:
                    self.persona_engine.set_persona(archetype)

                    # Update voice configuration based on tone
                    current_voice = self.persona_engine.current_persona["voice"]
                except Exception as e:
                    return f"⚠️ Error setting persona: {e}"

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
                return (
                    f"❌ Unknown archetype '{archetype_name}'. Available: {available}"
                )

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
        if not PERSONA_AVAILABLE or not self.persona_engine:
            return f"[Basic Mode] Processing: {command}\n\nPersona features not available. Basic response generated."

        try:
            archetype_name = self.persona_engine.current_persona["archetype"]["name"]
            voice = self.persona_engine.current_persona["voice"]

            # Convert archetype name to enum for lookup
            archetype_enum = PersonaArchetype(archetype_name.lower())
        except Exception:
            return f"[Fallback Mode] Processing: {command}\n\nPersona information unavailable."

        # Base response templates by archetype
        response_templates = {
            PersonaArchetype.GUARDIAN: {
                ContextType.DEBUGGING: "I'll help you systematically diagnose this issue. Let's start with the most critical security and stability aspects first.",
                ContextType.CREATING: "Great idea! Let's build this with security and maintainability in mind from the start.",
                ContextType.LEARNING: "I'll teach you this thoroughly, ensuring you understand both the concept and its safe implementation.",
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
                ContextType.EMERGENCY: "Crisis energy activated! Let's channel this urgency into rapid, decisive action.",
            },
        }

        # Get base response
        if (
            archetype_enum in response_templates
            and situation.context_type in response_templates[archetype_enum]
        ):
            base_response = response_templates[archetype_enum][situation.context_type]
        else:
            base_response = (
                "I'm here to help you with this task. Let's work through it together."
            )

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
            base_response += f"\n\n💡 Based on my experience, here's what I recommend:\n{self._get_specific_guidance(command, guidance)}"

        return base_response

    def _get_specific_guidance(self, command: str, guidance: dict) -> str:
        """Get specific guidance based on command and emotional memory"""
        if guidance.get("confidence", 0) > 0.5:
            patterns = guidance.get("recommended_approach", "Standard approach")
            return f"• {patterns}\n• Previous similar interactions were successful\n• Confidence level: {guidance.get('confidence', 0):.1%}"
        else:
            return "• I'll learn from this interaction to provide better guidance in the future\n• Feel free to provide feedback on my responses"


def main() -> None:
    """Main CLI entry point for the persona interface"""
    interface = NeuroCodePersonaInterface()

    parser = argparse.ArgumentParser(
        description="NeuroCode Persona Command Interface",
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

    parser.add_argument(
        "command", nargs="*", help="Command to process with persona adaptation"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show current persona status"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Enter interactive mode"
    )

    args = parser.parse_args()

    if args.status or (not args.command and not args.interactive):
        print(interface.show_persona_status())
        return

    if args.interactive:
        print("🧠 NeuroCode Persona Interactive Mode")
        print("Type commands or 'quit' to exit")
        print("=" * 50)

        while True:
            try:
                user_input = input("\nneurocode> ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    print(
                        "👋 Farewell! The persona remembers our interaction for next time."
                    )
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
        print(f"\n🤖 NeuroCode Response:\n{response}")

        # Show brief adaptation info
        if interface.contextual_adaptation and hasattr(
            interface.contextual_adaptation, "current_situation"
        ):
            situation = interface.contextual_adaptation.current_situation
            print(
                f"\n🔄 Context: {situation.context_type.value.title()} | Urgency: {situation.urgency_level.value.title()}"
            )
        else:
            print("\n🔄 Context: Standard | Urgency: Low")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
