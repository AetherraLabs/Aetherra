#!/usr/bin/env python3
"""
NeuroCode CLI Runner
Universal entry point for all NeuroCode CLI functionality.
"""

import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main CLI entry point with fallback options"""
    print("🧠 NeuroCode CLI")
    print("=" * 40)

    # Try different CLI modules in order of preference
    try:
        # Try advanced persona CLI first
        print("Attempting to load persona CLI...")
        from neurocode.cli.main import main as persona_main
        print("✅ Persona CLI available")
        persona_main()
        return
    except ImportError as e:
        print(f"⚠️ Persona CLI unavailable: {e}")

    try:
        # Try demo CLI
        print("Attempting to load demo CLI...")
        from neurocode.cli.demo import main as demo_main
        print("✅ Demo CLI available")
        demo_main()
        return
    except ImportError as e:
        print(f"⚠️ Demo CLI unavailable: {e}")

    try:
        # Fallback to basic CLI
        print("Loading basic CLI...")
        from neurocode.cli.basic import main as basic_main
        print("✅ Basic CLI loaded")
        basic_main()
        return
    except ImportError as e:
        print(f"❌ Basic CLI unavailable: {e}")

    # Ultimate fallback
    print("❌ No CLI modules available")
    print("Please check your installation")
    sys.exit(1)

if __name__ == "__main__":
    main()
