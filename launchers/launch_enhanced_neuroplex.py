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
        print("   • 🛠️ Full development environment")
        print("   • 🤖 Integrated NeuroChat interface")
        print("   • 📝 Enhanced code editor")
        print("   • 🧠 Memory & goal management")
        print("   • 🔌 Plugin ecosystem")
        print("   • 📊 Performance monitoring")
        print()
        print("🎭 Starting Enhanced Neuroplex...")

        return enhanced_main()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔄 Trying fallback options...")

        try:
            # Fallback to standard Neuroplex
            from neurocode.ui.neuroplex_fully_modular import main as fallback_main

            print("✅ Falling back to standard Neuroplex")
            return fallback_main()

        except ImportError as e2:
            print(f"❌ Fallback failed: {e2}")
            print("💡 Please ensure all dependencies are installed:")
            print("   • PySide6: pip install PySide6")
            print("   • NeuroCode components: Check project structure")
            return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
