#!/usr/bin/env python3
"""
Launch Enhanced Neuroplex - Integrated NeuroChat Edition
========================================================

Launcher for the enhanced Neuroplex with integrated NeuroChat interface.
This provides a unified AI-native development environment.
"""

import sys
from pathlib import Path


def main():
    """Launch the enhanced Neuroplex with integrated NeuroChat"""
    print("🚀 Launching Enhanced Neuroplex - Integrated NeuroChat Edition")
    print("=" * 60)

    # Add project paths
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src" / "neurocode" / "ui"))

    try:
        # Import and run enhanced Neuroplex
        from enhanced_neuroplex import main as enhanced_main
        
        print("✅ Enhanced Neuroplex components loaded")
        print("🎯 Features enabled:")
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
            from neuroplex_fully_modular import main as fallback_main
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
