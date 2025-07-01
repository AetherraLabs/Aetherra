#!/usr/bin/env python3
"""
Launch Fully Modular Neuroplex
==============================

This launcher starts the fully modular version of Neuroplex with all
extracted panel components.
"""

import sys
from pathlib import Path


def main():
    """Launch the fully modular Neuroplex GUI"""
    print("🚀 Launching Neuroplex v2.0 - Fully Modular Edition")

    # Add src to Python path to access neurocode package
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))

    try:
        # Import and run the fully modular version
        from neurocode.ui.neuroplex_fully_modular import main as modular_main

        return modular_main()

    except ImportError as e:
        print(f"❌ Could not import modular components: {e}")
        print("🔄 Falling back to simplified modular version...")

        try:
            # Fallback to the simplified modular version
            from neurocode.ui.neuroplex_modular import ModularNeuroplexWindow

            try:
                from PySide2.QtWidgets import QApplication
            except ImportError:
                from PyQt6.QtWidgets import QApplication

            app = QApplication.instance() or QApplication([])
            window = ModularNeuroplexWindow()
            window.show()

            print("✅ Running simplified modular version")
            return app.exec()

        except ImportError as e2:
            print(f"❌ Could not import simplified modular version: {e2}")
            print("🔄 Falling back to original monolithic version...")

            try:
                # Final fallback to original version
                from launch_neuroplex_v2 import main as original_main

                return original_main()

            except ImportError as e3:
                print(f"❌ All versions failed to import: {e3}")
                print("\n🔧 Troubleshooting suggestions:")
                print("1. Install required dependencies: pip install PySide6")
                print("2. Check that all files are present in the project")
                print("3. Run from the project root directory")
                return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
