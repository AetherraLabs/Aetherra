#!/usr/bin/env python3
"""
NeuroCode CLI Interface
======================

Command-line interface for the NeuroCode programming language.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NeuroCode - AI-Native Programming Language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neurocode run script.neuro          # Run a NeuroCode script
  neurocode gui                       # Launch Neuroplex GUI
  neurocode parse file.neuro          # Parse and show AST
  neurocode --version                 # Show version info
        """,
    )

    parser.add_argument("--version", action="version", version="NeuroCode 2.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Execute NeuroCode script")
    run_parser.add_argument("file", help="NeuroCode file to execute")
    run_parser.add_argument("--enhanced", action="store_true", help="Use enhanced interpreter")

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch Neuroplex GUI")
    gui_parser.add_argument("--modular", action="store_true", help="Use fully modular GUI")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse NeuroCode file")
    parse_parser.add_argument("file", help="NeuroCode file to parse")
    parse_parser.add_argument("--ast", action="store_true", help="Show AST")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "run":
            from core.neurocode_grammar import NEUROCODE_GRAMMAR
            from lark import Lark
            
            with open(args.file) as f:
                code = f.read()

            # Create parser and parse the code
            lark_parser = Lark(NEUROCODE_GRAMMAR, start='program')
            try:
                tree = lark_parser.parse(code)
                print("✅ Parse successful, execution would follow")
                print(f"AST: {tree.pretty()}")
            except Exception as e:
                print(f"❌ Parse error: {e}")

        elif args.command == "gui":
            if args.modular:
                from launchers.launch_fully_modular_neuroplex import main as launch_gui
            else:
                from launchers.launch_modular_neuroplex import main as launch_gui
            launch_gui()

        elif args.command == "parse":
            from core.neurocode_grammar import NEUROCODE_GRAMMAR
            from lark import Lark

            with open(args.file) as f:
                code = f.read()

            # Create parser and parse the code
            lark_parser = Lark(NEUROCODE_GRAMMAR, start='program')
            try:
                tree = lark_parser.parse(code)
                if args.ast:
                    print("🌳 Abstract Syntax Tree:")
                    print(tree.pretty())
                else:
                    print("✅ Parse successful")
            except Exception as e:
                print(f"❌ Parse error: {e}")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure NeuroCode is properly installed.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
