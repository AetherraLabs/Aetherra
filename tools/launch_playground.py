#!/usr/bin/env python3
"""
🧬 NeuroCode Playground Launcher
===============================

Quick launcher for the NeuroCode Playground web interface.
This starts the Streamlit app that provides an interactive
environment for learning and experimenting with NeuroCode.
"""

import subprocess
import sys
from pathlib import Path


def check_requirements():
    """Check if required packages are installed"""
    required_packages = ["streamlit", "lark"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:", ", ".join(missing_packages))
        print("📦 Installing requirements...")

        # Install missing packages
        parent_dir = Path(__file__).parent.parent
        requirements_file = parent_dir / "playground_requirements.txt"
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        else:
            for package in missing_packages:
                subprocess.run([sys.executable, "-m", "pip", "install", package])

        print("✅ Requirements installed!")


def launch_playground():
    """Launch the NeuroCode Playground"""
    print("🧬 Starting NeuroCode Playground...")
    print("🌐 The playground will open in your web browser")
    print("🎮 Interactive NeuroCode environment loading...")
    print("")
    print("Features available:")
    print("  ✅ Interactive code editor")
    print("  ✅ Standard library explorer")
    print("  ✅ Step-by-step tutorials")
    print("  ✅ Real-world examples")
    print("  ✅ Live syntax validation")
    print("")
    print("🚀 Launching...")

    # Get the playground file path
    parent_dir = Path(__file__).parent.parent
    playground_file = parent_dir / "ui" / "neurocode_playground.py"

    if not playground_file.exists():
        print("❌ Error: neurocode_playground.py not found!")
        print(f"Expected location: {playground_file}")
        return False

    # Launch Streamlit
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(playground_file),
                "--server.port",
                "8501",
                "--server.address",
                "localhost",
                "--browser.gatherUsageStats",
                "false",
            ]
        )
        return True
    except KeyboardInterrupt:
        print("\n🛑 Playground stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error launching playground: {e}")
        return False


if __name__ == "__main__":
    print("🧬 NeuroCode Playground Launcher")
    print("=" * 40)

    # Check and install requirements
    check_requirements()

    # Launch the playground
    success = launch_playground()

    if success:
        print("✅ Playground session completed")
    else:
        print("❌ Failed to launch playground")
        sys.exit(1)
