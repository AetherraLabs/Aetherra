#!/usr/bin/env python3
"""
Launch Lyrixa - AI-Native Development Environment
==================================================

Launcher for the main Lyrixa with integrated AI chat interface.
This provides a unified AI-native development environment with dark mode.
"""

import sys
from pathlib import Path


def main():
    """Launch the main Lyrixa with integrated AI chat"""
    print("🚀 Launching Lyrixa - AI-Native Development Environment")
    print("=" * 60)

    # Add project paths
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))

    try:
        # Import and run Lyrixa
        from aetherra.ui.lyrixa import main as lyrixa_main

        print("✅ Lyrixa components loaded")
        print("🎯 Features enabled:")
        print("   • 🛠️ Full development environment")
        print("   • 🌙 Modern dark mode interface")
        print("   • 🤖 Integrated AI chat assistant")
        print("   • 🎭 Multiple AI personalities")
        print("   • 🔌 Plugin system integration")
        print("   • ⚡ Real-time AI collaboration")
        print()

        # Launch Lyrixa
        result = lyrixa_main()
        print("👋 Lyrixa session ended")
        return result

    except ImportError as e:
        print(f"❌ Failed to launch Lyrixa: {e}")
        print("Please ensure Aetherra is correctly installed.")
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)


if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
