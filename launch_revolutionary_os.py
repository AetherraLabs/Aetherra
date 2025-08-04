#!/usr/bin/env python3
"""
🚀 Aetherra OS v3.0 Revolutionary Launcher
===========================================

Launch script for the completely redesigned Aetherra Operating System
- Eliminates wasted space
- Shows real system data
- Professional Aetherra Labs design
- True OS interface, not just conversation app
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """Setup proper Python paths for Aetherra system"""
    project_root = Path(__file__).parent
    aetherra_path = project_root / "Aetherra"

    # Add paths for imports
    paths_to_add = [
        str(project_root),
        str(aetherra_path),
        str(aetherra_path / "aetherra_core"),
        str(aetherra_path / "gui"),
    ]

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

    print(f"🔧 Python paths configured:")
    for path in paths_to_add:
        print(f"   📁 {path}")

def main():
    """Launch the revolutionary Aetherra OS"""
    print("🌌 Aetherra OS v3.0 Revolutionary Launcher")
    print("=" * 50)
    print("🏢 Aetherra Labs - The Future of AI Intelligence")
    print()

    # Setup paths
    setup_paths()

    try:
        # Import and launch the OS
        print("🔄 Loading revolutionary interface...")

        # Change to the project directory
        os.chdir(Path(__file__).parent)

        # Import the GUI module
        from Aetherra.gui.aetherra_enhanced_neural_os import main as launch_os

        print("✅ Interface loaded successfully")
        print("🚀 Launching Aetherra OS v3.0...")
        print()

        # Launch the OS
        launch_os()

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Attempting fallback launch...")

        try:
            # Fallback: try direct execution
            gui_file = Path(__file__).parent / "Aetherra" / "gui" / "aetherra_enhanced_neural_os.py"
            if gui_file.exists():
                exec(open(gui_file).read(), {"__name__": "__main__"})
            else:
                print(f"❌ GUI file not found: {gui_file}")

        except Exception as fallback_error:
            print(f"❌ Fallback failed: {fallback_error}")
            print()
            print("🔧 Debug Information:")
            print(f"   📁 Current directory: {os.getcwd()}")
            print(f"   📁 Script location: {Path(__file__).parent}")
            print(f"   🐍 Python path: {sys.path[:3]}")

    except Exception as e:
        print(f"❌ Launch Error: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Ensure PySide6 is installed: pip install PySide6")
        print("   2. Check file permissions")
        print("   3. Verify Python environment")

if __name__ == "__main__":
    main()
