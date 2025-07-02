#!/usr/bin/env python3
"""
Launch Neuroplex - AI-Native Development Environment
==================================================

Launcher for the main Neuroplex with integrated AI chat interface.
This provides a unified AI-native development environment with dark mode.
"""

import sys
from pathlib import Path


def main():
    """Launch the main Neuroplex with integrated AI chat"""
    print("🚀 Launching Neuroplex - AI-Native Development Environment")
    print("=" * 60)

    # Add project paths
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))

    try:
        # Import and run Neuroplex
        from neurocode.ui.neuroplex import main as neuroplex_main

        print("✅ Neuroplex components loaded")
        print("🎯 Features enabled:")
        print("   • 🛠️ Full development environment")
        print("   • 🌙 Modern dark mode interface")
        print("   • 🤖 Integrated AI chat assistant")
        print("   • 🎭 Multiple AI personalities")
        print("   • 🔌 Plugin system integration")
        print("   • ⚡ Real-time AI collaboration")
        print()

        # Launch Neuroplex
        result = neuroplex_main()
        print("👋 Neuroplex session ended")
        return result

    except ImportError as e:
        print(f"❌ Failed to import Neuroplex components: {e}")
        print("🔧 Make sure all dependencies are installed:")
        print("   pip install PySide6")
        return 1
    except Exception as e:
        print(f"❌ Error launching Neuroplex: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
