#!/usr/bin/env python3
"""
Demo launcher for the hybrid Lyrixa interface
This demonstrates the new Qt + Web hybrid approach
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication, QMessageBox


def setup_logging():
    """Setup logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("lyrixa_hybrid_demo.log"),
        ],
    )


def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        # Just test imports without using them
        import PySide6.QtWebChannel  # noqa: F401
        import PySide6.QtWebEngineWidgets  # noqa: F401

        return True, None
    except ImportError as e:
        return False, f"Missing required dependency: {e}"


def main():
    """Main demo launcher"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Lyrixa Hybrid Interface Demo")

    # Check dependencies
    deps_ok, error_msg = check_dependencies()
    if not deps_ok:
        print(f"❌ Dependency Error: {error_msg}")
        print("💡 Install with: pip install PySide6[WebEngine]")
        return 1

    # Create QApplication
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa Hybrid Demo")
    app.setApplicationVersion("1.0.0")

    try:
        # Try to import and create the hybrid interface
        try:
            from Aetherra.lyrixa.gui.aetherra_main_window_hybrid import (
                AetherraMainWindow,
            )

            logger.info("✅ Successfully imported hybrid interface")
        except ImportError as e:
            logger.error(f"❌ Failed to import hybrid interface: {e}")
            # Fallback to original interface
            try:
                from Aetherra.lyrixa.gui.aetherra_main_window import AetherraMainWindow

                logger.warning("⚠️ Using fallback original interface")
            except ImportError as e2:
                logger.error(f"❌ Failed to import any interface: {e2}")
                QMessageBox.critical(
                    None,
                    "Import Error",
                    f"Could not import Lyrixa interface:\n{e}\n\nFallback also failed:\n{e2}",
                )
                return 1

        # Create and show the main window
        logger.info("🚀 Creating main window...")
        window = AetherraMainWindow()

        # Show with some nice startup effects
        window.show()
        window.raise_()
        window.activateWindow()

        logger.info("✨ Lyrixa Hybrid Interface launched successfully!")
        print("🧠 Lyrixa Hybrid Interface Demo")
        print("📡 Web interface embedded in Qt application")
        print("🔧 Qt controls available in right panel")
        print("💬 Chat interface powered by modern web technologies")
        print("🌟 Cognitive aura overlay still active")
        print("\nPress Ctrl+C in terminal or close window to exit.")

        # Run the application
        return app.exec()

    except Exception as e:
        logger.exception(f"❌ Failed to start application: {e}")
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start Lyrixa interface:\n{e}\n\nCheck the log file for details.",
        )
        return 1

    finally:
        logger.info("🔚 Lyrixa Hybrid Interface Demo shutting down")


if __name__ == "__main__":
    sys.exit(main())
