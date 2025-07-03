#!/usr/bin/env python3
"""
NeuroCode Persona CLI - Command-line interface for persona management
"""

import argparse
import sys
from pathlib import Path

# Add core to path for imports
sys.path.append(str(Path(__file__).parent / "core"))

# Dynamic imports with global variables
PERSONA_ENGINE_AVAILABLE = False
PersonaArchetype = None  # type: ignore
PersonaEngine = None  # type: ignore
PersonaState = None  # type: ignore
VoiceConfiguration = None  # type: ignore
get_persona_engine = None  # type: ignore

try:
    # Try multiple import paths for persona modules
    try:
        import src.aethercode.persona.engine as engine_module
    except ImportError:
        try:
            import aetherra.persona.engine as engine_module
        except ImportError:
            # Skip the core.persona.engine import as it doesn't exist
            raise ImportError("Persona modules not found")

    # Dynamically assign from the loaded module
    PersonaArchetype = engine_module.PersonaArchetype  # type: ignore
    PersonaEngine = engine_module.PersonaEngine  # type: ignore
    VoiceConfiguration = engine_module.VoiceConfiguration  # type: ignore
    get_persona_engine = engine_module.get_persona_engine  # type: ignore

    # Always provide PersonaState as a fallback if not available in real module
    if not hasattr(engine_module, "PersonaState"):

        class PersonaState:  # type: ignore
            def __init__(self):
                self.active = False
                self.current_archetype = None
                self.blend_ratio = 1.0
                self.voice_config = None

            def get_status(self):
                return {"active": self.active, "archetype": self.current_archetype}

            def is_active(self):
                return self.active

        globals()["PersonaState"] = PersonaState
    else:
        PersonaState = engine_module.PersonaState  # type: ignore

    PERSONA_ENGINE_AVAILABLE = True

except ImportError:
    PERSONA_ENGINE_AVAILABLE = False

    # Create fallback classes and enums when imports fail
    from enum import Enum

    class PersonaArchetype(Enum):  # type: ignore
        GUARDIAN = "guardian"
        EXPLORER = "explorer"
        SAGE = "sage"
        OPTIMIST = "optimist"
        ANALYST = "analyst"
        CATALYST = "catalyst"

    class PersonaEngine:  # type: ignore
        def __init__(self):
            self.current_persona = None

        def set_persona(self, archetype, blend_ratio=1.0):
            return False

        def get_persona_status(self):
            return {"archetype": "fallback", "emoji": "🤖", "mindprint_id": "fallback"}

    class VoiceConfiguration:  # type: ignore
        def __init__(self, **kwargs):
            self.formality = "neutral"
            self.verbosity = "moderate"
            self.encouragement = "supportive"
            self.humor = "subtle"

    class PersonaState:  # type: ignore
        def __init__(self):
            self.active = False
            self.current_archetype = None
            self.blend_ratio = 1.0
            self.voice_config = None

        def get_status(self):
            return {"active": self.active, "archetype": self.current_archetype}

        def is_active(self):
            return self.active

    def get_persona_engine(installation_path=None):  # type: ignore
        return PersonaEngine()

    # Assign the fallback classes to global variables
    # (This ensures they can be imported directly)
    globals()["PersonaArchetype"] = PersonaArchetype
    globals()["PersonaEngine"] = PersonaEngine
    globals()["PersonaState"] = PersonaState
    globals()["VoiceConfiguration"] = VoiceConfiguration
    globals()["get_persona_engine"] = get_persona_engine


