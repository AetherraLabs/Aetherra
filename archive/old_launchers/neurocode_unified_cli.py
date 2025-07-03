#!/usr/bin/env python3
"""
NeuroCode - Unified Command Line Interface
The AI-native programming language with revolutionary persona system.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from neurocode.cli.demo import main as run_demo
    from neurocode.cli.main import NeuroCodePersonaInterface as NeuroCodeCLI
    from neurocode.cli.persona import PersonaCLI
    # Plugin CLI functions will be imported separately
except ImportError:
    # Fallback for development mode
    sys.path.insert(0, str(Path(__file__).parent))
    from neurocode_persona_cli import PersonaCLI
    from neurocode_persona_demo import main as run_demo

    # Add more fallback imports as needed
    NeuroCodeCLI = None


def main():
    """Main entry point for NeuroCode CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="neurocode",
        description="NeuroCode - AI-native programming language with persona system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neurocode                     # Start interactive REPL
  neurocode persona status      # Check persona status
  neurocode persona set sage    # Switch to Sage archetype
  neurocode plugin list         # List available plugins
  neurocode demo                # Run interactive demos
  neurocode demo --context debugging  # Test context adaptation
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Persona management
    persona_parser = subparsers.add_parser(
        "persona", help="Manage AI persona and personality", aliases=["p"]
    )
    persona_subparsers = persona_parser.add_subparsers(dest="persona_command")

    # Persona commands
    persona_subparsers.add_parser("status", help="Show current persona status")
    persona_subparsers.add_parser("list", help="List available archetypes")

    set_parser = persona_subparsers.add_parser("set", help="Set persona archetype")
    set_parser.add_argument("archetype", help="Archetype to switch to")

    blend_parser = persona_subparsers.add_parser("blend", help="Blend two archetypes")
    blend_parser.add_argument("primary", help="Primary archetype")
    blend_parser.add_argument("secondary", help="Secondary archetype")
    blend_parser.add_argument("--ratio", type=float, default=0.7, help="Blend ratio (0.0-1.0)")

    voice_parser = persona_subparsers.add_parser("voice", help="Configure voice settings")
    voice_parser.add_argument("--formality", help="Voice formality level")
    voice_parser.add_argument("--verbosity", help="Voice verbosity level")
    voice_parser.add_argument("--encouragement", help="Encouragement style")
    voice_parser.add_argument("--humor", help="Humor level")

    # Plugin management
    plugin_parser = subparsers.add_parser(
        "plugin", help="Manage plugins and extensions", aliases=["plugins"]
    )
    plugin_subparsers = plugin_parser.add_subparsers(dest="plugin_command")

    plugin_subparsers.add_parser("list", help="List available plugins")
    plugin_subparsers.add_parser("installed", help="List installed plugins")

    install_parser = plugin_subparsers.add_parser("install", help="Install a plugin")
    install_parser.add_argument("plugin", help="Plugin name or path")

    remove_parser = plugin_subparsers.add_parser("remove", help="Remove a plugin")
    remove_parser.add_argument("plugin", help="Plugin name")

    # Demo system
    demo_parser = subparsers.add_parser("demo", help="Run demonstrations")
    demo_parser.add_argument(
        "--context",
        choices=["debugging", "creating", "learning", "emergency"],
        help="Test specific context adaptation",
    )
    demo_parser.add_argument("--interactive", action="store_true", help="Run interactive demo")

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command in ["persona", "p"]:
        cli = PersonaCLI()

        if args.persona_command == "status":
            cli.show_status()
        elif args.persona_command == "list":
            cli.list_archetypes()
        elif args.persona_command == "set":
            cli.set_persona(args.archetype)
        elif args.persona_command == "blend":
            cli.blend_personas(args.primary, args.secondary, args.ratio)
        elif args.persona_command == "voice":
            cli.configure_voice(
                formality=args.formality,
                verbosity=args.verbosity,
                encouragement=args.encouragement,
                humor=args.humor,
            )
        else:
            persona_parser.print_help()

    elif args.command in ["plugin", "plugins"]:
        # Import plugin functions directly since it's not a class
        try:
            from neurocode.cli.plugin import main as plugin_main

            sys.argv = ["plugin"] + sys.argv[2:]  # Adjust argv for plugin CLI
            plugin_main()
        except ImportError:
            # Fallback to original plugin CLI
            try:
                import aetherra_plugin_cli

                neurocode_plugin_cli.main()
            except ImportError:
                print("Plugin CLI not available")
                return

    elif args.command == "demo":
        # Just run the demo function without parameters
        run_demo()

    else:
        # Default: Start interactive REPL or fallback
        if NeuroCodeCLI is not None:
            try:
                # Import and call the main function directly
                from neurocode.cli.main import main as cli_main

                cli_main()
            except Exception as e:
                print(f"Error starting NeuroCode CLI: {e}")
        else:
            print("🤖 NeuroCode Interactive REPL")
            print("Type 'help' for commands or 'exit' to quit")
            print()

            while True:
                try:
                    user_input = input("neurocode> ").strip()
                    if user_input.lower() in ["exit", "quit"]:
                        print("👋 Goodbye!")
                        break
                    elif user_input.lower() == "help":
                        print("Available commands:")
                        print("  persona - Manage AI persona")
                        print("  plugin  - Manage plugins")
                        print("  demo    - Run demonstrations")
                        print("  exit    - Exit NeuroCode")
                    else:
                        print(f"Executing: {user_input}")
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    print("\n👋 Goodbye!")
                    break


if __name__ == "__main__":
    main()
