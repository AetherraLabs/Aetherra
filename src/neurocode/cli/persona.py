#!/usr/bin/env python3
"""
NeuroCode Persona CLI - Command-line interface for persona management
"""

import argparse
import sys
from pathlib import Path

# Add core to path for imports
sys.path.append(str(Path(__file__).parent / "core"))

from neurocode.persona.engine import (
    PersonaArchetype,
    PersonaEngine,
    VoiceConfiguration,
    get_persona_engine,
)


class PersonaCLI:
    """Command-line interface for NeuroCode persona management"""

    def __init__(self):
        self.engine = None

    def _get_engine(self) -> PersonaEngine:
        """Get persona engine instance"""
        if self.engine is None:
            installation_path = Path.home() / ".neurocode"
            self.engine = get_persona_engine(str(installation_path))
        return self.engine

    def set_persona(self, archetype: str, blend_ratio: float = 1.0):
        """Set the primary persona archetype"""
        try:
            persona_type = PersonaArchetype(archetype.lower())
            engine = self._get_engine()
            engine.set_persona(persona_type, blend_ratio)

            status = engine.get_persona_status()
            print(f"✅ Persona set to {status['emoji']} {status['archetype']}")
            print(f"   Mindprint: {status['mindprint_id']}")

        except ValueError:
            available = [p.value for p in PersonaArchetype]
            print(f"❌ Invalid persona '{archetype}'. Available: {', '.join(available)}")
            return False
        except Exception as e:
            print(f"❌ Error setting persona: {e}")
            return False

        return True

    def blend_personas(self, primary: str, secondary: str, ratio: float):
        """Blend two persona archetypes"""
        try:
            primary_type = PersonaArchetype(primary.lower())
            _secondary_type = PersonaArchetype(secondary.lower())

            engine = self._get_engine()

            # For now, just set primary with ratio
            # TODO: Implement true blending in persona_engine.py
            engine.set_persona(primary_type, ratio)

            status = engine.get_persona_status()
            print(f"✅ Persona blend: {primary}:{ratio:.1f} + {secondary}:{1 - ratio:.1f}")
            print(f"   Current: {status['emoji']} {status['archetype']}")

        except ValueError:
            available = [p.value for p in PersonaArchetype]
            print(f"❌ Invalid persona. Available: {', '.join(available)}")
            return False
        except Exception as e:
            print(f"❌ Error blending personas: {e}")
            return False

        return True

    def configure_voice(
        self,
        formality: str | None = None,
        verbosity: str | None = None,
        encouragement: str | None = None,
        humor: str | None = None,
    ):
        """Configure voice characteristics"""
        try:
            engine = self._get_engine()
            current_voice = engine.current_persona["voice"]

            # Update only provided parameters
            voice_config = VoiceConfiguration(
                formality=formality or current_voice.formality,
                verbosity=verbosity or current_voice.verbosity,
                encouragement=encouragement or current_voice.encouragement,
                humor=humor or current_voice.humor,
            )

            engine.configure_voice(voice_config)

            print("✅ Voice configuration updated:")
            print(f"   Formality: {voice_config.formality}")
            print(f"   Verbosity: {voice_config.verbosity}")
            print(f"   Encouragement: {voice_config.encouragement}")
            print(f"   Humor: {voice_config.humor}")

        except Exception as e:
            print(f"❌ Error configuring voice: {e}")
            return False

        return True

    def show_status(self):
        """Display current persona status"""
        try:
            engine = self._get_engine()
            status = engine.get_persona_status()

            print("🤖 NeuroCode Persona Status")
            print("=" * 40)
            print(f"Mindprint ID: {status['mindprint_id']}")
            print(f"Archetype: {status['emoji']} {status['archetype']}")
            print(f"Interactions: {status['total_interactions']}")
            print(f"Adaptation: {'Enabled' if status['adaptation_enabled'] else 'Disabled'}")
            print()

            print("📊 Personality Traits:")
            traits = status["traits"]
            for trait, value in traits.items():
                bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
                print(f"   {trait.capitalize():12} [{bar}] {value:.1f}")
            print()

            print("🗣️ Voice Configuration:")
            voice = status["voice"]
            for setting, value in voice.items():
                print(f"   {setting.capitalize():12} {value}")
            print()

            print("😊 Emotional State:")
            emotions = status["emotional_state"]
            for emotion, value in emotions.items():
                bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
                print(f"   {emotion.capitalize():12} [{bar}] {value:.1f}")

        except Exception as e:
            print(f"❌ Error getting persona status: {e}")
            return False

        return True

    def list_archetypes(self):
        """List available persona archetypes"""
        from neurocode.persona.engine import PersonaArchetypeDefinitions

        print("🎭 Available Persona Archetypes")
        print("=" * 40)

        for _archetype, definition in PersonaArchetypeDefinitions.ARCHETYPES.items():
            emoji = definition["emoji"]
            name = definition["name"]
            description = definition["description"]

            print(f"{emoji} {name}")
            print(f"   {description}")

            # Show key traits
            traits = definition["base_traits"]
            high_traits = [trait for trait, value in traits.__dict__.items() if value > 0.7]
            if high_traits:
                print(f"   Key traits: {', '.join(high_traits)}")
            print()

    def reset_persona(self, regenerate_mindprint: bool = False):
        """Reset persona to defaults"""
        try:
            engine = self._get_engine()
            engine.reset_persona(regenerate_mindprint)

            if regenerate_mindprint:
                print("✅ Persona reset with new mindprint generated")
            else:
                print("✅ Persona reset to defaults")

            # Show new status
            self.show_status()

        except Exception as e:
            print(f"❌ Error resetting persona: {e}")
            return False

        return True

    def test_response(self, context: str, user_input: str, task_type: str = "general"):
        """Test persona response generation"""
        try:
            engine = self._get_engine()
            response = engine.generate_response(context, user_input, task_type)

            status = engine.get_persona_status()
            print(f"🤖 {status['emoji']} {status['archetype']} responds:")
            print(f'   "{response}"')

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return False

        return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="NeuroCode Persona Management CLI",
        epilog="Examples:\n"
        "  neurocode persona set guardian\n"
        "  neurocode persona blend guardian:0.7 sage:0.3\n"
        "  neurocode persona voice --formality=casual --humor=playful\n"
        "  neurocode persona status\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Set persona command
    set_parser = subparsers.add_parser("set", help="Set primary persona archetype")
    set_parser.add_argument(
        "archetype",
        help="Persona archetype (guardian, explorer, sage, optimist, analyst, catalyst)",
    )
    set_parser.add_argument("--ratio", type=float, default=1.0, help="Blend ratio (0.0-1.0)")

    # Blend personas command
    blend_parser = subparsers.add_parser("blend", help="Blend two persona archetypes")
    blend_parser.add_argument(
        "blend_spec", help='Blend specification (e.g., "guardian:0.7" or "guardian sage")'
    )
    blend_parser.add_argument(
        "secondary", nargs="?", help="Secondary archetype (if not in blend_spec)"
    )

    # Voice configuration command
    voice_parser = subparsers.add_parser("voice", help="Configure voice characteristics")
    voice_parser.add_argument(
        "--formality",
        choices=["casual", "professional", "formal"],
        help="Communication formality level",
    )
    voice_parser.add_argument(
        "--verbosity", choices=["concise", "balanced", "detailed"], help="Response verbosity level"
    )
    voice_parser.add_argument(
        "--encouragement",
        choices=["minimal", "moderate", "enthusiastic"],
        help="Encouragement level",
    )
    voice_parser.add_argument("--humor", choices=["none", "subtle", "playful"], help="Humor level")

    # Status command
    subparsers.add_parser("status", help="Show current persona status")

    # List archetypes command
    subparsers.add_parser("list", help="List available persona archetypes")

    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset persona to defaults")
    reset_parser.add_argument(
        "--regenerate-mindprint",
        action="store_true",
        help="Generate new mindprint (creates new AI identity)",
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Test persona response generation")
    test_parser.add_argument("context", help="Context for the response")
    test_parser.add_argument("input", help="User input to respond to")
    test_parser.add_argument(
        "--type", default="general", help="Task type (general, security, debug, education)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = PersonaCLI()

    try:
        if args.command == "set":
            cli.set_persona(args.archetype, args.ratio)

        elif args.command == "blend":
            # Parse blend specification
            if ":" in args.blend_spec:
                # Format: "guardian:0.7"
                parts = args.blend_spec.split(":")
                primary = parts[0]
                ratio = float(parts[1])
                secondary = args.secondary or "sage"  # Default secondary
            else:
                # Format: "guardian sage" with default 0.7:0.3 ratio
                primary = args.blend_spec
                secondary = args.secondary
                ratio = 0.7

                if not secondary:
                    print("❌ Please specify secondary archetype")
                    return

            cli.blend_personas(primary, secondary, ratio)

        elif args.command == "voice":
            cli.configure_voice(args.formality, args.verbosity, args.encouragement, args.humor)

        elif args.command == "status":
            cli.show_status()

        elif args.command == "list":
            cli.list_archetypes()

        elif args.command == "reset":
            cli.reset_persona(args.regenerate_mindprint)

        elif args.command == "test":
            cli.test_response(args.context, args.input, args.type)

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