class PersonaCLI:
    """Command-line interface for NeuroCode persona management"""

    def __init__(self):
        self.engine = None

    def _get_engine(self):
        """Get persona engine instance"""
        if self.engine is None:
            installation_path = Path.home() / ".aethercode"
            self.engine = get_persona_engine(str(installation_path))
        return self.engine

    def set_persona(self, archetype, blend_ratio=1.0):
        """Set the primary persona archetype"""
        if not PERSONA_ENGINE_AVAILABLE:
            print("⚠️ Persona system not available - running in fallback mode")
            print(f"Would set persona to: {archetype}")
            return True

        try:
            if hasattr(PersonaArchetype, archetype.upper()):
                persona_type = getattr(PersonaArchetype, archetype.upper())
            else:
                # Try by value
                persona_type = PersonaArchetype(archetype.lower())

            engine = self._get_engine()
            if hasattr(engine, "set_persona"):
                engine.set_persona(persona_type, blend_ratio)
                status = engine.get_persona_status()
                print(
                    f"✅ Persona set to {status.get('emoji', '🤖')} {status.get('archetype', archetype)}"
                )
                print(f"   Mindprint: {status.get('mindprint_id', 'fallback')}")
            else:
                print(f"✅ Persona set to {archetype} (fallback mode)")

        except (ValueError, AttributeError):
            if PERSONA_ENGINE_AVAILABLE:
                available = (
                    [p.value for p in PersonaArchetype]
                    if hasattr(PersonaArchetype, "__iter__")
                    else [
                        "guardian",
                        "explorer",
                        "sage",
                        "optimist",
                        "analyst",
                        "catalyst",
                    ]
                )
            else:
                available = [
                    "guardian",
                    "explorer",
                    "sage",
                    "optimist",
                    "analyst",
                    "catalyst",
                ]
            print(
                f"❌ Invalid persona '{archetype}'. Available: {', '.join(available)}"
            )
            return False
        except Exception as e:
            print(f"❌ Error setting persona: {e}")
            return False

        return True

    def show_status(self):
        """Display current persona status"""
        if not PERSONA_ENGINE_AVAILABLE:
            print("🤖 NeuroCode Persona Status")
            print("=" * 40)
            print("⚠️ Persona system not available")
            print("Running in fallback mode")
            return True

        try:
            engine = self._get_engine()
            status = engine.get_persona_status()

            print("🤖 NeuroCode Persona Status")
            print("=" * 40)
            print(f"Mindprint ID: {status.get('mindprint_id', 'fallback')}")
            print(
                f"Archetype: {status.get('emoji', '🤖')} {status.get('archetype', 'fallback')}"
            )
            print(f"Interactions: {status.get('total_interactions', 0)}")
            print(
                f"Adaptation: {'Enabled' if status.get('adaptation_enabled', False) else 'Disabled'}"
            )

        except Exception as e:
            print(f"❌ Error getting persona status: {e}")
            return False

        return True

    def list_archetypes(self):
        """List available persona archetypes"""
        print("🎭 Available Persona Archetypes")
        print("=" * 40)

        archetypes = {
            "GUARDIAN": ("🛡️", "Protective and security-focused"),
            "EXPLORER": ("🧭", "Curious and adventure-seeking"),
            "SAGE": ("📚", "Wise and knowledge-sharing"),
            "OPTIMIST": ("🌟", "Positive and encouraging"),
            "ANALYST": ("📊", "Data-driven and logical"),
            "CATALYST": ("⚡", "Change-focused and energetic"),
        }

        for archetype, (emoji, description) in archetypes.items():
            print(f"{emoji} {archetype.title()}")
            print(f"   {description}")
            print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="NeuroCode Persona Management CLI",
        epilog="Examples:\n"
        "  neurocode persona set guardian\n"
        "  neurocode persona status\n"
        "  neurocode persona list\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Set persona command
    set_parser = subparsers.add_parser("set", help="Set primary persona archetype")
    set_parser.add_argument(
        "archetype",
        help="Persona archetype (guardian, explorer, sage, optimist, analyst, catalyst)",
    )
    set_parser.add_argument(
        "--ratio", type=float, default=1.0, help="Blend ratio (0.0-1.0)"
    )

    # Status command
    subparsers.add_parser("status", help="Show current persona status")

    # List archetypes command
    subparsers.add_parser("list", help="List available persona archetypes")

    args = parser.parse_args()
    cli = PersonaCLI()

    if args.command == "set":
        success = cli.set_persona(args.archetype, args.ratio)
        sys.exit(0 if success else 1)
    elif args.command == "status":
        success = cli.show_status()
        sys.exit(0 if success else 1)
    elif args.command == "list":
        success = cli.list_archetypes()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
